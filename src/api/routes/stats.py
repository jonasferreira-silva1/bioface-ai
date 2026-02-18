"""
Rotas relacionadas a estatísticas e métricas.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...api.dependencies import get_db

router = APIRouter()


class StatsResponse(BaseModel):
    """Modelo de resposta de estatísticas."""
    total_users: int
    active_users: int
    total_embeddings: int
    total_emotion_logs: int
    emotions_distribution: Dict[str, int]
    recent_activity: Dict[str, int]


@router.get("", response_model=StatsResponse)
async def get_stats():
    """
    Obtém estatísticas gerais do sistema.
    
    Returns:
        Estatísticas agregadas
    """
    try:
        db = get_db()
        
        # Conta usuários
        all_users = db.list_users(include_inactive=True)
        total_users = len(all_users)
        active_users = len([u for u in all_users if u.is_active])
        
        # Conta embeddings
        total_embeddings = db.count_all_embeddings()
        
        # Conta logs de emoções
        all_emotions = db.get_emotion_history(limit=10000)
        total_emotion_logs = len(all_emotions)
        
        # Distribuição de emoções
        emotions_distribution = {}
        for emotion_log in all_emotions:
            emotion = emotion_log.emotion
            emotions_distribution[emotion] = emotions_distribution.get(emotion, 0) + 1
        
        # Atividade recente (últimas 24 horas)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_emotions = db.get_emotion_history(start_date=yesterday, limit=10000)
        recent_activity = {
            "emotions_last_24h": len(recent_emotions),
            "users_active_last_24h": len(set(e.user_id for e in recent_emotions if e.user_id))
        }
        
        return StatsResponse(
            total_users=total_users,
            active_users=active_users,
            total_embeddings=total_embeddings,
            total_emotion_logs=total_emotion_logs,
            emotions_distribution=emotions_distribution,
            recent_activity=recent_activity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

