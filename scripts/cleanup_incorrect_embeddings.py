"""
Script para limpar embeddings incorretos de um usuário.

Remove embeddings que estão muito próximos de outro usuário (provavelmente incorretos).

Uso:
    python scripts/cleanup_incorrect_embeddings.py --user-id 3 --threshold 0.1
"""

import sys
import argparse
from pathlib import Path
import numpy as np

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository
from src.database.models import FaceEmbedding, User

setup_logger()
logger = get_logger(__name__)


def cleanup_incorrect_embeddings(user_id: int, threshold: float = 0.1, confirm: bool = False):
    """
    Remove embeddings de um usuário que estão muito próximos de outros usuários.
    
    Args:
        user_id: ID do usuário a limpar
        threshold: Distância máxima para considerar como incorreto (0.0-1.0)
        confirm: Se True, não pede confirmação
    """
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        # Verifica se usuário existe
        user = db.get_user(user_id)
        if not user:
            print(f"ERRO: Usuario {user_id} nao encontrado!")
            return
        
        print("=" * 60)
        print("Limpeza de Embeddings Incorretos")
        print("=" * 60)
        print(f"\nUsuario: {user.name or f'Usuario {user_id}'} (ID: {user_id})")
        
        # Busca todos os embeddings do usuário
        user_embeddings = db.get_user_embeddings(user_id)
        print(f"Total de embeddings: {len(user_embeddings)}")
        
        if len(user_embeddings) == 0:
            print("Nenhum embedding para analisar.")
            return
        
        # Busca todos os outros usuários
        all_users = db.get_all_users()
        other_users = [u for u in all_users if u.id != user_id]
        
        if not other_users:
            print("Nenhum outro usuario para comparar.")
            return
        
        print(f"Comparando com {len(other_users)} outros usuarios...")
        
        # Para cada embedding do usuário, verifica se está muito próximo de outros usuários
        incorrect_embeddings = []
        
        for user_emb in user_embeddings:
            user_emb_array = np.array(user_emb.get_embedding_array(), dtype=np.float32)
            user_emb_norm = user_emb_array / (np.linalg.norm(user_emb_array) + 1e-8)
            
            # Compara com embeddings de outros usuários
            min_distance_to_others = float('inf')
            closest_other_user = None
            
            for other_user in other_users:
                other_embeddings = db.get_user_embeddings(other_user.id)
                
                for other_emb in other_embeddings:
                    other_emb_array = np.array(other_emb.get_embedding_array(), dtype=np.float32)
                    other_emb_norm = other_emb_array / (np.linalg.norm(other_emb_array) + 1e-8)
                    
                    # Distância cosseno
                    cosine_similarity = np.dot(user_emb_norm, other_emb_norm)
                    cosine_distance = 1.0 - cosine_similarity
                    
                    if cosine_distance < min_distance_to_others:
                        min_distance_to_others = cosine_distance
                        closest_other_user = other_user
            
            # Se está muito próximo de outro usuário, marca como incorreto
            if min_distance_to_others < threshold:
                incorrect_embeddings.append({
                    'embedding': user_emb,
                    'distance': min_distance_to_others,
                    'closest_user': closest_other_user
                })
        
        # Mostra resultados
        print(f"\nEmbeddings suspeitos encontrados: {len(incorrect_embeddings)}")
        
        if len(incorrect_embeddings) > 0:
            print("\nDetalhes:")
            for item in incorrect_embeddings[:10]:  # Mostra apenas os 10 primeiros
                closest_name = item['closest_user'].name or f"Usuario {item['closest_user'].id}"
                print(f"  - Embedding ID {item['embedding'].id}: "
                      f"distancia {item['distance']:.4f} de '{closest_name}'")
            
            if len(incorrect_embeddings) > 10:
                print(f"  ... e mais {len(incorrect_embeddings) - 10} embeddings")
            
            # Confirmação
            if not confirm:
                response = input(f"\nDeseja deletar {len(incorrect_embeddings)} embeddings suspeitos? (s/N): ")
                if response.lower() != 's':
                    print("Operacao cancelada.")
                    return
            
            # Deleta embeddings incorretos
            deleted_count = 0
            try:
                for item in incorrect_embeddings:
                    session.delete(item['embedding'])
                    deleted_count += 1
                
                session.commit()
                print(f"\n[OK] {deleted_count} embeddings deletados com sucesso!")
                print(f"Embeddings restantes: {len(user_embeddings) - deleted_count}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Erro ao deletar embeddings: {e}", exc_info=True)
                print(f"\nERRO: {e}")
                raise
        else:
            print("\n[OK] Nenhum embedding suspeito encontrado!")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpa embeddings incorretos de um usuário")
    parser.add_argument(
        '--user-id',
        type=int,
        required=True,
        help='ID do usuario a limpar'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.1,
        help='Distancia maxima para considerar como incorreto (padrao: 0.1)'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Nao pede confirmacao'
    )
    
    args = parser.parse_args()
    cleanup_incorrect_embeddings(args.user_id, args.threshold, args.confirm)

