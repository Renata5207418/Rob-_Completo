import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# ================================
# Configuração do Google Sheets API
# ================================

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Escopos de permissão para acessar o Google Sheets e o Google Drive
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Carrega as credenciais do arquivo JSON (definido no .env)
credentials_path = os.getenv('GOOGLE_CREDENTIALS_JSON')
spreadsheet_key = os.getenv('SPREADSHEET_KEY')

# Autenticação com o Google Sheets API
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(credentials)

# Acesso à planilha específica pelo ID fornecido no .env
spreadsheet = client.open_by_key(spreadsheet_key)


# ================================
# Funções para Manipulação do Google Sheets
# ================================

def post_sheet(aba='Sheet1', data=['1000']):
    """
    Insere uma nova linha na aba especificada do Google Sheets.

    Parâmetros:
    - aba (str): Nome da aba na planilha onde os dados serão inseridos. Padrão: 'Sheet1'.
    - data (list): Lista de dados a serem inseridos. Exemplo: ['valor1', 'valor2'].

    Funcionalidade:
    - Obtém o número da última linha preenchida.
    - Insere os dados fornecidos na próxima linha disponível.
    """
    worksheet = spreadsheet.worksheet(aba)  # Acessa a aba especificada
    data = [data]  # Transforma os dados em formato de lista dentro de outra lista
    col_values = worksheet.col_values(1)  # Pega os valores da primeira coluna
    last_row = len(col_values) + 1  # Calcula o número da próxima linha disponível
    worksheet.insert_row(data[0], last_row)  # Insere os dados na próxima linha


def get_sheet(aba='Sheet1'):
    """
    Retorna todos os valores da primeira coluna da aba especificada.

    Parâmetros:
    - aba (str): Nome da aba na planilha onde os dados serão buscados. Padrão: 'Sheet1'.

    Retorno:
    - col_values (list): Lista com os valores encontrados na primeira coluna.

    Funcionalidade:
    - Lê e retorna todos os valores preenchidos na primeira coluna.
    """
    worksheet = spreadsheet.worksheet(aba)  # Acessa a aba especificada
    col_values = worksheet.col_values(1)  # Obtém todos os valores da primeira coluna
    return col_values  # Retorna os valores encontrados
