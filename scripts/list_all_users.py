"""
Script para listar TODOS os usuários (incluindo inativos e anônimos).

Uso:
    python scripts/list_all_users.py
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository
from src.database.models import User

setup_logger()
logger = get_logger(__name__)


def list_all_users():
    """Lista TODOS os usuários (incluindo inativos e anônimos)."""
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        print("=" * 60)
        print("TODOS os Usuarios (incluindo inativos e anonimos)")
        print("=" * 60)
        
        # Busca TODOS os usuários (sem filtro)
        all_users = session.query(User).all()
        
        if not all_users:
            print("\nNenhum usuario encontrado.")
        else:
            print(f"\nTotal: {len(all_users)} usuario(s)\n")
            
            for user in all_users:
                embeddings = db.get_user_embeddings(user.id)
                
                status = "ATIVO" if user.is_active else "INATIVO"
                name = user.name or "(Anonimo)"
                
                print(f"ID: {user.id}")
                print(f"  Nome: {name}")
                print(f"  Status: {status}")
                print(f"  Cadastrado em: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Embeddings: {len(embeddings)}")
                print("-" * 60)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Erro ao listar usuarios: {e}", exc_info=True)
        print(f"\nERRO: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    list_all_users()

