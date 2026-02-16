"""
Script para mesclar todos os usuários anônimos com um usuário específico.

Uso:
    python scripts/merge_anonymous_to_user.py --target-user-id 2 --confirm
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


def merge_anonymous_to_user(target_user_id: int, confirm: bool = False):
    """Mescla todos os usuários anônimos com um usuário específico."""
    try:
        db = DatabaseRepository()
        session = db.get_session()
        
        target_user = db.get_user(target_user_id)
        if not target_user:
            print(f"ERRO: Usuario {target_user_id} nao encontrado!")
            return
        
        # Busca todos os usuários anônimos (sem nome)
        anonymous_users = session.query(User).filter(
            User.id != target_user_id,
            User.name.is_(None)
        ).all()
        
        if not anonymous_users:
            print("Nenhum usuario anonimo encontrado para mesclar.")
            return
        
        print("=" * 60)
        print("Mesclar Usuarios Anonimos")
        print("=" * 60)
        print(f"\nUsuario destino: {target_user.name or f'Usuario {target_user_id}'} (ID: {target_user_id})")
        print(f"\nUsuarios anonimos encontrados: {len(anonymous_users)}")
        
        total_embeddings = 0
        for anon_user in anonymous_users:
            embeddings = db.get_user_embeddings(anon_user.id)
            total_embeddings += len(embeddings)
            print(f"  - Usuario {anon_user.id}: {len(embeddings)} embeddings")
        
        if total_embeddings == 0:
            print("\nNenhum embedding para mover.")
            return
        
        if not confirm:
            response = input(f"\nMover {total_embeddings} embeddings de {len(anonymous_users)} usuarios anonimos para '{target_user.name or f'Usuario {target_user_id}'}'? (s/N): ")
            if response.lower() != 's':
                print("Operacao cancelada.")
                return
        
        # Move embeddings e deleta usuários anônimos
        moved_count = 0
        deleted_count = 0
        
        try:
            for anon_user in anonymous_users:
                embeddings = db.get_user_embeddings(anon_user.id)
                
                # Move embeddings
                updated = session.query(FaceEmbedding).filter(
                    FaceEmbedding.user_id == anon_user.id
                ).update({FaceEmbedding.user_id: target_user_id})
                
                moved_count += updated
                
                # Deleta usuário anônimo
                session.delete(anon_user)
                deleted_count += 1
            
            session.commit()
            
            print(f"\n[OK] {moved_count} embeddings movidos com sucesso!")
            print(f"[OK] {deleted_count} usuarios anonimos deletados.")
            
            # Mostra resultado final
            final_embeddings = db.get_user_embeddings(target_user_id)
            print(f"\nResultado final:")
            print(f"  Usuario {target_user_id} ({target_user.name or 'Anonimo'}): {len(final_embeddings)} embeddings")
            
            print("\n" + "=" * 60)
            print("Mesclagem concluida com sucesso!")
            print("=" * 60)
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao mesclar usuarios: {e}", exc_info=True)
            print(f"\nERRO: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        print(f"\nERRO: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mescla todos os usuários anônimos com um usuário específico")
    parser.add_argument(
        '--target-user-id',
        type=int,
        required=True,
        help='ID do usuario destino'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Nao pede confirmacao'
    )
    
    args = parser.parse_args()
    merge_anonymous_to_user(args.target_user_id, args.confirm)

