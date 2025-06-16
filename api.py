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
    allowed_ips: Optional[List[str]] = None  # Lista de IPs permitidos (opcional)

class RevokeRequest(BaseModel):
    key_id: int

# Adicionando verificação de IP de administração
async def verify_admin_access(request: Request):
    """
    Verifica se a solicitação tem acesso de administração.
    Pode ser expandido para incluir autenticação adicional.
    """
    # Lista de IPs permitidos para acesso administrativo
    admin_ips_setting = os.getenv("ADMIN_ALLOWED_IPS", "")
    client_ip = request.client.host
    
    # Se ADMIN_ALLOWED_IPS for "*", permite acesso de qualquer IP
    if admin_ips_setting.strip() == "*":
        return True
    
    allowed_admin_ips = admin_ips_setting.split(",")
    
    # Se não houver IPs configurados, permitimos o acesso de localhost (para desenvolvimento)
    if not any(ip.strip() for ip in allowed_admin_ips) and client_ip in ["127.0.0.1", "localhost", "::1"]:
        return True
    
    # Verifica se o IP do cliente está na lista de IPs permitidos
    if client_ip not in [ip.strip() for ip in allowed_admin_ips if ip.strip()]:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. IP não autorizado para acesso administrativo."
        )
    
    return True

# Endpoints para gerenciar API Keys (com proteção especial)
@app.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def create_key(request: Request, api_key_request: APIKeyRequest, _: bool = Depends(verify_admin_access)):
    """
    Cria uma nova API Key.
    
    Este endpoint deve ser protegido por senha ou estar em uma rede segura.
    Em um ambiente de produção, seria melhor adicionar autenticação adicional aqui.
    """
    try:
        result = await generate_api_key(
            name=api_key_request.name,
            expires_days=api_key_request.expires_days,
            allowed_ips=api_key_request.allowed_ips
        )
        return result
    except Exception as e:
        logger.error(f"Erro ao criar API Key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api-keys")
async def list_keys(request: Request, active_only: bool = False, _: bool = Depends(verify_admin_access)):
    """
    Lista todas as API Keys.
    
    Este endpoint está protegido e só pode ser acessado de IPs autorizados.
    """
    try:
        keys = await get_api_keys(active_only)
        return {"keys": keys, "count": len(keys)}
    except Exception as e:
        logger.error(f"Erro ao listar API Keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api-keys/revoke")
async def revoke_key(request: Request, revoke_request: RevokeRequest, _: bool = Depends(verify_admin_access)):
    """
    Revoga (desativa) uma API Key.
    
    Este endpoint está protegido e só pode ser acessado de IPs autorizados.
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
