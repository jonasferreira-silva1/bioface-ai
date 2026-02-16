"""
BioFace AI - Versão Leve (Sem TensorFlow)

Esta versão funciona apenas com detecção de faces, sem classificação de emoções.
Ideal para sistemas com pouca memória.

Uso: python -m src.main_light
"""

import cv2
import time
import argparse
from pathlib import Path
import sys

# Adiciona diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_settings
from src.vision.camera import Camera
from src.vision.face_detector import FaceDetector
from src.vision.face_processor import FaceProcessor

# Configura logging
setup_logger()
logger = get_logger(__name__)


class BioFacePipelineLight:
    """
    Pipeline leve do BioFace AI (sem classificação de emoções).
    
    Esta versão apenas detecta faces, sem processar emoções.
    Muito mais leve em memória (~200-500MB vs 2-4GB).
    """
    
    def __init__(self):
        """Inicializa o pipeline leve."""
        logger.info("=" * 60)
        logger.info("Inicializando BioFace AI - Versão Leve")
        logger.info("=" * 60)
        
        settings = get_settings()
        
        # Inicializa componentes (sem EmotionClassifier)
        logger.info("Inicializando componentes...")
        
        self.camera = Camera()
        logger.info("✓ Câmera inicializada")
        
        self.face_detector = FaceDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_faces=1
        )
        logger.info("✓ Face Detector inicializado")
        
        self.face_processor = FaceProcessor()
        logger.info("✓ Face Processor inicializado")
        
        # Contadores
        self.frame_count = 0
        self.skip_counter = 0
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        
        logger.info("=" * 60)
        logger.info("Pipeline leve inicializado!")
        logger.info("Nota: Esta versão não classifica emoções (sem TensorFlow)")
        logger.info("=" * 60)
    
    def process_frame(self, frame):
        """
        Processa um frame (apenas detecção, sem emoção).
        
        Args:
            frame: Frame BGR da câmera
            
        Returns:
            tuple: (frame_annotated, results)
        """
        results = []
        
        # Detecta faces
        faces = self.face_detector.detect(frame)
        
        # Processa cada face detectada (sem classificação de emoção)
        for face in faces:
            bbox = face['bbox']
            landmarks = face['landmarks_2d']
            
            result = {
                'bbox': bbox,
                'landmarks': landmarks,
                'confidence': face['confidence']
            }
            results.append(result)
        
        # Desenha anotações
        frame_annotated = self._draw_annotations(frame, results)
        
        return frame_annotated, results
    
    def _draw_annotations(self, frame, results):
        """Desenha anotações no frame."""
        frame_copy = frame.copy()
        
        for result in results:
            bbox = result['bbox']
            confidence = result['confidence']
            
            x, y, w, h = bbox
            
            # Cor verde para faces detectadas
            color = (0, 255, 0)
            
            # Desenha bounding box
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
            
            # Texto mais visível
            text = f"FACE DETECTADA: {confidence:.0%}"
            
            # Calcula tamanho do texto
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            # Fundo para texto (maior para melhor visibilidade)
            cv2.rectangle(
                frame_copy,
                (x - 5, y - text_height - 15),
                (x + text_width + 5, y + 5),
                (0, 0, 0),
                -1
            )
            
            # Borda verde
            cv2.rectangle(
                frame_copy,
                (x - 5, y - text_height - 15),
                (x + text_width + 5, y + 5),
                color,
                2
            )
            
            # Texto
            cv2.putText(
                frame_copy,
                text,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Desenha círculos nos cantos do retângulo para destacar
            corner_radius = 5
            cv2.circle(frame_copy, (x, y), corner_radius, color, -1)
            cv2.circle(frame_copy, (x + w, y), corner_radius, color, -1)
            cv2.circle(frame_copy, (x, y + h), corner_radius, color, -1)
            cv2.circle(frame_copy, (x + w, y + h), corner_radius, color, -1)
        
        # FPS
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
        
        # Contador
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
        
        # Aviso de versão leve
        warning_text = "LIGHT MODE - No Emotion Detection"
        cv2.putText(
            frame_copy,
            warning_text,
            (10, frame_copy.shape[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 165, 255),
            1
        )
        
        # Instruções de como fechar (sempre visível)
        instruction_text = "Pressione 'Q' para fechar"
        cv2.putText(
            frame_copy,
            instruction_text,
            (10, frame_copy.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        # Fundo para instrução (para melhor visibilidade)
        (text_width, text_height), baseline = cv2.getTextSize(
            instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            frame_copy,
            (5, frame_copy.shape[0] - text_height - 25),
            (15 + text_width, frame_copy.shape[0] - 5),
            (0, 0, 0),
            -1
        )
        cv2.putText(
            frame_copy,
            instruction_text,
            (10, frame_copy.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        return frame_copy
    
    def update_fps(self):
        """Atualiza cálculo de FPS."""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self):
        """Executa o pipeline."""
        logger.info("Iniciando loop principal...")
        logger.info("Pressione 'q' ou 'Q' na janela para sair")
        logger.info("OU pressione Ctrl+C no terminal para sair")
        
        settings = get_settings()
        
        # Cria janela e garante que está visível
        window_name = "BioFace AI - Light"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        
        try:
            while True:
                frame = self.camera.read()
                
                if frame is None:
                    continue
                
                # Frame skipping
                self.skip_counter += 1
                if self.skip_counter < settings.frame_skip:
                    # Mostra frame sem processar, mas com instruções
                    frame_with_instructions = frame.copy()
                    cv2.putText(
                        frame_with_instructions,
                        "Pressione 'Q' para fechar",
                        (10, frame_with_instructions.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                    cv2.imshow(window_name, frame_with_instructions)
                    if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
                        break
                    continue
                
                self.skip_counter = 0
                self.frame_count += 1
                
                # Processa frame
                frame_annotated, results = self.process_frame(frame)
                
                # Log (a cada 30 frames)
                if self.frame_count % 30 == 0:
                    logger.info(f"Frame {self.frame_count}: {len(results)} face(s) detectada(s)")
                    if len(results) > 0:
                        logger.info(f"  -> Face detectada com confiança: {results[0]['confidence']:.0%}")
                
                # Atualiza FPS
                self.update_fps()
                
                # Exibe frame com anotações
                cv2.imshow(window_name, frame_annotated)
                
                # Verifica tecla 'q' ou 'Q' para sair (waitKey também atualiza a janela)
                # IMPORTANTE: Clique na janela de vídeo antes de pressionar 'Q'
                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), ord('Q'), 27]:  # 'q', 'Q' ou ESC
                    logger.info("Saindo...")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Libera recursos."""
        logger.info("Limpando recursos...")
        
        if hasattr(self, 'camera'):
            self.camera.release()
        
        if hasattr(self, 'face_detector'):
            self.face_detector.release()
        
        cv2.destroyAllWindows()
        logger.info("Recursos liberados.")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="BioFace AI - Versão Leve (Sem TensorFlow)"
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=None,
        help='Índice da câmera'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help='Nível de logging'
    )
    
    args = parser.parse_args()
    
    if args.log_level:
        setup_logger(log_level=args.log_level)
    
    try:
        pipeline = BioFacePipelineLight()
        pipeline.run()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


