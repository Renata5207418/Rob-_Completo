import os
import shutil
import time
import json
import logging
from sheets_db import post_sheet  # Integração com planilhas Google Sheets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# ===================================
# Configurações Iniciais e Variáveis
# ===================================

# Carregar configurações do arquivo .env
url = os.getenv('PORTAL_URL')  # URL do portal, carregada do .env
dir = os.getenv('CHROME_USER_DIR')  # Caminho do perfil do Chrome, carregado do .env

# Configuração do navegador Chrome
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={dir}")  # Usa o perfil especificado no .env

# Seletores CSS utilizados para localizar elementos na página
css_anexos = r'[id^="a-attachment_"]'
css_os = r'div.filters-inline-group:nth-child(1) > span:nth-child(2)'
css_cliente = r'div.filters-inline-group:nth-child(3) > span:nth-child(2)'
css_apelido = r'div.filters-inline-group:nth-child(2) > span:nth-child(2)'
css_fechar = r'button.btn-lg:nth-child(1)'
css_pesquisa = r'.search__input'
css_detalhes = r'.bento-icon-info-filled'
css_assunto = r'div.row:nth-child(3) > div:nth-child(2) > span:nth-child(1)'
css_descricao = r'span.detail-data:nth-child(1)'


# ===================================
# Funções Auxiliares
# ===================================

def ultima_baixada():
    """
    Lê o arquivo ultima.json para verificar a última solicitação baixada.
    Retorna o número da última solicitação processada.
    """
    with open('ultima.json', 'r') as ultima:
        dados = json.load(ultima)
        ultima_baixada = dados['ultima']
    return ultima_baixada


def abrir_browser():
    """
    Abre o navegador Chrome configurado com o perfil especificado.
    Retorna o driver Selenium do navegador aberto.
    """
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)  # Aguarda o carregamento da página
    return driver


def get_ultima(driver):
    """
    Busca e retorna o número da última solicitação disponível no portal.
    """
    ultima = driver.find_element(By.CSS_SELECTOR, '.wj-state-active').text
    return ultima


def abrir_os(os, driver):
    """
    Busca e abre uma solicitação específica informada pelo número.
    """
    driver.find_element(By.CSS_SELECTOR, css_pesquisa).clear()
    time.sleep(0.5)
    driver.find_element(By.CSS_SELECTOR, css_pesquisa).send_keys(os)
    time.sleep(5)  # Tempo para carregar os resultados da busca
    driver.find_element(By.CSS_SELECTOR, css_detalhes).click()
    time.sleep(2)  # Aguarda a abertura dos detalhes


def download(driver):
    """
    Baixa todos os anexos disponíveis na solicitação aberta.
    """
    anexos = driver.find_elements(By.CSS_SELECTOR, '[id^="a-attachment_"]')  # Localiza os anexos
    quantidade_anexos = len(anexos)  # Quantidade de anexos encontrados

    for i in range(quantidade_anexos):
        driver.find_element(By.CSS_SELECTOR, f'#a-attachment_{i} > em').click()
        time.sleep(1.2)  # Intervalo entre downloads


def fechar(driver):
    """
    Fecha a solicitação aberta e retorna à tela inicial.
    """
    driver.find_element(By.CSS_SELECTOR, css_fechar).click()
    time.sleep(2)  # Aguarda o fechamento completo


# ===================================
# Fluxo Principal
# ===================================

def exe():
    """
    Executa o fluxo completo:
    1. Abre o navegador e verifica novas solicitações.
    2. Baixa arquivos anexos.
    3. Registra as informações na planilha do Google Sheets.
    """
    try:
        # Abre o navegador
        driver = abrir_browser()
        time.sleep(3)

        # Recupera última solicitação aberta e baixada
        ultima_aberta = get_ultima(driver)
        ultimo_download = ultima_baixada()

        # Verifica se há novas solicitações a serem processadas
        if int(ultimo_download) < int(ultima_aberta):

            # Loop pelas solicitações pendentes
            baixar = range(int(ultimo_download) + 1, int(ultima_aberta) + 1)
            for i in baixar:
                try:
                    abrir_os(i, driver)  # Abre a solicitação específica
                except:
                    continue  # Pula para a próxima em caso de erro

                # Coleta informações da solicitação
                cliente = driver.find_element(By.CSS_SELECTOR, css_cliente).text
                apelido = driver.find_element(By.CSS_SELECTOR, css_apelido).text
                solicitacao = driver.find_element(By.CSS_SELECTOR, css_os).text
                quantidade = driver.find_elements(By.CSS_SELECTOR, css_anexos)
                quantidade_cont = len(quantidade)

                # Fecha a solicitação
                fechar(driver)
                time.sleep(2)

                # Atualiza o número da última solicitação processada
                with open('ultima.json', 'r') as arquivo:
                    dados = json.load(arquivo)
                dados['ultima'] = i
                with open('ultima.json', 'w') as arquivo:
                    json.dump(dados, arquivo, indent=4)

                # Registra informações na planilha do Google Sheets
                dados = [i, solicitacao, apelido, cliente, quantidade_cont, 'Sucesso']
                post_sheet('Auditoria', dados)

        # Fecha o navegador ao final do processamento
        driver.quit()

    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")


# ===================================
# Execução Contínua
# ===================================
while True:
    exe()
    time.sleep(200)  # Aguarda 200 segundos antes de executar novamente
