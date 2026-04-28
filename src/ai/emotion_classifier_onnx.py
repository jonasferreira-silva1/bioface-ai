"""
Classificador de emoções usando modelo ONNX pré-treinado + override geométrico.

Usa o modelo emotion-ferplus-8 da Microsoft como base (treinado em ~35k imagens).
Aplica override via landmarks do MediaPipe para raiva e surpresa, que são as
emoções onde o modelo ONNX é mais fraco em webcam em tempo real.

Sem TensorFlow — apenas onnxruntime (~50MB).
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
from ..utils.logger import get_logger

logger = get_logger(__name__)

FERPLUS_LABELS = [
    "Neutral", "Happy", "Surprise", "Sad",
    "Angry",   "Disgust", "Fear",   "Contempt",
]

FERPLUS_TO_PROJECT = {
    "Neutral":  "Neutral",
    "Happy":    "Happy",
    "Surprise": "Surprise",
    "Sad":      "Sad",
    "Angry":    "Angry",
    "Disgust":  "Angry",
    "Fear":     "Sad",
    "Contempt": "Neutral",
}

EMOTION_LABELS_PT = {
    "Happy":    "Feliz",
    "Sad":      "Triste",
    "Angry":    "Raiva",
    "Surprise": "Surpresa",
    "Neutral":  "Neutro",
    "Unknown":  "Desconhecido",
}

MODEL_URL      = "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx"
MODEL_FILENAME = "emotion-ferplus-8.onnx"


class EmotionClassifierONNX:
    """
    Classificador híbrido: ONNX (FER+) + override geométrico via landmarks.

    - ONNX cuida de Happy, Sad, Neutral (bom em textura facial)
    - Override geométrico detecta Angry (sobrancelhas baixas) e
      Surprise (sobrancelhas altas + boca aberta) com muito mais precisão
    """

    EMOTION_LABELS        = ["Happy", "Sad", "Angry", "Surprise", "Neutral"]
    EMOTION_LABELS_PT_LIST = ["Feliz", "Triste", "Raiva", "Surpresa", "Neutro"]

    def __init__(self, confidence_threshold: float = 0.0,
                 models_dir: Optional[Path] = None):
        self.confidence_threshold = confidence_threshold
        self.session    = None
        self.input_name = None
        self._ready     = False

        # Histórico para estabilização temporal de raiva e surpresa
        # Guarda os últimos N resultados geométricos para evitar oscilação
        self._geo_history: list = []   # últimos brow/mar values
        self._GEO_HISTORY_SIZE = 6     # frames de memória

        if models_dir is None:
            models_dir = Path(__file__).parent.parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        self.model_path = models_dir / MODEL_FILENAME

        self._load_model()

    # ── Carregamento do modelo ────────────────────────────────────────────────

    def _load_model(self):
        try:
            import onnxruntime as ort
        except ImportError:
            logger.error("onnxruntime não instalado. Execute: pip install onnxruntime")
            return

        if not self.model_path.exists():
            logger.info(f"Modelo não encontrado. Baixando de {MODEL_URL}...")
            if not self._download_model():
                return

        try:
            opts = ort.SessionOptions()
            opts.inter_op_num_threads  = 2
            opts.intra_op_num_threads  = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.session    = ort.InferenceSession(
                str(self.model_path), sess_options=opts,
                providers=['CPUExecutionProvider']
            )
            self.input_name = self.session.get_inputs()[0].name
            self._ready     = True
            logger.info(f"Modelo ONNX carregado: {self.model_path.name}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo ONNX: {e}")

    def _download_model(self) -> bool:
        try:
            import urllib.request
            logger.info("Baixando modelo emotion-ferplus (~30MB)...")

            def progress(count, block_size, total_size):
                if total_size > 0:
                    pct = min(100, count * block_size * 100 // total_size)
                    if pct % 10 == 0:
                        logger.info(f"  Download: {pct}%")

            urllib.request.urlretrieve(MODEL_URL, self.model_path, reporthook=progress)
            logger.info(f"Modelo salvo em: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Falha ao baixar modelo: {e}")
            return False

    # ── Pré-processamento ─────────────────────────────────────────────────────

    def _preprocess(self, face: np.ndarray) -> np.ndarray:
        """Converte face para (1,1,64,64) float32 esperado pelo FER+."""
        if len(face.shape) == 3:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if face.shape[2] == 3 \
                   else face[:, :, 0]

        if face.max() <= 1.0:
            face = (face * 255.0).astype(np.float32)
        else:
            face = face.astype(np.float32)

        face = cv2.resize(face, (64, 64), interpolation=cv2.INTER_AREA)
        return face.reshape(1, 1, 64, 64)

    # ── Override geométrico ───────────────────────────────────────────────────

    def _extract_geometric_features(self, landmarks: np.ndarray) -> Dict[str, float]:
        """
        Extrai métricas geométricas dos 468 landmarks do MediaPipe (em pixels).
        Retorna dict vazio se landmarks inválidos.
        """
        try:
            if landmarks is None or landmarks.size == 0:
                return {}
            coords = landmarks[:, :2].astype(np.float32)
            if len(coords) < 468:
                return {}

            # Referências de tamanho do rosto
            face_h = abs(coords[152][1] - coords[10][1]) + 1e-6   # queixo → testa
            face_w = abs(coords[263][0] - coords[33][0])  + 1e-6   # olho ext → olho ext

            # ── EAR (Eye Aspect Ratio) ────────────────────────────────────────
            l_ear = abs(coords[159][1] - coords[145][1]) / face_h / \
                    (abs(coords[133][0] - coords[33][0])  / face_w + 1e-6)
            r_ear = abs(coords[386][1] - coords[374][1]) / face_h / \
                    (abs(coords[362][0] - coords[263][0]) / face_w + 1e-6)
            eye_ear = (l_ear + r_ear) / 2.0

            # ── Distância sobrancelha → olho ──────────────────────────────────
            l_brow_y = np.mean(coords[[70, 63, 105, 66, 107], 1])
            r_brow_y = np.mean(coords[[336, 296, 334, 293, 300], 1])
            brow_eye_dist = ((coords[159][1] - l_brow_y) +
                             (coords[386][1] - r_brow_y)) / 2.0 / face_h

            # ── Slope das sobrancelhas ────────────────────────────────────────
            dx_l = coords[107][0] - coords[70][0]
            sl   = (coords[107][1] - coords[70][1]) / (dx_l + 1e-6)
            dx_r = coords[300][0] - coords[336][0]
            sr   = (coords[336][1] - coords[300][1]) / (dx_r + 1e-6)
            brow_slope = (sl + sr) / 2.0

            # ── MAR (Mouth Aspect Ratio) ──────────────────────────────────────
            m_w   = abs(coords[291][0] - coords[61][0]) / face_w
            m_h   = abs(coords[17][1]  - coords[0][1])  / face_h
            mouth_mar = m_h / (m_w + 1e-6)

            # ── Curvatura da boca ─────────────────────────────────────────────
            corner_y = (coords[61][1] + coords[291][1]) / 2.0
            mouth_curve = (coords[17][1] - corner_y) / face_h

            # ── Largura da boca normalizada ───────────────────────────────────
            mouth_width_norm = m_w

            return {
                'eye_ear':          float(eye_ear),
                'brow_eye_dist':    float(brow_eye_dist),
                'brow_slope':       float(brow_slope),
                'mouth_mar':        float(mouth_mar),
                'mouth_curve':      float(mouth_curve),
                'mouth_width_norm': float(mouth_width_norm),
            }
        except Exception as e:
            logger.debug(f"Erro ao extrair features geométricas: {e}")
            return {}

    def _geometric_override(self, geo: Dict[str, float],
                            onnx_probs: Dict[str, float]) -> Dict[str, float]:
        """
        Substitui o resultado do ONNX quando sinais geométricos são fortes.

        Estratégia: se o sinal geométrico ultrapassar um limiar claro,
        ele SUBSTITUI o ONNX em vez de misturar — evita que Neutro alto
        do ONNX engula o sinal de raiva/surpresa após normalização.
        """
        if not geo:
            return onnx_probs

        brow = geo['brow_eye_dist']   # neutro ≈ 0.09
        mar  = geo['mouth_mar']       # neutro ≈ 0.20

        probs = dict(onnx_probs)

        # ── RAIVA ─────────────────────────────────────────────────────────────
        # Sinal: sobrancelhas descem abaixo de 0.075
        # Quanto mais baixo, mais certeza — abaixo de 0.060 é quase certo
        if brow < 0.075:
            # Força proporcional: 0.075→0.0 mapeia para 0.0→1.0
            strength = min(1.0, (0.075 - brow) / 0.030)

            # Abaixo de 0.060: substitui completamente
            # Entre 0.060-0.075: mistura progressiva
            angry_val = 0.75 + strength * 0.20   # 0.75 a 0.95

            probs['Angry']   = angry_val
            probs['Happy']   = probs.get('Happy', 0.0) * (1.0 - strength)
            probs['Neutral'] = probs.get('Neutral', 0.0) * (1.0 - strength * 0.85)
            probs['Sad']     = probs.get('Sad', 0.0) * 0.5
            probs['Surprise']= probs.get('Surprise', 0.0) * 0.3

        # ── SURPRESA ──────────────────────────────────────────────────────────
        # Sinal duplo: sobrancelhas sobem (brow > 0.105) E boca abre (mar > 0.25)
        # Ambos precisam estar presentes — evita falsos positivos
        elif brow > 0.100 and mar > 0.230:
            brow_strength = min(1.0, (brow - 0.100) / 0.040)  # 0.100→0.140
            mar_strength  = min(1.0, (mar  - 0.230) / 0.120)  # 0.230→0.350
            strength      = brow_strength * 0.55 + mar_strength * 0.45

            if strength > 0.25:
                surp_val = 0.70 + strength * 0.25   # 0.70 a 0.95

                probs['Surprise'] = surp_val
                probs['Neutral']  = probs.get('Neutral', 0.0) * (1.0 - strength * 0.85)
                probs['Happy']    = probs.get('Happy', 0.0) * (1.0 - strength * 0.50)

        # Re-normaliza
        total = sum(probs.values()) + 1e-8
        return {k: v / total for k, v in probs.items()}

    # ── Interface pública ─────────────────────────────────────────────────────

    def predict(self, face: np.ndarray,
                landmarks: Optional[np.ndarray] = None) -> Tuple[str, float]:
        if face is None or face.size == 0 or not self._ready:
            return "Unknown", 0.0

        try:
            # 1. Inferência ONNX
            inp     = self._preprocess(face)
            outputs = self.session.run(None, {self.input_name: inp})
            raw     = outputs[0][0]

            exp   = np.exp(raw - raw.max())
            probs = exp / exp.sum()

            project_probs: Dict[str, float] = {}
            for i, lbl in enumerate(FERPLUS_LABELS):
                proj = FERPLUS_TO_PROJECT[lbl]
                project_probs[proj] = project_probs.get(proj, 0.0) + float(probs[i])

            # 2. Override geométrico com histórico suavizado
            if landmarks is not None and landmarks.size > 0:
                geo = self._extract_geometric_features(landmarks)
                if geo:
                    # Acumula histórico de brow e mar
                    self._geo_history.append({
                        'brow': geo['brow_eye_dist'],
                        'mar':  geo['mouth_mar'],
                    })
                    if len(self._geo_history) > self._GEO_HISTORY_SIZE:
                        self._geo_history.pop(0)

                    # Usa a MEDIANA dos últimos N frames — muito mais estável que o valor instantâneo
                    # A mediana ignora frames ruidosos e mantém o sinal quando a expressão é sustentada
                    brows = [h['brow'] for h in self._geo_history]
                    mars  = [h['mar']  for h in self._geo_history]
                    geo_smooth = dict(geo)
                    geo_smooth['brow_eye_dist'] = float(np.median(brows))
                    geo_smooth['mouth_mar']     = float(np.median(mars))

                    project_probs = self._geometric_override(geo_smooth, project_probs)

            emotion    = max(project_probs, key=project_probs.get)
            confidence = project_probs[emotion]
            return emotion, float(confidence)

        except Exception as e:
            logger.error(f"Erro na inferência: {e}")
            return "Unknown", 0.0

    def predict_all(self, face: np.ndarray) -> Dict[str, float]:
        if face is None or face.size == 0 or not self._ready:
            return {e: 0.0 for e in self.EMOTION_LABELS}
        try:
            inp     = self._preprocess(face)
            outputs = self.session.run(None, {self.input_name: inp})
            raw     = outputs[0][0]
            exp     = np.exp(raw - raw.max())
            probs   = exp / exp.sum()
            result: Dict[str, float] = {}
            for i, lbl in enumerate(FERPLUS_LABELS):
                proj = FERPLUS_TO_PROJECT[lbl]
                result[proj] = result.get(proj, 0.0) + float(probs[i])
            return result
        except Exception as e:
            logger.error(f"Erro em predict_all: {e}")
            return {e: 0.0 for e in self.EMOTION_LABELS}

    def get_emotion_pt(self, emotion: str) -> str:
        return EMOTION_LABELS_PT.get(emotion, emotion)

    @property
    def is_ready(self) -> bool:
        return self._ready
