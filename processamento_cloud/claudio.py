import os
import time
import random
import json
import logging
from sheets_db import get_sheet, spreadsheet
from typing import Optional
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from tratamentos import (pattern_codservico, pattern_valor, pattern_data, pattern_cnpj, limpeza_cnpj, pattern_numero,
                         soma_csrf)
from consulta_for import dados_fornecedor
from acumuladores import acumuladores
from google.api_core import exceptions
from tratamentos_csv import exe

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Definições de variáveis globais e constantes
PROJECT_ID = "REDACTED"  # ID do projeto na Google Cloud
LOCATION = "us"  # Localização do processador
PROCESSOR_ID = "REDACTED"  # ID do processador Document AI
PROCESSOR_VERSION_ID = "REDACTED"  # Versão do processador a ser utilizada
MIME_TYPE = "application/pdf"  # Tipo MIME do documento a ser processado
CREDENTIALS_FILE = "REDACTED.json"  # Caminho para o arquivo de credenciais
PAGE_SELECTOR = [1]  # Seleciona a primeira página para processar
TEMPO_ESPERA = 16  # Tempo de espera entre as requisições, em segundos
DIR_BASE = "REDACTED"  # Caminho base para diretórios de empresas

def process_document(
        project_id: str,
        location: str,
        processor_id: str,
        file_path: str,
        mime_type: str,
        field_mask: Optional[str] = None,
        processor_version_id: Optional[str] = None) -> dict:
    """
    Processa um documento usando o Google Document AI.

    Returns:
        dict: Dicionário com entidades extraídas do documento.
    """
    opts = ClientOptions(
        api_endpoint=f"{location}-documentai.googleapis.com",
        credentials_file=CREDENTIALS_FILE
    )
    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if processor_version_id:
        name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
    else:
        name = client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as image:
        image_content = image.read()

    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    process_options = documentai.ProcessOptions(
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(pages=PAGE_SELECTOR)
    )

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    result = client.process_document(request=request)
    document = result.document
    entities = document.entities

    entities_dict = {}
    for entity in entities:
        if entity.type_ in entities_dict:
            if not isinstance(entities_dict[entity.type_], list):
                entities_dict[entity.type_] = [entities_dict[entity.type_]]
            entities_dict[entity.type_].append(entity.mention_text)
        else:
            entities_dict[entity.type_] = entity.mention_text

    return entities_dict


def listar_abas(spreadsheet):
    """Lista todas as abas disponíveis na planilha."""
    try:
        sheets = spreadsheet.worksheets()
        aba_names = [sheet.title for sheet in sheets]
        logging.info(f'Abas disponíveis: {aba_names}')
        return aba_names
    except Exception as e:
        logging.error(f'Erro ao listar abas: {e}')


def obter_empresas_a_processar(aba_separacao='Separação', aba_fila_claudio='Fila Claudio'):
    """
    Obtém a lista de empresas a serem processadas, considerando as prioridades e empresas já processadas.
    Retorna duas listas: empresas de prioridade 1 e prioridade 2.
    """
    try:
        worksheet_separacao = get_sheet(aba_separacao)
        worksheet_fila_claudio = get_sheet(aba_fila_claudio)

        if worksheet_separacao is None or worksheet_fila_claudio is None:
            logging.error(f'Uma ou ambas as abas "{aba_separacao}" e "{aba_fila_claudio}" não foram encontradas.')
            return [], []

        empresas_processadas = [
            row[0].strip() for row in worksheet_fila_claudio.get_all_values()
            if len(row) >= 2 and row[1].strip().lower() == 'ok claudio'
        ]

        linhas = worksheet_separacao.get_all_values()

        empresas_prioridade_1 = []
        empresas_prioridade_2 = []

        for idx, linha in enumerate(linhas[1:], start=2):
            if len(linha) < 6:
                logging.warning(f"Linha {idx} ignorada por não ter colunas suficientes.")
                continue

            empresa = linha[0].strip()
            prioridade_texto = linha[5].strip()

            try:
                prioridade = int(prioridade_texto)
                if prioridade == 1 and empresa not in empresas_processadas:
                    empresas_prioridade_1.append(empresa)
                elif prioridade == 2 and empresa not in empresas_processadas:
                    empresas_prioridade_2.append(empresa)
            except ValueError:
                logging.warning(f"Linha {idx} ignorada por ter prioridade inválida: '{prioridade_texto}'")

        return empresas_prioridade_1, empresas_prioridade_2
    except Exception as e:
        logging.error(f'Erro ao obter empresas a processar: {e}')
        return [], []


def atualizar_status_empresa(pasta: str, aba='Fila Claudio'):
    """
    Atualiza o status da empresa para 'Ok Claudio' na aba especificada.
    Cria uma nova linha se a empresa não for encontrada.
    """
    try:
        worksheet = get_sheet(aba)
        if worksheet is None:
            logging.error(f'A aba "{aba}" não foi encontrada. Verifique se o nome está correto.')
            return

        for i, row in enumerate(worksheet.get_all_values()):
            if row[0] == pasta:
                worksheet.update_cell(i + 1, 2, "Ok Claudio")
                logging.info(f'Status da empresa "{pasta}" atualizado para "Ok Claudio".')
                break
        else:
            worksheet.append_row([pasta, "Ok Claudio"])
            logging.info(f'Criada nova linha para a empresa "{pasta}" com status "Ok Claudio".')

    except Exception as e:
        logging.error(f'Erro ao atualizar o status da empresa "{pasta}": {e}')


listar_abas(spreadsheet)
logging.info(f'Os dados serão salvos em: REDACTED')

while True:
    empresas_prioridade_1, empresas_prioridade_2 = obter_empresas_a_processar()

    if not empresas_prioridade_1 and not empresas_prioridade_2:
        logging.info("Nenhuma nova empresa encontrada. Aguardando novas pastas para processar...")
        time.sleep(30)
        continue

    for empresa in empresas_prioridade_1 + empresas_prioridade_2:

        dir_empresa = rf'{DIR_BASE}\{empresa}'
        tomados_dir = rf'{dir_empresa}\TOMADOS'

        if not os.path.exists(tomados_dir):
            logging.warning(f"A pasta 'TOMADOS' não existe para a empresa '{empresa}'. Ignorando...")
            continue

        num_files = len(os.listdir(tomados_dir))
        if num_files > 150:
            logging.info(f"Pasta '{empresa}' possui {num_files} arquivos na pasta 'TOMADOS'. Ignorando...")
            continue

        try:
            os.chdir(dir_empresa)
            csv_line = ''

            for arquivo in os.listdir(tomados_dir):
                logging.info(f'Processando arquivo: {arquivo}')

                try:
                    response = process_document(
                        project_id=PROJECT_ID,
                        location=LOCATION,
                        processor_id=PROCESSOR_ID,
                        file_path=rf"TOMADOS\{arquivo}",
                        mime_type=MIME_TYPE,
                        processor_version_id=PROCESSOR_VERSION_ID
                    )
                except exceptions.GoogleAPICallError as api_error:
                    logging.error(f"Erro de API Google ao processar arquivo '{arquivo}': {api_error}")
                    continue
                except Exception as e:
                    logging.error(f"Erro geral ao processar arquivo '{arquivo}': {e}")
                    continue

                # Processamento de dados do arquivo
                prestador = pattern_cnpj(response.get('cnpj_prestador', ''))
                numero_nota = pattern_numero(response.get('numero_nota', ''))
                tomador = pattern_cnpj(response.get('cnpj_tomador', ''))
                valor_total = pattern_valor(response.get('valor_total', '0,00'))
                cod_servico = pattern_codservico(response.get('codigo_servico', ''))
                cofins = pattern_valor(response.get('cofins', '0,00'))
                data_emissao = pattern_data(response.get('data_emissao', ''))
                ir = pattern_valor(response.get('ir', '0,00'))
                pis = pattern_valor(response.get('pis', '0,00'))
                csll = pattern_valor(response.get('csll', '0,00'))
                inss = pattern_valor(response.get('valor_inss', '0,00'))

                prestador_clean = limpeza_cnpj(prestador)
                dados_prestador = dados_fornecedor(prestador_clean)
                acumulador = acumuladores.get(dados_prestador['cnae'], '')

                try:
                    csrf = soma_csrf(pis, cofins, csll)
                except Exception as e:
                    print(f"Erro ao calcular CSRF: {e}")
                    csrf = soma_csrf('', '', '')

                lista_csv = [
                    prestador, dados_prestador['razao_social'], dados_prestador['uf'], dados_prestador['municipio'], '',
                    numero_nota, '', data_emissao, '0', acumulador, '',
                    valor_total, '', valor_total, valor_total, '', '', '',
                    ir, '', '', '', csrf, inss, '', '', '', tomador
                ]

                novo_nome = rf'TOMADOS\{numero_nota} {dados_prestador["razao_social"]}-{random.randint(100000, 999999)}.pdf'
                os.rename(rf'TOMADOS\{arquivo}', novo_nome)

                csv_line += ";".join(lista_csv) + '\n'

                with open('GERAL.txt', 'a') as geral:
                    geral.write(";".join(lista_csv) + '\n')

                time.sleep(TEMPO_ESPERA)

            atualizar_status_empresa(empresa)

            exe(csv_line)

            atualizar_status_empresa(empresa)

        except Exception as e:
            logging.error(f"Erro ao processar a empresa '{empresa}': {e}")

    logging.info("Processamento de todas as empresas concluído. Verificando novas pastas em breve...")
    time.sleep(30)
