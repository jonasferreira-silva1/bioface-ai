"""
API principal do BioFace AI usando FastAPI.

Fornece endpoints REST e WebSocket para acesso ao sistema.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_settings
from src.database.repository import DatabaseRepository
from .routes import users, emotions, stats
from .websocket_manager import WebSocketManager
from .dependencies import set_db_repository, set_websocket_manager

# Configura logging
setup_logger()
logger = get_logger(__name__)

# Instância global do repositório
db_repository: Optional[DatabaseRepository] = None
websocket_manager: Optional[WebSocketManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia ciclo de vida da aplicação.
    Inicializa recursos na startup e limpa na shutdown.
    """
    global db_repository, websocket_manager
    
    # Startup
    logger.info("Inicializando API BioFace AI...")
    try:
        db_repository = DatabaseRepository()
        websocket_manager = WebSocketManager()
        
        # Define nas dependências
        set_db_repository(db_repository)
        set_websocket_manager(websocket_manager)
        
        logger.info("API inicializada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Encerrando API BioFace AI...")
    if websocket_manager:
        await websocket_manager.disconnect_all()
    logger.info("API encerrada.")


# Cria aplicação FastAPI
app = FastAPI(
    title="BioFace AI API",
    description="API REST para sistema de reconhecimento facial e análise comportamental",
    version="1.0.0",
    lifespan=lifespan
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui rotas
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(emotions.router, prefix="/api/emotions", tags=["emotions"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "name": "BioFace AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """
    Health check do sistema.
    
    Verifica se todos os componentes estão funcionando.
    """
    try:
        from .dependencies import get_db, get_websocket_manager
        
        # Verifica banco de dados
        db = get_db()
        
        # Testa conexão com banco
        session = db.get_session()
        try:
            from src.database.models import User
            user_count = session.query(User).count()
        finally:
            session.close()
        
        # Verifica WebSocket
        ws_manager = get_websocket_manager()
        ws_connections = len(ws_manager.active_connections.get("detections", set())) + \
                        len(ws_manager.active_connections.get("emotions", set()))
        
        return {
            "status": "healthy",
            "database": "connected",
            "users_count": user_count,
            "websocket_connections": ws_connections
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.websocket("/ws/detections")
async def websocket_detections(websocket: WebSocket):
    """
    WebSocket para streaming de detecções em tempo real.
    
    Clientes conectados recebem atualizações sobre:
    - Detecções de faces
    - Identificações de usuários
    - Emoções detectadas
    """
    await websocket_manager.connect(websocket, "detections")
    
    try:
        while True:
            # Mantém conexão viva
            await asyncio.sleep(1)
            
            # Envia ping para verificar conexão
            try:
                await websocket.send_json({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
            except Exception:
                break
                
    except WebSocketDisconnect:
        logger.info("Cliente desconectado do WebSocket de detecções")
    finally:
        websocket_manager.disconnect(websocket, "detections")


@app.websocket("/ws/emotions")
async def websocket_emotions(websocket: WebSocket):
    """
    WebSocket para streaming de emoções em tempo real.
    
    Clientes conectados recebem atualizações sobre emoções detectadas.
    """
    await websocket_manager.connect(websocket, "emotions")
    
    try:
        while True:
            await asyncio.sleep(1)
            
            try:
                await websocket.send_json({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
            except Exception:
                break
                
    except WebSocketDisconnect:
        logger.info("Cliente desconectado do WebSocket de emoções")
    finally:
        websocket_manager.disconnect(websocket, "emotions")



