"""
Módulo de Visão Computacional do BioFace AI.

Contém todas as funcionalidades relacionadas à captura de vídeo,
detecção de faces e processamento de imagens.
"""

from .camera import Camera
from .face_detector import FaceDetector
from .face_processor import FaceProcessor

__all__ = ["Camera", "FaceDetector", "FaceProcessor"]

