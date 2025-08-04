from fastapi import FastAPI, HTTPException, Depends, Request, status, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import uvicorn
from typing import Optional, List
from src.security import (
    get_api_key, generate_api_key, 
    revoke_api_key, get_api_keys
)
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializações
    logger.info("Sistema de Gerenciamento de API Keys iniciado!")
    yield
    logger.info("Sistema de Gerenciamento de API Keys encerrado!")

app = FastAPI(
    title="API Key Manager",
    description="API para gerenciamento de API Keys",
    version="1.0.0",
    lifespan=lifespan
)

# Classes para requisições
class APIKeyRequest(BaseModel):
    name: str
    expires_days: Optional[int] = 365  # Validade em dias, padrão de 1 ano

class RevokeRequest(BaseModel):
    key_id: int


# Endpoints para gerenciar API Keys (com proteção especial)
@app.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def create_key(request: Request, api_key_request: APIKeyRequest):
    """
    Cria uma nova API Key.
    
    Este endpoint deve ser protegido por senha ou estar em uma rede segura.
    Em um ambiente de produção, seria melhor adicionar autenticação adicional aqui.
    """
    try:
        result = await generate_api_key(
            name=api_key_request.name,
            expires_days=api_key_request.expires_days
        )
        return result
    except Exception as e:
        logger.error(f"Erro ao criar API Key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api-keys")
async def list_keys(request: Request, active_only: bool = False):
    """
    Lista todas as API Keys.
    """
    try:
        keys = await get_api_keys(active_only)
        return {"keys": keys, "count": len(keys)}
    except Exception as e:
        logger.error(f"Erro ao listar API Keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api-keys/revoke")
async def revoke_key(request: Request, revoke_request: RevokeRequest):
    """
    Revoga (desativa) uma API Key.
    """
    try:
        success = await revoke_api_key(revoke_request.key_id)
        if not success:
            raise HTTPException(status_code=404, detail="API Key não encontrada")
        return {"message": "API Key revogada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao revogar API Key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status():
    """
    Verifica o status da API
    """
    return {"status": "online", "service": "API Key Manager"}


if __name__ == "__main__":
    # Obter a porta da variável de ambiente API_PORT ou usar 8003 como padrão
    api_port = int(os.getenv("API_PORT", "8003"))
    uvicorn.run("api:app", host="0.0.0.0", port=api_port, reload=True)
