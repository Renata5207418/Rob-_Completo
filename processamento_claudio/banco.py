import os
import sqlanydb
import logging
import unicodedata
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logs
logging.basicConfig(level=logging.INFO)


class DatabaseConnection:
    """
    Classe para gerenciar conexão e operações com o banco de dados SQL Anywhere.
    """

    def __init__(self, host, port, dbname, user, password):
        """
        Inicializa os parâmetros de conexão.
        """
        self.conn_str = {
            "servername": host,
            "dbn": dbname,
            "userid": user,
            "password": password,
            "LINKS": f"tcpip(host={host};port={port})"
        }
        self.conn = None

    def connect(self):
        """
        Estabelece a conexão com o banco de dados.
        """
        try:
            logging.info("Tentando conectar ao banco de dados...")
            self.conn = sqlanydb.connect(**self.conn_str)
            logging.info("Conexão estabelecida com sucesso.")
        except sqlanydb.Error as e:
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            self.conn = None

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.conn is not None:
            self.conn.close()
            logging.info("Conexão fechada.")

    def execute_query(self, query, params=None):
        """
        Executa uma consulta SQL e retorna os resultados.
        """
        if self.conn is None:
            logging.error("Conexão ao banco não foi estabelecida.")
            return None

        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados
        except sqlanydb.Error as e:
            logging.error(f"Erro ao executar a consulta: {e}")
            return None
        finally:
            cursor.close()


def normalizar_string(s):
    """
    Remove acentos e caracteres especiais de uma string.
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def obter_codigo_empresa(apelido_empresa):
    """
    Busca o código da empresa no banco de dados com base no apelido fornecido.
    Se a empresa for filial, tenta localizar a matriz.
    """
    logging.info(f"Buscando código da empresa com apelido: {apelido_empresa}")

    # Normaliza o apelido da empresa
    apelido_empresa_normalizado = normalizar_string(apelido_empresa)

    logging.info(f"Parâmetro normalizado para consulta: '{apelido_empresa_normalizado}'")

    # Carregar parâmetros do banco de dados do arquivo .env
    db_params = {
        "host": os.getenv('DB_HOST'),
        "port": int(os.getenv('DB_PORT')),
        "dbname": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD')
    }

    # Estabelece conexão com o banco
    db_conn = DatabaseConnection(**db_params)
    db_conn.connect()
    if not db_conn.conn:
        logging.error("Conexão não foi estabelecida. Encerrando busca.")
        return None, None

    # Consulta para buscar empresa
    query_empresa = """
        SELECT codi_emp, apel_emp, cgce_emp, LEFT(cgce_emp, 8) AS cnpj_base
        FROM bethadba.geempre 
        WHERE apel_emp LIKE ?;
    """

    empresa = db_conn.execute_query(query_empresa, (f'%{apelido_empresa_normalizado}%',))

    # Se encontrar empresa
    if empresa:
        codi_emp = empresa[0][0]
        apel_emp = empresa[0][1]
        cnpj_base = empresa[0][3]
        logging.info(f"Código encontrado: {codi_emp}, Apelido: {apel_emp}, CNPJ Base: {cnpj_base}")

        # Verifica se é filial
        if 'FILIAL' in apel_emp.upper():
            query_matriz = """
                SELECT codi_emp, apel_emp
                FROM bethadba.geempre
                WHERE LEFT(cgce_emp, 8) = ? AND UPPER(apel_emp) NOT LIKE '%FILIAL%';
            """

            matriz = db_conn.execute_query(query_matriz, (cnpj_base,))
            if matriz:
                codi_emp_matriz = matriz[0][0]
                apel_emp_matriz = matriz[0][1]
                logging.info(f"Matriz encontrada: Código {codi_emp_matriz}, Apelido {apel_emp_matriz}")
                db_conn.close()
                return codi_emp, codi_emp_matriz
            else:
                logging.warning("Matriz não encontrada.")
                db_conn.close()
                return codi_emp, None
        else:
            logging.info("Empresa não é uma filial.")
            db_conn.close()
            return codi_emp, None
    else:
        logging.error(f"Empresa com apelido '{apelido_empresa}' não encontrada.")
        db_conn.close()
        return None, None
