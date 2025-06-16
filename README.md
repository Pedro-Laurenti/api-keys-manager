# API Key Manager

Este serviço gerencia API Keys que são utilizadas para autenticar usuários na API de transcrição de áudio Whisper.

## Características

- Criação de novas API Keys
- Listagem de API Keys existentes
- Revogação de API Keys
- Suporte a restrição de IPs para cada API Key
- Expiração automática de API Keys

## Endpoints

- `POST /api-keys`: Cria uma nova API Key
- `GET /api-keys`: Lista todas as API Keys
- `POST /api-keys/revoke`: Revoga (desativa) uma API Key
- `GET /status`: Verifica o status da API

## Requisitos

- Python 3.8+
- PostgreSQL
- Dependências listadas em `requirements.txt`

## Configuração

1. Crie um arquivo `.env` baseado no exemplo fornecido em `.env.example`
2. Configure as variáveis de ambiente para conexão com o banco de dados

## Instalação

```bash
# Crie um ambiente virtual (opcional, mas recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Execução

```bash
python api.py
```

ou

```bash
uvicorn api:app --host 0.0.0.0 --port 8003 --reload
```

## Segurança

Por padrão, os endpoints administrativos só podem ser acessados a partir de endereços IP listados na variável de ambiente `ADMIN_ALLOWED_IPS`.

## Compartilhamento do banco de dados

Este serviço compartilha o mesmo banco de dados com a API de transcrição de áudio Whisper. As informações sobre API Keys são armazenadas na tabela `api_keys`.
