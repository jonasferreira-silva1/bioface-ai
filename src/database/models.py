"""
Modelos de banco de dados do BioFace AI.

Define as tabelas e relacionamentos usando SQLAlchemy.
"""

from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from typing import Optional
import json

Base = declarative_base()


class User(Base):
    """
    Tabela de usuários.
    
    Armazena informações básicas dos usuários identificados pelo sistema.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)  # Nome opcional (pode ser anônimo)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    embeddings = relationship("FaceEmbedding", back_populates="user", cascade="all, delete-orphan")
    emotions = relationship("EmotionLog", back_populates="user", cascade="all, delete-orphan")
    events = relationship("EventLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class FaceEmbedding(Base):
    """
    Tabela de embeddings faciais.
    
    Armazena os vetores de características (embeddings) das faces detectadas.
    Cada embedding está associado a um usuário.
    """
    __tablename__ = "face_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Embedding como JSON (array de floats)
    # Exemplo: [0.123, -0.456, 0.789, ...]
    embedding = Column(Text, nullable=False)  # JSON string do array
    
    # Metadados
    confidence = Column(Float, nullable=False)  # Confiança da detecção
    face_size = Column(Integer)  # Tamanho da face (largura x altura)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="embeddings")
    
    def get_embedding_array(self) -> list:
        """Converte embedding JSON string para array Python."""
        return json.loads(self.embedding)
    
    def set_embedding_array(self, embedding: list):
        """Converte array Python para JSON string."""
        self.embedding = json.dumps(embedding)
    
    def __repr__(self):
        return f"<FaceEmbedding(id={self.id}, user_id={self.user_id}, confidence={self.confidence:.2f})>"


class EmotionLog(Base):
    """
    Tabela de logs de emoções.
    
    Armazena histórico de emoções detectadas ao longo do tempo.
    """
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null = anônimo
    
    # Emoção detectada
    emotion = Column(String(50), nullable=False)  # "Happy", "Sad", etc.
    confidence = Column(Float, nullable=False)
    
    # Metadados
    frame_number = Column(Integer)  # Número do frame
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Dados adicionais (landmarks, bbox, etc.)
    extra_data = Column(JSON, nullable=True)  # Renomeado de 'metadata' (palavra reservada SQLAlchemy)
    
    # Relacionamentos
    user = relationship("User", back_populates="emotions")
    
    def __repr__(self):
        return f"<EmotionLog(id={self.id}, emotion={self.emotion}, confidence={self.confidence:.2f})>"


class EventLog(Base):
    """
    Tabela de logs de eventos.
    
    Armazena eventos disparados pelo motor de regras.
    """
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Evento
    event_type = Column(String(100), nullable=False)  # "emotion_detected", "rule_triggered", etc.
    event_data = Column(JSON, nullable=True)  # Dados do evento (renomeado de 'metadata')
    
    # Metadados
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    severity = Column(String(20), default="info")  # "info", "warning", "error"
    
    # Relacionamentos
    user = relationship("User", back_populates="events")
    
    def __repr__(self):
        return f"<EventLog(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"

