import requests
import re


def dados_fornecedor(cnpj: str):
    """
    Consulta os dados de um fornecedor a partir do seu CNPJ na API ReceitaWS.

    A função realiza uma requisição GET para a API ReceitaWS, que retorna informações sobre o fornecedor,
    como sua razão social, UF (Unidade da Federação), município e o código CNAE. Caso ocorra algum erro
    durante a requisição ou no processamento dos dados, a função retorna um dicionário vazio com os campos
    correspondentes.

    Parâmetros:
        cnpj (str): O CNPJ do fornecedor que será consultado na API.

    Retorna:
        dict: Um dicionário contendo as seguintes chaves:
            - 'razao_social' (str): Razão social do fornecedor.
            - 'uf' (str): Unidade da Federação onde o fornecedor está registrado.
            - 'municipio' (str): Município onde o fornecedor está localizado.
            - 'cnae' (str): Código CNAE do fornecedor, com caracteres não numéricos removidos.
    """
    try:

        response = requests.get(url=rf'https://receitaws.com.br/v1/cnpj/{cnpj}')
        response_json = response.json()
        razao_social = re.sub(r'[^0-9a-zA-Z ]', '', response_json.get('nome', ''))
        uf = response_json.get('uf', '')
        municipio = response_json.get('municipio', '')
        cnae_grupo = response_json.get('atividade_principal', '')[0]
        cod_cnae = cnae_grupo['code']
        cod_cnae_limpo = re.sub(r'[^0-9]', '', cod_cnae)

        return {'razao_social': f'{razao_social}',
                'uf': f'{uf}',
                'municipio': f'{municipio}',
                'cnae': f'{cod_cnae_limpo}'}

    except Exception as e:
        print(f"Erro ao obter dados do fornecedor para o CNPJ '{cnpj}': {e}")
        return {'razao_social': '', 'uf': '', 'municipio': '', 'cnae': ''}
