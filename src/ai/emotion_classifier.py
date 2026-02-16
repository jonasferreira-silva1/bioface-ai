"""
Módulo de classificação de emoções do BioFace AI.

Usa modelos pré-treinados de Deep Learning para classificar emoções
em faces detectadas. Suporta múltiplos modelos e datasets.
"""

import numpy as np
import tensorflow as tf
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)


class EmotionClassifier:
    """
    Classe para classificação de emoções faciais.
    
    Usa modelos de Deep Learning pré-treinados para classificar emoções.
    Suporta diferentes modelos e pode ser facilmente estendido.
    
    Emoções suportadas (FER-2013):
    - Angry (Raiva)
    - Disgust (Nojo)
    - Fear (Medo)
    - Happy (Feliz)
    - Sad (Triste)
    - Surprise (Surpresa)
    - Neutral (Neutro)
    
    Attributes:
        model: Modelo TensorFlow/Keras
        emotion_labels: Lista de labels de emoções
        input_size: Tamanho de entrada do modelo (48x48)
        confidence_threshold: Threshold mínimo de confiança
        
    Example:
        >>> classifier = EmotionClassifier()
        >>> emotion, confidence = classifier.predict(face_image)
        >>> print(f"Emoção: {emotion}, Confiança: {confidence:.2%}")
    """
    
    # Labels de emoções padrão (FER-2013)
    EMOTION_LABELS = [
        "Angry",      # 0
        "Disgust",    # 1
        "Fear",       # 2
        "Happy",      # 3
        "Sad",        # 4
        "Surprise",   # 5
        "Neutral"     # 6
    ]
    
    # Labels em português
    EMOTION_LABELS_PT = [
        "Raiva",
        "Nojo",
        "Medo",
        "Feliz",
        "Triste",
        "Surpresa",
        "Neutro"
    ]
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None
    ):
        """
        Inicializa o classificador de emoções.
        
        Args:
            model_path: Caminho para o modelo (usa modelo padrão se None)
            confidence_threshold: Threshold mínimo de confiança
            
        Note:
            Se model_path não for fornecido, tenta carregar modelo padrão.
            Se não encontrar, cria um modelo simples para demonstração.
        """
        settings = get_settings()
        
        self.confidence_threshold = (
            confidence_threshold or settings.emotion_confidence_threshold
        )
        self.input_size = settings.face_size_emotion  # 48x48
        
        self.model: Optional[tf.keras.Model] = None
        self.emotion_labels = self.EMOTION_LABELS
        
        # Carrega ou cria modelo
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
        else:
            self._create_default_model()
        
        logger.info(
            f"EmotionClassifier inicializado: "
            f"emoções={len(self.emotion_labels)}, "
            f"threshold={self.confidence_threshold}"
        )
    
    def _load_model(self, model_path: str) -> None:
        """
        Carrega um modelo pré-treinado.
        
        Args:
            model_path: Caminho para o arquivo do modelo (.h5 ou SavedModel)
        """
        try:
            logger.info(f"Carregando modelo de emoção: {model_path}")
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Modelo carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            logger.warning("Criando modelo padrão como fallback")
            self._create_default_model()
    
    def _create_default_model(self) -> None:
        """
        Cria um modelo simples para demonstração.
        
        Este modelo não é treinado e serve apenas para demonstração.
        Em produção, você deve usar um modelo pré-treinado real.
        
        Note:
            Para um modelo real, você pode:
            1. Baixar modelos pré-treinados do Hugging Face
            2. Treinar seu próprio modelo usando FER-2013
            3. Usar modelos como FERPlus ou AffectNet
        """
        logger.warning("Criando modelo de demonstração (não treinado)")
        logger.info("Para produção, use um modelo pré-treinado real")
        
        # Cria uma CNN simples para demonstração
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.input_size, self.input_size, 1)),
            
            # Primeira camada convolucional
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Segunda camada convolucional
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Terceira camada convolucional
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Flatten e camadas densas
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            
            # Camada de saída (7 emoções)
            tf.keras.layers.Dense(len(self.EMOTION_LABELS), activation='softmax')
        ])
        
        # Compila o modelo (mesmo sem treinar, precisa estar compilado)
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        logger.info("Modelo de demonstração criado")
    
    def predict(self, face: np.ndarray) -> Tuple[str, float]:
        """
        Classifica a emoção em uma face.
        
        Args:
            face: Face normalizada (48x48 grayscale, valores [0, 1])
                  Shape esperado: (48, 48, 1) ou (48, 48)
                  
        Returns:
            Tuple[str, float]: (emoção, confiança)
            
        Example:
            >>> classifier = EmotionClassifier()
            >>> emotion, confidence = classifier.predict(face)
            >>> print(f"{emotion}: {confidence:.2%}")
        """
        if self.model is None:
            logger.error("Modelo não inicializado")
            return "Unknown", 0.0
        
        if face is None or face.size == 0:
            logger.warning("Face inválida para classificação")
            return "Unknown", 0.0
        
        try:
            # Prepara a face para predição
            face_prepared = self._prepare_face(face)
            
            # Faz a predição
            predictions = self.model.predict(face_prepared, verbose=0)
            
            # Obtém a emoção com maior confiança
            emotion_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][emotion_idx])
            
            # Verifica threshold
            if confidence < self.confidence_threshold:
                logger.debug(
                    f"Confiança abaixo do threshold: {confidence:.2f} < {self.confidence_threshold}"
                )
                return "Unknown", confidence
            
            emotion = self.emotion_labels[emotion_idx]
            
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Erro ao classificar emoção: {e}")
            return "Unknown", 0.0
    
    def predict_all(self, face: np.ndarray) -> Dict[str, float]:
        """
        Retorna todas as probabilidades de emoções.
        
        Útil para análise detalhada e visualização.
        
        Args:
            face: Face normalizada (48x48 grayscale)
            
        Returns:
            Dict[str, float]: Dicionário com todas as emoções e suas confianças
            
        Example:
            >>> classifier = EmotionClassifier()
            >>> emotions = classifier.predict_all(face)
            >>> for emotion, conf in emotions.items():
            ...     print(f"{emotion}: {conf:.2%}")
        """
        if self.model is None:
            return {emotion: 0.0 for emotion in self.emotion_labels}
        
        try:
            face_prepared = self._prepare_face(face)
            predictions = self.model.predict(face_prepared, verbose=0)
            
            emotions_dict = {
                self.emotion_labels[i]: float(predictions[0][i])
                for i in range(len(self.emotion_labels))
            }
            
            return emotions_dict
            
        except Exception as e:
            logger.error(f"Erro ao obter todas as emoções: {e}")
            return {emotion: 0.0 for emotion in self.emotion_labels}
    
    def _prepare_face(self, face: np.ndarray) -> np.ndarray:
        """
        Prepara a face para predição.
        
        Normaliza formato, dimensões e valores.
        
        Args:
            face: Face normalizada
            
        Returns:
            np.ndarray: Face preparada para o modelo
        """
        # Garante que é um array numpy
        if not isinstance(face, np.ndarray):
            face = np.array(face)
        
        # Redimensiona se necessário
        if face.shape[:2] != (self.input_size, self.input_size):
            from ..vision.face_processor import FaceProcessor
            processor = FaceProcessor()
            face = processor.normalize_face(face, self.input_size, grayscale=True)
        
        # Adiciona dimensão de batch se necessário
        if len(face.shape) == 2:
            face = np.expand_dims(face, axis=-1)
        
        if len(face.shape) == 3:
            face = np.expand_dims(face, axis=0)
        
        # Garante valores [0, 1]
        if face.max() > 1.0:
            face = face / 255.0
        
        return face
    
    def get_emotion_pt(self, emotion: str) -> str:
        """
        Retorna o label da emoção em português.
        
        Args:
            emotion: Emoção em inglês
            
        Returns:
            str: Emoção em português
        """
        try:
            idx = self.emotion_labels.index(emotion)
            return self.EMOTION_LABELS_PT[idx]
        except ValueError:
            return emotion


