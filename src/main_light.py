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
from src.ai.face_recognizer import FaceRecognizer
from src.database.repository import DatabaseRepository

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
        
        # Salva settings como atributo da classe
        self.settings = get_settings()
        
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
        
        # Reconhecimento facial (Fase 2)
        self.face_recognizer = FaceRecognizer(embedding_size=128)
        logger.info("✓ Face Recognizer inicializado")
        
        # Banco de dados (Fase 2)
        self.db = DatabaseRepository()
        logger.info("✓ Banco de dados inicializado")
        
        # Contadores
        self.frame_count = 0
        self.skip_counter = 0
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        
        # Sistema de estabilização temporal (evita oscilação)
        self.identification_history = []  # Histórico das últimas identificações
        self.history_size = 8  # Quantos frames manter no histórico (reduzido)
        self.consensus_threshold = 5  # Quantos frames precisam concordar para mudar (reduzido)
        self.min_confidence_to_show = 0.5  # Confiança mínima para mostrar nome (50% - mais permissivo)
        self.current_stable_id = None  # ID estável atual
        self.stable_name = None  # Nome estável atual
        self.stable_confidence = 0.0  # Confiança estável atual
        
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
        
        # Processa cada face detectada (com identificação)
        for face in faces:
            bbox = face['bbox']
            landmarks = face['landmarks_2d']
            confidence = face['confidence']
            
            # Gera embedding para identificação
            embedding = self.face_recognizer.generate_embedding_from_bbox(frame, bbox)
            
            # Tenta identificar a pessoa
            user_id = None
            user_name = None
            identification_confidence = 0.0
            
            if embedding is not None:
                # Busca no banco de dados
                # Usa threshold mais restritivo e validação de ambiguidade
                match = self.db.find_user_by_embedding(
                    embedding.tolist(),
                    threshold=self.settings.recognition_distance_threshold,
                    ambiguity_threshold=self.settings.recognition_ambiguity_threshold
                )
                
                # Log ocasional para debug
                if len(self.identification_history) % 60 == 0:
                    if match:
                        logger.debug(
                            f"Match encontrado: user_id={match['user_id']}, "
                            f"dist={match['distance']:.4f}"
                        )
                    else:
                        logger.debug("Nenhum match encontrado no banco")
                
                if match:
                    # Verifica se a distância está dentro do threshold
                    distance = match['distance']
                    identification_confidence = 1.0 - distance
                    
                    # Identifica se a distância estiver dentro do threshold
                    if distance <= self.settings.recognition_distance_threshold:
                        user_id = match['user_id']
                        
                        # Busca nome do usuário
                        user = self.db.get_user(user_id)
                        if user:
                            user_name = user.name or f"Usuario {user_id}"
                        
                        # Log da identificação
                        logger.info(
                            f"Face identificada: {user_name} (ID: {user_id}, "
                            f"dist={distance:.4f}, conf={identification_confidence:.2%})"
                        )
                    else:
                        # Distância muito alta - não identifica
                        user_id = None
                        user_name = None
                        identification_confidence = 0.0
                        logger.debug(f"Distancia muito alta ({distance:.4f} > {self.settings.recognition_distance_threshold})")
                else:
                    # Face desconhecida (find_user_by_embedding retornou None)
                    user_id = None
                    user_name = None
                    identification_confidence = 0.0
                    # Log apenas ocasionalmente para não poluir
                    if len(self.identification_history) % 30 == 0:
                        logger.debug(f"Face desconhecida (sem match no banco)")
                    if not self.settings.anonymous_mode:
                        # Cria usuário anônimo automaticamente (pode ser melhorado depois)
                        pass
                
                # Adiciona ao histórico para estabilização temporal
                self.identification_history.append({
                    'user_id': user_id,
                    'user_name': user_name,
                    'confidence': identification_confidence,
                    'distance': match['distance'] if match else float('inf')
                })
            else:
                # Sem embedding - adiciona entrada vazia ao histórico
                self.identification_history.append({
                    'user_id': None,
                    'user_name': None,
                    'confidence': 0.0,
                    'distance': float('inf')
                })
            
            # Mantém apenas os últimos N frames
            if len(self.identification_history) > self.history_size:
                self.identification_history.pop(0)
            
            # Aplica estabilização temporal (sempre, mesmo sem embedding)
            stable_user_id, stable_user_name, stable_conf = self._stabilize_identification()
            
            # Usa identificação estável no resultado
            user_id = stable_user_id
            user_name = stable_user_name
            identification_confidence = stable_conf
            
            result = {
                'bbox': bbox,
                'landmarks': landmarks,
                'confidence': confidence,
                'embedding': embedding.tolist() if embedding is not None else None,
                'user_id': user_id,
                'user_name': user_name,
                'identification_confidence': identification_confidence
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
            
            # Texto com identificação (usa nome estável)
            stable_name = result.get('user_name')
            stable_conf = result.get('identification_confidence', 0.0)
            
            if stable_name and stable_conf >= self.min_confidence_to_show:
                text = f"{stable_name}: {stable_conf:.0%}"
                color = (0, 255, 0)  # Verde para identificado
            else:
                text = f"DESCONHECIDO: {confidence:.0%}"
                color = (0, 165, 255)  # Laranja para desconhecido
            
            # Desenha bounding box
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
            
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
    
    def _stabilize_identification(self):
        """
        Estabiliza identificação usando histórico temporal.
        
        Evita oscilação entre nomes diferentes usando votação por maioria
        e requerendo consenso antes de mudar a identificação.
        
        Returns:
            tuple: (user_id, user_name, confidence) estáveis
        """
        if not self.identification_history:
            return None, None, 0.0
        
        # Conta votos por usuário no histórico recente
        votes = {}  # {user_id: {'count': int, 'total_confidence': float, 'min_distance': float}}
        
        for entry in self.identification_history:
            uid = entry['user_id']
            conf = entry['confidence']
            dist = entry.get('distance', float('inf'))
            
            if uid is not None and conf >= self.min_confidence_to_show:
                if uid not in votes:
                    votes[uid] = {
                        'count': 0,
                        'total_confidence': 0.0,
                        'min_distance': float('inf'),
                        'name': entry['user_name']
                    }
                
                votes[uid]['count'] += 1
                votes[uid]['total_confidence'] += conf
                votes[uid]['min_distance'] = min(votes[uid]['min_distance'], dist)
        
        if not votes:
            # Nenhuma identificação confiável no histórico
            self.current_stable_id = None
            self.stable_name = None
            self.stable_confidence = 0.0
            return None, None, 0.0
        
        # Encontra o usuário com mais votos
        best_user_id = max(votes.keys(), key=lambda uid: (
            votes[uid]['count'],  # Prioriza quem tem mais votos
            -votes[uid]['min_distance']  # Em caso de empate, menor distância
        ))
        
        best_vote = votes[best_user_id]
        consensus_count = best_vote['count']
        avg_confidence = best_vote['total_confidence'] / consensus_count
        
        # Só muda a identificação se houver consenso suficiente
        if consensus_count >= self.consensus_threshold:
            # Há consenso - pode mudar ou manter
            if best_user_id != self.current_stable_id:
                # Mudança de identificação - só aceita se houver consenso forte
                if consensus_count >= self.consensus_threshold:
                    self.current_stable_id = best_user_id
                    self.stable_name = best_vote['name']
                    self.stable_confidence = avg_confidence
                    logger.info(
                        f"Mudanca de identificacao: {self.stable_name} "
                        f"(conf={self.stable_confidence:.2f}, votos={consensus_count})"
                    )
        elif self.current_stable_id is not None:
            # Não há consenso suficiente, mas já temos uma identificação estável
            # Mantém a identificação atual se ainda aparecer no histórico
            if self.current_stable_id in votes:
                # Ainda aparece no histórico - mantém e atualiza confiança
                self.stable_confidence = votes[self.current_stable_id]['total_confidence'] / votes[self.current_stable_id]['count']
            else:
                # Não aparece mais no histórico - conta quantos frames sem aparecer
                # Só limpa se não aparecer por muitos frames consecutivos
                frames_without_stable = sum(
                    1 for entry in self.identification_history
                    if entry['user_id'] != self.current_stable_id
                )
                # Só limpa se não aparecer por mais de 50% do histórico
                if frames_without_stable >= len(self.identification_history) * 0.5:
                    logger.debug(
                        f"Limpando identificacao estavel: {self.stable_name} "
                        f"(nao aparece ha {frames_without_stable} frames)"
                    )
                    self.current_stable_id = None
                    self.stable_name = None
                    self.stable_confidence = 0.0
                # Caso contrário, mantém a identificação estável mesmo sem aparecer recentemente
        else:
            # Não há identificação estável ainda - espera consenso
            if consensus_count >= self.consensus_threshold:
                self.current_stable_id = best_user_id
                self.stable_name = best_vote['name']
                self.stable_confidence = avg_confidence
                logger.info(
                    f"Nova identificacao: {self.stable_name} "
                    f"(conf={self.stable_confidence:.2f}, votos={consensus_count})"
                )
        
        # Retorna identificação estável
        return self.current_stable_id, self.stable_name, self.stable_confidence
    
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
                if self.skip_counter < self.settings.frame_skip:
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
                
                # Log e salva no banco (a cada 30 frames)
                if self.frame_count % 30 == 0:
                    logger.info(f"Frame {self.frame_count}: {len(results)} face(s) detectada(s)")
                    if len(results) > 0:
                        result = results[0]
                        logger.info(f"  -> Face detectada com confiança: {result['confidence']:.0%}")
                        
                        # Atualiza identificação se encontrou match (salva novo embedding)
                        if result.get('user_id') and result.get('embedding'):
                            # Salva novo embedding para melhorar identificação futura
                            try:
                                self.db.save_embedding(
                                    user_id=result['user_id'],
                                    embedding=result['embedding'],
                                    confidence=result['confidence'],
                                    face_size=result['bbox'][2] * result['bbox'][3]
                                )
                                logger.debug(f"  -> Embedding atualizado para usuario {result['user_id']}")
                            except Exception as e:
                                logger.debug(f"Erro ao atualizar embedding: {e}")
                        
                        # NÃO cria usuários anônimos automaticamente (desabilitado)
                        # Isso estava criando muitos usuários e interferindo na identificação
                
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
        
        if hasattr(self, 'face_recognizer'):
            self.face_recognizer.release()
        
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


