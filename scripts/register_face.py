"""
Script para cadastrar uma nova face no sistema.

Uso:
    python scripts/register_face.py --name "João Silva"
"""

import cv2
import argparse
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_settings
from src.vision.camera import Camera
from src.vision.face_detector import FaceDetector
from src.ai.face_recognizer import FaceRecognizer
from src.database.repository import DatabaseRepository

setup_logger()
logger = get_logger(__name__)


def register_face(name: str = None):
    """
    Cadastra uma nova face no sistema.
    
    Args:
        name: Nome da pessoa (opcional)
    """
    logger.info("=" * 60)
    logger.info("Cadastro de Nova Face")
    logger.info("=" * 60)
    
    # Inicializa componentes
    camera = Camera()
    face_detector = FaceDetector(max_num_faces=1)
    face_recognizer = FaceRecognizer()
    db = DatabaseRepository()
    
    logger.info("Posicione-se na frente da câmera...")
    logger.info("Pressione ESPAÇO para capturar, ESC para cancelar")
    
    window_name = "Cadastro de Face - Pressione ESPAÇO para capturar"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue
            
            # Detecta faces
            faces = face_detector.detect(frame)
            
            # Desenha na tela
            frame_display = frame.copy()
            
            if faces:
                face = faces[0]
                bbox = face['bbox']
                x, y, w, h = bbox
                
                # Desenha retângulo verde
                cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame_display,
                    "Face detectada - Pressione ESPACO",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
            else:
                cv2.putText(
                    frame_display,
                    "Nenhuma face detectada",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
            
            cv2.imshow(window_name, frame_display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):  # ESPAÇO
                if faces:
                    face = faces[0]
                    bbox = face['bbox']
                    
                    # Gera embedding
                    logger.info("Gerando embedding...")
                    embedding = face_recognizer.generate_embedding_from_bbox(frame, bbox)
                    
                    if embedding is None:
                        logger.error("Falha ao gerar embedding. Tente novamente.")
                        continue
                    
                    # Verifica se a face já está cadastrada
                    # Usa o mesmo threshold do sistema de reconhecimento para consistência
                    settings = get_settings()
                    existing_match = db.find_user_by_embedding(
                        embedding.tolist(),
                        threshold=settings.recognition_distance_threshold,
                        ambiguity_threshold=settings.recognition_ambiguity_threshold
                    )
                    
                    user = None
                    
                    if existing_match:
                        # Face já existe - IMPEDE cadastro duplicado
                        existing_user = db.get_user(existing_match['user_id'])
                        existing_name = existing_user.name or f"Usuario {existing_user.id}"
                        
                        logger.warning("=" * 60)
                        logger.warning(f"ERRO: Usuario ja cadastrado!")
                        logger.warning(f"  Usuario existente: {existing_name} (ID: {existing_user.id})")
                        logger.warning(f"  Distancia: {existing_match['distance']:.4f}")
                        logger.warning("=" * 60)
                        
                        # Mostra mensagem na tela
                        cv2.putText(
                            frame_display,
                            "USUARIO JA CADASTRADO!",
                            (10, frame_display.shape[0] - 80),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            2
                        )
                        cv2.putText(
                            frame_display,
                            f"Usuario: {existing_name} (ID: {existing_user.id})",
                            (10, frame_display.shape[0] - 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2
                        )
                        cv2.putText(
                            frame_display,
                            "Pressione qualquer tecla para continuar...",
                            (10, frame_display.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 255, 255),
                            1
                        )
                        cv2.imshow(window_name, frame_display)
                        cv2.waitKey(3000)  # Mostra por 3 segundos
                        
                        logger.info("Cadastro bloqueado: usuario ja existe no sistema")
                        continue  # Volta ao loop sem cadastrar
                    else:
                        # Face não existe - cria novo usuário
                        logger.info("Face nova detectada. Criando novo usuario...")
                        user = db.create_user(name=name)
                    
                    # Salva embedding
                    db.save_embedding(
                        user_id=user.id,
                        embedding=embedding.tolist(),
                        confidence=face['confidence'],
                        face_size=bbox[2] * bbox[3]
                    )
                    
                    logger.info("=" * 60)
                    logger.info("Face cadastrada com sucesso!")
                    logger.info(f"  Usuario ID: {user.id}")
                    logger.info(f"  Nome: {user.name or '(Anonimo)'}")
                    logger.info(f"  Confianca: {face['confidence']:.0%}")
                    logger.info("=" * 60)
                    
                    # Mostra sucesso na tela
                    cv2.putText(
                        frame_display,
                        "CADASTRADO COM SUCESSO!",
                        (10, frame_display.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )
                    cv2.putText(
                        frame_display,
                        f"Usuario: {user.name or 'Anonimo'} (ID: {user.id})",
                        (10, frame_display.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
                    cv2.imshow(window_name, frame_display)
                    cv2.waitKey(2000)  # Mostra por 2 segundos
                    
                    break
                else:
                    logger.warning("Nenhuma face detectada. Tente novamente.")
            
            elif key == 27:  # ESC
                logger.info("Cancelado pelo usuário")
                break
    
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
    finally:
        camera.release()
        face_detector.release()
        face_recognizer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cadastra uma nova face no sistema")
    parser.add_argument(
        '--name',
        type=str,
        default=None,
        help='Nome da pessoa (opcional)'
    )
    
    args = parser.parse_args()
    register_face(name=args.name)

