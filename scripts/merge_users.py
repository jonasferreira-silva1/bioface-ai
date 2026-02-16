"""
Script para mesclar dois usuários (mover embeddings de um para outro).

Útil quando você cadastrou a mesma pessoa duas vezes com nomes diferentes.

Uso:
    python scripts/merge_users.py --from 1 --to 2
    python scripts/merge_users.py --from 1 --to 2 --delete-old
"""

import sys
import argparse
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.database.repository import DatabaseRepository
from sqlalchemy import update

setup_logger()
logger = get_logger(__name__)


def merge_users(from_user_id: int, to_user_id: int, delete_old: bool = False):
    """
    Mescla dois usuários movendo embeddings de um para outro.
    
    Args:
        from_user_id: ID do usuário de origem (será deletado)
        to_user_id: ID do usuário de destino (receberá os embeddings)
        delete_old: Se True, deleta o usuário antigo após mesclar
    """
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        # Verifica se usuários existem
        from_user = db.get_user(from_user_id)
        to_user = db.get_user(to_user_id)
        
        if not from_user:
            print(f"ERRO: Usuário {from_user_id} não encontrado!")
            return
        
        if not to_user:
            print(f"ERRO: Usuário {to_user_id} não encontrado!")
            return
        
        print("=" * 60)
        print("Mesclando Usuarios")
        print("=" * 60)
        print(f"\nDe: ID {from_user_id} - {from_user.name or '(Anonimo)'}")
        print(f"Para: ID {to_user_id} - {to_user.name or '(Anonimo)'}")
        
        # Conta embeddings antes
        from_embeddings = db.get_user_embeddings(from_user_id)
        to_embeddings = db.get_user_embeddings(to_user_id)
        
        print(f"\nEmbeddings antes:")
        print(f"  Usuario {from_user_id}: {len(from_embeddings)}")
        print(f"  Usuario {to_user_id}: {len(to_embeddings)}")
        
        # Confirmação
        response = input(f"\nMover {len(from_embeddings)} embeddings de '{from_user.name or 'Anonimo'}' para '{to_user.name or 'Anonimo'}'? (s/N): ")
        if response.lower() != 's':
            print("Operacao cancelada.")
            return
        
        # Move embeddings
        try:
            from src.database.models import FaceEmbedding
            
            updated = session.query(FaceEmbedding).filter(
                FaceEmbedding.user_id == from_user_id
            ).update({FaceEmbedding.user_id: to_user_id})
            
            session.commit()
            
            print(f"\n✓ {updated} embeddings movidos com sucesso!")
            
            # Atualiza nome se o usuário destino não tiver nome
            if not to_user.name and from_user.name:
                to_user.name = from_user.name
                session.commit()
                print(f"✓ Nome atualizado: '{to_user.name}'")
            
            # Deleta usuário antigo se solicitado
            if delete_old:
                session.delete(from_user)
                session.commit()
                print(f"✓ Usuario {from_user_id} deletado.")
            
            # Mostra resultado final
            final_embeddings = db.get_user_embeddings(to_user_id)
            print(f"\nResultado final:")
            print(f"  Usuario {to_user_id}: {len(final_embeddings)} embeddings")
            
            print("\n" + "=" * 60)
            print("Mesclagem concluida com sucesso!")
            print("=" * 60)
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao mesclar usuarios: {e}", exc_info=True)
            print(f"\nERRO: {e}")
            raise
        
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mescla dois usuarios (move embeddings)")
    parser.add_argument(
        '--from',
        type=int,
        required=True,
        dest='from_user_id',
        help='ID do usuario de origem (sera deletado)'
    )
    parser.add_argument(
        '--to',
        type=int,
        required=True,
        dest='to_user_id',
        help='ID do usuario de destino (recebera os embeddings)'
    )
    parser.add_argument(
        '--delete-old',
        action='store_true',
        help='Deleta o usuario antigo apos mesclar'
    )
    
    args = parser.parse_args()
    merge_users(args.from_user_id, args.to_user_id, args.delete_old)

