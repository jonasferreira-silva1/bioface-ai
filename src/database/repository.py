"""
Repositório de banco de dados do BioFace AI.

Gerencia acesso e operações no banco de dados.
"""

from typing import Optional, List, Dict
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import numpy as np
from datetime import datetime, timedelta
import sqlite3

from .models import Base, User, FaceEmbedding, EmotionLog, EventLog
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..exceptions import (
    DatabaseConnectionError,
    DatabaseCorruptedError,
    DatabaseLockedError,
    handle_database_error
)

logger = get_logger(__name__)


class DatabaseRepository:
    """
    Repositório para acesso ao banco de dados.
    
    Gerencia todas as operações de CRUD e queries complexas.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Inicializa o repositório.
        
        Args:
            database_url: URL do banco de dados (usa config se None)
        """
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        
        # Cria engine e sessão
        try:
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Testa conexão
            with self.engine.connect() as conn:
                conn.execute(func.select(1))
            
            # Cria tabelas se não existirem
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"Banco de dados inicializado: {self.database_url}")
        except sqlite3.OperationalError as e:
            error_str = str(e).lower()
            if "locked" in error_str:
                raise DatabaseLockedError(self.database_url)
            elif "corrupt" in error_str or "malformed" in error_str:
                raise DatabaseCorruptedError(self.database_url)
            else:
                raise handle_database_error(e, self.database_url)
        except Exception as e:
            raise handle_database_error(e, self.database_url)
    
    def get_session(self) -> Session:
        """
        Retorna uma nova sessão do banco.
        
        Raises:
            DatabaseConnectionError: Se não conseguir conectar
            DatabaseLockedError: Se o banco estiver bloqueado
        """
        try:
            return self.SessionLocal()
        except sqlite3.OperationalError as e:
            error_str = str(e).lower()
            if "locked" in error_str:
                raise DatabaseLockedError(self.database_url)
            elif "corrupt" in error_str or "malformed" in error_str:
                raise DatabaseCorruptedError(self.database_url)
            else:
                raise handle_database_error(e, self.database_url)
        except Exception as e:
            raise handle_database_error(e, self.database_url)
    
    # ============================================
    # OPERAÇÕES DE USUÁRIO
    # ============================================
    
    def create_user(self, name: Optional[str] = None) -> User:
        """
        Cria um novo usuário.
        
        Args:
            name: Nome do usuário (opcional, pode ser anônimo)
            
        Returns:
            User: Usuário criado
        """
        session = self.get_session()
        try:
            user = User(name=name)
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Usuário criado: id={user.id}, name={user.name}")
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro ao criar usuário: {e}")
            raise
        finally:
            session.close()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Retorna usuário por ID."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def get_all_users(self) -> List[User]:
        """Retorna todos os usuários ativos."""
        session = self.get_session()
        try:
            return session.query(User).filter(User.is_active == True).all()
        finally:
            session.close()
    
    # ============================================
    # OPERAÇÕES DE EMBEDDINGS
    # ============================================
    
    def save_embedding(
        self,
        user_id: int,
        embedding: List[float],
        confidence: float,
        face_size: Optional[int] = None
    ) -> FaceEmbedding:
        """
        Salva um embedding facial.
        
        Args:
            user_id: ID do usuário
            embedding: Array de floats (vetor de características)
            confidence: Confiança da detecção
            face_size: Tamanho da face (opcional)
            
        Returns:
            FaceEmbedding: Embedding salvo
        """
        session = self.get_session()
        try:
            face_embedding = FaceEmbedding(
                user_id=user_id,
                confidence=confidence,
                face_size=face_size
            )
            face_embedding.set_embedding_array(embedding)
            
            session.add(face_embedding)
            session.commit()
            session.refresh(face_embedding)
            
            logger.debug(f"Embedding salvo: user_id={user_id}, confidence={confidence:.2f}")
            return face_embedding
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro ao salvar embedding: {e}")
            raise
        finally:
            session.close()
    
    def find_user_by_embedding(
        self,
        embedding: List[float],
        threshold: float = 0.4,
        ambiguity_threshold: float = 0.1,
        limit: int = 1
    ) -> Optional[Dict]:
        """
        Encontra usuário por similaridade de embedding.
        
        Melhorado: Agrupa embeddings por usuário, escolhe o melhor match,
        e valida se não há ambiguidade (dois matches muito próximos).
        
        Args:
            embedding: Embedding a comparar
            threshold: Distância máxima para considerar match (0.0-1.0)
            ambiguity_threshold: Diferença mínima entre melhor e segundo melhor para evitar ambiguidade
            limit: Número máximo de resultados
            
        Returns:
            Dict com user_id e distance, ou None se não encontrar ou houver ambiguidade
        """
        session = self.get_session()
        try:
            # Busca TODOS os embeddings (incluindo usuários com e sem nome)
            # Isso garante que usuários cadastrados sejam reconhecidos corretamente
            from .models import User
            all_embeddings = session.query(FaceEmbedding).all()
            
            if not all_embeddings:
                return None
            
            # Converte embedding de entrada para numpy
            query_embedding = np.array(embedding, dtype=np.float32)
            
            # Agrupa embeddings por usuário
            user_distances = {}  # {user_id: [distances]}
            
            # Compara com cada embedding no banco usando distância cosseno
            for face_embedding in all_embeddings:
                db_embedding = np.array(face_embedding.get_embedding_array(), dtype=np.float32)
                
                # Normaliza embeddings
                query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
                db_norm = db_embedding / (np.linalg.norm(db_embedding) + 1e-8)
                
                # Calcula distância cosseno (1 - similaridade cosseno)
                cosine_similarity = np.dot(query_norm, db_norm)
                cosine_distance = 1.0 - cosine_similarity
                
                # Só considera se estiver dentro do threshold
                if cosine_distance <= threshold:
                    user_id = face_embedding.user_id
                    if user_id not in user_distances:
                        user_distances[user_id] = []
                    user_distances[user_id].append(cosine_distance)
            
            if not user_distances:
                return None
            
            # Encontra os dois melhores usuários (menor distância mínima e melhor média)
            user_min_distances = [
                (user_id, min(distances), np.mean(distances), len(distances))
                for user_id, distances in user_distances.items()
            ]
            
            # Ordena por: 1) distância mínima, 2) média de distâncias, 3) número de embeddings (mais = melhor)
            user_min_distances.sort(key=lambda x: (x[1], x[2], -x[3]))
            
            if not user_min_distances:
                return None
            
            best_user_id, best_min_distance, best_avg_distance, best_num_embeddings = user_min_distances[0]
            
            # VALIDAÇÃO 1: Qualidade mínima do match
            # Só aceita se a distância mínima for realmente boa (< 0.35)
            # Isso evita identificações incorretas quando o match não é suficientemente bom
            min_quality_threshold = 0.35
            if best_min_distance > min_quality_threshold:
                logger.debug(
                    f"Match rejeitado por qualidade insuficiente: user_id={best_user_id}, "
                    f"dist={best_min_distance:.4f} > {min_quality_threshold}"
                )
                return None
            
            # VALIDAÇÃO 2: Validação de ambiguidade simplificada
            # REGRA PRINCIPAL: Prioriza usuários com nome sobre anônimos
            from .models import User
            best_user = session.query(User).filter(User.id == best_user_id).first()
            best_has_name = best_user and best_user.name is not None
            
            if len(user_min_distances) > 1:
                second_best_user_id, second_best_min_distance, second_avg_distance, _ = user_min_distances[1]
                distance_diff = second_best_min_distance - best_min_distance
                
                second_best_user = session.query(User).filter(User.id == second_best_user_id).first()
                second_has_name = second_best_user and second_best_user.name is not None
                
                # Calcula diferença relativa (%)
                relative_diff = (distance_diff / (best_min_distance + 1e-8)) * 100
                
                # REGRA 1: Se melhor tem nome, ACEITA SEMPRE (ignora anônimos completamente)
                if best_has_name:
                    logger.debug(
                        f"Match aceito (usuario com nome tem prioridade absoluta): melhor={best_user_id} "
                        f"({best_user.name if best_user else 'N/A'}, min={best_min_distance:.4f}), "
                        f"segundo={second_best_user_id} (min={second_best_min_distance:.4f})"
                    )
                    # Aceita o melhor match (já está selecionado)
                # REGRA 2: Se melhor é anônimo mas segundo tem nome e está dentro do threshold, SEMPRE prioriza o nomeado
                elif not best_has_name and second_has_name and second_best_min_distance <= threshold:
                    logger.debug(
                        f"Match priorizado (usuario com nome sobre anonimo): melhor={second_best_user_id} "
                        f"({second_best_user.name if second_best_user else 'N/A'}, min={second_best_min_distance:.4f}), "
                        f"anonimo={best_user_id} (min={best_min_distance:.4f}), diff={distance_diff:.4f}"
                    )
                    # Substitui o melhor match pelo usuário com nome
                    best_user_id = second_best_user_id
                    best_min_distance = second_best_min_distance
                    best_avg_distance = second_avg_distance
                    best_num_embeddings = len(user_distances[second_best_user_id])
                    best_user = second_best_user
                    best_has_name = True
                elif best_has_name and second_has_name:
                    # Ambos têm nome - verifica ambiguidade apenas entre usuários nomeados
                    avg_diff = second_avg_distance - best_avg_distance
                    is_ambiguous = (
                        distance_diff < ambiguity_threshold and
                        relative_diff < 15.0 and  # Diferença relativa < 15%
                        second_best_min_distance <= threshold and
                        avg_diff < 0.05
                    )
                    
                    if is_ambiguous:
                        logger.warning(
                            f"Ambiguidade entre usuarios nomeados: melhor={best_user_id} "
                            f"(min={best_min_distance:.4f}), segundo={second_best_user_id} "
                            f"(min={second_best_min_distance:.4f}), diff={distance_diff:.4f}"
                        )
                        return None
                    else:
                        logger.debug(
                            f"Match aceito: melhor={best_user_id} (min={best_min_distance:.4f}), "
                            f"segundo={second_best_user_id} (min={second_best_min_distance:.4f})"
                        )
                else:
                    # Melhor é anônimo - critérios mais permissivos
                    if best_min_distance < 0.3:
                        logger.debug(
                            f"Match aceito (muito bom): melhor={best_user_id} "
                            f"(min={best_min_distance:.4f})"
                        )
                    else:
                        # Verifica ambiguidade apenas se ambos são anônimos
                        avg_diff = second_avg_distance - best_avg_distance
                        is_ambiguous = (
                            distance_diff < ambiguity_threshold and
                            relative_diff < 10.0 and  # Muito restritivo para anônimos
                            second_best_min_distance <= threshold and
                            avg_diff < 0.03
                        )
                        
                        if is_ambiguous:
                            logger.warning(
                                f"Ambiguidade entre usuarios anonimos: melhor={best_user_id} "
                                f"(min={best_min_distance:.4f}), segundo={second_best_user_id} "
                                f"(min={second_best_min_distance:.4f})"
                            )
                            return None
                        else:
                            logger.debug(
                                f"Match aceito: melhor={best_user_id} (min={best_min_distance:.4f})"
                            )
            
            # VALIDAÇÃO 3: Confirma que a média também é boa
            # Se a média for muito maior que a mínima, pode indicar inconsistência
            # Mas só rejeita se a diferença for muito grande (> 0.2) E a média estiver acima do threshold
            avg_diff = best_avg_distance - best_min_distance
            if avg_diff > 0.2 and best_avg_distance > threshold:
                logger.debug(
                    f"Match rejeitado por inconsistência: user_id={best_user_id}, "
                    f"min={best_min_distance:.4f}, avg={best_avg_distance:.4f}, "
                    f"diff={avg_diff:.4f} > 0.2 e avg > threshold"
                )
                return None
            
            # Retorna o melhor match (passou todas as validações)
            best_match = {
                "user_id": best_user_id,
                "distance": float(best_min_distance),
                "avg_distance": float(best_avg_distance),
                "num_embeddings": best_num_embeddings
            }
            
            logger.debug(
                f"Usuário encontrado: user_id={best_user_id}, "
                f"min_distance={best_min_distance:.4f}, "
                f"avg_distance={best_avg_distance:.4f}, "
                f"embeddings={len(user_distances[best_user_id])}"
            )
            
            return best_match
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por embedding: {e}")
            return None
        finally:
            session.close()
    
    def get_user_embeddings(self, user_id: int) -> List[FaceEmbedding]:
        """Retorna todos os embeddings de um usuário."""
        session = self.get_session()
        try:
            return session.query(FaceEmbedding).filter(
                FaceEmbedding.user_id == user_id
            ).all()
        finally:
            session.close()
    
    # ============================================
    # OPERAÇÕES DE EMOÇÕES
    # ============================================
    
    def log_emotion(
        self,
        emotion: str,
        confidence: float,
        user_id: Optional[int] = None,
        frame_number: Optional[int] = None,
        extra_data: Optional[Dict] = None
    ) -> EmotionLog:
        """
        Registra uma emoção detectada.
        
        Args:
            emotion: Nome da emoção ("Happy", "Sad", etc.)
            confidence: Confiança (0.0-1.0)
            user_id: ID do usuário (None = anônimo)
            frame_number: Número do frame
            extra_data: Dados adicionais (bbox, landmarks, etc.)
            
        Returns:
            EmotionLog: Log criado
        """
        session = self.get_session()
        try:
            emotion_log = EmotionLog(
                user_id=user_id,
                emotion=emotion,
                confidence=confidence,
                frame_number=frame_number,
                extra_data=extra_data
            )
            
            session.add(emotion_log)
            session.commit()
            session.refresh(emotion_log)
            
            logger.debug(f"Emoção registrada: {emotion} ({confidence:.2f})")
            return emotion_log
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro ao registrar emoção: {e}")
            raise
        finally:
            session.close()
    
    def get_emotion_history(
        self,
        user_id: Optional[int] = None,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[EmotionLog]:
        """
        Retorna histórico de emoções.
        
        Args:
            user_id: ID do usuário (None = todos)
            limit: Número máximo de registros
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de EmotionLog
        """
        session = self.get_session()
        try:
            query = session.query(EmotionLog)
            
            if user_id is not None:
                query = query.filter(EmotionLog.user_id == user_id)
            
            if start_date:
                query = query.filter(EmotionLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(EmotionLog.timestamp <= end_date)
            
            return query.order_by(EmotionLog.timestamp.desc()).limit(limit).all()
            
        finally:
            session.close()
    
    # ============================================
    # OPERAÇÕES DE EVENTOS
    # ============================================
    
    def log_event(
        self,
        event_type: str,
        event_data: Optional[Dict] = None,
        user_id: Optional[int] = None,
        severity: str = "info"
    ) -> EventLog:
        """
        Registra um evento.
        
        Args:
            event_type: Tipo do evento
            event_data: Dados do evento
            user_id: ID do usuário (None = anônimo)
            severity: Severidade ("info", "warning", "error")
            
        Returns:
            EventLog: Log criado
        """
        session = self.get_session()
        try:
            event_log = EventLog(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data,
                severity=severity
            )
            
            session.add(event_log)
            session.commit()
            session.refresh(event_log)
            
            logger.debug(f"Evento registrado: {event_type}")
            return event_log
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro ao registrar evento: {e}")
            raise
        finally:
            session.close()
    
    # ============================================
    # LIMPEZA E MANUTENÇÃO
    # ============================================
    
    def cleanup_old_data(self, days: int = 30):
        """
        Remove dados antigos (conforme data_retention_days).
        
        Args:
            days: Dias de retenção
        """
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Remove emoções antigas
            deleted_emotions = session.query(EmotionLog).filter(
                EmotionLog.timestamp < cutoff_date
            ).delete()
            
            # Remove eventos antigos
            deleted_events = session.query(EventLog).filter(
                EventLog.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            
            logger.info(f"Limpeza: {deleted_emotions} emoções e {deleted_events} eventos removidos")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Erro na limpeza: {e}")
        finally:
            session.close()

