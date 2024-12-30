import os
import shutil
import zipfile
import rarfile
import random
import requests

# Gera um número aleatório para ser usado na criação de nomes de arquivos temporários.
numero_aleatorio = random.randint(10000, 99999)


def extrair_arquivos(arquivo):
    """
    Função para extrair arquivos compactados nos formatos ZIP e RAR.

    Parâmetros:
    - arquivo (str): Caminho ou nome do arquivo compactado.

    Funcionalidade:
    - Para arquivos ZIP:
        - Extrai cada item do arquivo mantendo o conteúdo original.
        - Renomeia os arquivos extraídos com um prefixo 'DOCZIP_' seguido de um número aleatório.
    - Para arquivos RAR:
        - Processa de forma semelhante, adicionando o prefixo 'DOCRAR_'.

    Observação:
    - Arquivos com outros formatos são ignorados e exibem uma mensagem de erro.
    """
    _, extensao = os.path.splitext(arquivo)

    if extensao.lower() == '.zip':
        with zipfile.ZipFile(arquivo, 'r') as zip_ref:

            id = 1
            for membro in zip_ref.namelist():
                if not membro.endswith('/'):
                    nome_arquivo = f'DOCZIP_{str(random.randint(10000, 99999))}_' + os.path.basename(membro)
                    with zip_ref.open(membro) as arquivo_zipado, open(nome_arquivo, 'wb') as arquivo_destino:
                        shutil.copyfileobj(arquivo_zipado, arquivo_destino)

                id += 1

    elif extensao.lower() == '.rar':
        with rarfile.RarFile(arquivo, 'r') as rar_ref:
            id = 1
            for membro in rar_ref.namelist():
                if not membro.endswith('/'):
                    nome_arquivo = f'DOCRAR_{str(random.randint(10000, 99999))}_' + os.path.basename(membro)
                    with rar_ref.open(membro) as arquivo_rar, open(nome_arquivo, 'wb') as arquivo_destino:
                        shutil.copyfileobj(arquivo_rar, arquivo_destino)

                id += 1
    else:
        print(f"Formato de arquivo não suportado: {extensao}")


def exe_extract():
    """
        Função para identificar e processar todos os arquivos compactados no diretório atual.

        Funcionalidade:
        - Busca arquivos com as extensões .zip e .rar.
        - Chama a função 'extrair_arquivos()' para descompactá-los.

        Observação:
        - Ignora arquivos que não sejam suportados (diferentes de ZIP e RAR).
        """

    arquivos_zipados = [f for f in os.listdir() if f.lower().endswith(('.rar', '.zip'))]

    try:
        for i in arquivos_zipados:
            arquivo_zip = i
            extrair_arquivos(arquivo_zip)


    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        return
