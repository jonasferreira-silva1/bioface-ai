"""
BioFace AI - Versão Leve (Sem TensorFlow)

Esta versão funciona apenas com detecção de faces, sem classificação de emoções.
Ideal para sistemas com pouca memória.

Uso: python -m src.main_light
"""

import cv2
import time
import argparse
from pathlib import Path
import sys
from typing import Optional
import asyncio
from datetime import datetime

# Adiciona diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_settings
from src.vision.camera import Camera
from src.vision.face_detector import FaceDetector
from src.vision.face_processor import FaceProcessor
from src.ai.face_recognizer import FaceRecognizer
from src.ai.emotion_classifier_light import EmotionClassifierLight
from src.database.repository import DatabaseRepository
from src.exceptions import (
    CameraNotOpenedError,
    CameraDisconnectedError,
    CameraReadError,
    DatabaseConnectionError,
    DatabaseCorruptedError,
    DatabaseLockedError,
    EmbeddingGenerationError,
    FaceNotDetectedError
)

# Configura logging
setup_logger()
logger = get_logger(__name__)


class BioFacePipelineLight:
    """
    Pipeline leve do BioFace AI (sem classificação de emoções).
    
    Esta versão apenas detecta faces, sem processar emoções.
    Muito mais leve em memória (~200-500MB vs 2-4GB).
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Inicializa o pipeline leve.
        
        Args:
            api_url: URL da API para enviar dados (opcional). Se None, roda standalone.
        """
        logger.info("=" * 60)
        logger.info("Inicializando BioFace AI - Versão Leve")
        logger.info("=" * 60)
        
        # Salva settings como atributo da classe
        self.settings = get_settings()
        
        # Cliente da API (opcional)
        self.api_client = None
        self.api_url = api_url or getattr(self.settings, 'api_url', None)
        self.api_loop = None
        if self.api_url:
            try:
                from src.api.client import APIClient
                self.api_client = APIClient(self.api_url)
                
                # Verifica se API está disponível
                if self.api_client.health_check():
                    logger.info(f"✓ Cliente da API configurado: {self.api_url}")
                    logger.info("✓ API está online e acessível")
                else:
                    logger.warning(f"API configurada mas não está acessível: {self.api_url}")
                    logger.warning("Pipeline continuará em modo standalone")
                    self.api_client = None
            except ImportError:
                logger.warning("Cliente da API não disponível (websockets não instalado?)")
                self.api_client = None
            except Exception as e:
                logger.warning(f"Erro ao configurar cliente da API: {e}")
                self.api_client = None
        
        # Inicializa componentes (sem EmotionClassifier)
        logger.info("Inicializando componentes...")
        
        self.camera = Camera()
        logger.info("✓ Câmera inicializada")
        
        self.face_detector = FaceDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_faces=1
        )
        logger.info("✓ Face Detector inicializado")
        
        self.face_processor = FaceProcessor()
        logger.info("✓ Face Processor inicializado")
        
        # Reconhecimento facial (Fase 2)
        self.face_recognizer = FaceRecognizer(embedding_size=128)
        logger.info("✓ Face Recognizer inicializado")
        
        # Classificação de emoções (Fase 3)
        # Escolhe classificador baseado na configuração
        emotion_type = self.settings.emotion_classifier_type.lower()
        
        if emotion_type == "deepface":
            try:
                from .ai.emotion_classifier_deepface import EmotionClassifierDeepFace
                self.emotion_classifier = EmotionClassifierDeepFace()
                logger.info("✓ Emotion Classifier (DeepFace) inicializado")
            except (ImportError, Exception) as e:
                logger.warning(
                    f"DeepFace não disponível ({e}), usando EmotionClassifierLight. "
                    "Execute: pip install deepface"
                )
                self.emotion_classifier = EmotionClassifierLight()
                logger.info("✓ Emotion Classifier (Light) inicializado")
        else:
            self.emotion_classifier = EmotionClassifierLight()
            logger.info("✓ Emotion Classifier (Light) inicializado")
        
        # Banco de dados (Fase 2)
        self.db = DatabaseRepository()
        logger.info("✓ Banco de dados inicializado")
        
        # Contadores
        self.frame_count = 0
        self.skip_counter = 0
        self.fps_start_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0
        
        # Sistema de estabilização temporal (evita oscilação)
        self.identification_history = []  # Histórico das últimas identificações
        self.history_size = 8  # Quantos frames manter no histórico (reduzido)
        self.consensus_threshold = 5  # Quantos frames precisam concordar para mudar (reduzido)
        self.min_confidence_to_show = 0.5  # Confiança mínima para mostrar nome (50% - mais permissivo)
        self.current_stable_id = None  # ID estável atual
        self.stable_name = None  # Nome estável atual
        self.stable_confidence = 0.0  # Confiança estável atual
        
        # Sistema de estabilização temporal para emoções (evita oscilação)
        self.emotion_history = []  # Histórico das últimas emoções
        self.emotion_history_size = 6  # Quantos frames manter no histórico de emoções
        self.emotion_consensus_threshold = 4  # Quantos frames precisam concordar para mudar emoção
        self.current_stable_emotion = None  # Emoção estável atual
        self.current_stable_emotion_pt = None  # Emoção estável em português
        self.current_stable_emotion_confidence = 0.0  # Confiança estável atual
        self._last_saved_emotion = None  # Última emoção salva (para evitar duplicatas)
        
        logger.info("=" * 60)
        logger.info("Pipeline leve inicializado!")
        logger.info("✓ Detecção facial: Ativa")
        logger.info("✓ Reconhecimento facial: Ativo")
        logger.info("✓ Classificação de emoções: Ativa (versão leve)")
        logger.info("=" * 60)
    
    def process_frame(self, frame):
        """
        Processa um frame (apenas detecção, sem emoção).
        
        Args:
            frame: Frame BGR da câmera
            
        Returns:
            tuple: (frame_annotated, results)
        """
        results = []
        
        # Detecta faces
        faces = self.face_detector.detect(frame)
        
        # Log ocasional para debug
        if len(faces) == 0 and self.frame_count % 60 == 0:
            logger.debug("Nenhuma face detectada no frame")
        
        # Processa cada face detectada (com identificação)
        for face in faces:
            bbox = face['bbox']
            landmarks = face['landmarks_2d']
            landmarks_3d = face.get('landmarks')  # Landmarks 3D completos (para emoções)
            confidence = face['confidence']
            
            # Gera embedding para identificação
            embedding = self.face_recognizer.generate_embedding_from_bbox(frame, bbox)
            
            # Tenta identificar a pessoa
            user_id = None
            user_name = None
            identification_confidence = 0.0
            
            if embedding is not None:
                # Busca no banco de dados
                # Usa threshold mais restritivo e validação de ambiguidade
                match = self.db.find_user_by_embedding(
                    embedding.tolist(),
                    threshold=self.settings.recognition_distance_threshold,
                    ambiguity_threshold=self.settings.recognition_ambiguity_threshold
                )
                
                # Log ocasional para debug
                if len(self.identification_history) % 60 == 0:
                    if match:
                        logger.debug(
                            f"Match encontrado: user_id={match['user_id']}, "
                            f"dist={match['distance']:.4f}"
                        )
                    else:
                        logger.debug("Nenhum match encontrado no banco")
                
                if match:
                    # Verifica se a distância está dentro do threshold
                    distance = match['distance']
                    identification_confidence = 1.0 - distance
                    
                    # Identifica se a distância estiver dentro do threshold
                    if distance <= self.settings.recognition_distance_threshold:
                        user_id = match['user_id']
                        
                        # Busca nome do usuário
                        user = self.db.get_user(user_id)
                        if user:
                            user_name = user.name or f"Usuario {user_id}"
                        
                        # Log da identificação
                        logger.info(
                            f"Face identificada: {user_name} (ID: {user_id}, "
                            f"dist={distance:.4f}, conf={identification_confidence:.2%})"
                        )
                    else:
                        # Distância muito alta - não identifica
                        user_id = None
                        user_name = None
                        identification_confidence = 0.0
                        logger.debug(f"Distancia muito alta ({distance:.4f} > {self.settings.recognition_distance_threshold})")
                else:
                    # Face desconhecida (find_user_by_embedding retornou None)
                    user_id = None
                    user_name = None
                    identification_confidence = 0.0
                    # Log apenas ocasionalmente para não poluir
                    if len(self.identification_history) % 30 == 0:
                        logger.debug(f"Face desconhecida (sem match no banco)")
                    if not self.settings.anonymous_mode:
                        # Cria usuário anônimo automaticamente (pode ser melhorado depois)
                        pass
                
                # Adiciona ao histórico para estabilização temporal
                self.identification_history.append({
                    'user_id': user_id,
                    'user_name': user_name,
                    'confidence': identification_confidence,
                    'distance': match['distance'] if match else float('inf')
                })
            else:
                # Sem embedding - adiciona entrada vazia ao histórico
                self.identification_history.append({
                    'user_id': None,
                    'user_name': None,
                    'confidence': 0.0,
                    'distance': float('inf')
                })
            
            # Mantém apenas os últimos N frames
            if len(self.identification_history) > self.history_size:
                self.identification_history.pop(0)
            
            # Aplica estabilização temporal (sempre, mesmo sem embedding)
            stable_user_id, stable_user_name, stable_conf = self._stabilize_identification()
            
            # Usa identificação estável no resultado
            user_id = stable_user_id
            user_name = stable_user_name
            identification_confidence = stable_conf
            
            # Classifica emoção (Fase 3)
            emotion = None
            emotion_pt = None
            emotion_confidence = 0.0
            
            # Processa face para emoção (a cada frame, mas pode otimizar depois)
            face_processed = self.face_processor.process_for_emotion(frame, bbox)
            if face_processed is not None:
                # Passa landmarks 3D para melhorar classificação (especialmente para Angry)
                emotion, emotion_confidence = self.emotion_classifier.predict(
                    face_processed, 
                    landmarks=landmarks_3d
                )
                emotion_pt = self.emotion_classifier.get_emotion_pt(emotion)
                
                # Adiciona ao histórico de emoções
                self.emotion_history.append({
                    'emotion': emotion,
                    'emotion_pt': emotion_pt,
                    'confidence': emotion_confidence
                })
                
                # Mantém apenas os últimos N frames
                if len(self.emotion_history) > self.emotion_history_size:
                    self.emotion_history.pop(0)
                
                # Aplica estabilização temporal de emoções
                stable_emotion, stable_emotion_pt, stable_emotion_conf = self._stabilize_emotion()
                
                # Usa emoção estável
                emotion = stable_emotion
                emotion_pt = stable_emotion_pt
                emotion_confidence = stable_emotion_conf
            
            result = {
                'bbox': bbox,
                'landmarks': landmarks,
                'confidence': confidence,
                'embedding': embedding.tolist() if embedding is not None else None,
                'user_id': user_id,
                'user_name': user_name,
                'identification_confidence': identification_confidence,
                'emotion': emotion,
                'emotion_pt': emotion_pt,
                'emotion_confidence': emotion_confidence
            }
            results.append(result)
        
        # Desenha anotações
        frame_annotated = self._draw_annotations(frame, results)
        
        # Log ocasional para debug
        if len(results) > 0 and self.frame_count % 30 == 0:
            result = results[0]
            logger.debug(
                f"Desenhando anotacoes: faces={len(results)}, "
                f"nome={result.get('user_name')}, "
                f"emocao={result.get('emotion_pt')}"
            )
        
        return frame_annotated, results
    
    def _draw_annotations(self, frame, results):
        """Desenha anotações no frame."""
        frame_copy = frame.copy()
        
        # Se não houver resultados, ainda mostra o frame (sem anotações)
        if not results:
            # Adiciona mensagem indicando que está aguardando face
            cv2.putText(
                frame_copy,
                "Aguardando face...",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )
        
        for result in results:
            bbox = result['bbox']
            confidence = result['confidence']
            
            x, y, w, h = bbox
            
            # Texto com identificação (usa nome estável)
            stable_name = result.get('user_name')
            stable_conf = result.get('identification_confidence', 0.0)
            
            # Emoção detectada
            emotion_pt = result.get('emotion_pt')
            emotion_conf = result.get('emotion_confidence', 0.0)
            
            if stable_name and stable_conf >= self.min_confidence_to_show:
                text = f"{stable_name}: {stable_conf:.0%}"
                color = (0, 255, 0)  # Verde para identificado
            else:
                text = f"DESCONHECIDO: {confidence:.0%}"
                color = (0, 165, 255)  # Laranja para desconhecido
            
            # Adiciona emoção ao texto se detectada
            if emotion_pt and emotion_conf >= self.emotion_classifier.confidence_threshold:
                text += f" | {emotion_pt}: {emotion_conf:.0%}"
            
            # Desenha bounding box
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
            
            # Calcula tamanho do texto
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            # Fundo para texto (maior para melhor visibilidade)
            cv2.rectangle(
                frame_copy,
                (x - 5, y - text_height - 15),
                (x + text_width + 5, y + 5),
                (0, 0, 0),
                -1
            )
            
            # Borda verde
            cv2.rectangle(
                frame_copy,
                (x - 5, y - text_height - 15),
                (x + text_width + 5, y + 5),
                color,
                2
            )
            
            # Texto
            cv2.putText(
                frame_copy,
                text,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
            # Desenha círculos nos cantos do retângulo para destacar
            corner_radius = 5
            cv2.circle(frame_copy, (x, y), corner_radius, color, -1)
            cv2.circle(frame_copy, (x + w, y), corner_radius, color, -1)
            cv2.circle(frame_copy, (x, y + h), corner_radius, color, -1)
            cv2.circle(frame_copy, (x + w, y + h), corner_radius, color, -1)
        
        # FPS
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(
            frame_copy,
            fps_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Contador
        frame_text = f"Frames: {self.frame_count}"
        cv2.putText(
            frame_copy,
            frame_text,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Aviso de versão leve
        warning_text = "LIGHT MODE - No Emotion Detection"
        cv2.putText(
            frame_copy,
            warning_text,
            (10, frame_copy.shape[0] - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 165, 255),
            1
        )
        
        # Instruções de como fechar (sempre visível)
        instruction_text = "Pressione 'Q' para fechar"
        cv2.putText(
            frame_copy,
            instruction_text,
            (10, frame_copy.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        
        # Fundo para instrução (para melhor visibilidade)
        (text_width, text_height), baseline = cv2.getTextSize(
            instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        cv2.rectangle(
            frame_copy,
            (5, frame_copy.shape[0] - text_height - 25),
            (15 + text_width, frame_copy.shape[0] - 5),
            (0, 0, 0),
            -1
        )
        cv2.putText(
            frame_copy,
            instruction_text,
            (10, frame_copy.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        return frame_copy
    
    def _stabilize_identification(self):
        """
        Estabiliza identificação usando histórico temporal.
        
        Evita oscilação entre nomes diferentes usando votação por maioria
        e requerendo consenso antes de mudar a identificação.
        
        Returns:
            tuple: (user_id, user_name, confidence) estáveis
        """
        if not self.identification_history:
            return None, None, 0.0
        
        # Conta votos por usuário no histórico recente
        votes = {}  # {user_id: {'count': int, 'total_confidence': float, 'min_distance': float}}
        
        for entry in self.identification_history:
            uid = entry['user_id']
            conf = entry['confidence']
            dist = entry.get('distance', float('inf'))
            
            if uid is not None and conf >= self.min_confidence_to_show:
                if uid not in votes:
                    votes[uid] = {
                        'count': 0,
                        'total_confidence': 0.0,
                        'min_distance': float('inf'),
                        'name': entry['user_name']
                    }
                
                votes[uid]['count'] += 1
                votes[uid]['total_confidence'] += conf
                votes[uid]['min_distance'] = min(votes[uid]['min_distance'], dist)
        
        if not votes:
            # Nenhuma identificação confiável no histórico
            self.current_stable_id = None
            self.stable_name = None
            self.stable_confidence = 0.0
            return None, None, 0.0
        
        # Encontra o usuário com mais votos
        best_user_id = max(votes.keys(), key=lambda uid: (
            votes[uid]['count'],  # Prioriza quem tem mais votos
            -votes[uid]['min_distance']  # Em caso de empate, menor distância
        ))
        
        best_vote = votes[best_user_id]
        consensus_count = best_vote['count']
        avg_confidence = best_vote['total_confidence'] / consensus_count
        
        # Só muda a identificação se houver consenso suficiente
        if consensus_count >= self.consensus_threshold:
            # Há consenso - pode mudar ou manter
            if best_user_id != self.current_stable_id:
                # Mudança de identificação - aceita pois já há consenso suficiente
                self.current_stable_id = best_user_id
                self.stable_name = best_vote['name']
                self.stable_confidence = avg_confidence
                logger.info(
                    f"Mudanca de identificacao: {self.stable_name} "
                    f"(conf={self.stable_confidence:.2f}, votos={consensus_count})"
                )
            else:
                # Mesmo usuário - apenas atualiza confiança
                self.stable_confidence = avg_confidence
        elif self.current_stable_id is not None:
            # Não há consenso suficiente, mas já temos uma identificação estável
            # Mantém a identificação atual se ainda aparecer no histórico
            if self.current_stable_id in votes:
                # Ainda aparece no histórico - mantém e atualiza confiança
                self.stable_confidence = votes[self.current_stable_id]['total_confidence'] / votes[self.current_stable_id]['count']
            else:
                # Não aparece mais no histórico - conta quantos frames sem aparecer
                # Só limpa se não aparecer por muitos frames consecutivos
                frames_without_stable = sum(
                    1 for entry in self.identification_history
                    if entry['user_id'] != self.current_stable_id
                )
                # Só limpa se não aparecer por mais de 50% do histórico
                if frames_without_stable >= len(self.identification_history) * 0.5:
                    logger.debug(
                        f"Limpando identificacao estavel: {self.stable_name} "
                        f"(nao aparece ha {frames_without_stable} frames)"
                    )
                    self.current_stable_id = None
                    self.stable_name = None
                    self.stable_confidence = 0.0
                # Caso contrário, mantém a identificação estável mesmo sem aparecer recentemente
        else:
            # Não há identificação estável ainda - espera consenso
            if consensus_count >= self.consensus_threshold:
                self.current_stable_id = best_user_id
                self.stable_name = best_vote['name']
                self.stable_confidence = avg_confidence
                logger.info(
                    f"Nova identificacao: {self.stable_name} "
                    f"(conf={self.stable_confidence:.2f}, votos={consensus_count})"
                )
        
        # Retorna identificação estável
        return self.current_stable_id, self.stable_name, self.stable_confidence
    
    def _stabilize_emotion(self):
        """
        Estabiliza emoção usando histórico temporal.
        
        Evita oscilação entre emoções diferentes usando votação por maioria.
        
        Returns:
            tuple: (emotion, emotion_pt, confidence) estáveis
        """
        if not self.emotion_history:
            return None, None, 0.0
        
        # Conta votos por emoção no histórico recente
        votes = {}  # {emotion: {'count': int, 'total_confidence': float}}
        
        for entry in self.emotion_history:
            emo = entry['emotion']
            conf = entry['confidence']
            
            if emo is not None and emo != "Unknown" and conf >= self.emotion_classifier.confidence_threshold:
                if emo not in votes:
                    votes[emo] = {
                        'count': 0,
                        'total_confidence': 0.0,
                        'emotion_pt': entry.get('emotion_pt', emo)
                    }
                
                votes[emo]['count'] += 1
                votes[emo]['total_confidence'] += conf
        
        if not votes:
            # Nenhuma emoção confiável no histórico
            self.current_stable_emotion = None
            self.current_stable_emotion_pt = None
            self.current_stable_emotion_confidence = 0.0
            return None, None, 0.0
        
        # Encontra a emoção com mais votos
        best_emotion = max(votes.keys(), key=lambda e: (
            votes[e]['count'],  # Prioriza quem tem mais votos
            votes[e]['total_confidence'] / votes[e]['count']  # Em caso de empate, maior confiança média
        ))
        
        best_vote = votes[best_emotion]
        consensus_count = best_vote['count']
        avg_confidence = best_vote['total_confidence'] / consensus_count
        
        # Só muda a emoção se houver consenso suficiente
        if consensus_count >= self.emotion_consensus_threshold:
            # Há consenso - pode mudar ou manter
            if best_emotion != self.current_stable_emotion:
                # Mudança de emoção - aceita pois já há consenso suficiente
                self.current_stable_emotion = best_emotion
                self.current_stable_emotion_pt = best_vote['emotion_pt']
                self.current_stable_emotion_confidence = avg_confidence
                logger.debug(
                    f"Mudanca de emocao: {self.current_stable_emotion_pt} "
                    f"(conf={self.current_stable_emotion_confidence:.2f}, votos={consensus_count})"
                )
            else:
                # Mesma emoção - apenas atualiza confiança
                self.current_stable_emotion_confidence = avg_confidence
        elif self.current_stable_emotion is not None:
            # Não há consenso suficiente, mas já temos uma emoção estável
            # Mantém a emoção atual se ainda aparecer no histórico
            if self.current_stable_emotion in votes:
                # Ainda aparece no histórico - mantém e atualiza confiança
                self.current_stable_emotion_confidence = votes[self.current_stable_emotion]['total_confidence'] / votes[self.current_stable_emotion]['count']
            else:
                # Não aparece mais no histórico - limpa após alguns frames
                frames_without_stable = sum(
                    1 for entry in self.emotion_history
                    if entry['emotion'] != self.current_stable_emotion
                )
                # Só limpa se não aparecer por mais de 50% do histórico
                if frames_without_stable >= len(self.emotion_history) * 0.5:
                    logger.debug(
                        f"Limpando emocao estavel: {self.current_stable_emotion_pt} "
                        f"(nao aparece ha {frames_without_stable} frames)"
                    )
                    self.current_stable_emotion = None
                    self.current_stable_emotion_pt = None
                    self.current_stable_emotion_confidence = 0.0
        else:
            # Não há emoção estável ainda - espera consenso
            if consensus_count >= self.emotion_consensus_threshold:
                self.current_stable_emotion = best_emotion
                self.current_stable_emotion_pt = best_vote['emotion_pt']
                self.current_stable_emotion_confidence = avg_confidence
                logger.debug(
                    f"Nova emocao: {self.current_stable_emotion_pt} "
                    f"(conf={self.current_stable_emotion_confidence:.2f}, votos={consensus_count})"
                )
        
        # Retorna emoção estável
        return self.current_stable_emotion, self.current_stable_emotion_pt, self.current_stable_emotion_confidence
    
    def update_fps(self):
        """Atualiza cálculo de FPS."""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self):
        """Executa o pipeline."""
        logger.info("Iniciando loop principal...")
        logger.info("Pressione 'q' ou 'Q' na janela para sair")
        logger.info("OU pressione Ctrl+C no terminal para sair")
        
        # Inicializa loop assíncrono para API (se necessário)
        if self.api_client:
            try:
                self.api_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.api_loop)
                # Conecta WebSocket em background
                self.api_loop.run_until_complete(self.api_client.connect_websocket("detections"))
                logger.info("✓ WebSocket conectado para envio de detecções")
            except Exception as e:
                logger.warning(f"Falha ao conectar WebSocket: {e}")
                self.api_client = None
        
        settings = get_settings()
        
        # Cria janela e garante que está visível
        window_name = "BioFace AI - Light"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        cv2.moveWindow(window_name, 100, 100)  # Move para posição visível
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 0)  # Não fica sempre no topo
        
        try:
            while True:
                try:
                    frame = self.camera.read()
                except CameraDisconnectedError as e:
                    logger.warning(f"{e.message}, tentando reconectar...")
                    if self.camera.reconnect(max_retries=3):
                        continue
                    else:
                        logger.error("Não foi possível reconectar à câmera. Encerrando...")
                        break
                except CameraReadError as e:
                    logger.warning(f"{e.message}, pulando frame...")
                    continue
                
                if frame is None:
                    continue
                
                # Frame skipping - processa apenas 1 frame a cada N
                self.skip_counter += 1
                should_process = (self.skip_counter >= self.settings.frame_skip)
                
                if should_process:
                    self.skip_counter = 0
                    self.frame_count += 1
                    
                    # Processa frame
                    frame_annotated, results = self.process_frame(frame)
                else:
                    # Não processa, mas usa o último frame processado (se existir)
                    if hasattr(self, '_last_annotated_frame'):
                        frame_annotated = self._last_annotated_frame
                        results = getattr(self, '_last_results', [])
                    else:
                        # Primeira vez - processa mesmo assim
                        self.frame_count += 1
                        frame_annotated, results = self.process_frame(frame)
                
                # Salva frame processado para usar nos frames skipped
                self._last_annotated_frame = frame_annotated
                self._last_results = results
                
                # Log e salva no banco (a cada 30 frames)
                if self.frame_count % 30 == 0:
                    logger.info(f"Frame {self.frame_count}: {len(results)} face(s) detectada(s)")
                    if len(results) > 0:
                        result = results[0]
                        logger.info(f"  -> Face detectada com confiança: {result['confidence']:.0%}")
                        
                        # Envia detecção para API (se conectado)
                        if self.api_client and self.api_loop:
                            try:
                                detection_data = {
                                    "user_id": result.get('user_id'),
                                    "user_name": result.get('user_name'),
                                    "emotion": result.get('emotion'),
                                    "emotion_confidence": result.get('emotion_confidence', 0.0),
                                    "confidence": result['confidence'],
                                    "bbox": result['bbox'],
                                    "frame_number": self.frame_count,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                                # Envia de forma não bloqueante
                                asyncio.run_coroutine_threadsafe(
                                    self.api_client.send_detection(detection_data),
                                    self.api_loop
                                )
                            except Exception as e:
                                logger.debug(f"Erro ao enviar detecção para API: {e}")
                        
                        # Atualiza identificação se encontrou match (salva novo embedding)
                        if result.get('user_id') and result.get('embedding'):
                            # Salva novo embedding para melhorar identificação futura
                            try:
                                self.db.save_embedding(
                                    user_id=result['user_id'],
                                    embedding=result['embedding'],
                                    confidence=result['confidence'],
                                    face_size=result['bbox'][2] * result['bbox'][3]
                                )
                                logger.debug(f"  -> Embedding atualizado para usuario {result['user_id']}")
                            except (DatabaseLockedError, DatabaseCorruptedError) as e:
                                logger.error(f"Erro crítico no banco ao salvar embedding: {e.message}")
                                # Tenta recuperar se corrompido
                                if isinstance(e, DatabaseCorruptedError):
                                    try:
                                        self.db.recover_from_backup()
                                        logger.info("Banco recuperado, tentando novamente...")
                                    except Exception as recover_error:
                                        logger.error(f"Falha ao recuperar banco: {recover_error}")
                            except Exception as e:
                                logger.debug(f"Erro ao atualizar embedding: {e}")
                        
                        # Salva emoção detectada (Fase 3) - apenas a emoção estável
                        # Salva apenas se a emoção estável mudou ou a cada 60 frames (evita spam)
                        stable_emotion = result.get('emotion')
                        stable_emotion_conf = result.get('emotion_confidence', 0.0)
                        
                        if (stable_emotion and 
                            stable_emotion != "Unknown" and 
                            stable_emotion_conf >= self.emotion_classifier.confidence_threshold and
                            (self.frame_count % 60 == 0 or  # Salva a cada 60 frames
                             stable_emotion != getattr(self, '_last_saved_emotion', None))):  # Ou se mudou
                            try:
                                self.db.save_emotion(
                                    user_id=result.get('user_id'),
                                    emotion=stable_emotion,
                                    confidence=stable_emotion_conf,
                                    frame_number=self.frame_count,
                                    extra_data={
                                        'bbox': result['bbox'],
                                        'landmarks_count': len(result.get('landmarks', []))
                                    }
                                )
                                self._last_saved_emotion = stable_emotion  # Marca como salva
                                logger.debug(
                                    f"  -> Emoção registrada: {result.get('emotion_pt', stable_emotion)} "
                                    f"({stable_emotion_conf:.2%})"
                                )
                                
                                # Envia emoção para API (se conectado)
                                if self.api_client and self.api_loop:
                                    try:
                                        emotion_data = {
                                            "user_id": result.get('user_id'),
                                            "emotion": stable_emotion,
                                            "confidence": stable_emotion_conf,
                                            "timestamp": datetime.utcnow().isoformat(),
                                            "frame_number": self.frame_count
                                        }
                                        # Envia de forma não bloqueante
                                        asyncio.run_coroutine_threadsafe(
                                            self.api_client.send_emotion(emotion_data),
                                            self.api_loop
                                        )
                                    except Exception as e:
                                        logger.debug(f"Erro ao enviar emoção para API: {e}")
                            except (DatabaseLockedError, DatabaseCorruptedError) as e:
                                logger.error(f"Erro crítico no banco ao salvar emoção: {e.message}")
                                # Tenta recuperar se corrompido
                                if isinstance(e, DatabaseCorruptedError):
                                    try:
                                        self.db.recover_from_backup()
                                        logger.info("Banco recuperado, tentando novamente...")
                                    except Exception as recover_error:
                                        logger.error(f"Falha ao recuperar banco: {recover_error}")
                            except Exception as e:
                                logger.debug(f"Erro ao salvar emoção: {e}")
                        
                        # NÃO cria usuários anônimos automaticamente (desabilitado)
                        # Isso estava criando muitos usuários e interferindo na identificação
                
                # Atualiza FPS
                self.update_fps()
                
                # Exibe frame com anotações
                # Garante que a janela está visível e redimensionada
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                
                # Log ocasional para debug
                if self.frame_count % 60 == 0:
                    logger.debug(
                        f"Exibindo frame {self.frame_count}: "
                        f"shape={frame_annotated.shape}, "
                        f"faces={len(results)}"
                    )
                
                cv2.imshow(window_name, frame_annotated)
                
                # Força atualização da janela (importante para Windows)
                cv2.waitKey(1)
                
                # Verifica tecla 'q' ou 'Q' para sair
                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), ord('Q'), 27]:  # 'q', 'Q' ou ESC
                    logger.info("Saindo...")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário (Ctrl+C)")
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Libera recursos."""
        logger.info("Limpando recursos...")
        
        # Desconecta WebSocket se conectado
        if hasattr(self, 'api_client') and self.api_client and hasattr(self, 'api_loop') and self.api_loop:
            try:
                self.api_loop.run_until_complete(self.api_client.disconnect_websocket())
                self.api_loop.close()
                logger.info("WebSocket desconectado")
            except Exception as e:
                logger.debug(f"Erro ao desconectar WebSocket: {e}")
        
        if hasattr(self, 'camera'):
            self.camera.release()
        
        if hasattr(self, 'face_detector'):
            self.face_detector.release()
        
        if hasattr(self, 'face_recognizer'):
            self.face_recognizer.release()
        
        cv2.destroyAllWindows()
        logger.info("Recursos liberados.")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="BioFace AI - Versão Leve (Sem TensorFlow)"
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=None,
        help='Índice da câmera'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help='Nível de logging'
    )
    
    parser.add_argument(
        '--api-url',
        type=str,
        default=None,
        help='URL da API para enviar dados (ex: http://localhost:8000). Se não fornecido, roda standalone.'
    )
    
    args = parser.parse_args()
    
    if args.log_level:
        setup_logger(log_level=args.log_level)
    
    try:
        pipeline = BioFacePipelineLight(api_url=args.api_url)
        pipeline.run()
    except (CameraNotOpenedError, DatabaseConnectionError) as e:
        logger.error(f"Erro crítico de inicialização: {e.message}")
        logger.error("Verifique se a câmera está conectada e o banco de dados está acessível")
        return 1
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


