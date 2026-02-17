"""
Módulo de classificação de emoções leve (sem TensorFlow).

Usa características visuais e heurísticas para classificar emoções básicas.
Versão inicial que pode ser substituída por modelo ONNX posteriormente.
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
from pathlib import Path
from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)


class EmotionClassifierLight:
    """
    Classificador de emoções leve (sem TensorFlow).
    
    Usa características visuais e heurísticas para classificar emoções básicas.
    Esta é uma versão inicial que pode ser substituída por modelo ONNX posteriormente.
    
    Emoções suportadas:
    - Happy (Feliz)
    - Sad (Triste)
    - Angry (Raiva)
    - Surprise (Surpresa)
    - Neutral (Neutro)
    
    Attributes:
        emotion_labels: Lista de labels de emoções
        input_size: Tamanho de entrada (48x48)
        confidence_threshold: Threshold mínimo de confiança
        
    Example:
        >>> classifier = EmotionClassifierLight()
        >>> emotion, confidence = classifier.predict(face_image)
        >>> print(f"Emoção: {emotion}, Confiança: {confidence:.2%}")
    """
    
    # Labels de emoções
    EMOTION_LABELS = [
        "Happy",      # 0
        "Sad",        # 1
        "Angry",      # 2
        "Surprise",   # 3
        "Neutral"     # 4
    ]
    
    # Labels em português
    EMOTION_LABELS_PT = [
        "Feliz",
        "Triste",
        "Raiva",
        "Surpresa",
        "Neutro"
    ]
    
    def __init__(
        self,
        confidence_threshold: Optional[float] = None
    ):
        """
        Inicializa o classificador de emoções leve.
        
        Args:
            confidence_threshold: Threshold mínimo de confiança
        """
        settings = get_settings()
        
        self.confidence_threshold = (
            confidence_threshold or settings.emotion_confidence_threshold
        )
        self.input_size = settings.face_size_emotion  # 48x48
        
        logger.info(
            f"EmotionClassifierLight inicializado: "
            f"emoções={len(self.EMOTION_LABELS)}, "
            f"threshold={self.confidence_threshold}"
        )
    
    def predict(
        self, 
        face: np.ndarray,
        landmarks: Optional[np.ndarray] = None
    ) -> Tuple[str, float]:
        """
        Classifica a emoção em uma face usando características visuais e landmarks.
        
        Args:
            face: Face normalizada (48x48 grayscale, valores [0, 1])
                  Shape esperado: (48, 48, 1) ou (48, 48)
            landmarks: Landmarks do MediaPipe (468 pontos) - opcional, melhora precisão
                  
        Returns:
            Tuple[str, float]: (emoção, confiança)
            
        Example:
            >>> classifier = EmotionClassifierLight()
            >>> emotion, confidence = classifier.predict(face, landmarks)
            >>> print(f"{emotion}: {confidence:.2%}")
        """
        if face is None or face.size == 0:
            logger.warning("Face inválida para classificação")
            return "Unknown", 0.0
        
        try:
            # Prepara a face
            face_prepared = self._prepare_face(face)
            
            # Extrai características visuais
            features = self._extract_features(face_prepared)
            
            # Se landmarks disponíveis, adiciona análise geométrica
            if landmarks is not None:
                geometric_features = self._extract_geometric_features(landmarks)
                features.update(geometric_features)
            
            # Classifica usando heurísticas melhoradas
            emotion, confidence = self._classify_from_features(features)
            
            # Verifica threshold
            if confidence < self.confidence_threshold:
                logger.debug(
                    f"Confiança abaixo do threshold: {confidence:.2f} < {self.confidence_threshold}"
                )
                return "Unknown", confidence
            
            return emotion, confidence
            
        except Exception as e:
            logger.error(f"Erro ao classificar emoção: {e}")
            return "Unknown", 0.0
    
    def predict_all(self, face: np.ndarray) -> Dict[str, float]:
        """
        Retorna todas as probabilidades de emoções.
        
        Args:
            face: Face normalizada (48x48 grayscale)
            
        Returns:
            Dict[str, float]: Dicionário com todas as emoções e suas confianças
        """
        if face is None or face.size == 0:
            return {emotion: 0.0 for emotion in self.EMOTION_LABELS}
        
        try:
            face_prepared = self._prepare_face(face)
            features = self._extract_features(face_prepared)
            
            # Calcula confiança para cada emoção
            emotions_dict = {}
            for emotion in self.EMOTION_LABELS:
                _, conf = self._classify_from_features(features, target_emotion=emotion)
                emotions_dict[emotion] = conf
            
            # Normaliza para somar 1.0
            total = sum(emotions_dict.values())
            if total > 0:
                emotions_dict = {k: v / total for k, v in emotions_dict.items()}
            
            return emotions_dict
            
        except Exception as e:
            logger.error(f"Erro ao obter todas as emoções: {e}")
            return {emotion: 0.0 for emotion in self.EMOTION_LABELS}
    
    def _prepare_face(self, face: np.ndarray) -> np.ndarray:
        """
        Prepara a face para análise.
        
        Args:
            face: Face normalizada
            
        Returns:
            np.ndarray: Face preparada
        """
        # Garante que é um array numpy
        if not isinstance(face, np.ndarray):
            face = np.array(face)
        
        # Remove dimensão de batch se existir
        if len(face.shape) == 4:
            face = face[0]
        
        # Remove dimensão de canal se existir (grayscale)
        if len(face.shape) == 3:
            if face.shape[2] == 1:
                face = face[:, :, 0]
            else:
                # Se for colorida, converte para grayscale
                face = cv2.cvtColor((face * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY) / 255.0
        
        # Redimensiona se necessário
        if face.shape[:2] != (self.input_size, self.input_size):
            face = cv2.resize(
                face,
                (self.input_size, self.input_size),
                interpolation=cv2.INTER_AREA
            )
        
        # Garante valores [0, 1]
        if face.max() > 1.0:
            face = face / 255.0
        
        return face
    
    def _extract_features(self, face: np.ndarray) -> Dict[str, float]:
        """
        Extrai características visuais da face.
        
        Args:
            face: Face normalizada (48x48 grayscale)
            
        Returns:
            Dict com características extraídas
        """
        # Converte para uint8 para processamento
        face_uint8 = (face * 255).astype(np.uint8)
        
        # 1. Brilho médio (indica iluminação geral)
        brightness = np.mean(face)
        
        # 2. Contraste (desvio padrão)
        contrast = np.std(face)
        
        # 3. Região dos olhos (linhas 10-20, colunas 10-38)
        eye_region = face[10:20, 10:38]
        eye_brightness = np.mean(eye_region)
        eye_contrast = np.std(eye_region)
        
        # 4. Região da boca (linhas 25-35, colunas 10-38)
        mouth_region = face[25:35, 10:38]
        mouth_brightness = np.mean(mouth_region)
        mouth_contrast = np.std(mouth_region)
        
        # 5. Assimetria facial (diferença entre lados)
        left_half = face[:, :24]
        right_half = face[:, 24:]
        asymmetry = np.abs(np.mean(left_half) - np.mean(right_half))
        
        # 6. Bordas (detecta expressões)
        edges = cv2.Canny(face_uint8, 50, 150)
        edge_density = np.sum(edges > 0) / (face.shape[0] * face.shape[1])
        
        # 7. Histograma (distribuição de intensidades)
        hist = cv2.calcHist([face_uint8], [0], None, [32], [0, 256])
        hist_normalized = hist.flatten() / (hist.sum() + 1e-8)
        hist_skew = np.mean((hist_normalized - np.mean(hist_normalized)) ** 3)
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'eye_brightness': float(eye_brightness),
            'eye_contrast': float(eye_contrast),
            'mouth_brightness': float(mouth_brightness),
            'mouth_contrast': float(mouth_contrast),
            'asymmetry': float(asymmetry),
            'edge_density': float(edge_density),
            'hist_skew': float(hist_skew)
        }
    
    def _extract_geometric_features(self, landmarks: np.ndarray) -> Dict[str, float]:
        """
        Extrai características geométricas dos landmarks do MediaPipe.
        
        Usa posições específicas dos landmarks para detectar expressões:
        - Sobrancelhas (pontos 107, 336, 9, 10)
        - Olhos (pontos 33, 7, 163, 144, 145, 153, 154, 155, 157, 158, 159, 160, 161, 246)
        - Boca (pontos 61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318)
        
        Args:
            landmarks: Array de landmarks (468 pontos) do MediaPipe
            
        Returns:
            Dict com características geométricas
        """
        try:
            # Índices dos landmarks importantes (MediaPipe Face Mesh)
            # Sobrancelhas
            left_eyebrow = [107, 336, 9, 10, 151]
            right_eyebrow = [337, 299, 333, 298, 301]
            
            # Olhos
            left_eye = [33, 7, 163, 144, 145, 153, 154, 155, 157, 158, 159, 160, 161, 246]
            right_eye = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
            
            # Boca
            mouth_outer = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
            mouth_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324]
            
            # Extrai coordenadas
            if len(landmarks.shape) == 2 and landmarks.shape[1] >= 2:
                # Landmarks 2D (x, y)
                coords = landmarks[:, :2]
            elif len(landmarks.shape) == 2 and landmarks.shape[1] >= 3:
                # Landmarks 3D (x, y, z) - usa apenas x, y
                coords = landmarks[:, :2]
            else:
                return {}
            
            # Normaliza coordenadas para [0, 1]
            # O face_detector retorna landmarks em pixels (multiplicado por w, h)
            # Precisamos normalizar de volta para [0, 1] para análise geométrica
            if coords.max() > 1.0:
                # Coordenadas em pixels - normaliza pelo máximo encontrado
                coords_max = coords.max(axis=0)
                if coords_max[0] > 1.0 and coords_max[1] > 1.0:
                    # Normaliza pelo máximo de cada eixo (mais robusto)
                    coords = coords / (coords_max + 1e-8)
                else:
                    # Se algum eixo já está normalizado, normaliza apenas o que precisa
                    if coords_max[0] > 1.0:
                        coords[:, 0] = coords[:, 0] / coords_max[0]
                    if coords_max[1] > 1.0:
                        coords[:, 1] = coords[:, 1] / coords_max[1]
            
            features = {}
            
            # 1. Abertura dos olhos (distância entre pálpebras)
            if len(left_eye) >= 4 and len(right_eye) >= 4:
                # Ponto superior e inferior do olho
                left_eye_top = coords[33] if 33 < len(coords) else coords[0]
                left_eye_bottom = coords[145] if 145 < len(coords) else coords[0]
                left_eye_open = np.linalg.norm(left_eye_top - left_eye_bottom)
                
                right_eye_top = coords[362] if 362 < len(coords) else coords[0]
                right_eye_bottom = coords[386] if 386 < len(coords) else coords[0]
                right_eye_open = np.linalg.norm(right_eye_top - right_eye_bottom)
                
                features['eye_openness'] = float((left_eye_open + right_eye_open) / 2.0)
            else:
                features['eye_openness'] = 0.5
            
            # 2. Posição das sobrancelhas (altura relativa)
            if len(left_eyebrow) >= 2 and len(right_eyebrow) >= 2:
                left_eyebrow_y = np.mean([coords[i][1] for i in left_eyebrow if i < len(coords)])
                right_eyebrow_y = np.mean([coords[i][1] for i in right_eyebrow if i < len(coords)])
                eyebrow_height = float((left_eyebrow_y + right_eyebrow_y) / 2.0)
                features['eyebrow_height'] = eyebrow_height
            else:
                features['eyebrow_height'] = 0.5
            
            # 3. Abertura da boca (largura e altura)
            if len(mouth_outer) >= 4:
                mouth_points = [coords[i] for i in mouth_outer if i < len(coords)]
                if len(mouth_points) >= 4:
                    mouth_width = np.max([p[0] for p in mouth_points]) - np.min([p[0] for p in mouth_points])
                    mouth_height = np.max([p[1] for p in mouth_points]) - np.min([p[1] for p in mouth_points])
                    features['mouth_width'] = float(mouth_width)
                    features['mouth_height'] = float(mouth_height)
                    features['mouth_aspect_ratio'] = float(mouth_height / (mouth_width + 1e-8))
                else:
                    features['mouth_width'] = 0.1
                    features['mouth_height'] = 0.05
                    features['mouth_aspect_ratio'] = 0.5
            else:
                features['mouth_width'] = 0.1
                features['mouth_height'] = 0.05
                features['mouth_aspect_ratio'] = 0.5
            
            # 4. Inclinação das sobrancelhas (detecta raiva/tristeza)
            # Slope negativo = sobrancelha inclinada para baixo (raiva)
            # Slope positivo = sobrancelha inclinada para cima (surpresa)
            if len(left_eyebrow) >= 2 and len(right_eyebrow) >= 2:
                # Pega pontos externos das sobrancelhas
                left_eyebrow_start_idx = left_eyebrow[0] if left_eyebrow[0] < len(coords) else 0
                left_eyebrow_end_idx = left_eyebrow[-1] if left_eyebrow[-1] < len(coords) else 0
                left_eyebrow_start = coords[left_eyebrow_start_idx]
                left_eyebrow_end = coords[left_eyebrow_end_idx]
                
                # Calcula slope: (y_end - y_start) / (x_end - x_start)
                # Se slope negativo, sobrancelha está descendo (raiva)
                dx_left = left_eyebrow_end[0] - left_eyebrow_start[0]
                if abs(dx_left) > 1e-6:
                    left_eyebrow_slope = (left_eyebrow_end[1] - left_eyebrow_start[1]) / dx_left
                else:
                    left_eyebrow_slope = 0.0
                
                right_eyebrow_start_idx = right_eyebrow[0] if right_eyebrow[0] < len(coords) else 0
                right_eyebrow_end_idx = right_eyebrow[-1] if right_eyebrow[-1] < len(coords) else 0
                right_eyebrow_start = coords[right_eyebrow_start_idx]
                right_eyebrow_end = coords[right_eyebrow_end_idx]
                
                dx_right = right_eyebrow_end[0] - right_eyebrow_start[0]
                if abs(dx_right) > 1e-6:
                    right_eyebrow_slope = (right_eyebrow_end[1] - right_eyebrow_start[1]) / dx_right
                else:
                    right_eyebrow_slope = 0.0
                
                # Média dos slopes (negativo = raiva)
                features['eyebrow_slope'] = float((left_eyebrow_slope + right_eyebrow_slope) / 2.0)
            else:
                features['eyebrow_slope'] = 0.0
            
            return features
            
        except Exception as e:
            logger.debug(f"Erro ao extrair características geométricas: {e}")
            return {}
    
    def _classify_from_features(
        self,
        features: Dict[str, float],
        target_emotion: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Classifica emoção a partir de características visuais.
        
        Usa heurísticas baseadas em características faciais conhecidas.
        
        Args:
            features: Características extraídas
            target_emotion: Se fornecido, calcula confiança apenas para esta emoção
            
        Returns:
            Tuple[str, float]: (emoção, confiança)
        """
        scores = {}
        
        # Happy (Feliz): boca aberta/curvada para cima, olhos mais brilhantes
        happy_score = 0.0
        
        # Se tiver características geométricas, usa elas
        if 'mouth_aspect_ratio' in features:
            # Boca aberta (alta altura relativa) = feliz
            mouth_open = features['mouth_aspect_ratio'] * 2.0
            happy_score += mouth_open * 0.4
        
        if 'mouth_width' in features:
            # Boca larga = sorriso
            mouth_wide = min(1.0, features['mouth_width'] * 5.0)
            happy_score += mouth_wide * 0.3
        
        # Características visuais
        happy_score += (
            features['mouth_brightness'] * 0.2 +
            features['eye_brightness'] * 0.1
        )
        
        scores['Happy'] = min(1.0, happy_score * 1.5)
        
        # Sad (Triste): boca mais escura, olhos mais escuros, mais assimetria
        sad_score = (
            (1.0 - features['mouth_brightness']) * 0.4 +
            (1.0 - features['eye_brightness']) * 0.3 +
            features['asymmetry'] * 0.2 +
            (1.0 - features['edge_density']) * 0.1
        )
        scores['Sad'] = min(1.0, sad_score * 2.0)
        
        # Angry (Raiva): sobrancelhas baixas/inclinadas para baixo, boca fechada/tensa
        angry_score = 0.0
        has_geometric = False
        
        # Se tiver características geométricas, usa elas (mais preciso)
        if 'eyebrow_slope' in features:
            # Sobrancelhas inclinadas para baixo (negativo) = raiva
            # Slope negativo significa que a direita está mais baixa que a esquerda
            eyebrow_slope_angry = max(0.0, -features['eyebrow_slope']) * 3.0
            angry_score += min(1.0, eyebrow_slope_angry) * 0.5
            has_geometric = True
        
        if 'eyebrow_height' in features:
            # Sobrancelhas baixas = raiva (quanto menor, mais raiva)
            eyebrow_low = (1.0 - features['eyebrow_height']) * 2.0
            angry_score += min(1.0, eyebrow_low) * 0.3
            has_geometric = True
        
        if 'mouth_aspect_ratio' in features:
            # Boca fechada/tensa (baixa altura relativa à largura) = raiva
            # Aspect ratio baixo = boca fechada/tensa
            mouth_tight = (1.0 - features['mouth_aspect_ratio']) * 2.5
            angry_score += min(1.0, mouth_tight) * 0.2
            has_geometric = True
        
        # Características visuais (fallback se não tiver landmarks, ou complemento)
        if not has_geometric:
            # Sem landmarks - usa apenas características visuais
            angry_score = (
                features['contrast'] * 0.25 +
                features['edge_density'] * 0.35 +
                features['asymmetry'] * 0.25 +
                (1.0 - features['mouth_brightness']) * 0.15  # Boca escura = tensa
            )
        else:
            # Com landmarks - adiciona características visuais como complemento
            angry_score += (
                features['contrast'] * 0.1 +
                features['edge_density'] * 0.1 +
                (1.0 - features['mouth_brightness']) * 0.05  # Boca escura = tensa
            )
        
        scores['Angry'] = min(1.0, angry_score * 2.0)  # Multiplica por 2.0 para aumentar sensibilidade
        
        # Surprise (Surpresa): olhos muito brilhantes, alto contraste, alta densidade de bordas
        surprise_score = (
            features['eye_brightness'] * 0.4 +
            features['contrast'] * 0.3 +
            features['edge_density'] * 0.3
        )
        scores['Surprise'] = min(1.0, surprise_score * 1.8)
        
        # Neutral (Neutro): características médias, baixa assimetria, baixa densidade de bordas
        neutral_score = (
            (1.0 - features['asymmetry']) * 0.4 +
            (1.0 - features['edge_density']) * 0.3 +
            (1.0 - abs(features['brightness'] - 0.5)) * 0.3
        )
        scores['Neutral'] = min(1.0, neutral_score * 1.5)
        
        # Se target_emotion foi fornecido, retorna apenas essa
        if target_emotion:
            return target_emotion, scores.get(target_emotion, 0.0)
        
        # Encontra a emoção com maior score
        best_emotion = max(scores.keys(), key=lambda e: scores[e])
        best_confidence = scores[best_emotion]
        
        # Normaliza confiança (ajusta para range mais realista)
        # Como são heurísticas, reduz um pouco a confiança
        # Mas mantém mais alta se tiver características geométricas
        if 'eyebrow_slope' in features or 'mouth_aspect_ratio' in features:
            # Com landmarks - confiança mais alta
            best_confidence = min(0.95, best_confidence * 0.85)
        else:
            # Sem landmarks - confiança mais baixa
            best_confidence = min(0.95, best_confidence * 0.7)
        
        return best_emotion, best_confidence
    
    def get_emotion_pt(self, emotion: str) -> str:
        """
        Retorna o label da emoção em português.
        
        Args:
            emotion: Emoção em inglês
            
        Returns:
            str: Emoção em português
        """
        try:
            idx = self.EMOTION_LABELS.index(emotion)
            return self.EMOTION_LABELS_PT[idx]
        except ValueError:
            return emotion

