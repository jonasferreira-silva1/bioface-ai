"""
Módulo de processamento de faces do BioFace AI.

Normaliza e pré-processa faces detectadas para uso em modelos de IA.
Inclui recorte, redimensionamento e conversão para escala de cinza.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)


class FaceProcessor:
    """
    Classe para processamento e normalização de faces.
    
    Normaliza faces detectadas para tamanhos padrão usados pelos modelos:
    - 48x48 para classificação de emoção (grayscale)
    - 160x160 para reconhecimento facial (RGB)
    
    Attributes:
        emotion_size: Tamanho da face para emoção (48x48)
        recognition_size: Tamanho da face para reconhecimento (160x160)
        
    Example:
        >>> processor = FaceProcessor()
        >>> face_emotion = processor.process_for_emotion(frame, bbox)
        >>> face_recognition = processor.process_for_recognition(frame, bbox)
    """
    
    def __init__(
        self,
        emotion_size: Optional[int] = None,
        recognition_size: Optional[int] = None
    ):
        """
        Inicializa o processador de faces.
        
        Args:
            emotion_size: Tamanho da face para emoção (usa config se None)
            recognition_size: Tamanho da face para reconhecimento (usa config se None)
        """
        settings = get_settings()
        
        self.emotion_size = emotion_size or settings.face_size_emotion
        self.recognition_size = recognition_size or settings.face_size_recognition
        
        logger.info(
            f"FaceProcessor inicializado: "
            f"emoção={self.emotion_size}x{self.emotion_size}, "
            f"reconhecimento={self.recognition_size}x{self.recognition_size}"
        )
    
    def extract_face(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Extrai a região da face do frame usando o bounding box.
        
        Args:
            frame: Frame completo BGR
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            np.ndarray: Face extraída ou None se inválida
            
        Example:
            >>> processor = FaceProcessor()
            >>> bbox = (100, 100, 200, 200)
            >>> face = processor.extract_face(frame, bbox)
        """
        if frame is None or frame.size == 0:
            logger.warning("Frame inválido para extração")
            return None
        
        x, y, w, h = bbox
        
        # Verifica se o bounding box está dentro do frame
        h_frame, w_frame = frame.shape[:2]
        x = max(0, min(x, w_frame))
        y = max(0, min(y, h_frame))
        w = min(w, w_frame - x)
        h = min(h, h_frame - y)
        
        if w <= 0 or h <= 0:
            logger.warning(f"Bounding box inválido: {bbox}")
            return None
        
        # Extrai a região da face
        face = frame[y:y+h, x:x+w]
        
        return face
    
    def normalize_face(
        self,
        face: np.ndarray,
        target_size: int,
        grayscale: bool = False
    ) -> Optional[np.ndarray]:
        """
        Normaliza uma face para o tamanho alvo.
        
        Args:
            face: Face extraída (BGR)
            target_size: Tamanho alvo (width = height = target_size)
            grayscale: Se True, converte para escala de cinza
            
        Returns:
            np.ndarray: Face normalizada ou None se inválida
            
        Example:
            >>> processor = FaceProcessor()
            >>> face_normalized = processor.normalize_face(face, 48, grayscale=True)
        """
        if face is None or face.size == 0:
            logger.warning("Face inválida para normalização")
            return None
        
        # Converte para escala de cinza se necessário
        if grayscale:
            if len(face.shape) == 3:
                face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            else:
                face_gray = face
        else:
            face_gray = face
        
        # Redimensiona para o tamanho alvo
        # Usa INTER_AREA para downsampling (melhor qualidade)
        face_resized = cv2.resize(
            face_gray,
            (target_size, target_size),
            interpolation=cv2.INTER_AREA
        )
        
        # Normaliza valores para [0, 1] se necessário
        # (Alguns modelos esperam valores normalizados)
        if face_resized.dtype != np.float32:
            face_resized = face_resized.astype(np.float32) / 255.0
        
        return face_resized
    
    def process_for_emotion(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Processa face para classificação de emoção.
        
        Extrai, normaliza e converte para escala de cinza 48x48.
        
        Args:
            frame: Frame completo BGR
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            np.ndarray: Face processada (48x48 grayscale, valores [0, 1])
            
        Example:
            >>> processor = FaceProcessor()
            >>> face_emotion = processor.process_for_emotion(frame, bbox)
            >>> # face_emotion.shape = (48, 48) ou (48, 48, 1)
        """
        # Extrai a face
        face = self.extract_face(frame, bbox)
        if face is None:
            return None
        
        # Normaliza para 48x48 em escala de cinza
        face_normalized = self.normalize_face(
            face,
            self.emotion_size,
            grayscale=True
        )
        
        # Adiciona dimensão de canal se necessário (para modelos que esperam)
        if len(face_normalized.shape) == 2:
            face_normalized = np.expand_dims(face_normalized, axis=-1)
        
        return face_normalized
    
    def process_for_recognition(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Processa face para reconhecimento facial.
        
        Extrai e normaliza para 160x160 RGB.
        
        Args:
            frame: Frame completo BGR
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            np.ndarray: Face processada (160x160 RGB, valores [0, 1])
            
        Example:
            >>> processor = FaceProcessor()
            >>> face_recognition = processor.process_for_recognition(frame, bbox)
            >>> # face_recognition.shape = (160, 160, 3)
        """
        # Extrai a face
        face = self.extract_face(frame, bbox)
        if face is None:
            return None
        
        # Normaliza para 160x160 em RGB
        # Converte BGR para RGB
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        
        # Normaliza
        face_normalized = self.normalize_face(
            face_rgb,
            self.recognition_size,
            grayscale=False
        )
        
        return face_normalized
    
    def enhance_face(self, face: np.ndarray) -> np.ndarray:
        """
        Melhora a qualidade da face usando equalização de histograma.
        
        Útil para melhorar detecção em condições de iluminação variável.
        
        Args:
            face: Face em escala de cinza
            
        Returns:
            np.ndarray: Face melhorada
            
        Example:
            >>> processor = FaceProcessor()
            >>> face_enhanced = processor.enhance_face(face)
        """
        if len(face.shape) == 3:
            # Se for colorida, converte para grayscale
            face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        else:
            face_gray = face
        
        # Aplica equalização de histograma adaptativa
        # (melhor que equalização simples para iluminação variável)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face_enhanced = clahe.apply(face_gray)
        
        return face_enhanced

