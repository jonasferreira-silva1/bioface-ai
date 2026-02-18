"""
Testes de integração para exceções de câmera.

Valida que as exceções são lançadas corretamente
nos cenários reais de uso.
"""

import pytest
import cv2
from unittest.mock import Mock, patch, MagicMock
from src.vision.camera import Camera
from src.exceptions import (
    CameraNotOpenedError,
    CameraDisconnectedError,
    CameraReadError
)


class TestCameraExceptions:
    """Testes para exceções de câmera em uso real."""
    
    @patch('cv2.VideoCapture')
    def test_camera_not_opened_error_on_init(self, mock_video_capture):
        """Testa que CameraNotOpenedError é lançada quando câmera não abre."""
        # Simula câmera que não abre
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        with pytest.raises(CameraNotOpenedError) as exc_info:
            Camera(index=999)  # Índice inválido
        
        assert exc_info.value.details["camera_index"] == 999
        assert "não foi possível abrir" in exc_info.value.message.lower()
    
    @patch('cv2.VideoCapture')
    def test_camera_disconnected_error_on_read(self, mock_video_capture):
        """Testa que CameraDisconnectedError é lançada quando câmera desconecta."""
        # Simula câmera que abre mas depois desconecta
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False  # Desconectada
        mock_video_capture.return_value = mock_cap
        
        # Primeiro inicializa com sucesso
        with patch.object(Camera, '_initialize') as mock_init:
            mock_init.return_value = None
            camera = Camera.__new__(Camera)
            camera.index = 0
            camera.cap = mock_cap
        
        # Tenta ler quando desconectada
        with pytest.raises(CameraDisconnectedError) as exc_info:
            camera.read()
        
        assert exc_info.value.details["camera_index"] == 0
        assert "não está aberta" in exc_info.value.message.lower()
    
    @patch('cv2.VideoCapture')
    def test_camera_read_error_on_failed_read(self, mock_video_capture):
        """Testa que CameraReadError é lançada quando falha ao ler frame."""
        # Simula câmera que está aberta mas falha ao ler
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)  # Falha ao ler
        mock_video_capture.return_value = mock_cap
        
        # Inicializa câmera
        with patch.object(Camera, '_initialize') as mock_init:
            mock_init.return_value = None
            camera = Camera.__new__(Camera)
            camera.index = 0
            camera.cap = mock_cap
        
        # Tenta ler quando falha
        with pytest.raises(CameraReadError) as exc_info:
            camera.read()
        
        assert exc_info.value.details["camera_index"] == 0
        assert "ler frame" in exc_info.value.message.lower()
    
    @patch('cv2.VideoCapture')
    def test_camera_reconnect_success(self, mock_video_capture):
        """Testa que reconexão funciona quando câmera volta."""
        # Simula câmera que desconecta e depois reconecta
        mock_cap_disconnected = Mock()
        mock_cap_disconnected.isOpened.return_value = False
        
        mock_cap_connected = Mock()
        mock_cap_connected.isOpened.return_value = True
        mock_cap_connected.get.return_value = 640  # width
        mock_cap_connected.read.return_value = (True, Mock())  # Frame válido
        
        # Primeira tentativa: desconectada
        # Segunda tentativa: conectada
        mock_video_capture.side_effect = [mock_cap_disconnected, mock_cap_connected]
        
        camera = Camera.__new__(Camera)
        camera.index = 0
        camera.width = 640
        camera.height = 480
        camera.fps = 30
        camera.cap = mock_cap_disconnected
        
        # Tenta reconectar
        result = camera.reconnect(max_retries=3)
        
        assert result is True
        assert camera.cap == mock_cap_connected
    
    @patch('cv2.VideoCapture')
    def test_camera_reconnect_failure(self, mock_video_capture):
        """Testa que reconexão falha após todas as tentativas."""
        # Simula câmera que nunca reconecta
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        camera = Camera.__new__(Camera)
        camera.index = 999
        camera.width = 640
        camera.height = 480
        camera.fps = 30
        camera.cap = mock_cap
        
        # Tenta reconectar (deve falhar)
        with pytest.raises(CameraNotOpenedError) as exc_info:
            camera.reconnect(max_retries=2)
        
        assert exc_info.value.details["camera_index"] == 999

