"""
Script para testar e diagnosticar problemas de reconhecimento.

Mostra as distâncias entre embeddings para entender por que não está identificando.

Uso:
    python scripts/test_recognition.py --user-id 3
"""

import sys
import cv2
import argparse
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


def test_recognition(user_id: int):
    """
    Testa reconhecimento de um usuário específico.
    
    Args:
        user_id: ID do usuário a testar
    """
    try:
        db = DatabaseRepository()
        settings = get_settings()
        
        # Verifica se usuário existe
        user = db.get_user(user_id)
        if not user:
            print(f"ERRO: Usuario {user_id} nao encontrado!")
            return
        
        print("=" * 60)
        print(f"Teste de Reconhecimento - {user.name or 'Anonimo'}")
        print("=" * 60)
        
        # Busca embeddings do usuário
        user_embeddings = db.get_user_embeddings(user_id)
        print(f"\nEmbeddings do usuario: {len(user_embeddings)}")
        
        if len(user_embeddings) == 0:
            print("ERRO: Usuario nao tem embeddings!")
            return
        
        # Inicializa componentes
        camera = Camera()
        face_detector = FaceDetector(max_num_faces=1)
        face_recognizer = FaceRecognizer()
        
        print("\nPosicione-se na frente da camera...")
        print("Pressione ESPACO para capturar e testar, ESC para sair")
        
        window_name = f"Teste - {user.name or 'Anonimo'}"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        try:
            while True:
                frame = camera.read()
                if frame is None:
                    continue
                
                # Detecta faces
                faces = face_detector.detect(frame)
                
                frame_display = frame.copy()
                
                if faces:
                    face = faces[0]
                    bbox = face['bbox']
                    x, y, w, h = bbox
                    
                    cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        frame_display,
                        "Pressione ESPACO para testar",
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
                        embedding = face_recognizer.generate_embedding_from_bbox(frame, bbox)
                        
                        if embedding is None:
                            print("ERRO: Falha ao gerar embedding")
                            continue
                        
                        print("\n" + "=" * 60)
                        print("Testando Reconhecimento...")
                        print("=" * 60)
                        
                        # Testa com diferentes thresholds
                        thresholds = [0.3, 0.35, 0.4, 0.45, 0.5]
                        
                        for threshold in thresholds:
                            match = db.find_user_by_embedding(
                                embedding.tolist(),
                                threshold=threshold,
                                ambiguity_threshold=0.1
                            )
                            
                            if match:
                                distance = match['distance']
                                confidence = 1.0 - distance
                                matched_user = db.get_user(match['user_id'])
                                
                                print(f"\nThreshold {threshold}:")
                                print(f"  Match: {matched_user.name if matched_user else 'N/A'}")
                                print(f"  Distancia: {distance:.4f}")
                                print(f"  Confianca: {confidence:.2%}")
                                print(f"  User ID: {match['user_id']}")
                                
                                # Verifica se é o usuário esperado
                                if match['user_id'] == user_id:
                                    print(f"  ✓ CORRETO!")
                                else:
                                    print(f"  ✗ INCORRETO (esperado: {user_id})")
                            else:
                                print(f"\nThreshold {threshold}: Nenhum match")
                        
                        # Testa sem validação de ambiguidade
                        print("\n" + "-" * 60)
                        print("Teste SEM validacao de ambiguidade:")
                        print("-" * 60)
                        
                        # Busca todos os matches sem threshold
                        import numpy as np
                        from src.database.models import FaceEmbedding
                        from sqlalchemy.orm import Session
                        
                        session = db.get_session()
                        try:
                            all_embeddings = session.query(FaceEmbedding).all()
                            query_embedding = np.array(embedding, dtype=np.float32)
                            
                            distances_by_user = {}
                            
                            for fe in all_embeddings:
                                db_emb = np.array(fe.get_embedding_array(), dtype=np.float32)
                                dist = np.linalg.norm(query_embedding - db_emb)
                                
                                if fe.user_id not in distances_by_user:
                                    distances_by_user[fe.user_id] = []
                                distances_by_user[fe.user_id].append(dist)
                            
                            print("\nDistâncias por usuário (top 5 menores):")
                            for uid, dists in distances_by_user.items():
                                min_dist = min(dists)
                                avg_dist = np.mean(dists)
                                u = db.get_user(uid)
                                print(f"  {u.name if u else 'N/A'} (ID {uid}): min={min_dist:.4f}, avg={avg_dist:.4f}")
                            
                            # Ordena por menor distância
                            sorted_users = sorted(
                                distances_by_user.items(),
                                key=lambda x: min(x[1])
                            )
                            
                            if len(sorted_users) >= 2:
                                best_uid, best_dists = sorted_users[0]
                                second_uid, second_dists = sorted_users[1]
                                
                                best_min = min(best_dists)
                                second_min = min(second_dists)
                                diff = second_min - best_min
                                
                                print(f"\nMelhor match: {db.get_user(best_uid).name} (dist={best_min:.4f})")
                                print(f"Segundo melhor: {db.get_user(second_uid).name} (dist={second_min:.4f})")
                                print(f"Diferença: {diff:.4f}")
                                
                                if diff < 0.1:
                                    print(f"⚠ AMBIGUIDADE detectada (diff < 0.1)")
                                else:
                                    print(f"✓ Sem ambiguidade")
                        finally:
                            session.close()
                        
                        print("\n" + "=" * 60)
                
                elif key == 27:  # ESC
                    break
        
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuario")
        finally:
            camera.release()
            face_detector.release()
            face_recognizer.release()
            cv2.destroyAllWindows()
            
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testa reconhecimento de um usuario")
    parser.add_argument(
        '--user-id',
        type=int,
        required=True,
        help='ID do usuario a testar'
    )
    
    args = parser.parse_args()
    test_recognition(args.user_id)

