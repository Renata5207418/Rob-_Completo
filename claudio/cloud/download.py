import os
import time
import json
import shutil
import logging
from selenium import webdriver
from sheets_db import post_sheet
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from dotenv import load_dotenv

"""
Script: download.py
Descrição: Automatiza o download de anexos associados a ordens de serviço no portal Onvio.
Versão: 1.0.0

Funcionalidades:
- Acesso ao portal Onvio via Selenium.
- Login automático com credenciais armazenadas no .env.
- Verificação e download de arquivos anexos nas ordens de serviço.
- Organização dos arquivos em pastas por ordem de serviço.
- Registro de logs e status no Google Sheets.

Dependências:
- Selenium
- Python-dotenv
- Sheets_db
"""

# Carregar variáveis do .env
load_dotenv()

# Configurações do Selenium e do Portal
PORTAL_URL = os.getenv('PORTAL_URL')
CHROME_USER_DIR = os.getenv('CHROME_USER_DIR')
PORTAL_USER = os.getenv('PORTAL_USER')
PORTAL_PASS = os.getenv('PORTAL_PASS')
PASTA_BAIXADOS = os.getenv('PASTA_BAIXADOS')
PASTA_ORIGEM = os.getenv('PASTA_ORIGEM')
PASTA_SEPARADOS = os.getenv('PASTA_SEPARADOS')

chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={CHROME_USER_DIR}")

# Configuração de Logs
logging.basicConfig(filename='download_logs.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Seletores CSS
css_anexos = r'[id^="a-attachment_"]'
css_os = r'div.filters-inline-group:nth-child(1) > span:nth-child(2)'
css_cliente = r'div.filters-inline-group:nth-child(3) > span:nth-child(2)'
css_apelido = r'div.filters-inline-group:nth-child(2) > span:nth-child(2)'
css_fechar = r'button.btn-lg:nth-child(1)'
css_pesquisa = r'.search__input'
css_detalhes = r'.bento-icon-info-filled'
css_assunto = r'div.row:nth-child(3) > div:nth-child(2) > span:nth-child(1)'
css_descricao = r'span.detail-data:nth-child(1)'


def ultima_baixada():
    """
    Lê o arquivo JSON e retorna o número da última ordem de serviço baixada.
    """
    with open('ultima.json', 'r') as ultima:
        dados = json.load(ultima)
        ultima_baixada = dados['ultima']
    return ultima_baixada


def realizar_primeiro_clique(driver):
    """
    Realiza o primeiro clique para iniciar o login no portal.
    """
    try:
        driver.maximize_window()
        WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.ID, "trauth-continue-signin-btn"))
        )
        login_button = driver.find_element(By.ID, "trauth-continue-signin-btn")
        if login_button.is_displayed() and login_button.is_enabled():
            driver.execute_script("arguments[0].click();", login_button)
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "uid"))
        )
    except Exception as e:
        logging.error(f"Erro ao realizar o primeiro clique: {e}")


def realizar_login(driver, usuario, senha):
    """
    Realiza o login no portal utilizando as credenciais fornecidas.
    """
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "password"))
        )
        email_input = driver.find_element(By.NAME, "username")
        email_input.clear()
        email_input.send_keys(usuario)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(senha)

        entrar_button = driver.find_element(By.CSS_SELECTOR, 'button._button-login-password')
        driver.execute_script("arguments[0].click();", entrar_button)

        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".portal-homepage"))
        )
    except Exception as e:
        logging.error(f"Erro ao realizar login: {e}")


def abrir_browser():
    """
    Abre o navegador e realiza o login no portal.
    """
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(PORTAL_URL)
    realizar_primeiro_clique(driver)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url or "auth.thomsonreuters" in d.current_url
    )
    if "login" in driver.current_url:
        realizar_login(driver, PORTAL_USER, PORTAL_PASS)
    if "dashboard-core-center" in driver.current_url:
        driver.get(PORTAL_URL)
    return driver


def download(driver):
    """
    Baixa todos os anexos disponíveis na ordem de serviço aberta.
    """
    anexos = driver.find_elements(By.CSS_SELECTOR, css_anexos)
    for i, anexo in enumerate(anexos):
        try:
            anexo.click()
            time.sleep(1.2)
        except Exception as e:
            logging.error(f"Erro ao baixar anexo {i + 1}: {e}")


def fechar(driver):
    """
    Fecha a ordem de serviço atual.
    """
    driver.find_element(By.CSS_SELECTOR, css_fechar).click()
    time.sleep(2)


def exe():
    """
    Executa o fluxo principal de baixar ordens de serviço.
    """
    try:
        driver = abrir_browser()
        ultima_aberta = get_ultima(driver)
        ultimo_dowload = ultima_baixada()

        if int(ultimo_dowload) < int(ultima_aberta):
            for i in range(int(ultimo_dowload) + 1, int(ultima_aberta) + 1):
                abrir_os(i, driver)
                download(driver)
                fechar(driver)
                salvar_dados(i)
        driver.quit()
    except Exception as e:
        logging.error(f"Erro na execução do fluxo: {e}")


def salvar_dados(id_os):
    """
    Salva o status da OS no JSON e move os arquivos baixados para as pastas corretas.
    """
    destino = os.path.join(PASTA_BAIXADOS, f'OS-{id_os}')
    os.makedirs(destino, exist_ok=True)

    for arquivo in os.listdir(PASTA_ORIGEM):
        shutil.move(os.path.join(PASTA_ORIGEM, arquivo), os.path.join(destino, arquivo))

    shutil.copytree(destino, os.path.join(PASTA_SEPARADOS, f'OS-{id_os}'))


while True:
    exe()
    time.sleep(200)
