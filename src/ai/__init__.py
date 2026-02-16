"""
Módulo de IA do BioFace AI.

Contém modelos de Machine Learning para classificação de emoções
e reconhecimento facial.
"""

# Importação opcional do EmotionClassifier (requer TensorFlow)
try:
    from .emotion_classifier import EmotionClassifier
    __all__ = ["EmotionClassifier", "FaceRecognizer"]
except ImportError:
    # TensorFlow não instalado (versão leve)
    EmotionClassifier = None
    __all__ = ["FaceRecognizer"]

# Importação do FaceRecognizer (não requer TensorFlow)
from .face_recognizer import FaceRecognizer
