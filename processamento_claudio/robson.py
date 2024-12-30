import time
import datetime
import requests
import logging
from extract import exe_extract
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import base64
import os
import shutil
import PyPDF2
import io
import traceback
from extensoes import organiza_extensao
import random
from sheets_db import get_sheet, post_sheet
import json
from banco import obter_codigo_empresa

logging.basicConfig(level=logging.DEBUG)

# Variáveis de configuração (caminhos dos diretórios locais do sistema devem ser configurados no .env)
BASE_CLIENTES = os.getenv("BASE_CLIENTES")  # Caminho para a pasta de clientes
BASE_TRIAGEM = os.getenv("BASE_TRIAGEM")  # Caminho para a pasta de triagem
BASE_TESTES = os.getenv("BASE_TESTES")  # Caminho para a pasta de testes

# Pastas de destino para documentos
PASTAS = {
    'guia': 'DOCUMENTOS GERAIS',
    'boleto': 'DOCUMENTOS GERAIS',
    'invoice_exterior': 'INVOICE',
    'fatura_consumo': 'DOCUMENTOS GERAIS',
    'comprovante_pagamento': 'DOCUMENTOS GERAIS',
    'danfe': 'DANFE',
    'nota_servico': 'TOMADOS',
    'extrato': 'EXTRATO'
}
TOMADOS_DIR = 'TOMADOS'
LOW_CONFIDENCE_DIR = 'LOW_CONFIDENCE'
ERRO_PROCESSAMENTO_DIR = 'ERRO_PROCESSAMENTO'
LIMITE_PAGINAS_DIR = 'LIMITE_PAGINAS'


def obter_mes_ano_anterior():
    """Retorna o mês e ano anteriores ao atual."""
    data_atual = datetime.datetime.now()
    mes_anterior = data_atual - datetime.timedelta(days=data_atual.day)
    return mes_anterior.strftime("%m"), mes_anterior.strftime("%Y")


mes_anterior, ano_anterior = obter_mes_ano_anterior()
pasta_mes_anterior = f"{mes_anterior}_{ano_anterior}"


# Estruturas de diretório
PASTA_FINAL = os.getenv("PASTA_FINAL")
BASE_CONTABIL = os.getenv("BASE_CONTABIL").format(ano_anterior=ano_anterior, mes_anterior=mes_anterior)
BASE_FISCAL = os.getenv("BASE_FISCAL").format(ano_anterior=ano_anterior, mes_anterior=mes_anterior)


def requisicao_robson(pdf_base64_string):
    """Função para realizar a requisição para o serviço de análise de documentos."""
    # Caminho do arquivo de credenciais, configurável via .env
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/...']
    )

    credentials.refresh(Request())
    url = ("GOOGLE_API_URL")

    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "skipHumanReview": True,
        "rawDocument": {
            "mimeType": "application/pdf",
            "content": f"{pdf_base64_string}"}
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        json_retorno = response.json()['document']['entities']
        retorno_ordenado = sorted(json_retorno, key=lambda x: x['confidence'], reverse=True)
        classificacao_dict = retorno_ordenado[0]
        classificacao = [classificacao_dict['type'],
                         classificacao_dict['confidence']]
    except:
        classificacao = ['extrato', 0.4]

    return classificacao



def pagina_unica(documento):
    """Processa documentos PDF com uma única página e retorna a classificação."""
    with open(documento, 'rb') as doc_unico:
        pdf_unico = PyPDF2.PdfReader(doc_unico)
        dados = PyPDF2.PdfWriter()
        dados.add_page(pdf_unico.pages[0])
        bytes_doc = io.BytesIO()
        dados.write(bytes_doc)
        value_bytes = bytes_doc.getvalue()

        response = base64.b64encode(value_bytes).decode('utf-8')
        retorno_robson = requisicao_robson(response)
        time.sleep(1.5)
        return retorno_robson


def varias_paginas(documento):
    """Processa documentos PDF com várias páginas."""

    def split_tomados(base64_string, nome):
        """Função auxiliar para dividir documentos PDF com várias páginas e classificar como 'TOMADOS'."""
        pdf_bytes = base64.b64decode(base64_string)
        pdf_file_like = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file_like)
        writer_split = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer_split.add_page(page)

        os.makedirs(TOMADOS_DIR, exist_ok=True)

        with open(f'{TOMADOS_DIR}/SPLIT_DOCUMENTO_{str(random.randint(10000, 99999))}_{nome}', 'wb') as novo_pdf:
            writer_split.write(novo_pdf)

    LIMITE_PAGINAS_DIR = "LIMITE_PAGINAS"
    caminho_absoluto_documento = os.path.abspath(documento)

    with open(caminho_absoluto_documento, 'rb') as document:
        pdf_completo = PyPDF2.PdfReader(document)

        if len(pdf_completo.pages) > 299:
            print(f"PDF {documento} possui mais de 300 páginas, movendo para a pasta '{LIMITE_PAGINAS_DIR}'.")
            os.makedirs(LIMITE_PAGINAS_DIR, exist_ok=True)
            document.close()

            novo_caminho = os.path.join(LIMITE_PAGINAS_DIR, os.path.basename(documento))
            shutil.move(caminho_absoluto_documento, novo_caminho)

            return ['ignore', 0]

        index = 0
        primeira_pagina = ''
        for page in pdf_completo.pages:
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            bytes_buffer = io.BytesIO()
            writer.write(bytes_buffer)
            writer_bytes = bytes_buffer.getvalue()
            base = base64.b64encode(writer_bytes).decode('utf-8')
            robson = requisicao_robson(base)

            if robson[0] == 'nota_servico' and robson[1] > 0.99:
                split_tomados(base, documento)

            primeira_pagina = robson if index == 0 else primeira_pagina
            time.sleep(1.5)
            index += 1

    return primeira_pagina


def exe(pasta_mesa):
    """Executa a extração de dados dos arquivos na pasta."""
    diretorio = os.path.join(os.getenv('BASE_TRIAGEM'), pasta_mesa)
    os.chdir(diretorio)
    exe_extract()
    organiza_extensao()
    arquivos = [f for f in os.listdir() if os.path.isfile(f)]

    for i in arquivos:
        try:
            with open(i, 'rb') as doc:
                pdf = PyPDF2.PdfReader(doc)
                paginas = len(pdf.pages)

            if paginas > 299:
                destino = LIMITE_PAGINAS_DIR
                caminho_destino = os.path.join(destino, os.path.basename(i))
                os.makedirs(destino, exist_ok=True)
                shutil.move(i, caminho_destino)
                print(f"PDF {i} possui mais de 300 páginas, movido para a pasta '{destino}'")
                continue

            if paginas == 1:
                classificacao = pagina_unica(i)
                if classificacao[1] > 0.99:
                    destino = PASTAS[classificacao[0]]
                    caminho_destino = os.path.join(destino)
                    os.makedirs(caminho_destino, exist_ok=True)
                    shutil.move(i, caminho_destino)
                else:
                    destino = LOW_CONFIDENCE_DIR
                    caminho_destino = os.path.join(destino)
                    os.makedirs(caminho_destino, exist_ok=True)
                    shutil.move(i, caminho_destino)
            else:
                classificacao = varias_paginas(i)

                if classificacao[1] > 0.99:
                    destino = PASTAS[classificacao[0]]
                    caminho_destino = os.path.join(destino)
                    os.makedirs(caminho_destino, exist_ok=True)
                    shutil.move(i, caminho_destino)
                else:
                    destino = LOW_CONFIDENCE_DIR
                    caminho_destino = os.path.join(destino)
                    os.makedirs(caminho_destino, exist_ok=True)
                    shutil.move(i, caminho_destino)

        except Exception as e:
            destino = ERRO_PROCESSAMENTO_DIR
            os.makedirs(destino, exist_ok=True)
            shutil.move(i, destino)
            erro_detalhado = traceback.format_exc()
            logging.error(f"Erro ao processar o arquivo {i}: {e}, movido para {destino}")
            logging.error(f"Detalhes do erro:\n{erro_detalhado}")


def get_ultima():
    """Obtém a última pasta separada."""
    with open('separadas.json', 'r') as arquivo:
        dados = json.load(arquivo)

    return dados['ultima_separada']


def set_ultima(pasta):
    """Atualiza a última pasta separada no arquivo JSON."""
    os.chdir(r'C:\Users\usuario\seu_projeto')
    ultima = pasta[:5]
    with open('separadas.json', 'r') as arquivo:
        dados = json.load(arquivo)
    dados['ultima_separada'] = int(ultima)
    with open('separadas.json', 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)


def pastas_separar():
    """Retorna uma lista de pastas a serem separadas."""
    relacao_pastas = {}
    pastas_diretorio = os.listdir(BASE_TRIAGEM)

    for i in pastas_diretorio:
        hifen = i.find('-')
        req = i[:hifen]
        relacao_pastas[int(req)] = i

    ultima_separada = get_ultima()
    ultima_baixada = get_sheet(aba="Download")

    separar = []
    if ultima_baixada > ultima_separada:
        intervalo = range(int(ultima_separada) + 1, int(ultima_baixada) + 1)
        for i in intervalo:
            try:
                separar.append(relacao_pastas[i])
            except KeyError:
                continue

    return separar


def mover_cliente(pasta):
    """Move as pastas do cliente para os diretórios apropriados."""
    try:
        hifen = pasta.find("-") + 1
        apelido = pasta[hifen:].strip()

        codi_emp, codi_emp_matriz = obter_codigo_empresa(apelido)
        if not codi_emp:
            return "NÃO ENVIADO PARA PASTA DO CLIENTE"

        if codi_emp_matriz:
            codigo_para_busca = codi_emp_matriz
            logging.info(f"Empresa {codi_emp} é uma filial. Usando código da matriz {codi_emp_matriz}.")
        else:
            codigo_para_busca = codi_emp

        pasta_cliente = next((nome_pasta for nome_pasta in os.listdir(BASE_CLIENTES)
                              if nome_pasta.startswith(f"{codigo_para_busca}-")), None)

        if not pasta_cliente:
            logging.warning(f"Pasta do cliente com código {codigo_para_busca} não encontrada.")
            return "NÃO ENVIADO PARA PASTA DO CLIENTE"

        origem = os.path.join(BASE_TRIAGEM, pasta)
        destino_contabil = os.path.join(BASE_CLIENTES, pasta_cliente, BASE_CONTABIL, PASTA_FINAL, pasta)
        destino_fiscal = os.path.join(BASE_CLIENTES, pasta_cliente, BASE_FISCAL, PASTA_FINAL, pasta)

        os.makedirs(destino_contabil, exist_ok=True)
        os.makedirs(destino_fiscal, exist_ok=True)

        shutil.copytree(origem, destino_contabil, dirs_exist_ok=True)
        shutil.copytree(origem, destino_fiscal, dirs_exist_ok=True)

        logging.info(f"Conteúdo da pasta {pasta} movido para Contábil e Fiscal com sucesso.")
        return "Sucesso"

    except Exception as e:
        logging.error(f"Erro ao mover cliente {pasta}: {e}")
        erro_detalhado = traceback.format_exc()
        logging.error(f"Detalhes do erro:\n{erro_detalhado}")
        return "NÃO ENVIADO PARA PASTA DO CLIENTE"


while True:
    try:
        pastas = pastas_separar()
        logging.info(f"Pastas encontradas: {pastas}")

        for i in pastas:
            logging.info(f"Processando a pasta: {i}")
            pasta = i
            exe(i)
            logging.info(f"Execução da pasta {i} concluída.")
            set_ultima(i)
            logging.info(f"Última pasta separada atualizada: {i}")
            pasta_cliente = mover_cliente(i)
            logging.info(f"Movimentação da pasta {i} para cliente concluída: {pasta_cliente}")

            path_pasta = os.listdir(os.path.join(os.getenv("BASE_TRIAGEM"), f'{i}'))
            gerou_tomados = "SIM" if "TOMADOS" in path_pasta else "NÃO"
            gerou_extrato = "SIM" if "EXTRATO" in path_pasta else "NÃO"

            planilha = [i, "Separado", pasta_cliente, gerou_tomados, gerou_extrato]
            post_sheet("Separação", planilha)

        time.sleep(60)

    except Exception as e:
        logging.error(f"Erro durante a execução principal: {e}")
        logging.error(f"Detalhes do erro:\n{traceback.format_exc()}")
        time.sleep(60)
