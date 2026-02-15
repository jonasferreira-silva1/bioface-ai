"""
BioFace AI - Pipeline Principal

Este é o ponto de entrada principal do sistema. Integra todas as camadas:
- Captura de vídeo
- Detecção de faces
- Classificação de emoções
- Visualização em tempo real

Execute este arquivo para iniciar o sistema.
"""

import cv2
import time
import argparse
from typing import Optional
from pathlib import Path

# Importa módulos do projeto
from .utils.logger import setup_logger, get_logger
from .utils.config import get_settings
from .vision.camera import Camera
from .vision.face_detector import FaceDetector
from .vision.face_processor import FaceProcessor
from .ai.emotion_classifier import EmotionClassifier

# Configura logging
setup_logger()
logger = get_logger(__name__)


class BioFacePipeline:
    """
    Pipeline principal do BioFace AI.
    
    Integra todas as camadas do sistema em um pipeline de processamento
    em tempo real. Processa frames da webcam, detecta faces, classifica
    emoções e exibe resultados.
    
    Attributes:
        camera: Objeto de captura de vídeo
        face_detector: Detector de faces (MediaPipe)
        face_processor: Processador de faces
        emotion_classifier: Classificador de emoções
        frame_count: Contador de frames processados
        skip_counter: Contador para frame skipping
        
    Example:
        >>> pipeline = BioFacePipeline()
        >>> pipeline.run()
    """
    
    def __init__(self):
        """Inicializa o pipeline com todos os componentes."""
        logger.info("=" * 60)
        logger.info("Inicializando BioFace AI Pipeline")
        logger.info("=" * 60)
        
        settings = get_settings()
        
        # Inicializa componentes
        logger.info("Inicializando componentes...")
        
        # Câmera
        self.camera = Camera()
        logger.info("✓ Câmera inicializada")
        
        # Detector de faces
        self.face_detector = FaceDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_faces=1
        )
        logger.info("✓ Face Detector inicializado")
        
        # Processador de faces
        self.face_processor = FaceProcessor()
        logger.info("✓ Face Processor inicializado")
        
        # Classificador de emoções
        self.emotion_classifier = EmotionClassifier()
        logger.info("✓ Emotion Classifier inicializado")
        
        # Contadores
        self.frame_count = 0
        self.skip_counter = 0
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        
        logger.info("=" * 60)
        logger.info("Pipeline inicializado com sucesso!")
        logger.info("=" * 60)
    
    def process_frame(self, frame) -> tuple:
        """
        Processa um único frame.
        
        Args:
            frame: Frame BGR da câmera
            
        Returns:
            tuple: (frame_annotated, results)
                - frame_annotated: Frame com anotações desenhadas
                - results: Lista de resultados (faces detectadas + emoções)
        """
        results = []
        
        # Detecta faces
        faces = self.face_detector.detect(frame)
        
        # Processa cada face detectada
        for face in faces:
            bbox = face['bbox']
            landmarks = face['landmarks_2d']
            
            # Processa face para emoção
            face_processed = self.face_processor.process_for_emotion(frame, bbox)
            
            if face_processed is not None:
                # Classifica emoção
                emotion, confidence = self.emotion_classifier.predict(face_processed)
                
                # Adiciona resultado
                result = {
                    'bbox': bbox,
                    'emotion': emotion,
                    'emotion_pt': self.emotion_classifier.get_emotion_pt(emotion),
                    'confidence': confidence,
                    'landmarks': landmarks
                }
                results.append(result)
            else:
                # Face detectada mas não processada
                result = {
                    'bbox': bbox,
                    'emotion': 'Unknown',
                    'emotion_pt': 'Desconhecido',
                    'confidence': 0.0,
                    'landmarks': landmarks
                }
                results.append(result)
        
        # Desenha anotações no frame
        frame_annotated = self._draw_annotations(frame, results)
        
        return frame_annotated, results
    
    def _draw_annotations(self, frame, results) -> cv2.typing.MatLike:
        """
        Desenha anotações no frame (bounding boxes, emoções, etc).
        
        Args:
            frame: Frame original
            results: Lista de resultados de detecção
            
        Returns:
            Frame com anotações desenhadas
        """
        frame_copy = frame.copy()
        
        for result in results:
            bbox = result['bbox']
            emotion = result['emotion_pt']
            confidence = result['confidence']
            
            x, y, w, h = bbox
            
            # Cores baseadas na emoção
            color = self._get_emotion_color(result['emotion'])
            
            # Desenha bounding box
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
            
            # Prepara texto
            text = f"{emotion}: {confidence:.0%}"
            
            # Calcula tamanho do texto para fundo
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Desenha fundo para texto (melhora legibilidade)
            cv2.rectangle(
                frame_copy,
                (x, y - text_height - 10),
                (x + text_width, y),
                color,
                -1
            )
            
            # Desenha texto
            cv2.putText(
                frame_copy,
                text,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        # Desenha FPS
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(
            frame_copy,
            fps_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Desenha contador de frames
        frame_text = f"Frames: {self.frame_count}"
        cv2.putText(
            frame_copy,
            frame_text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        return frame_copy
    
    def _get_emotion_color(self, emotion: str) -> tuple:
        """
        Retorna cor BGR baseada na emoção.
        
        Args:
            emotion: Emoção detectada
            
        Returns:
            tuple: Cor BGR (B, G, R)
        """
        color_map = {
            'Happy': (0, 255, 0),      # Verde
            'Sad': (255, 0, 0),        # Azul
            'Angry': (0, 0, 255),       # Vermelho
            'Surprise': (0, 255, 255),  # Amarelo
            'Fear': (128, 0, 128),      # Roxo
            'Disgust': (0, 128, 255),   # Laranja
            'Neutral': (128, 128, 128), # Cinza
            'Unknown': (64, 64, 64)     # Cinza escuro
        }
        
        return color_map.get(emotion, (128, 128, 128))
    
    def update_fps(self):
        """Atualiza cálculo de FPS."""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:  # Atualiza a cada segundo
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self):
        """
        Executa o pipeline principal.
        
        Loop principal que captura frames, processa e exibe resultados.
        Pressione 'q' para sair.
        """
        logger.info("Iniciando loop principal...")
        logger.info("Pressione 'q' para sair")
        
        settings = get_settings()
        
        try:
            while True:
                # Lê frame da câmera
                frame = self.camera.read()
                
                if frame is None:
                    logger.warning("Frame vazio, continuando...")
                    continue
                
                # Frame skipping para melhorar performance
                self.skip_counter += 1
                if self.skip_counter < settings.frame_skip:
                    # Mostra frame sem processar
                    cv2.imshow("BioFace AI", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    continue
                
                self.skip_counter = 0
                self.frame_count += 1
                
                # Processa frame
                frame_annotated, results = self.process_frame(frame)
                
                # Loga resultados (apenas a cada 30 frames para não poluir)
                if self.frame_count % 30 == 0:
                    for result in results:
                        logger.info(
                            f"Frame {self.frame_count}: "
                            f"{result['emotion_pt']} "
                            f"({result['confidence']:.0%})"
                        )
                
                # Atualiza FPS
                self.update_fps()
                
                # Exibe frame
                cv2.imshow("BioFace AI", frame_annotated)
                
                # Verifica tecla 'q' para sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Saindo...")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Libera recursos e finaliza o pipeline."""
        logger.info("Limpando recursos...")
        
        if hasattr(self, 'camera'):
            self.camera.release()
        
        if hasattr(self, 'face_detector'):
            self.face_detector.release()
        
        cv2.destroyAllWindows()
        
        logger.info("Recursos liberados. Encerrando...")


def main():
    """
    Função principal do programa.
    
    Parse de argumentos de linha de comando e inicialização do pipeline.
    """
    parser = argparse.ArgumentParser(
        description="BioFace AI - Real-Time Behavioral Intelligence System"
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=None,
        help='Índice da câmera (padrão: usa configuração)'
    )
    
    parser.add_argument(
        '--skip-frames',
        type=int,
        default=None,
        help='Processar 1 frame a cada N frames (padrão: usa configuração)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help='Nível de logging'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['dev', 'prod'],
        default='dev',
        help='Modo de execução (dev ou prod)'
    )
    
    args = parser.parse_args()
    
    # Configura logging se especificado
    if args.log_level:
        setup_logger(log_level=args.log_level)
    
    # Cria e executa pipeline
    try:
        pipeline = BioFacePipeline()
        pipeline.run()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

