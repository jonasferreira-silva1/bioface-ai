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
        Extrai características geométricas dos landmarks do MediaPipe Face Mesh.

        Índices corretos do MediaPipe Face Mesh 468 pontos:
        - Sobrancelha esquerda (da perspectiva da câmera): 70, 63, 105, 66, 107
        - Sobrancelha direita (da perspectiva da câmera): 336, 296, 334, 293, 300
        - Olho esquerdo (pálpebra): topo=159, base=145, canto_int=133, canto_ext=33
        - Olho direito (pálpebra): topo=386, base=374, canto_int=362, canto_ext=263
        - Boca externa: canto_esq=61, canto_dir=291, topo=0, base=17
        - Boca interna: topo=13, base=14
        - Nariz (referência vertical): ponta=1, base=2
        - Queixo (referência vertical): 152
        - Testa (referência vertical): 10

        Args:
            landmarks: Array de landmarks (468 pontos) do MediaPipe, em pixels

        Returns:
            Dict com características geométricas normalizadas
        """
        try:
            # Extrai apenas x, y
            if landmarks.shape[1] >= 2:
                coords = landmarks[:, :2].astype(np.float32)
            else:
                return {}

            if len(coords) < 468:
                return {}

            # Normaliza pelo tamanho do rosto (distância testa-queixo)
            # Isso torna as métricas invariantes à distância da câmera
            face_top_y    = coords[10][1]   # testa
            face_bottom_y = coords[152][1]  # queixo
            face_height   = abs(face_bottom_y - face_top_y) + 1e-6

            # Referência horizontal: largura entre cantos externos dos olhos
            face_left_x  = coords[33][0]   # canto externo olho esquerdo
            face_right_x = coords[263][0]  # canto externo olho direito
            face_width   = abs(face_right_x - face_left_x) + 1e-6

            features = {}

            # ── 1. ABERTURA DOS OLHOS (Eye Aspect Ratio - EAR) ──────────────
            # EAR = altura_vertical / largura_horizontal
            # Olho aberto: EAR alto | Olho fechado/semicerrado: EAR baixo
            # Surpresa: EAR muito alto | Raiva/tristeza: EAR baixo
            left_eye_h  = abs(coords[159][1] - coords[145][1]) / face_height
            left_eye_w  = abs(coords[133][0] - coords[33][0])  / face_width
            left_ear    = left_eye_h / (left_eye_w + 1e-6)

            right_eye_h = abs(coords[386][1] - coords[374][1]) / face_height
            right_eye_w = abs(coords[362][0] - coords[263][0]) / face_width
            right_ear   = right_eye_h / (right_eye_w + 1e-6)

            features['eye_ear'] = float((left_ear + right_ear) / 2.0)

            # ── 2. DISTÂNCIA SOBRANCELHA → OLHO (normalizada) ───────────────
            # Raiva: sobrancelhas descem → distância diminui
            # Surpresa: sobrancelhas sobem → distância aumenta
            # Tristeza: sobrancelhas internas sobem, externas descem
            left_brow_y  = np.mean([coords[i][1] for i in [70, 63, 105, 66, 107]])
            right_brow_y = np.mean([coords[i][1] for i in [336, 296, 334, 293, 300]])

            left_eye_top_y  = coords[159][1]
            right_eye_top_y = coords[386][1]

            # Distância positiva = sobrancelha ACIMA do olho (normal)
            # Distância pequena = sobrancelha próxima do olho (raiva/tensão)
            left_brow_dist  = (left_eye_top_y  - left_brow_y)  / face_height
            right_brow_dist = (right_eye_top_y - right_brow_y) / face_height
            features['brow_eye_dist'] = float((left_brow_dist + right_brow_dist) / 2.0)

            # ── 3. INCLINAÇÃO DAS SOBRANCELHAS ──────────────────────────────
            # Raiva: ponta interna sobe, ponta externa desce → slope positivo (Y cresce para baixo)
            # Tristeza: ponta interna sobe, ponta externa desce (igual raiva, mas menos intenso)
            # Surpresa: sobrancelha arqueada para cima → slope próximo de zero
            #
            # Sobrancelha esquerda: ponta_interna=107 (mais à direita na imagem), ponta_externa=70
            # Slope = (y_interna - y_externa) / (x_interna - x_externa)
            # Raiva: y_interna < y_externa (interna mais alta) → slope negativo
            left_brow_inner  = coords[107]  # ponta interna sobrancelha esquerda
            left_brow_outer  = coords[70]   # ponta externa sobrancelha esquerda
            dx_left = left_brow_inner[0] - left_brow_outer[0]
            left_slope = (left_brow_inner[1] - left_brow_outer[1]) / (dx_left + 1e-6)

            # Sobrancelha direita: ponta_interna=336, ponta_externa=300
            right_brow_inner = coords[336]
            right_brow_outer = coords[300]
            dx_right = right_brow_outer[0] - right_brow_inner[0]
            right_slope = (right_brow_inner[1] - right_brow_outer[1]) / (dx_right + 1e-6)

            # Slope médio: negativo = raiva/tristeza, positivo = neutro/surpresa
            features['brow_slope'] = float((left_slope + right_slope) / 2.0)

            # ── 4. MOUTH ASPECT RATIO (MAR) ──────────────────────────────────
            # MAR = altura_boca / largura_boca
            # Feliz/Surpresa: MAR alto (boca aberta)
            # Neutro/Raiva/Tristeza: MAR baixo (boca fechada)
            mouth_width  = abs(coords[291][0] - coords[61][0]) / face_width
            mouth_height = abs(coords[17][1]  - coords[0][1])  / face_height
            features['mouth_mar'] = float(mouth_height / (mouth_width + 1e-6))

            # ── 5. LARGURA DA BOCA NORMALIZADA ───────────────────────────────
            # Sorriso: boca mais larga que o normal
            # Referência: distância entre cantos externos dos olhos
            features['mouth_width_norm'] = float(mouth_width)

            # ── 6. CURVATURA DA BOCA (canto vs centro) ───────────────────────
            # Feliz: cantos da boca sobem → curvatura positiva
            # Triste: cantos da boca descem → curvatura negativa
            # Ponto central inferior da boca: 17 (lábio inferior)
            # Cantos: 61 (esquerdo), 291 (direito)
            mouth_corner_y = (coords[61][1] + coords[291][1]) / 2.0
            mouth_center_y = coords[17][1]
            # Positivo = cantos mais altos que centro = sorriso
            # Negativo = cantos mais baixos que centro = tristeza
            mouth_curve = (mouth_center_y - mouth_corner_y) / face_height
            features['mouth_curve'] = float(mouth_curve)

            # ── 7. DISTÂNCIA NARIZ → QUEIXO (compressão facial vertical) ─────
            # Raiva intensa: mandíbula tensionada, face levemente comprimida
            nose_to_chin = abs(coords[152][1] - coords[1][1]) / face_height
            features['nose_chin_dist'] = float(nose_to_chin)

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
        Classifica emoção a partir de características geométricas e visuais.

        Lógica baseada em Action Units (AU) do sistema FACS:
        - Happy:    AU6+AU12 → curvatura positiva da boca + boca larga
        - Sad:      AU1+AU4  → sobrancelhas internas sobem (slope negativo) + cantos da boca descem
        - Angry:    AU4+AU5+AU23 → sobrancelhas descem/aproximam + olhos semicerrados + boca tensa
        - Surprise: AU1+AU2+AU5+AU26 → sobrancelhas sobem + olhos abertos + boca aberta
        - Neutral:  ausência de sinais expressivos

        Args:
            features: Características extraídas (geométricas + visuais)
            target_emotion: Se fornecido, calcula confiança apenas para esta emoção

        Returns:
            Tuple[str, float]: (emoção, confiança)
        """
        has_geo = 'brow_eye_dist' in features  # landmarks disponíveis?

        scores = {}

        if has_geo:
            brow_eye_dist    = features['brow_eye_dist']
            brow_slope       = features['brow_slope']
            eye_ear          = features['eye_ear']
            mouth_mar        = features['mouth_mar']
            mouth_width_norm = features['mouth_width_norm']
            mouth_curve      = features['mouth_curve']

            # ── VALORES CALIBRADOS ────────────────────────────────────────────
            # Neutro:   EAR=0.1081  brow=0.1149  curve=0.0614
            # Feliz:    EAR=0.0967  brow=0.0974  curve=0.0972
            # Bravo:    EAR=0.1352  brow=0.0743  curve=0.0751
            # Triste:   EAR=0.1393  brow=0.0882  curve=0.0571
            # Surpresa: EAR=0.1676  brow=0.0926  curve=0.0731

            # ── RAIVA (veto dominante — sobrancelha baixa bloqueia feliz) ─────
            brow_down   = max(0.0, 0.0946 - brow_eye_dist) * 15.0
            ear_angry   = max(0.0, 0.1216 - eye_ear) * 10.0
            slope_angry = max(0.0, abs(brow_slope) - 0.03) * 3.0
            scores['Angry'] = min(1.0, brow_down*0.60 + ear_angry*0.25 + slope_angry*0.15)

            # ── FELIZ (bloqueado se sobrancelha franzida) ─────────────────────
            brow_ok     = 1.0 if brow_eye_dist > 0.0996 else 0.0
            curve_happy = max(0.0, mouth_curve - 0.0793) * 10.0
            width_happy = max(0.0, mouth_width_norm - 0.6080) * 5.0
            scores['Happy'] = min(1.0, (curve_happy*0.65 + width_happy*0.35) * brow_ok)

            # ── TRISTE ────────────────────────────────────────────────────────
            curve_sad  = max(0.0, -0.0592 - mouth_curve) * 10.0
            slope_sad  = max(0.0, -brow_slope - 0.08) * 4.0
            scores['Sad'] = min(1.0, curve_sad*0.65 + slope_sad*0.35)

            # ── SURPRESA ──────────────────────────────────────────────────────
            brow_up  = max(0.0, brow_eye_dist - 0.1037) * 14.0
            ear_surp = max(0.0, eye_ear - 0.1378) * 12.0
            mar_surp = max(0.0, mouth_mar - 0.2301) * 5.0
            scores['Surprise'] = min(1.0, brow_up*0.40 + ear_surp*0.35 + mar_surp*0.25)

            # ── NEUTRO ────────────────────────────────────────────────────────
            curve_neutral = max(0.0, 1.0 - abs(mouth_curve - 0.0614) * 14.0)
            brow_neutral  = max(0.0, 1.0 - abs(brow_eye_dist - 0.1149) * 25.0)
            ear_neutral   = max(0.0, 1.0 - abs(eye_ear - 0.1081) * 20.0)
            scores['Neutral'] = min(1.0, curve_neutral*0.5 + brow_neutral*0.3 + ear_neutral*0.2)

            confidence_scale = 0.92

        else:
            # ── FALLBACK: apenas características visuais ──────────────────────
            # Menos preciso, mas funciona sem landmarks
            brightness   = features['brightness']
            contrast     = features['contrast']
            edge_density = features['edge_density']
            asymmetry    = features['asymmetry']
            mouth_bright = features['mouth_brightness']
            eye_bright   = features['eye_brightness']

            scores['Happy']    = min(1.0, (mouth_bright * 0.5 + eye_bright * 0.3 + (1.0 - asymmetry) * 0.2) * 1.4)
            scores['Sad']      = min(1.0, ((1.0 - mouth_bright) * 0.4 + (1.0 - eye_bright) * 0.3 + asymmetry * 0.3) * 1.6)
            scores['Angry']    = min(1.0, (contrast * 0.35 + edge_density * 0.35 + asymmetry * 0.30) * 1.8)
            scores['Surprise'] = min(1.0, (eye_bright * 0.4 + contrast * 0.3 + edge_density * 0.3) * 1.6)
            scores['Neutral']  = min(1.0, ((1.0 - asymmetry) * 0.4 + (1.0 - edge_density) * 0.3 + (1.0 - abs(brightness - 0.5)) * 0.3) * 1.4)

            confidence_scale = 0.65  # sem landmarks, confiança mais baixa

        # Se target_emotion foi fornecido, retorna apenas essa
        if target_emotion:
            return target_emotion, float(scores.get(target_emotion, 0.0) * confidence_scale)

        # Normaliza scores para somar 1.0 (distribuição de probabilidade)
        total = sum(scores.values()) + 1e-8
        probs = {e: v / total for e, v in scores.items()}

        # Emoção vencedora
        best_emotion = max(probs, key=lambda e: probs[e])
        # Confiança = probabilidade normalizada × escala
        best_confidence = min(0.95, probs[best_emotion] * confidence_scale)

        return best_emotion, float(best_confidence)
    
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

