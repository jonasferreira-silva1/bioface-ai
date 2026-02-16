"""
Script para limpar embeddings órfãos (sem usuário associado).

Uso:
    python scripts/cleanup_orphan_embeddings.py
    python scripts/cleanup_orphan_embeddings.py --confirm
"""

import sys
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository
from src.database.models import FaceEmbedding, User

setup_logger()
logger = get_logger(__name__)


def cleanup_orphan_embeddings(confirm: bool = False):
    """Remove embeddings que não têm usuário associado."""
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        # Busca todos os embeddings
        all_embeddings = session.query(FaceEmbedding).all()
        
        # Busca todos os IDs de usuários válidos
        all_users = session.query(User).all()
        valid_user_ids = {user.id for user in all_users}
        
        # Encontra embeddings órfãos
        orphan_embeddings = [
            emb for emb in all_embeddings
            if emb.user_id not in valid_user_ids
        ]
        
        if not orphan_embeddings:
            print("Nenhum embedding orfao encontrado.")
            return
        
        print("=" * 60)
        print("Limpar Embeddings Orfaos")
        print("=" * 60)
        print(f"\nEmbeddings orfaos encontrados: {len(orphan_embeddings)}")
        
        # Agrupa por user_id
        by_user_id = {}
        for emb in orphan_embeddings:
            if emb.user_id not in by_user_id:
                by_user_id[emb.user_id] = []
            by_user_id[emb.user_id].append(emb)
        
        print("\nEmbeddings por user_id inexistente:")
        for user_id, embs in by_user_id.items():
            print(f"  User ID {user_id}: {len(embs)} embeddings")
        
        if not confirm:
            response = input(f"\nDeletar {len(orphan_embeddings)} embeddings orfaos? (s/N): ")
            if response.lower() != 's':
                print("Operacao cancelada.")
                return
        
        # Deleta embeddings órfãos
        deleted_count = 0
        for emb in orphan_embeddings:
            session.delete(emb)
            deleted_count += 1
        
        session.commit()
        
        print(f"\n[OK] {deleted_count} embeddings orfaos deletados com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")
        if 'session' in locals():
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Limpa embeddings orfaos (sem usuario)")
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirma automaticamente sem pedir confirmacao'
    )
    args = parser.parse_args()
    cleanup_orphan_embeddings(confirm=args.confirm)

