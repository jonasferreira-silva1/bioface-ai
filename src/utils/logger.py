"""
Módulo de logging do BioFace AI.

Sistema de logging estruturado usando Loguru para facilitar
debugging e monitoramento do sistema.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from .config import get_settings


def setup_logger(log_file: Optional[str] = None, log_level: Optional[str] = None) -> None:
    """
    Configura o sistema de logging do BioFace AI.
    
    Remove handlers padrão do Loguru e adiciona handlers customizados:
    - Console handler (colorido, formatado)
    - File handler (estruturado, rotativo)
    
    Args:
        log_file: Caminho do arquivo de log (opcional, usa config se None)
        log_level: Nível de logging (opcional, usa config se None)
        
    Example:
        >>> setup_logger()
        >>> logger.info("Sistema iniciado")
    """
    settings = get_settings()
    
    # Remove handler padrão do Loguru
    logger.remove()
    
    # Define nível de log
    level = log_level or settings.log_level
    
    # Define arquivo de log
    if log_file is None:
        log_file = settings.log_file
    
    # Cria diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Formato para console (colorido e legível)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Formato para arquivo (estruturado)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # Adiciona handler para console
    logger.add(
        sys.stdout,
        format=console_format,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Adiciona handler para arquivo
    logger.add(
        log_file,
        format=file_format,
        level=level,
        rotation="10 MB",  # Rotaciona quando atinge 10MB
        retention="7 days",  # Mantém logs por 7 dias
        compression="zip",  # Comprime logs antigos
        backtrace=True,
        diagnose=True
    )
    
    logger.info(f"Sistema de logging configurado: nível={level}, arquivo={log_file}")


def get_logger(name: Optional[str] = None):
    """
    Retorna uma instância do logger.
    
    Args:
        name: Nome do módulo (opcional, usa __name__ se None)
        
    Returns:
        Logger: Instância do logger do Loguru
        
    Example:
        >>> log = get_logger(__name__)
        >>> log.info("Mensagem de log")
    """
    if name:
        return logger.bind(name=name)
    return logger

