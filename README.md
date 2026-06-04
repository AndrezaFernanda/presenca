# PresençaCerta 📋✅

**Sistema de Controle de Presença em Treinamentos Corporativos**

Plataforma web para registrar e auditar a presença de colaboradores em treinamentos, com geração de QR Code, link compartilhável e relatórios exportáveis.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🗂 Gestão de Treinamentos | Crie, edite, encerre e exclua treinamentos |
| 📱 QR Code | Gerado automaticamente para cada treinamento |
| 🔗 Link compartilhável | Envie por e-mail ou projete em tela |
| 👤 Registro de Presença | Colaborador se identifica por nome, CPF e e-mail |
| ✅ Validação | CPF com dígitos verificadores + e-mail + nome completo |
| 🚫 Anti-duplicata | Impede registro duplo do mesmo CPF no treinamento |
| 📊 Relatório Auditável | Tabela completa com filtro de busca |
| ⬇ Exportação CSV | Com metadados completos do treinamento |
| 📗 Exportação Excel | Planilha formatada e profissional |
| 🔒 Encerramento | Treinamentos encerrados não aceitam novas presenças |
| 🗄 Banco de Dados | SQLite (padrão) ou PostgreSQL |

---

## 🚀 Instalação Local

### Pré-requisitos
- Python 3.10 ou superior
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/presencacerta.git
cd presencacerta

# 2. Crie um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 5. Execute a aplicação
streamlit run app.py
```

A aplicação estará disponível em: **http://localhost:8501**

---

## ☁️ Deploy no Streamlit Cloud (gratuito)

1. Faça fork deste repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Clique em **"New app"** e selecione o repositório
4. Configure o arquivo principal: `app.py`
5. Em **Settings → Secrets**, adicione:

```toml
APP_URL = "https://seu-app.streamlit.app"
EMPRESA_NOME = "Minha Empresa"
DB_TYPE = "sqlite"
```

> ⚠️ **Atenção:** No Streamlit Cloud, o SQLite é efêmero (reinicia com o deploy).
> Para persistência permanente, use **PostgreSQL** (veja abaixo).

---

## 🐘 Configuração PostgreSQL

Para persistência de dados em produção, use PostgreSQL (ex: [Neon](https://neon.tech), [Supabase](https://supabase.com), [Render](https://render.com) — todos têm plano gratuito).

### No `.env` (local):
```env
DB_TYPE=postgres
POSTGRES_HOST=seu-host.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=presencacerta
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua-senha
```

### No Streamlit Cloud (secrets.toml):
```toml
DB_TYPE = "postgres"

[postgres]
host     = "seu-host.neon.tech"
port     = 5432
db       = "presencacerta"
user     = "postgres"
password = "sua-senha"
```

---

## 🔗 Como funciona o fluxo

```
Organizador cria treinamento
         ↓
  QR Code / Link gerado
         ↓
Colaborador escaneia com o celular
         ↓
  Preenche: Nome, CPF, E-mail
         ↓
  Presença registrada no banco
         ↓
Organizador acessa Relatório → Exporta CSV/Excel
```

---

## 📁 Estrutura do Projeto

```
presencacerta/
├── app.py                    # Ponto de entrada (roteador principal)
├── requirements.txt          # Dependências Python
├── .env.example              # Template de configuração
│
├── pages/
│   ├── painel.py             # Painel do organizador
│   ├── presenca.py           # Registro de presença (colaborador)
│   └── relatorio.py          # Relatório auditável
│
├── utils/
│   ├── database.py           # Camada de dados (SQLite + PostgreSQL)
│   ├── helpers.py            # Validações, QR Code, exportações
│   └── styles.py             # CSS global + componentes visuais
│
└── .streamlit/
    ├── config.toml           # Configurações do Streamlit
    └── secrets.toml.example  # Template de segredos
```

---

## 🛡️ Segurança e Auditoria

- CPF validado com algoritmo oficial de dígitos verificadores
- Prevenção de duplicatas por treinamento (índice UNIQUE no banco)
- Treinamentos encerrados rejeitam novas presenças
- Timestamp de cada registro armazenado
- Relatório CSV inclui metadados completos para fins de auditoria
- Suporte a HTTPS via Streamlit Cloud / proxy reverso

---

## 📄 Licença

MIT License — livre para uso comercial e modificação.

---

*Desenvolvido com ❤️ usando Python + Streamlit*
