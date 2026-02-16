"""
Script para deletar todos os embeddings de um usuário.

Uso:
    python scripts/delete_all_user_embeddings.py --user-id 3 --confirm
"""

import sys
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository
from src.database.models import FaceEmbedding

setup_logger()
logger = get_logger(__name__)


def delete_all_embeddings(user_id: int, confirm: bool = False):
    """Deleta todos os embeddings de um usuário."""
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        user = db.get_user(user_id)
        if not user:
            print(f"ERRO: Usuario {user_id} nao encontrado!")
            return
        
        embeddings = db.get_user_embeddings(user_id)
        
        print("=" * 60)
        print("Deletar Todos os Embeddings")
        print("=" * 60)
        print(f"\nUsuario: {user.name or f'Usuario {user_id}'} (ID: {user_id})")
        print(f"Total de embeddings: {len(embeddings)}")
        
        if len(embeddings) == 0:
            print("Nenhum embedding para deletar.")
            return
        
        if not confirm:
            response = input(f"\nDeseja deletar TODOS os {len(embeddings)} embeddings? (s/N): ")
            if response.lower() != 's':
                print("Operacao cancelada.")
                return
        
        try:
            deleted = session.query(FaceEmbedding).filter(
                FaceEmbedding.user_id == user_id
            ).delete()
            
            session.commit()
            print(f"\n[OK] {deleted} embeddings deletados com sucesso!")
            print("\nRecomendacao: Recadastre o usuario para criar novos embeddings corretos.")
            print(f"Comando: python scripts/register_face.py --name \"{user.name or 'Nome'}\"")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao deletar embeddings: {e}", exc_info=True)
            print(f"\nERRO: {e}")
            raise
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deleta todos os embeddings de um usuário")
    parser.add_argument(
        '--user-id',
        type=int,
        required=True,
        help='ID do usuario'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Nao pede confirmacao'
    )
    
    args = parser.parse_args()
    delete_all_embeddings(args.user_id, args.confirm)

