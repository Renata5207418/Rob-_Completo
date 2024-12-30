import os


def organiza_extensao():
    """
    Função para organizar arquivos por extensão em pastas específicas.

    Extensões suportadas:
    - Planilhas: .csv, .xls, .xlsx
    - Imagens: .jpeg, .jpg, .png
    - Arquivos compactados: .zip, .rar
    - Textos: .txt
    - XML: .xml

    Pastas criadas:
    - PLANILHA: Armazena arquivos CSV, XLS, XLSX.
    - TXT: Armazena arquivos de texto (.txt).
    - IMAGEM_PRINT: Armazena arquivos de imagem (JPEG, JPG, PNG).
    - ZIP: Armazena arquivos compactados (.zip, .rar).
    - XML: Armazena arquivos XML.
    """

    arquivos_xml = [f for f in os.listdir() if f.lower().endswith('.xml')]
    arquivos_xlsx = [f for f in os.listdir() if f.lower().endswith('.xlsx')]
    arquivos_rar = [f for f in os.listdir() if f.lower().endswith('.rar')]
    arquivos_zip = [f for f in os.listdir() if f.lower().endswith('.zip')]
    arquivos_jpeg = [f for f in os.listdir() if f.lower().endswith('.jpeg')]
    arquivos_jpg = [f for f in os.listdir() if f.lower().endswith('.jpg')]
    arquivos_png = [f for f in os.listdir() if f.lower().endswith('.png')]
    arquivos_xls = [f for f in os.listdir() if f.lower().endswith('.xls')]
    arquivos_csv = [f for f in os.listdir() if f.lower().endswith('.csv')]
    arquivos_txt = [f for f in os.listdir() if f.lower().endswith('.txt')]


    for csv in arquivos_csv:
        os.makedirs(f'PLANILHA', exist_ok=True)

        caminho_atual = os.path.join(csv)
        caminho_destino = os.path.join('PLANILHA', csv)
        os.replace(caminho_atual, caminho_destino)

    for txt in arquivos_txt:
        os.makedirs(f'TXT', exist_ok=True)

        caminho_atual = os.path.join(txt)
        caminho_destino = os.path.join('TXT', txt)
        os.replace(caminho_atual, caminho_destino)

    for xls in arquivos_xls:
        os.makedirs(f'PLANILHA', exist_ok=True)

        caminho_atual = os.path.join(xls)
        caminho_destino = os.path.join('PLANILHA', xls)
        os.replace(caminho_atual, caminho_destino)

    for png in arquivos_png:
        os.makedirs(f'IMAGEM_PRINT', exist_ok=True)

        caminho_atual = os.path.join(png)
        caminho_destino = os.path.join('IMAGEM_PRINT', png)
        os.replace(caminho_atual, caminho_destino)

    for jpg in arquivos_jpg:
        os.makedirs(f'IMAGEM_PRINT', exist_ok=True)

        caminho_atual = os.path.join(jpg)
        caminho_destino = os.path.join('IMAGEM_PRINT', jpg)
        os.replace(caminho_atual, caminho_destino)

    for jpeg in arquivos_jpeg:
        os.makedirs(f'IMAGEM_PRINT', exist_ok=True)

        caminho_atual = os.path.join(jpeg)
        caminho_destino = os.path.join('IMAGEM_PRINT', jpeg)
        os.replace(caminho_atual, caminho_destino)

    for zip in arquivos_zip:
        os.makedirs(f'ZIP', exist_ok=True)

        caminho_atual = os.path.join(zip)
        caminho_destino = os.path.join('ZIP', zip)
        os.replace(caminho_atual, caminho_destino)

    for rar in arquivos_rar:
        os.makedirs(f'ZIP', exist_ok=True)

        caminho_atual = os.path.join(rar)
        caminho_destino = os.path.join('ZIP', rar)
        os.replace(caminho_atual, caminho_destino)

    for xml in arquivos_xml:
        os.makedirs(f'XML', exist_ok=True)

        caminho_atual = os.path.join(xml)
        caminho_destino = os.path.join('XML', xml)
        os.replace(caminho_atual, caminho_destino)

    for xlsx in arquivos_xlsx:
        os.makedirs(f'PLANILHA', exist_ok=True)

        caminho_atual = os.path.join(xlsx)
        caminho_destino = os.path.join('PLANILHA', xlsx)
        os.replace(caminho_atual, caminho_destino)
