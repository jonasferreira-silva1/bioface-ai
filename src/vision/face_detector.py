"""
Módulo de detecção facial do BioFace AI.

Usa MediaPipe Face Mesh para detectar faces e extrair landmarks (468 pontos).
MediaPipe é otimizado para tempo real e oferece alta precisão.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FaceDetector:
    """
    Classe para detecção de faces usando MediaPipe Face Mesh.
    
    MediaPipe Face Mesh detecta faces e extrai 468 landmarks faciais,
    permitindo análise detalhada de expressões e geometria facial.
    
    Attributes:
        mp_face_mesh: Objeto MediaPipe Face Mesh
        mp_drawing: Utilitário de desenho do MediaPipe
        mp_drawing_styles: Estilos de desenho
        
    Example:
        >>> detector = FaceDetector()
        >>> faces = detector.detect(frame)
        >>> for face in faces:
        ...     bbox = face['bbox']
        ...     landmarks = face['landmarks']
    """
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        max_num_faces: int = 1
    ):
        """
        Inicializa o detector de faces.
        
        Args:
            min_detection_confidence: Confiança mínima para detecção (0.0-1.0)
            min_tracking_confidence: Confiança mínima para tracking (0.0-1.0)
            max_num_faces: Número máximo de faces a detectar
            
        Note:
            MediaPipe usa um modelo de detecção + tracking. O tracking
            é mais rápido que detecção, então valores mais baixos de
            min_tracking_confidence podem melhorar performance.
        """
        logger.info("Inicializando MediaPipe Face Mesh...")
        
        # Inicializa MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Cria o detector com configurações
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,  # Modo vídeo (mais rápido)
            max_num_faces=max_num_faces,
            refine_landmarks=True,  # Refina landmarks para maior precisão
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        logger.info("MediaPipe Face Mesh inicializado")
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """
        Detecta faces em um frame e extrai landmarks.
        
        Args:
            frame: Frame BGR (OpenCV usa BGR, não RGB)
            
        Returns:
            List[dict]: Lista de faces detectadas, cada uma contendo:
                - 'bbox': (x, y, width, height) - bounding box
                - 'landmarks': np.ndarray - 468 landmarks (x, y, z)
                - 'landmarks_2d': np.ndarray - landmarks 2D (x, y)
                - 'confidence': float - confiança da detecção
                
        Example:
            >>> detector = FaceDetector()
            >>> frame = cv2.imread("photo.jpg")
            >>> faces = detector.detect(frame)
            >>> print(f"Faces detectadas: {len(faces)}")
        """
        if frame is None or frame.size == 0:
            logger.warning("Frame vazio ou inválido")
            return []
        
        # MediaPipe espera RGB, mas OpenCV usa BGR
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processa o frame
        results = self.face_mesh.process(frame_rgb)
        
        faces = []
        
        if results.multi_face_landmarks:
            h, w = frame.shape[:2]
            
            for face_landmarks in results.multi_face_landmarks:
                # Converte landmarks para array numpy
                landmarks = np.array([
                    [lm.x * w, lm.y * h, lm.z * w]
                    for lm in face_landmarks.landmark
                ])
                
                # Extrai landmarks 2D (apenas x, y)
                landmarks_2d = landmarks[:, :2]
                
                # Calcula bounding box a partir dos landmarks
                x_min = int(landmarks_2d[:, 0].min())
                y_min = int(landmarks_2d[:, 1].min())
                x_max = int(landmarks_2d[:, 0].max())
                y_max = int(landmarks_2d[:, 1].max())
                
                # Adiciona margem ao bounding box
                margin = 10
                x_min = max(0, x_min - margin)
                y_min = max(0, y_min - margin)
                x_max = min(w, x_max + margin)
                y_max = min(h, y_max + margin)
                
                bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
                
                # Calcula confiança (simplificado - MediaPipe não retorna confiança direta)
                # Usamos a presença de landmarks como indicador
                confidence = 1.0 if len(landmarks) == 468 else 0.5
                
                faces.append({
                    'bbox': bbox,
                    'landmarks': landmarks,
                    'landmarks_2d': landmarks_2d,
                    'confidence': confidence
                })
        
        return faces
    
    def draw_landmarks(
        self,
        frame: np.ndarray,
        faces: List[dict],
        draw_connections: bool = True
    ) -> np.ndarray:
        """
        Desenha landmarks e bounding boxes no frame.
        
        Útil para visualização e debugging.
        
        Args:
            frame: Frame BGR onde desenhar
            faces: Lista de faces detectadas
            draw_connections: Se True, desenha conexões entre landmarks
            
        Returns:
            np.ndarray: Frame com landmarks desenhados
            
        Example:
            >>> detector = FaceDetector()
            >>> faces = detector.detect(frame)
            >>> frame_annotated = detector.draw_landmarks(frame, faces)
            >>> cv2.imshow("Faces", frame_annotated)
        """
        frame_copy = frame.copy()
        
        for face in faces:
            bbox = face['bbox']
            landmarks_2d = face['landmarks_2d']
            
            # Desenha bounding box
            x, y, w, h = bbox
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Desenha landmarks (pontos principais)
            # Desenha apenas alguns pontos para não poluir a imagem
            key_points = [10, 33, 61, 199, 291, 468]  # Pontos principais do rosto
            for idx in key_points:
                if idx < len(landmarks_2d):
                    pt = tuple(landmarks_2d[idx].astype(int))
                    cv2.circle(frame_copy, pt, 2, (255, 0, 0), -1)
        
        return frame_copy
    
    def release(self) -> None:
        """
        Libera recursos do detector.
        
        Example:
            >>> detector = FaceDetector()
            >>> # ... usar detector ...
            >>> detector.release()
        """
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
            logger.info("FaceDetector liberado")

