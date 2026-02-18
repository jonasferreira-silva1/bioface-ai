"""
Rotas relacionadas a emoções.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ...api.dependencies import get_db

router = APIRouter()


class EmotionLogResponse(BaseModel):
    """Modelo de resposta de log de emoção."""
    id: int
    user_id: Optional[int]
    emotion: str
    confidence: float
    timestamp: datetime
    frame_number: Optional[int] = None

    class Config:
        from_attributes = True


class EmotionHistoryResponse(BaseModel):
    """Modelo de resposta para histórico de emoções."""
    emotions: List[EmotionLogResponse]
    total: int
    user_id: Optional[int] = None


@router.get("/history", response_model=EmotionHistoryResponse)
async def get_emotion_history(
    user_id: Optional[int] = Query(
        None, description="Filtrar por ID de usuário"),
    limit: int = Query(100, ge=1, le=1000,
                       description="Número máximo de registros"),
    start_date: Optional[datetime] = Query(
        None, description="Data inicial (ISO format)"),
    end_date: Optional[datetime] = Query(
        None, description="Data final (ISO format)")
):
    """
    Obtém histórico de emoções detectadas.

    Args:
        user_id: ID do usuário (opcional, filtra por usuário)
        limit: Número máximo de registros
        start_date: Data inicial para filtrar
        end_date: Data final para filtrar

    Returns:
        Histórico de emoções
    """
    try:
        db = get_db()
        emotion_logs = db.get_emotion_history(
            user_id=user_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )

        emotions = [
            EmotionLogResponse(
                id=log.id,
                user_id=log.user_id,
                emotion=log.emotion,
                confidence=log.confidence,
                timestamp=log.timestamp,
                frame_number=log.frame_number
            )
            for log in emotion_logs
        ]

        return EmotionHistoryResponse(
            emotions=emotions,
            total=len(emotions),
            user_id=user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter histórico de emoções: {str(e)}")


@router.get("/users/{user_id}/emotions", response_model=EmotionHistoryResponse)
async def get_user_emotions(
    user_id: int,
    limit: int = Query(100, ge=1, le=1000,
                       description="Número máximo de registros")
):
    """
    Obtém histórico de emoções de um usuário específico.

    Args:
        user_id: ID do usuário
        limit: Número máximo de registros

    Returns:
        Histórico de emoções do usuário
    """
    try:
        db = get_db()
        user = db.get_user(user_id)

        if user is None:
            raise HTTPException(
                status_code=404, detail=f"Usuário {user_id} não encontrado")

        emotion_logs = db.get_emotion_history(user_id=user_id, limit=limit)

        emotions = [
            EmotionLogResponse(
                id=log.id,
                user_id=log.user_id,
                emotion=log.emotion,
                confidence=log.confidence,
                timestamp=log.timestamp,
                frame_number=log.frame_number
            )
            for log in emotion_logs
        ]

        return EmotionHistoryResponse(
            emotions=emotions,
            total=len(emotions),
            user_id=user_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter emoções do usuário: {str(e)}")
