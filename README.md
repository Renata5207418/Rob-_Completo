# 📊 Sistema de Processamento e Integração de Dados - Projeto Claudio

Este projeto automatiza o **processamento de dados**, realizando integração com serviços em nuvem e manipulação de arquivos via scripts Python. Ele contém **três robôs separados**, que operam de forma independente para diferentes funcionalidades.

---

## 🚀 **Funcionalidades**

- 📥 **Importação de Dados:** Leitura e validação de arquivos CSV e Excel.
- ☁️ **Integração com Nuvem:** Conexão com APIs para armazenamento e consulta.
- 🔧 **Processamento e Análise:** Tratamento de dados e geração de relatórios.
- 📊 **Exportação Personalizada:** Criação de arquivos organizados para análises posteriores.
- 📝 **Logs Detalhados:** Registro de processamento para diagnóstico de erros.

### Robôs Disponíveis:

1. 🤖 **Robô de Download**: Utilizando Selenium, este robô acessa um portal e faz o download dos arquivos necessários para o processamento.
2. 🤖 **Robô de Nuvem**: Conecta-se com APIs de serviços em nuvem, realiza integrações e organiza os dados em pastas para posterior análise.
3. 🤖 **Robô de Exportação**: Processa os dados obtidos, realiza transformações necessárias e exporta-os para arquivos organizados e prontos para análise posterior.

---


## 🛠️ **Pré-requisitos**

- **Python 3.10 ou superior.**
- Bibliotecas listadas no arquivo `requirements.txt`.
- Configurações de ambiente no arquivo **`.env`**.

---

## 🧩 **Instalação**

1. Clone o repositório:
   ```bash
   git clone https://github.com/usuario/projeto-claudio.git
   cd projeto-claudio
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/Mac
   .venv\Scripts\activate        # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente no arquivo **`.env`**:
   ```plaintext
   # Configurações de credenciais e API
   API_KEY=suachaveaqui
   DATABASE_URL=sqlite:///db.sqlite3
   CLOUD_CONFIG=claudio-418319-d3c155f4d0a0.json
   ```

---

## ⚙️ **Execução do Sistema**

Este projeto contém **três robôs independentes**. Você pode executar qualquer um deles separadamente, conforme necessário.

### 1. Robô de Extração:

Este robô é responsável pela **extração de dados** de fontes externas, como arquivos CSV ou APIs.

Execute o robô de extração:
```bash
python processamento_claudio/extract.py
```

### 2. Robô de Nuvem:

Este robô conecta-se com APIs em nuvem para salvar ou processar dados.

Execute o robô de nuvem:
```bash
python cloud/download.py
```

### 3. Robô de Exportação:

Este robô processa os dados extraídos e gera arquivos organizados.

Execute o robô de exportação:
```bash
python processamento_claudio/export.py
```

---

## 📊 **Logs**

Logs são gerados automaticamente no arquivo **`processamento.log`** durante a execução.
Eles devem ser revisados para diagnóstico e excluídos do versionamento.

---

## 🧑‍💻 **Tecnologias Utilizadas**

- **Python:** Processamento e automação de tarefas.
- **Google Cloud API:** Integração com serviços de nuvem.
- **Pandas:** Manipulação de dados estruturados.
- **Flask (opcional):** Interface web para uploads e consultas.

---

## ❓ **Dúvidas ou Problemas?**

Caso encontre problemas ou tenha dúvidas, abra uma **issue** neste repositório ou entre em contato diretamente.

---

## 📝 **Licença**

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.
```
