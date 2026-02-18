"""
Rotas relacionadas a usuários.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ...api.dependencies import get_db

router = APIRouter()


class UserCreate(BaseModel):
    """Modelo para criação de usuário."""
    name: Optional[str] = None


class UserResponse(BaseModel):
    """Modelo de resposta de usuário."""
    id: int
    name: Optional[str]
    created_at: datetime
    is_active: bool
    embeddings_count: int = 0
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Modelo de resposta para lista de usuários."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros")
):
    """
    Lista usuários cadastrados.
    
    Args:
        skip: Número de registros para pular (paginação)
        limit: Número máximo de registros a retornar
        
    Returns:
        Lista de usuários com paginação
    """
    try:
        db = get_db()
        all_users = db.list_users(include_inactive=False)
        
        total = len(all_users)
        users_page = all_users[skip:skip + limit]
        
        # Adiciona contagem de embeddings
        users_with_counts = []
        for user in users_page:
            embeddings_count = db.count_embeddings(user.id)
            users_with_counts.append(UserResponse(
                id=user.id,
                name=user.name,
                created_at=user.created_at,
                is_active=user.is_active,
                embeddings_count=embeddings_count
            ))
        
        return UserListResponse(
            users=users_with_counts,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate):
    """
    Cria um novo usuário.
    
    Args:
        user_data: Dados do usuário (nome opcional)
        
    Returns:
        Usuário criado
    """
    try:
        db = get_db()
        user = db.create_user(name=user_data.name)
        
        return UserResponse(
            id=user.id,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active,
            embeddings_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Obtém detalhes de um usuário específico.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Detalhes do usuário
    """
    try:
        db = get_db()
        user = db.get_user(user_id)
        
        if user is None:
            raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado")
        
        embeddings_count = db.count_embeddings(user_id)
        
        return UserResponse(
            id=user.id,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active,
            embeddings_count=embeddings_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário: {str(e)}")


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    """
    Deleta um usuário e todos os seus embeddings.
    
    Args:
        user_id: ID do usuário a deletar
    """
    try:
        db = get_db()
        deleted = db.delete_user(user_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado")
        
        # Status 204 não retorna corpo
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")

