"""
Script para debugar problemas de reconhecimento em tempo real.

Mostra informações detalhadas sobre o processo de identificação.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_settings
from src.database.repository import DatabaseRepository
from src.ai.face_recognizer import FaceRecognizer
from src.vision.face_detector import FaceDetector

setup_logger()
logger = get_logger(__name__)
settings = get_settings()


def debug_recognition():
    """Debuga o processo de reconhecimento."""
    try:
        db = DatabaseRepository()
        face_detector = FaceDetector()
        face_recognizer = FaceRecognizer()
        
        # Lista todos os usuários
        from src.database.models import User, FaceEmbedding
        session = db.get_session()
        all_users = session.query(User).all()
        all_embeddings = session.query(FaceEmbedding).all()
        
        print("=" * 80)
        print("DEBUG DE RECONHECIMENTO")
        print("=" * 80)
        print(f"\nTotal de usuarios: {len(all_users)}")
        print(f"Total de embeddings: {len(all_embeddings)}")
        print("\nUsuarios no banco:")
        for user in all_users:
            user_embeddings = [e for e in all_embeddings if e.user_id == user.id]
            print(f"  ID {user.id}: {user.name or '(Anonimo)'} - {len(user_embeddings)} embeddings")
        
        print("\n" + "=" * 80)
        print("Aguardando face na camera...")
        print("Pressione ESPACO para capturar e analisar")
        print("Pressione ESC para sair")
        print("=" * 80)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERRO: Nao foi possivel abrir a camera")
            return
        
        window_name = "Debug Reconhecimento"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        frame_count = 0
        captured_frame = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detecta faces
            detections = face_detector.detect(frame)
            
            # Desenha detecções
            frame_display = frame.copy()
            if detections:
                for det in detections:
                    x, y, w, h = det['bbox']
                    cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        frame_display,
                        f"Face detectada",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
            
            # Mostra instruções
            cv2.putText(
                frame_display,
                "Pressione ESPACO para capturar",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            cv2.imshow(window_name, frame_display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                if detections:
                    captured_frame = frame.copy()
                    break
            elif key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured_frame is None:
            print("Nenhuma face capturada")
            return
        
        # Processa frame capturado
        print("\n" + "=" * 80)
        print("ANALISANDO FRAME CAPTURADO...")
        print("=" * 80)
        
        detections = face_detector.detect(captured_frame)
        if not detections:
            print("ERRO: Nenhuma face detectada no frame capturado")
            return
        
        detection = detections[0]
        x, y, w, h = detection['bbox']
        face_image = captured_frame[y:y+h, x:x+w]
        
        # Gera embedding
        print("\nGerando embedding...")
        embedding = face_recognizer.generate_embedding(face_image)
        if embedding is None:
            print("ERRO: Nao foi possivel gerar embedding")
            return
        
        print(f"Embedding gerado: {len(embedding)} dimensoes")
        print(f"Norma do embedding: {np.linalg.norm(embedding):.4f}")
        
        # Compara com todos os embeddings no banco
        print("\n" + "=" * 80)
        print("COMPARANDO COM TODOS OS EMBEDDINGS NO BANCO...")
        print("=" * 80)
        
        query_embedding = np.array(embedding, dtype=np.float32)
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        all_distances = []
        
        for face_embedding in all_embeddings:
            db_embedding = np.array(face_embedding.get_embedding_array(), dtype=np.float32)
            db_norm = db_embedding / (np.linalg.norm(db_embedding) + 1e-8)
            
            cosine_similarity = np.dot(query_norm, db_norm)
            cosine_distance = 1.0 - cosine_similarity
            
            user = session.query(User).filter(User.id == face_embedding.user_id).first()
            user_name = user.name if user and user.name else f"Anonimo {face_embedding.user_id}"
            
            all_distances.append({
                'user_id': face_embedding.user_id,
                'user_name': user_name,
                'embedding_id': face_embedding.id,
                'distance': cosine_distance
            })
        
        # Ordena por distância
        all_distances.sort(key=lambda x: x['distance'])
        
        # Agrupa por usuário
        user_distances = {}
        for dist_info in all_distances:
            user_id = dist_info['user_id']
            if user_id not in user_distances:
                user_distances[user_id] = []
            user_distances[user_id].append(dist_info['distance'])
        
        # Calcula estatísticas por usuário
        user_stats = []
        for user_id, distances in user_distances.items():
            user = session.query(User).filter(User.id == user_id).first()
            user_name = user.name if user and user.name else f"Anonimo {user_id}"
            user_stats.append({
                'user_id': user_id,
                'user_name': user_name,
                'min_distance': min(distances),
                'avg_distance': np.mean(distances),
                'max_distance': max(distances),
                'num_embeddings': len(distances),
                'has_name': user and user.name is not None
            })
        
        user_stats.sort(key=lambda x: x['min_distance'])
        
        # Mostra resultados
        print(f"\nThreshold de reconhecimento: {settings.recognition_distance_threshold}")
        print(f"Threshold de ambiguidade: {settings.recognition_ambiguity_threshold}")
        print(f"\n{'ID':<5} {'Nome':<20} {'Min Dist':<10} {'Avg Dist':<10} {'Max Dist':<10} {'Emb':<5} {'Tem Nome':<10}")
        print("-" * 80)
        
        for stat in user_stats:
            within_threshold = "OK" if stat['min_distance'] <= settings.recognition_distance_threshold else "X"
            print(f"{stat['user_id']:<5} {stat['user_name']:<20} {stat['min_distance']:<10.4f} "
                  f"{stat['avg_distance']:<10.4f} {stat['max_distance']:<10.4f} "
                  f"{stat['num_embeddings']:<5} {('Sim' if stat['has_name'] else 'Nao'):<10} {within_threshold}")
        
        # Simula a lógica de find_user_by_embedding
        print("\n" + "=" * 80)
        print("SIMULANDO LOGICA DE find_user_by_embedding...")
        print("=" * 80)
        
        # Filtra usuários dentro do threshold
        valid_users = [s for s in user_stats if s['min_distance'] <= settings.recognition_distance_threshold]
        
        if not valid_users:
            print("\nRESULTADO: Nenhum usuario encontrado (todos acima do threshold)")
        else:
            best = valid_users[0]
            print(f"\nMelhor match: ID {best['user_id']} - {best['user_name']}")
            print(f"  Distancia minima: {best['min_distance']:.4f}")
            print(f"  Distancia media: {best['avg_distance']:.4f}")
            print(f"  Tem nome: {best['has_name']}")
            print(f"  Numero de embeddings: {best['num_embeddings']}")
            
            # Validação de qualidade
            min_quality_threshold = 0.35
            if best['min_distance'] > min_quality_threshold:
                print(f"\n[REJEITADO] Qualidade insuficiente ({best['min_distance']:.4f} > {min_quality_threshold})")
            else:
                print(f"\n[OK] Qualidade OK ({best['min_distance']:.4f} <= {min_quality_threshold})")
            
            # Validação de ambiguidade
            if len(valid_users) > 1:
                second = valid_users[1]
                distance_diff = second['min_distance'] - best['min_distance']
                relative_diff = (distance_diff / (best['min_distance'] + 1e-8)) * 100
                avg_diff = second['avg_distance'] - best['avg_distance']
                
                print(f"\nSegundo melhor: ID {second['user_id']} - {second['user_name']}")
                print(f"  Distancia minima: {second['min_distance']:.4f}")
                print(f"  Distancia media: {second['avg_distance']:.4f}")
                print(f"  Tem nome: {second['has_name']}")
                print(f"  Diferenca absoluta: {distance_diff:.4f}")
                print(f"  Diferenca relativa: {relative_diff:.1f}%")
                print(f"  Diferenca de media: {avg_diff:.4f}")
                
                # Verifica ambiguidade
                is_ambiguous = (
                    distance_diff < settings.recognition_ambiguity_threshold and
                    relative_diff < 20.0 and
                    second['min_distance'] <= settings.recognition_distance_threshold and
                    avg_diff < 0.05
                )
                
                # Se melhor tem nome e segundo é anônimo, não é ambíguo
                if best['has_name'] and not second['has_name']:
                    print(f"\n[OK] AMBIGUIDADE RESOLVIDA: Melhor tem nome, segundo é anônimo")
                    is_ambiguous = False
                
                if is_ambiguous:
                    print(f"\n[REJEITADO] Ambiguidade detectada")
                else:
                    print(f"\n[OK] AMBIGUIDADE OK: Match aceito")
            else:
                print(f"\n[OK] Nenhuma ambiguidade (apenas 1 usuario dentro do threshold)")
        
        session.close()
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        logger.error(f"Erro no debug: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    debug_recognition()

