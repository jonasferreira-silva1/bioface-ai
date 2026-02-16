"""
Módulo de captura de vídeo do BioFace AI.

Gerencia a captura de frames da webcam usando OpenCV de forma
assíncrona e eficiente.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)


class Camera:
    """
    Classe para gerenciar captura de vídeo da webcam.
    
    Esta classe encapsula toda a lógica de captura de vídeo usando OpenCV,
    incluindo inicialização, captura de frames e liberação de recursos.
    
    Attributes:
        index (int): Índice da câmera
        width (int): Largura do frame
        height (int): Altura do frame
        fps (int): FPS alvo
        cap (cv2.VideoCapture): Objeto de captura do OpenCV
        
    Example:
        >>> camera = Camera()
        >>> frame = camera.read()
        >>> if frame is not None:
        ...     cv2.imshow("Frame", frame)
        >>> camera.release()
    """
    
    def __init__(
        self,
        index: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None
    ):
        """
        Inicializa a câmera com as configurações fornecidas.
        
        Args:
            index: Índice da câmera (usa config se None)
            width: Largura do frame (usa config se None)
            height: Altura do frame (usa config se None)
            fps: FPS alvo (usa config se None)
            
        Raises:
            RuntimeError: Se não conseguir abrir a câmera
        """
        settings = get_settings()
        
        self.index = index if index is not None else settings.camera_index
        self.width = width if width is not None else settings.camera_width
        self.height = height if height is not None else settings.camera_height
        self.fps = fps if fps is not None else settings.fps_target
        
        # Inicializa o objeto de captura
        self.cap: Optional[cv2.VideoCapture] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """
        Inicializa a conexão com a câmera.
        
        Raises:
            RuntimeError: Se não conseguir abrir a câmera
        """
        logger.info(f"Inicializando câmera {self.index}...")
        
        # Cria objeto VideoCapture
        self.cap = cv2.VideoCapture(self.index)
        
        if not self.cap.isOpened():
            error_msg = f"Não foi possível abrir a câmera {self.index}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Configura propriedades da câmera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Lê propriedades reais (podem ser diferentes do solicitado)
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(
            f"Câmera inicializada: {actual_width}x{actual_height} @ {actual_fps}fps"
        )
    
    def read(self) -> Optional[np.ndarray]:
        """
        Lê um frame da câmera.
        
        Returns:
            np.ndarray: Frame BGR (Blue, Green, Red) ou None se falhar
            
        Example:
            >>> camera = Camera()
            >>> frame = camera.read()
            >>> if frame is not None:
            ...     print(f"Frame shape: {frame.shape}")
        """
        if self.cap is None or not self.cap.isOpened():
            logger.warning("Tentativa de ler frame de câmera não inicializada")
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.warning("Falha ao ler frame da câmera")
            return None
        
        return frame
    
    def is_opened(self) -> bool:
        """
        Verifica se a câmera está aberta e funcionando.
        
        Returns:
            bool: True se a câmera está aberta
            
        Example:
            >>> camera = Camera()
            >>> if camera.is_opened():
            ...     print("Câmera funcionando")
        """
        return self.cap is not None and self.cap.isOpened()
    
    def release(self) -> None:
        """
        Libera os recursos da câmera.
        
        Deve ser chamado quando a câmera não for mais necessária para
        liberar o dispositivo.
        
        Example:
            >>> camera = Camera()
            >>> # ... usar câmera ...
            >>> camera.release()
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.info("Câmera liberada")
    
    def __enter__(self):
        """Context manager: entrada"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: saída (libera recursos)"""
        self.release()
    
    def __del__(self):
        """Destrutor: garante liberação de recursos"""
        self.release()


