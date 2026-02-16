"""
Script para adicionar múltiplos embeddings a um usuário existente.

Útil para melhorar a precisão de identificação cadastrando a mesma pessoa
várias vezes em diferentes condições.

Uso:
    python scripts/add_embeddings.py --user-id 3 --count 5
"""

import sys
import argparse
import cv2
import time
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


def add_embeddings(user_id: int, count: int = 5):
    """
    Adiciona múltiplos embeddings a um usuário.
    
    Args:
        user_id: ID do usuário
        count: Número de embeddings a adicionar
    """
    try:
        db = DatabaseRepository()
        
        # Verifica se usuário existe
        user = db.get_user(user_id)
        if not user:
            print(f"ERRO: Usuario {user_id} nao encontrado!")
            return
        
        print("=" * 60)
        print(f"Adicionando Embeddings - {user.name or 'Anonimo'}")
        print("=" * 60)
        print(f"\nUsuario: ID {user_id} - {user.name or '(Anonimo)'}")
        print(f"Embeddings atuais: {len(db.get_user_embeddings(user_id))}")
        print(f"Novos embeddings a adicionar: {count}")
        print("\nPosicione-se na frente da camera...")
        print("O sistema capturara automaticamente a cada 2 segundos")
        print("Pressione ESC para cancelar")
        
        # Inicializa componentes
        camera = Camera()
        face_detector = FaceDetector(max_num_faces=1)
        face_recognizer = FaceRecognizer()
        
        window_name = f"Adicionando Embeddings - {user.name or 'Anonimo'}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        embeddings_added = 0
        last_capture_time = 0
        
        try:
            while embeddings_added < count:
                frame = camera.read()
                if frame is None:
                    continue
                
                # Detecta faces
                faces = face_detector.detect(frame)
                
                # Desenha na tela
                frame_display = frame.copy()
                
                current_time = time.time()
                time_since_last = current_time - last_capture_time
                
                if faces:
                    face = faces[0]
                    bbox = face['bbox']
                    x, y, w, h = bbox
                    
                    # Desenha retângulo
                    color = (0, 255, 0) if time_since_last >= 2.0 else (0, 165, 255)
                    cv2.rectangle(frame_display, (x, y), (x + w, y + h), color, 2)
                    
                    # Texto
                    if time_since_last >= 2.0:
                        text = f"Face detectada - Capturando em breve... ({embeddings_added}/{count})"
                    else:
                        text = f"Aguarde... ({embeddings_added}/{count})"
                    
                    cv2.putText(
                        frame_display,
                        text,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2
                    )
                    
                    # Captura automaticamente a cada 2 segundos
                    if time_since_last >= 2.0:
                        # Gera embedding
                        embedding = face_recognizer.generate_embedding_from_bbox(frame, bbox)
                        
                        if embedding is not None:
                            # Salva embedding
                            db.save_embedding(
                                user_id=user_id,
                                embedding=embedding.tolist(),
                                confidence=face['confidence'],
                                face_size=bbox[2] * bbox[3]
                            )
                            
                            embeddings_added += 1
                            last_capture_time = current_time
                            
                            logger.info(f"Embedding {embeddings_added}/{count} adicionado!")
                            
                            # Feedback visual
                            cv2.putText(
                                frame_display,
                                f"CAPTURADO! ({embeddings_added}/{count})",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.0,
                                (0, 255, 0),
                                3
                            )
                        else:
                            logger.warning("Falha ao gerar embedding. Tentando novamente...")
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
                
                # Status
                status_text = f"Embeddings adicionados: {embeddings_added}/{count}"
                cv2.putText(
                    frame_display,
                    status_text,
                    (10, frame_display.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                cv2.imshow(window_name, frame_display)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    logger.info("Cancelado pelo usuario")
                    break
                
                # Pequeno delay para não sobrecarregar
                time.sleep(0.1)
            
            # Resultado final
            final_count = len(db.get_user_embeddings(user_id))
            
            print("\n" + "=" * 60)
            print("Concluido!")
            print("=" * 60)
            print(f"Embeddings adicionados: {embeddings_added}")
            print(f"Total de embeddings agora: {final_count}")
            print("=" * 60)
            
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuario")
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)
        finally:
            camera.release()
            face_detector.release()
            face_recognizer.release()
            cv2.destroyAllWindows()
            
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adiciona multiplos embeddings a um usuario")
    parser.add_argument(
        '--user-id',
        type=int,
        required=True,
        help='ID do usuario'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Numero de embeddings a adicionar (padrao: 5)'
    )
    
    args = parser.parse_args()
    add_embeddings(args.user_id, args.count)

