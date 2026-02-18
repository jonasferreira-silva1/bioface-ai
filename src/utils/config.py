"""
Módulo de configuração do BioFace AI.

Este módulo gerencia todas as configurações do sistema através de variáveis
de ambiente e arquivo .env. Usa Pydantic para validação e type safety.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Classe de configurações do sistema.
    
    Todas as configurações são carregadas de variáveis de ambiente ou
    do arquivo .env. Valores padrão são fornecidos para desenvolvimento.
    """
    
    # ============================================
    # CONFIGURAÇÕES DE CÂMERA
    # ============================================
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
    """Índice da câmera a ser usada (0 = primeira câmera)"""
    
    camera_width: int = int(os.getenv("CAMERA_WIDTH", "640"))
    """Largura do frame de vídeo em pixels"""
    
    camera_height: int = int(os.getenv("CAMERA_HEIGHT", "480"))
    """Altura do frame de vídeo em pixels"""
    
    fps_target: int = int(os.getenv("FPS_TARGET", "30"))
    """FPS alvo para captura de vídeo"""
    
    # ============================================
    # CONFIGURAÇÕES DE PROCESSAMENTO
    # ============================================
    frame_skip: int = int(os.getenv("FRAME_SKIP", "2"))
    """
    Processar apenas 1 frame a cada N frames.
    Exemplo: frame_skip=2 significa processar 1 frame a cada 2 frames.
    Isso melhora a performance em tempo real.
    """
    
    face_size_emotion: int = int(os.getenv("FACE_SIZE_EMOTION", "48"))
    """Tamanho da face normalizada para classificação de emoção (48x48)"""
    
    face_size_recognition: int = int(os.getenv("FACE_SIZE_RECOGNITION", "160"))
    """Tamanho da face normalizada para reconhecimento facial (160x160)"""
    
    # ============================================
    # CONFIGURAÇÕES DE IA
    # ============================================
    emotion_confidence_threshold: float = float(
        os.getenv("EMOTION_CONFIDENCE_THRESHOLD", "0.5")
    )
    """Confiança mínima para considerar uma emoção válida (0.0 a 1.0)"""
    
    emotion_classifier_type: str = os.getenv("EMOTION_CLASSIFIER_TYPE", "light")
    """
    Tipo de classificador de emoções a usar:
    - 'light': EmotionClassifierLight (heurísticas, rápido, menos preciso)
    - 'deepface': EmotionClassifierDeepFace (deep learning, mais preciso, requer DeepFace)
    """
    
    recognition_distance_threshold: float = float(
        os.getenv("RECOGNITION_DISTANCE_THRESHOLD", "0.35")
    )
    """Distância cosseno máxima para considerar faces como a mesma pessoa (0.0-1.0). 
    Usa distância cosseno: 0.0 = idêntico, 1.0 = completamente diferente.
    Valores menores = mais restritivo. Recomendado: 0.25-0.35 para maior precisão"""
    
    recognition_ambiguity_threshold: float = float(
        os.getenv("RECOGNITION_AMBIGUITY_THRESHOLD", "0.03")
    )
    """Diferença absoluta mínima entre melhor e segundo melhor match para evitar ambiguidade (0.0-1.0).
    Também considera diferença relativa (< 20%). Valores menores = mais permissivo.
    Recomendado: 0.02-0.05"""
    
    # ============================================
    # CONFIGURAÇÕES DE BANCO DE DADOS
    # ============================================
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./bioface.db"
    )
    """URL de conexão com o banco de dados"""
    
    # ============================================
    # CONFIGURAÇÕES DE SEGURANÇA
    # ============================================
    anonymous_mode: bool = os.getenv("ANONYMOUS_MODE", "false").lower() == "true"
    """
    Modo anônimo: se True, não identifica pessoas, apenas emoções.
    Útil para conformidade com LGPD.
    """
    
    encrypt_embeddings: bool = os.getenv("ENCRYPT_EMBEDDINGS", "true").lower() == "true"
    """Se True, criptografa embeddings antes de salvar no banco"""
    
    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))
    """Dias para manter dados antes de expirar (0 = sem expiração)"""
    
    # ============================================
    # CONFIGURAÇÕES DE LOGGING
    # ============================================
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    """Nível de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL"""
    
    log_file: str = os.getenv("LOG_FILE", "logs/bioface.log")
    """Caminho do arquivo de log"""
    
    # ============================================
    # CONFIGURAÇÕES DE API (para fases futuras)
    # ============================================
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    """Host do servidor API"""
    
    api_port: int = int(os.getenv("API_PORT", "8000"))
    """Porta do servidor API"""
    
    api_reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    """Se True, recarrega automaticamente em desenvolvimento"""
    
    class Config:
        """Configuração do Pydantic"""
        case_sensitive = False
        env_file = ".env"
        
        # API (opcional)
        api_url: Optional[str] = os.getenv("API_URL", None)
        """URL da API para enviar dados (ex: http://localhost:8000). Se None, roda standalone."""


# Instância global de configurações
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retorna a instância global de configurações (singleton).
    
    Returns:
        Settings: Instância de configurações do sistema
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.camera_index)
        0
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


