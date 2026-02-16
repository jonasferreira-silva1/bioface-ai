"""
Script para deletar um usuário e todos os seus embeddings.

Uso:
    python scripts/delete_user.py --id 1
    python scripts/delete_user.py --id 1 --confirm
"""

import sys
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository

setup_logger()
logger = get_logger(__name__)


def delete_user(user_id: int, confirm: bool = False):
    """
    Deleta um usuário e todos os seus embeddings.
    
    Args:
        user_id: ID do usuário a deletar
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
        
        # Conta embeddings
        embeddings = db.get_user_embeddings(user_id)
        
        print("=" * 60)
        print("Deletar Usuario")
        print("=" * 60)
        print(f"\nUsuario: ID {user_id}")
        print(f"  Nome: {user.name or '(Anonimo)'}")
        print(f"  Embeddings: {len(embeddings)}")
        print(f"  Cadastrado em: {user.created_at}")
        
        # Confirmação
        if not confirm:
            response = input(f"\nATENCAO: Isso deletara o usuario e {len(embeddings)} embeddings! Continuar? (s/N): ")
            if response.lower() != 's':
                print("Operacao cancelada.")
                return
        
        # Deleta (cascade deleta embeddings automaticamente)
        try:
            from src.database.models import User
            
            session.delete(user)
            session.commit()
            
            print(f"\n✓ Usuario {user_id} e {len(embeddings)} embeddings deletados com sucesso!")
            print("=" * 60)
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao deletar usuario: {e}", exc_info=True)
            print(f"\nERRO: {e}")
            raise
        
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deleta um usuario e seus embeddings")
    parser.add_argument(
        '--id',
        type=int,
        required=True,
        help='ID do usuario a deletar'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Nao pede confirmacao'
    )
    
    args = parser.parse_args()
    delete_user(args.id, args.confirm)

