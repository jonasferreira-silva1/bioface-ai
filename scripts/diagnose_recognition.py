"""
Script para diagnosticar problemas de reconhecimento facial.

Mostra quais usuários estão sendo confundidos e suas distâncias.

Uso:
    python scripts/diagnose_recognition.py
    python scripts/diagnose_recognition.py --user-id 2
"""

import sys
import argparse
from pathlib import Path
import numpy as np

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


def diagnose_recognition(user_id: int = None):
    """
    Diagnostica problemas de reconhecimento facial.
    
    Captura uma face e mostra as distâncias para todos os usuários cadastrados.
    
    Args:
        user_id: ID do usuário esperado (opcional)
    """
    try:
        db = DatabaseRepository()
        settings = get_settings()
        
        # Lista todos os usuários
        all_users = db.get_all_users()
        if not all_users:
            print("ERRO: Nenhum usuario cadastrado!")
            return
        
        print("=" * 60)
        print("Diagnostico de Reconhecimento Facial")
        print("=" * 60)
        print(f"\nUsuarios cadastrados: {len(all_users)}")
        for user in all_users:
            embeddings = db.get_user_embeddings(user.id)
            print(f"  - {user.name or f'Usuario {user.id}'} (ID: {user.id}): {len(embeddings)} embeddings")
        
        if user_id:
            expected_user = db.get_user(user_id)
            if expected_user:
                print(f"\nUsuario esperado: {expected_user.name or f'Usuario {user_id}'} (ID: {user_id})")
            else:
                print(f"\nAVISO: Usuario {user_id} nao encontrado!")
        
        print("\n" + "=" * 60)
        print("Posicione-se na frente da camera...")
        print("Pressione ESPACO para capturar e diagnosticar, ESC para sair")
        print("=" * 60)
        
        # Inicializa componentes
        camera = Camera()
        face_detector = FaceDetector(max_num_faces=1)
        face_recognizer = FaceRecognizer()
        
        window_name = "Diagnostico - Pressione ESPACO para capturar"
        import cv2
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
                        print("\nGerando embedding...")
                        embedding = face_recognizer.generate_embedding_from_bbox(frame, bbox)
                        
                        if embedding is None:
                            print("ERRO: Falha ao gerar embedding. Tente novamente.")
                            continue
                        
                        # Busca todos os embeddings no banco
                        print("\nCalculando distancias para todos os usuarios...")
                        from src.database.models import FaceEmbedding
                        session = db.get_session()
                        try:
                            all_embeddings = session.query(FaceEmbedding).all()
                        finally:
                            session.close()
                        
                        if not all_embeddings:
                            print("ERRO: Nenhum embedding no banco de dados!")
                            continue
                        
                        # Calcula distâncias para cada usuário
                        query_embedding = np.array(embedding, dtype=np.float32)
                        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
                        
                        user_distances = {}  # {user_id: [distances]}
                        
                        for fe in all_embeddings:
                            db_embedding = np.array(fe.get_embedding_array(), dtype=np.float32)
                            db_norm = db_embedding / (np.linalg.norm(db_embedding) + 1e-8)
                            
                            # Distância cosseno
                            cosine_similarity = np.dot(query_norm, db_norm)
                            cosine_distance = 1.0 - cosine_similarity
                            
                            if fe.user_id not in user_distances:
                                user_distances[fe.user_id] = []
                            user_distances[fe.user_id].append(cosine_distance)
                        
                        # Calcula estatísticas por usuário
                        user_stats = []
                        for uid, distances in user_distances.items():
                            user = db.get_user(uid)
                            user_stats.append({
                                'user_id': uid,
                                'name': user.name if user else f'Usuario {uid}',
                                'min_distance': min(distances),
                                'avg_distance': np.mean(distances),
                                'max_distance': max(distances),
                                'num_embeddings': len(distances)
                            })
                        
                        # Ordena por distância mínima
                        user_stats.sort(key=lambda x: x['min_distance'])
                        
                        # Mostra resultados
                        print("\n" + "=" * 80)
                        print("RESULTADOS DO DIAGNOSTICO")
                        print("=" * 80)
                        print(f"\n{'Usuario':<20} {'ID':<5} {'Min Dist':<10} {'Avg Dist':<10} {'Max Dist':<10} {'Embeddings':<10}")
                        print("-" * 80)
                        
                        for stat in user_stats:
                            is_expected = user_id and stat['user_id'] == user_id
                            marker = " <-- ESPERADO" if is_expected else ""
                            
                            print(f"{stat['name']:<20} {stat['user_id']:<5} "
                                  f"{stat['min_distance']:<10.4f} {stat['avg_distance']:<10.4f} "
                                  f"{stat['max_distance']:<10.4f} {stat['num_embeddings']:<10}{marker}")
                        
                        # Análise
                        print("\n" + "=" * 80)
                        print("ANALISE")
                        print("=" * 80)
                        
                        best = user_stats[0]
                        print(f"\nMelhor match: {best['name']} (ID: {best['user_id']})")
                        print(f"  Distancia minima: {best['min_distance']:.4f}")
                        print(f"  Distancia media: {best['avg_distance']:.4f}")
                        print(f"  Numero de embeddings: {best['num_embeddings']}")
                        
                        if len(user_stats) > 1:
                            second = user_stats[1]
                            diff = second['min_distance'] - best['min_distance']
                            relative_diff = (diff / (best['min_distance'] + 1e-8)) * 100
                            
                            print(f"\nSegundo melhor: {second['name']} (ID: {second['user_id']})")
                            print(f"  Distancia minima: {second['min_distance']:.4f}")
                            print(f"  Diferenca: {diff:.4f} ({relative_diff:.1f}%)")
                            
                            # Verifica se há ambiguidade
                            if diff < settings.recognition_ambiguity_threshold:
                                print(f"\n⚠ AMBIGUIDADE DETECTADA!")
                                print(f"  Diferenca muito pequena ({diff:.4f} < {settings.recognition_ambiguity_threshold})")
                                print(f"  O sistema pode rejeitar a identificacao por ambiguidade.")
                            
                            if best['min_distance'] > settings.recognition_distance_threshold:
                                print(f"\n⚠ DISTANCIA ACIMA DO THRESHOLD!")
                                print(f"  Distancia minima ({best['min_distance']:.4f}) > threshold ({settings.recognition_distance_threshold})")
                                print(f"  O sistema nao identificara este usuario.")
                        
                        if user_id:
                            expected_stat = next((s for s in user_stats if s['user_id'] == user_id), None)
                            if expected_stat:
                                if expected_stat['user_id'] != best['user_id']:
                                    print(f"\n*** PROBLEMA DETECTADO! ***")
                                    print(f"  Usuario esperado ({expected_stat['name']}) nao e o melhor match.")
                                    print(f"  Melhor match: {best['name']} (distancia: {best['min_distance']:.4f})")
                                    print(f"  Esperado: {expected_stat['name']} (distancia: {expected_stat['min_distance']:.4f})")
                                    print(f"\n  SOLUCAO: Recadastre o usuario '{expected_stat['name']}' novamente.")
                                else:
                                    print(f"\n[OK] Usuario esperado e o melhor match!")
                        
                        print("\n" + "=" * 80)
                        print("\nPressione qualquer tecla para continuar...")
                        cv2.waitKey(0)
                        break
                    else:
                        print("Nenhuma face detectada. Tente novamente.")
                
                elif key == 27:  # ESC
                    print("Cancelado pelo usuario")
                    break
        
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuario")
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)
            print(f"\nERRO: {e}")
        finally:
            camera.release()
            face_detector.release()
            face_recognizer.release()
            cv2.destroyAllWindows()
    
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnostica problemas de reconhecimento facial")
    parser.add_argument(
        '--user-id',
        type=int,
        default=None,
        help='ID do usuario esperado (opcional)'
    )
    
    args = parser.parse_args()
    diagnose_recognition(args.user_id)

