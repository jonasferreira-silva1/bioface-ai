"""
Módulo de IA do BioFace AI.

Contém modelos de Machine Learning para classificação de emoções
e reconhecimento facial.
"""

# Importação opcional do EmotionClassifier (requer TensorFlow)
try:
    from .emotion_classifier import EmotionClassifier
    HAS_TENSORFLOW = True
except ImportError:
    # TensorFlow não instalado (versão leve)
    EmotionClassifier = None
    HAS_TENSORFLOW = False

# Importação do EmotionClassifierLight (não requer TensorFlow)
from .emotion_classifier_light import EmotionClassifierLight

# Importação do EmotionClassifierDeepFace (requer DeepFace)
try:
    from .emotion_classifier_deepface import EmotionClassifierDeepFace
    HAS_DEEPFACE = True
except ImportError:
    EmotionClassifierDeepFace = None
    HAS_DEEPFACE = False

# Importação do FaceRecognizer (não requer TensorFlow)
from .face_recognizer import FaceRecognizer

# Define exports
__all__ = ["EmotionClassifierLight", "FaceRecognizer"]
if HAS_TENSORFLOW:
    __all__.append("EmotionClassifier")
if HAS_DEEPFACE:
    __all__.append("EmotionClassifierDeepFace")
