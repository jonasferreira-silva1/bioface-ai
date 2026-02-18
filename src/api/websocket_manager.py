"""
Gerenciador de conexões WebSocket para streaming em tempo real.
"""

from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """
    Gerencia conexões WebSocket e broadcasting de mensagens.
    
    Permite múltiplos clientes conectados simultaneamente e
    envia atualizações em tempo real.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "detections": set(),
            "emotions": set()
        }
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, channel: str):
        """
        Aceita nova conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
            channel: Canal ("detections" ou "emotions")
        """
        await websocket.accept()
        
        async with self._lock:
            if channel in self.active_connections:
                self.active_connections[channel].add(websocket)
                logger.info(f"Nova conexão WebSocket no canal '{channel}'. Total: {len(self.active_connections[channel])}")
            else:
                logger.warning(f"Canal desconhecido: {channel}")
    
    def disconnect(self, websocket: WebSocket, channel: str):
        """
        Remove conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
            channel: Canal
        """
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"Conexão WebSocket removida do canal '{channel}'. Total: {len(self.active_connections[channel])}")
    
    async def disconnect_all(self):
        """Fecha todas as conexões WebSocket."""
        async with self._lock:
            for channel, connections in self.active_connections.items():
                for websocket in list(connections):
                    try:
                        await websocket.close()
                    except Exception as e:
                        logger.debug(f"Erro ao fechar conexão: {e}")
                connections.clear()
            logger.info("Todas as conexões WebSocket fechadas")
    
    async def broadcast_detection(self, detection_data: dict):
        """
        Envia detecção para todos os clientes conectados no canal 'detections'.
        
        Args:
            detection_data: Dados da detecção (bbox, user_id, user_name, emotion, etc.)
        """
        await self._broadcast("detections", {
            "type": "detection",
            "data": detection_data
        })
    
    async def broadcast_emotion(self, emotion_data: dict):
        """
        Envia emoção para todos os clientes conectados no canal 'emotions'.
        
        Args:
            emotion_data: Dados da emoção (user_id, emotion, confidence, timestamp)
        """
        await self._broadcast("emotions", {
            "type": "emotion",
            "data": emotion_data
        })
    
    async def _broadcast(self, channel: str, message: dict):
        """
        Envia mensagem para todos os clientes de um canal.
        
        Args:
            channel: Canal ("detections" ou "emotions")
            message: Mensagem a enviar
        """
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[channel]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.debug(f"Erro ao enviar mensagem WebSocket: {e}")
                disconnected.add(websocket)
        
        # Remove conexões desconectadas
        if disconnected:
            async with self._lock:
                self.active_connections[channel] -= disconnected
                logger.debug(f"Removidas {len(disconnected)} conexões desconectadas do canal '{channel}'")

