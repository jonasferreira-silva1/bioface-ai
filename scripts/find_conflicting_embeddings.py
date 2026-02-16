"""
Script para encontrar embeddings conflitantes entre dois usuários.

Uso:
    python scripts/find_conflicting_embeddings.py --user1 2 --user2 3
"""

import sys
import argparse
from pathlib import Path
import numpy as np

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository

setup_logger()
logger = get_logger(__name__)


def find_conflicting_embeddings(user1_id: int, user2_id: int, threshold: float = 0.1):
    """
    Encontra embeddings que estão muito próximos entre dois usuários.
    
    Args:
        user1_id: ID do primeiro usuário
        user2_id: ID do segundo usuário
        threshold: Distância máxima para considerar conflitante
    """
    try:
        db = DatabaseRepository()
        
        user1 = db.get_user(user1_id)
        user2 = db.get_user(user2_id)
        
        if not user1 or not user2:
            print("ERRO: Um ou ambos os usuarios nao foram encontrados!")
            return
        
        print("=" * 60)
        print("Busca de Embeddings Conflitantes")
        print("=" * 60)
        print(f"\nUsuario 1: {user1.name or f'Usuario {user1_id}'} (ID: {user1_id})")
        print(f"Usuario 2: {user2.name or f'Usuario {user2_id}'} (ID: {user2_id})")
        print(f"Threshold: {threshold}")
        
        # Busca embeddings
        embeddings1 = db.get_user_embeddings(user1_id)
        embeddings2 = db.get_user_embeddings(user2_id)
        
        print(f"\nEmbeddings do Usuario 1: {len(embeddings1)}")
        print(f"Embeddings do Usuario 2: {len(embeddings2)}")
        
        # Encontra conflitos
        conflicts_user1 = []  # Embeddings do user1 muito próximos do user2
        conflicts_user2 = []  # Embeddings do user2 muito próximos do user1
        
        print("\nComparando embeddings...")
        
        for emb1 in embeddings1:
            emb1_array = np.array(emb1.get_embedding_array(), dtype=np.float32)
            emb1_norm = emb1_array / (np.linalg.norm(emb1_array) + 1e-8)
            
            min_dist = float('inf')
            closest_emb2 = None
            
            for emb2 in embeddings2:
                emb2_array = np.array(emb2.get_embedding_array(), dtype=np.float32)
                emb2_norm = emb2_array / (np.linalg.norm(emb2_array) + 1e-8)
                
                cosine_similarity = np.dot(emb1_norm, emb2_norm)
                cosine_distance = 1.0 - cosine_similarity
                
                if cosine_distance < min_dist:
                    min_dist = cosine_distance
                    closest_emb2 = emb2
            
            if min_dist < threshold:
                conflicts_user1.append({
                    'embedding': emb1,
                    'distance': min_dist,
                    'closest': closest_emb2
                })
        
        for emb2 in embeddings2:
            emb2_array = np.array(emb2.get_embedding_array(), dtype=np.float32)
            emb2_norm = emb2_array / (np.linalg.norm(emb2_array) + 1e-8)
            
            min_dist = float('inf')
            closest_emb1 = None
            
            for emb1 in embeddings1:
                emb1_array = np.array(emb1.get_embedding_array(), dtype=np.float32)
                emb1_norm = emb1_array / (np.linalg.norm(emb1_array) + 1e-8)
                
                cosine_similarity = np.dot(emb1_norm, emb2_norm)
                cosine_distance = 1.0 - cosine_similarity
                
                if cosine_distance < min_dist:
                    min_dist = cosine_distance
                    closest_emb1 = emb1
            
            if min_dist < threshold:
                conflicts_user2.append({
                    'embedding': emb2,
                    'distance': min_dist,
                    'closest': closest_emb1
                })
        
        # Mostra resultados
        print("\n" + "=" * 60)
        print("RESULTADOS")
        print("=" * 60)
        
        print(f"\nEmbeddings do {user1.name or f'Usuario {user1_id}'} muito proximos do {user2.name or f'Usuario {user2_id}'}: {len(conflicts_user1)}")
        if conflicts_user1:
            conflicts_user1.sort(key=lambda x: x['distance'])
            for i, conflict in enumerate(conflicts_user1[:10], 1):
                print(f"  {i}. Embedding ID {conflict['embedding'].id}: distancia {conflict['distance']:.4f}")
        
        print(f"\nEmbeddings do {user2.name or f'Usuario {user2_id}'} muito proximos do {user1.name or f'Usuario {user1_id}'}: {len(conflicts_user2)}")
        if conflicts_user2:
            conflicts_user2.sort(key=lambda x: x['distance'])
            for i, conflict in enumerate(conflicts_user2[:10], 1):
                print(f"  {i}. Embedding ID {conflict['embedding'].id}: distancia {conflict['distance']:.4f}")
        
        # Recomendações
        if conflicts_user1 or conflicts_user2:
            print("\n" + "=" * 60)
            print("RECOMENDACOES")
            print("=" * 60)
            
            if len(conflicts_user2) > len(conflicts_user1):
                print(f"\nRecomendacao: Deletar {len(conflicts_user2)} embeddings do {user2.name or f'Usuario {user2_id}'}")
                print(f"Comando: python scripts/delete_embeddings.py --user-id {user2_id} --embedding-ids {','.join([str(c['embedding'].id) for c in conflicts_user2])}")
            else:
                print(f"\nRecomendacao: Deletar {len(conflicts_user1)} embeddings do {user1.name or f'Usuario {user1_id}'}")
                print(f"Comando: python scripts/delete_embeddings.py --user-id {user1_id} --embedding-ids {','.join([str(c['embedding'].id) for c in conflicts_user1])}")
        else:
            print("\n[OK] Nenhum conflito encontrado!")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encontra embeddings conflitantes entre dois usuários")
    parser.add_argument(
        '--user1',
        type=int,
        required=True,
        help='ID do primeiro usuario'
    )
    parser.add_argument(
        '--user2',
        type=int,
        required=True,
        help='ID do segundo usuario'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.1,
        help='Distancia maxima para considerar conflitante (padrao: 0.1)'
    )
    
    args = parser.parse_args()
    find_conflicting_embeddings(args.user1, args.user2, args.threshold)

