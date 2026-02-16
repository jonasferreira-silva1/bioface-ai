"""
Módulo de banco de dados do BioFace AI.

Gerencia modelos de dados, repositórios e acesso ao banco de dados.
"""

from .models import User, FaceEmbedding, EmotionLog, EventLog
from .repository import DatabaseRepository

__all__ = [
    "User",
    "FaceEmbedding", 
    "EmotionLog",
    "EventLog",
    "DatabaseRepository"
]

