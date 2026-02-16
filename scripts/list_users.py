"""
Script para listar todos os usuários cadastrados no sistema.

Uso:
    python scripts/list_users.py
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository

setup_logger()
logger = get_logger(__name__)


def list_users():
    """Lista todos os usuários cadastrados."""
    try:
        db = DatabaseRepository()
        
        print("=" * 60)
        print("Usuarios Cadastrados")
        print("=" * 60)
        
        users = db.get_all_users()
        
        if not users:
            print("\nNenhum usuario cadastrado.")
            print("Use: python scripts/register_face.py --name 'Nome'")
        else:
            print(f"\nTotal: {len(users)} usuario(s)\n")
            
            for user in users:
                embeddings = db.get_user_embeddings(user.id)
                
                print(f"ID: {user.id}")
                print(f"  Nome: {user.name or '(Anonimo)'}")
                print(f"  Cadastrado em: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Embeddings: {len(embeddings)}")
                print(f"  Ativo: {'Sim' if user.is_active else 'Nao'}")
                print("-" * 60)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Erro ao listar usuarios: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    list_users()

