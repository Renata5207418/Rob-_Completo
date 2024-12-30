import re


def pattern_codservico(cod: str):
    """
    Limpa o código do serviço, removendo qualquer caractere não numérico.

    A função recebe um código de serviço, remove qualquer caractere não numérico e retorna apenas os números
    presentes no código. A quantidade de números é determinada pela quantidade de caracteres no código limpo.

    Parâmetros:
        cod (str): O código do serviço a ser processado.

    Retorna:
        str: O código de serviço limpo, contendo apenas os números.
    """
    cod = cod
    cod_numerico = re.sub(r'[^0-9]', '', cod)
    quantidade = len(cod_numerico)

    # df = pd.read_excel('acumuladores.xlsx', sheet_name=str(quantidade), dtype=str)
    # acumulador = df[df['cod_serv'] == cod]['acumulador']

    return cod_numerico


def pattern_valor(valor: str):
    """
      Limpa o valor, removendo qualquer caractere que não seja numérico ou vírgula.

      A função recebe um valor monetário no formato de string e remove qualquer caractere que não seja numérico ou vírgula,
      retornando a string limpa.

      Parâmetros:
          valor (str): O valor monetário a ser processado.

      Retorna:
          str: O valor limpo, contendo apenas números e vírgulas.
      """
    valor = re.sub(r'[^0-9,]', '', valor)
    return valor


def pattern_data(data: str):
    """
    Limpa a data, removendo qualquer caractere que não seja numérico ou barra.

    A função recebe uma data no formato de string e remove qualquer caractere que não seja numérico ou barra (/),
    e retorna apenas os 10 primeiros caracteres, correspondendo ao formato "dd/mm/aaaa".

    Parâmetros:
        data (str): A data a ser processada.

    Retorna:
        str: A data limpa, no formato "dd/mm/aaaa".
    """
    data = re.sub(r'[^0-9/]', '', data)
    data = data[:10]
    return data


def limpeza_cnpj(cnpj: str):
    """
    Limpa o CNPJ, removendo caracteres não numéricos e preenchendo com zeros à esquerda.

    A função recebe um CNPJ no formato de string e remove qualquer caractere que não seja numérico,
    preenchendo com zeros à esquerda para garantir que tenha 14 dígitos.

    Parâmetros:
        cnpj (str): O CNPJ a ser processado.

    Retorna:
        str: O CNPJ limpo, com exatamente 14 dígitos numéricos.
    """
    limpeza = re.sub(r'[^0-9]', '', cnpj)
    digitos = limpeza.zfill(14)

    return digitos


def pattern_cnpj(cnpj: str):
    """
    Formata o CNPJ no padrão 'XX.XXX.XXX/XXXX-XX'.

    A função recebe um CNPJ limpo de 14 dígitos e retorna o CNPJ formatado no padrão 'XX.XXX.XXX/XXXX-XX'.

    Parâmetros:
        cnpj (str): O CNPJ a ser processado.

    Retorna:
        str: O CNPJ formatado no padrão 'XX.XXX.XXX/XXXX-XX'.
    """
    digitos = limpeza_cnpj(cnpj)
    pattern = f'{digitos[0:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:14]}'
    return pattern


def pattern_numero(numero: str):
    """
    Limpa o número, removendo zeros à esquerda e caracteres não numéricos.

    A função recebe um número no formato de string e remove qualquer caractere não numérico, além de remover
    os zeros à esquerda, retornando apenas os números.

    Parâmetros:
        numero (str): O número a ser processado.

    Retorna:
        str: O número limpo, sem zeros à esquerda.
    """
    apenas_numeros = re.sub(r'[^0-9]', '', numero)
    pattern = re.sub(r'^0+', '', apenas_numeros)
    return pattern


def soma_csrf(pis='0,00', cofins='0,00', csll='0,00'):
    """
    Calcula o total do CSRF somando os valores de PIS, COFINS e CSLL.

    A função recebe os valores de PIS, COFINS e CSLL no formato de string, realiza a conversão para float,
    soma os valores e retorna o total como uma string no formato "xx,xx".

    Parâmetros:
        pis (str, opcional): O valor do PIS a ser somado. O valor padrão é '0,00'.
        cofins (str, opcional): O valor do COFINS a ser somado. O valor padrão é '0,00'.
        csll (str, opcional): O valor do CSLL a ser somado. O valor padrão é '0,00'.

    Retorna:
        str: O total do CSRF como uma string no formato "xx,xx".
    """
    pis = pis if pis else '0,00'
    cofins = cofins if cofins else '0,00'
    csll = csll if csll else '0,00'

    pis_float = float(pis.replace(",", "."))
    cofins_float = float(cofins.replace(",", "."))
    csll_float = float(csll.replace(",", "."))

    csrf = pis_float + cofins_float + csll_float
    csrf_str = str(csrf).replace(".", ",")

    return csrf_str
