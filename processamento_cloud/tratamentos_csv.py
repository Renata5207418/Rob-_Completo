import time
import pandas as pd
from io import StringIO
import re
import consulta_for

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

# Dados de exemplo para serem processados (excluídos os dados sensíveis de datas)
data = """
XX.XXX.XXX/0001-XX;NOME DA EMPRESA 1;PR;CURITIBA;;49067;;<DATA SENSÍVEL>;;0;;;11224,00;;11224,00;11224,00;11224,00;;;;0,00;;;;0,0;0,00;;;
XX.XXX.XXX/0001-XX;NOME DA EMPRESA 2;SP;SAO PAULO;;907177;;<DATA SENSÍVEL>;;0;;;0,00;;0,00;0,00;0,00;;;;0,00;;;;0,0;0,00;;;
XX.XXX.XXX/0001-XX;NOME DA EMPRESA 3;PR;CURITIBA;;258;;<DATA SENSÍVEL>;;0;17;;750,00;;750,00;750,00;750,00;;;;0,00;;;;0,0;0,00;;;
"""

def instancia_df(data):
    """
    Cria um DataFrame a partir dos dados fornecidos no formato CSV.

    A função converte os dados fornecidos em formato de string CSV para um DataFrame pandas,
    atribuindo nomes às colunas e tratando os tipos de dados, substituindo valores nulos por strings vazias.

    Parâmetros:
        data (str): Dados fornecidos no formato CSV.

    Retorna:
        pd.DataFrame: DataFrame contendo os dados processados.
    """
    col_names = ['CPF/CNPJ', 'Razão Social', 'UF', 'Município', 'Endereço',
                 'Número Documento', 'Série', 'Data', 'Situação (0- Regular / 2- Cancelada)', 'Acumulador', 'CFOP',
                 'Valor Serviços', 'Valor Descontos', 'Valor Contábil', 'Base de Calculo', 'Alíquota ISS',
                 'Valor ISS Normal', 'Valor ISS Retido', 'Valor IRRF', 'Valor PIS', 'Valor COFINS', 'Valor CSLL',
                 'Valo CRF', 'Valor INSS', 'Código do Item', 'Quantidade', 'Valor Unitário', 'tomador']

    df = pd.read_csv(StringIO(data), delimiter=';', names=col_names, dtype={'Acumulador': str, 'Número Documento': str})
    df = df.astype(object)
    df.fillna('', inplace=True)

    return df


def elimina_duplicidade(df):
    """
      Elimina as duplicidades no DataFrame baseado no CPF/CNPJ e número de documento.

      A função remove as linhas duplicadas do DataFrame, considerando as colunas 'CPF/CNPJ' e 'Número Documento'.

      Parâmetros:
          df (pd.DataFrame): DataFrame com os dados a serem processados.

      Retorna:
          pd.DataFrame: DataFrame sem as linhas duplicadas.
      """
    df_unique = df.drop_duplicates(subset=['CPF/CNPJ', 'Número Documento'])
    return df_unique


def split_tomador(df):
    """
    Processa os dados de tomador e os separa por estado.

    A função percorre as entradas de tomador no DataFrame e, com base na UF do tomador, atribui um código CFOP
    específico (1933 ou 2933) dependendo da origem do tomador. Os dados são então salvos em arquivos de texto separados.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados a serem processados.

    Retorna:
        None
    """
    unico = df['tomador'].unique()
    for i in unico:
        dados_tomador = consulta_for.dados_fornecedor(re.sub("[^0-9]", "", i))
        uf = dados_tomador.get('uf')
        tomador = df[df['tomador'] == i].copy()  # Cria uma cópia explícita

        tomador.loc[tomador['UF'] == uf, 'CFOP'] = 1933
        tomador.loc[tomador['UF'] != uf, 'CFOP'] = 2933

        tomador.to_csv(fr'TOMADOS {dados_tomador["razao_social"]} - {re.sub("[^0-9]", "", i)}.txt', index=False,
                       sep=";", encoding='latin-1')
        time.sleep(18)


def exe(csv):
    """
     Função principal para processar os dados CSV.

     A função chama outras funções auxiliares para criar o DataFrame, eliminar duplicidades e separar os dados
     de tomador em arquivos individuais.

     Parâmetros:
         csv (str): Dados fornecidos no formato CSV para processamento.

     Retorna:
         None
     """
    df = instancia_df(csv)
    df = elimina_duplicidade(df)
    split_tomador(df)


exe(data)
