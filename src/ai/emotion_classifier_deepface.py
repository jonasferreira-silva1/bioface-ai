"""
Módulo de classificação de emoções usando DeepFace.

Usa modelos pré-treinados (FER2013) para classificação de emoções com alta precisão.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from pathlib import Path
from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)

# Tenta importar DeepFace
try:
    from deepface import DeepFace
    _has_deepface = True
except ImportError:
    _has_deepface = False
    DeepFace = None
    logger.warning("DeepFace não está instalado. Execute: pip install deepface")


class EmotionClassifierDeepFace:
    """
    Classificador de emoções usando DeepFace.
    
    Usa modelos pré-treinados (FER2013) para classificação de emoções com alta precisão.
    
    Emoções suportadas:
    - Happy (Feliz)
    - Sad (Triste)
    - Angry (Raiva)
    - Surprise (Surpresa)
    - Fear (Medo)
    - Disgust (Nojo)
    - Neutral (Neutro)
    
    Attributes:
        emotion_labels: Lista de labels de emoções
        confidence_threshold: Threshold mínimo de confiança
        backend: Backend do DeepFace ('opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe')
        
    Example:
        >>> classifier = EmotionClassifierDeepFace()
        >>> emotion, confidence = classifier.predict(face_image)
        >>> print(f"Emoção: {emotion}, Confiança: {confidence:.2%}")
    """
    
    # Labels de emoções (mapeamento DeepFace -> nosso sistema)
    EMOTION_LABELS = [
        "Happy",      # Feliz
        "Sad",        # Triste
        "Angry",      # Raiva
        "Surprise",   # Surpresa
        "Fear",       # Medo
        "Disgust",    # Nojo
        "Neutral"     # Neutro
    ]
    
    # Labels em português
    EMOTION_LABELS_PT = [
        "Feliz",
        "Triste",
        "Raiva",
        "Surpresa",
        "Medo",
        "Nojo",
        "Neutro"
    ]
    
    # Mapeamento DeepFace -> nosso sistema
    DEEPFACE_TO_OUR = {
        'happy': 'Happy',
        'sad': 'Sad',
        'angry': 'Angry',
        'surprise': 'Surprise',
        'fear': 'Fear',
        'disgust': 'Disgust',
        'neutral': 'Neutral'
    }
    
    def __init__(
        self,
        confidence_threshold: Optional[float] = None,
        backend: str = 'opencv',
        enforce_detection: bool = False
    ):
        """
        Inicializa o classificador de emoções DeepFace.
        
        Args:
            confidence_threshold: Threshold mínimo de confiança
            backend: Backend do DeepFace ('opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe')
            enforce_detection: Se True, lança erro se não detectar face. Se False, retorna 'Unknown'
        """
        if not _has_deepface:
            raise ImportError(
                "DeepFace não está instalado. Execute: pip install deepface"
            )
        
        settings = get_settings()
        
        self.confidence_threshold = (
            confidence_threshold or settings.emotion_confidence_threshold
        )
        self.backend = backend
        self.enforce_detection = enforce_detection
        
        # Cache para melhorar performance (opcional)
        self._cache = {}
        self._cache_size = 10
        
        logger.info(
            f"EmotionClassifierDeepFace inicializado: "
            f"emoções={len(self.EMOTION_LABELS)}, "
            f"threshold={self.confidence_threshold}, "
            f"backend={self.backend}"
        )
    
    def predict(
        self,
        face: np.ndarray,
        landmarks: Optional[np.ndarray] = None
    ) -> Tuple[str, float]:
        """
        Classifica a emoção em uma face usando DeepFace.
        
        Args:
            face: Face normalizada (qualquer tamanho, BGR ou RGB)
                  Shape esperado: (H, W, 3) ou (H, W)
            landmarks: Landmarks do MediaPipe (ignorado, DeepFace não usa)
                  
        Returns:
            Tuple[str, float]: (emoção, confiança)
            
        Example:
            >>> classifier = EmotionClassifierDeepFace()
            >>> emotion, confidence = classifier.predict(face)
            >>> print(f"{emotion}: {confidence:.2%}")
        """
        if not _has_deepface:
            return "Unknown", 0.0
        
        if face is None or face.size == 0:
            logger.warning("Face inválida para classificação")
            return "Unknown", 0.0
        
        try:
            # Prepara a face para DeepFace
            # DeepFace espera BGR (OpenCV padrão) ou pode converter automaticamente
            face_prepared = self._prepare_face(face)
            
            # Salva temporariamente para DeepFace processar
            temp_path = self._save_temp_face(face_prepared)
            
            if temp_path is None:
                return "Unknown", 0.0
            
            try:
                # Analisa emoção usando DeepFace
                # enforce_detection=False evita erro se não detectar face
                result = DeepFace.analyze(
                    img_path=str(temp_path),
                    actions=['emotion'],
                    enforce_detection=self.enforce_detection,
                    silent=True  # Suprime logs do DeepFace
                )
                
                # DeepFace retorna lista se múltiplas faces, pega a primeira
                if isinstance(result, list):
                    result = result[0]
                
                # Extrai emoção dominante e confiança
                if 'dominant_emotion' in result:
                    emotion_deepface = result['dominant_emotion'].lower()
                    emotion = self.DEEPFACE_TO_OUR.get(emotion_deepface, 'Neutral')
                else:
                    # Se não tem dominant_emotion, pega a maior do dict de emoções
                    emotions_dict = result.get('emotion', {})
                    if emotions_dict:
                        emotion_deepface = max(emotions_dict.items(), key=lambda x: x[1])[0].lower()
                        emotion = self.DEEPFACE_TO_OUR.get(emotion_deepface, 'Neutral')
                    else:
                        return "Unknown", 0.0
                
                # Calcula confiança (normaliza valores do DeepFace)
                if 'emotion' in result:
                    emotions_dict = result['emotion']
                    # DeepFace retorna valores que somam ~100, normaliza para [0, 1]
                    max_confidence = max(emotions_dict.values()) / 100.0
                    confidence = float(max_confidence)
                else:
                    confidence = 0.5  # Fallback
                
                # Verifica threshold
                if confidence < self.confidence_threshold:
                    logger.debug(
                        f"Confiança abaixo do threshold: {confidence:.2f} < {self.confidence_threshold}"
                    )
                    return "Unknown", confidence
                
                return emotion, confidence
                
            finally:
                # Remove arquivo temporário
                if temp_path and temp_path.exists():
                    try:
                        temp_path.unlink()
                    except Exception as e:
                        logger.debug(f"Erro ao remover arquivo temporário: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao classificar emoção com DeepFace: {e}")
            return "Unknown", 0.0
    
    def _prepare_face(self, face: np.ndarray) -> np.ndarray:
        """
        Prepara a face para DeepFace.
        
        Args:
            face: Face em qualquer formato
            
        Returns:
            Face preparada (BGR, uint8)
        """
        # Converte para uint8 se necessário
        if face.dtype != np.uint8:
            if face.max() <= 1.0:
                face = (face * 255).astype(np.uint8)
            else:
                face = face.astype(np.uint8)
        
        # Converte para BGR se necessário
        if len(face.shape) == 2:
            # Grayscale -> BGR
            face = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
        elif len(face.shape) == 3 and face.shape[2] == 1:
            # Grayscale com canal -> BGR
            face = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
        elif len(face.shape) == 3 and face.shape[2] == 3:
            # Já é colorido, assume BGR (OpenCV padrão)
            pass
        else:
            logger.warning(f"Formato de face inválido: {face.shape}")
            return None
        
        return face
    
    def _save_temp_face(self, face: np.ndarray) -> Optional[Path]:
        """
        Salva face temporariamente para DeepFace processar.
        
        Args:
            face: Face preparada
            
        Returns:
            Path do arquivo temporário ou None
        """
        try:
            import tempfile
            import os
            
            # Cria diretório temporário se não existir
            temp_dir = Path(tempfile.gettempdir()) / "bioface_deepface"
            temp_dir.mkdir(exist_ok=True)
            
            # Gera nome único
            import uuid
            temp_file = temp_dir / f"face_{uuid.uuid4().hex[:8]}.jpg"
            
            # Salva imagem
            cv2.imwrite(str(temp_file), face)
            
            if not temp_file.exists():
                logger.warning("Falha ao salvar arquivo temporário")
                return None
            
            return temp_file
            
        except Exception as e:
            logger.error(f"Erro ao salvar face temporária: {e}")
            return None
    
    def get_emotion_pt(self, emotion: str) -> str:
        """
        Retorna label da emoção em português.
        
        Args:
            emotion: Emoção em inglês
            
        Returns:
            Emoção em português
        """
        try:
            idx = self.EMOTION_LABELS.index(emotion)
            return self.EMOTION_LABELS_PT[idx]
        except ValueError:
            return emotion
    
    def release(self):
        """Libera recursos do classificador."""
        # Limpa cache
        self._cache.clear()
        
        # Limpa arquivos temporários antigos (opcional)
        try:
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "bioface_deepface"
            if temp_dir.exists():
                # Remove arquivos mais antigos que 1 hora
                import time
                current_time = time.time()
                for file in temp_dir.glob("*.jpg"):
                    if current_time - file.stat().st_mtime > 3600:
                        try:
                            file.unlink()
                        except:
                            pass
        except Exception as e:
            logger.debug(f"Erro ao limpar arquivos temporários: {e}")
        
        logger.info("EmotionClassifierDeepFace liberado")
