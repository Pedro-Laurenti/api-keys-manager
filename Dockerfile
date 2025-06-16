FROM python:3.12-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos do projeto
COPY . .

# Porta em que a API estará disponível
EXPOSE 8003

# Comando para executar a API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003"]
