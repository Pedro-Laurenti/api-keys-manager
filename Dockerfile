FROM python:3.12-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos do projeto
COPY . .

# Porta em que a API estará disponível
# A variável API_PORT será definida em tempo de execução
EXPOSE ${API_PORT:-8003}

# Comando para executar a API usando um script de inicialização para interpretar variáveis de ambiente
CMD python api.py
