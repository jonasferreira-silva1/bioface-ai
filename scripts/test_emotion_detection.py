"""
Script de teste para validar detecção de emoções.

Mostra a emoção detectada em tempo real com painel visual completo.
Também imprime as métricas geométricas no terminal para calibração.

Uso:
    python scripts/test_emotion_detection.py
"""

import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.vision.camera import Camera
from src.vision.face_detector import FaceDetector
from src.vision.face_processor import FaceProcessor
from src.ai.emotion_classifier_light import EmotionClassifierLight

setup_logger()
logger = get_logger(__name__)

# Cores e ícones por emoção
EMOTION_COLORS = {
    'Happy':    (0, 220, 0),
    'Sad':      (200, 80, 0),
    'Angry':    (0, 0, 220),
    'Surprise': (0, 220, 220),
    'Neutral':  (160, 160, 160),
    'Unknown':  (80, 80, 80),
}
EMOTION_ICONS = {
    'Happy':    ':)',
    'Sad':      ':(',
    'Angry':    '>:(',
    'Surprise': ':O',
    'Neutral':  ':|',
    'Unknown':  '?',
}
EMOTION_PT = {
    'Happy': 'Feliz', 'Sad': 'Triste', 'Angry': 'Raiva',
    'Surprise': 'Surpresa', 'Neutral': 'Neutro', 'Unknown': 'Analisando',
}


def draw_emotion_panel(frame, bbox, emotion, confidence, geo):
    """Desenha painel de emoção sobre o rosto."""
    x, y, w, h = bbox
    h_frame, w_frame = frame.shape[:2]

    color    = EMOTION_COLORS.get(emotion, (200, 200, 200))
    icon     = EMOTION_ICONS.get(emotion, '?')
    label_pt = EMOTION_PT.get(emotion, emotion)

    # Bounding box colorida
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # Cantos decorativos
    corner, thick = 14, 3
    for cx, cy, dx, dy in [(x, y, 1, 1), (x+w, y, -1, 1),
                            (x, y+h, 1, -1), (x+w, y+h, -1, -1)]:
        cv2.line(frame, (cx, cy), (cx + dx*corner, cy), color, thick)
        cv2.line(frame, (cx, cy), (cx, cy + dy*corner), color, thick)

    # Texto principal: ícone + nome + confiança
    main_text = f"{icon}  {label_pt}  {confidence:.0%}"
    font, fs, ft = cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2
    (tw, th), _ = cv2.getTextSize(main_text, font, fs, ft)

    px = max(0, x)
    py = max(0, y - th - 20)

    # Fundo semitransparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (px - 4, py - 4), (px + tw + 12, py + th + 8), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.rectangle(frame, (px - 4, py - 4), (px + tw + 12, py + th + 8), color, 1)

    cv2.putText(frame, main_text, (px + 4, py + th), font, fs, color, ft)

    # Barra de confiança abaixo da bbox
    bar_x, bar_y = x, y + h + 6
    bar_w = w
    bar_h = 8
    filled = int(bar_w * confidence)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled, bar_y + bar_h), color, -1)

    # Métricas geométricas (canto inferior esquerdo do frame)
    if geo:
        metrics = [
            f"EAR (olhos): {geo.get('eye_ear', 0):.3f}",
            f"Brow-Eye:    {geo.get('brow_eye_dist', 0):.3f}",
            f"Brow slope:  {geo.get('brow_slope', 0):.3f}",
            f"Mouth MAR:   {geo.get('mouth_mar', 0):.3f}",
            f"Mouth curve: {geo.get('mouth_curve', 0):.3f}",
        ]
        mfont, mfs = cv2.FONT_HERSHEY_SIMPLEX, 0.45
        my = h_frame - len(metrics) * 18 - 10
        for i, m in enumerate(metrics):
            cv2.putText(frame, m, (10, my + i * 18), mfont, mfs, (180, 180, 180), 1)


def main():
    logger.info("Iniciando teste de emocoes — pressione Q para sair")

    camera           = Camera()
    face_detector    = FaceDetector()
    face_processor   = FaceProcessor()

    # Tenta ONNX primeiro, fallback para Light
    try:
        from src.ai.emotion_classifier_onnx import EmotionClassifierONNX
        emotion_clf = EmotionClassifierONNX(confidence_threshold=0.0)
        if emotion_clf.is_ready:
            logger.info("Usando classificador ONNX (FER+)")
        else:
            raise RuntimeError("ONNX não carregou")
    except Exception as e:
        logger.warning(f"ONNX indisponível ({e}), usando Light")
        emotion_clf = EmotionClassifierLight(confidence_threshold=0.0)

    frame_count = 0

    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue

            frame_count += 1
            faces = face_detector.detect(frame)

            if not faces:
                cv2.putText(frame, "Aguardando rosto...", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            for face in faces:
                bbox         = face['bbox']
                landmarks_3d = face.get('landmarks')

                face_proc = face_processor.process_for_emotion(frame, bbox)
                if face_proc is None:
                    continue

                # Classifica — threshold 0.0 garante que sempre retorna algo
                emotion, confidence = emotion_clf.predict(face_proc, landmarks=landmarks_3d)

                # Extrai métricas geométricas para exibir no canto
                geo = {}
                if landmarks_3d is not None and hasattr(emotion_clf, '_extract_geometric_features'):
                    geo = emotion_clf._extract_geometric_features(landmarks_3d)

                # Log a cada 30 frames
                if frame_count % 30 == 0:
                    logger.info(
                        f"Emocao: {EMOTION_PT.get(emotion, emotion)} ({confidence:.1%}) | "
                        f"EAR={geo.get('eye_ear',0):.3f} "
                        f"brow_dist={geo.get('brow_eye_dist',0):.3f} "
                        f"slope={geo.get('brow_slope',0):.3f} "
                        f"MAR={geo.get('mouth_mar',0):.3f} "
                        f"curve={geo.get('mouth_curve',0):.3f}"
                    )

                draw_emotion_panel(frame, bbox, emotion, confidence, geo)

            # FPS
            cv2.putText(frame, f"Frame {frame_count}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)

            cv2.imshow("BioFace AI - Teste de Emocoes", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        face_detector.release()
        cv2.destroyAllWindows()
        logger.info("Teste finalizado")


if __name__ == "__main__":
    main()
