"""
Cliente HTTP para comunicação com a API BioFace AI.

Permite que o pipeline envie dados para a API.
"""

import requests
import asyncio
import websockets
import json
from typing import Optional, Dict, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """
    Cliente para comunicação com a API BioFace AI.
    
    Permite enviar detecções e emoções para a API via HTTP e WebSocket.
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Inicializa o cliente da API.
        
        Args:
            api_base_url: URL base da API (ex: "http://localhost:8000")
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.ws_connected = False
    
    def health_check(self) -> bool:
        """
        Verifica se a API está disponível.
        
        Returns:
            bool: True se API está online
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/api/health",
                timeout=2
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check falhou: {e}")
            return False
    
    async def connect_websocket(self, channel: str = "detections") -> bool:
        """
        Conecta ao WebSocket da API.
        
        Args:
            channel: Canal ("detections" ou "emotions")
            
        Returns:
            bool: True se conectou com sucesso
        """
        try:
            ws_url = self.api_base_url.replace("http://", "ws://").replace("https://", "wss://")
            self.ws_connection = await websockets.connect(
                f"{ws_url}/ws/{channel}",
                ping_interval=20,
                ping_timeout=10
            )
            self.ws_connected = True
            logger.info(f"Conectado ao WebSocket: {channel}")
            return True
        except Exception as e:
            logger.warning(f"Falha ao conectar WebSocket: {e}")
            self.ws_connected = False
            return False
    
    async def disconnect_websocket(self):
        """Desconecta do WebSocket."""
        if self.ws_connection:
            try:
                await self.ws_connection.close()
                logger.info("Desconectado do WebSocket")
            except Exception as e:
                logger.debug(f"Erro ao desconectar: {e}")
            finally:
                self.ws_connection = None
                self.ws_connected = False
    
    async def send_detection(self, detection_data: Dict[str, Any]) -> bool:
        """
        Envia detecção via WebSocket.
        
        Args:
            detection_data: Dados da detecção (bbox, user_id, user_name, emotion, etc.)
            
        Returns:
            bool: True se enviou com sucesso
        """
        if not self.ws_connected or not self.ws_connection:
            # Tenta reconectar
            if not await self.connect_websocket("detections"):
                return False
        
        try:
            message = {
                "type": "detection",
                "data": detection_data
            }
            await self.ws_connection.send(json.dumps(message))
            return True
        except Exception as e:
            logger.debug(f"Erro ao enviar detecção via WebSocket: {e}")
            self.ws_connected = False
            return False
    
    async def send_emotion(self, emotion_data: Dict[str, Any]) -> bool:
        """
        Envia emoção via WebSocket.
        
        Args:
            emotion_data: Dados da emoção (user_id, emotion, confidence, timestamp)
            
        Returns:
            bool: True se enviou com sucesso
        """
        if not self.ws_connected or not self.ws_connection:
            # Tenta reconectar
            if not await self.connect_websocket("emotions"):
                return False
        
        try:
            message = {
                "type": "emotion",
                "data": emotion_data
            }
            await self.ws_connection.send(json.dumps(message))
            return True
        except Exception as e:
            logger.debug(f"Erro ao enviar emoção via WebSocket: {e}")
            self.ws_connected = False
            return False
    
    def send_emotion_http(self, user_id: Optional[int], emotion: str, confidence: float) -> bool:
        """
        Envia emoção via HTTP (fallback se WebSocket não estiver disponível).
        
        Nota: A API atual não tem endpoint POST para emoções, mas pode ser adicionado.
        Por enquanto, emoções são salvas diretamente no banco pelo pipeline.
        
        Args:
            user_id: ID do usuário
            emotion: Emoção detectada
            confidence: Confiança
            
        Returns:
            bool: True se enviou com sucesso
        """
        # Por enquanto, emoções são salvas diretamente no banco
        # Este método pode ser usado no futuro se adicionarmos endpoint POST
        logger.debug("Emoções são salvas diretamente no banco, não via HTTP")
        return True

