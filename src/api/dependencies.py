"""
Dependências da API (para evitar imports circulares).
"""

from fastapi import HTTPException
from typing import Optional
from ..database.repository import DatabaseRepository
from .websocket_manager import WebSocketManager

# Instâncias globais (serão inicializadas no main.py)
_db_repository: Optional[DatabaseRepository] = None
_websocket_manager: Optional[WebSocketManager] = None


def set_db_repository(repo: DatabaseRepository):
    """Define o repositório de banco de dados."""
    global _db_repository
    _db_repository = repo


def set_websocket_manager(manager: WebSocketManager):
    """Define o gerenciador de WebSocket."""
    global _websocket_manager
    _websocket_manager = manager


def get_db() -> DatabaseRepository:
    """Retorna instância do repositório de banco de dados."""
    if _db_repository is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return _db_repository


def get_websocket_manager() -> WebSocketManager:
    """Retorna instância do gerenciador de WebSocket."""
    if _websocket_manager is None:
        raise HTTPException(status_code=503, detail="WebSocket manager not initialized")
    return _websocket_manager

