"""
Módulo de exceções customizadas do BioFace AI.

Define exceções específicas para diferentes cenários de erro,
facilitando tratamento e recuperação adequados.
"""

from typing import Optional


class BioFaceError(Exception):
    """
    Exceção base para todos os erros do BioFace AI.

    Todas as exceções customizadas herdam desta classe,
    permitindo captura genérica quando necessário.
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        """
        Inicializa a exceção.

        Args:
            message: Mensagem de erro descritiva
            details: Dicionário com detalhes adicionais do erro
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(
                f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ============================================
# EXCEÇÕES DE CÂMERA
# ============================================

class CameraError(BioFaceError):
    """Exceção base para erros relacionados à câmera."""


class CameraNotOpenedError(CameraError):
    """
    Exceção lançada quando não é possível abrir a câmera.

    Pode ocorrer quando:
    - Câmera não está conectada
    - Câmera está sendo usada por outro programa
    - Índice da câmera é inválido
    """

    def __init__(self, camera_index: int, message: Optional[str] = None):
        msg = message or f"Não foi possível abrir a câmera {camera_index}"
        super().__init__(msg, {"camera_index": camera_index})


class CameraDisconnectedError(CameraError):
    """
    Exceção lançada quando a câmera desconecta durante o uso.

    Diferente de CameraNotOpenedError, esta ocorre quando a câmera
    estava funcionando mas desconectou (ex: cabo USB desconectado).
    """

    def __init__(self, camera_index: int, message: Optional[str] = None):
        msg = message or f"Câmera {camera_index} desconectada durante o uso"
        super().__init__(msg, {"camera_index": camera_index})


class CameraReadError(CameraError):
    """
    Exceção lançada quando falha ao ler frame da câmera.

    Pode ocorrer quando:
    - Câmera trava
    - Buffer da câmera está cheio
    - Driver da câmera apresenta erro
    """

    def __init__(self, camera_index: int, message: Optional[str] = None):
        msg = message or f"Falha ao ler frame da câmera {camera_index}"
        super().__init__(msg, {"camera_index": camera_index})


# ============================================
# EXCEÇÕES DE BANCO DE DADOS
# ============================================

class DatabaseError(BioFaceError):
    """Exceção base para erros relacionados ao banco de dados."""


class DatabaseConnectionError(DatabaseError):
    """
    Exceção lançada quando não é possível conectar ao banco de dados.

    Pode ocorrer quando:
    - Arquivo do banco está bloqueado
    - Permissões insuficientes
    - Banco não existe e não pode ser criado
    """

    def __init__(self, database_url: str, message: Optional[str] = None):
        msg = message or f"Não foi possível conectar ao banco de dados: {database_url}"
        super().__init__(msg, {"database_url": database_url})


class DatabaseCorruptedError(DatabaseError):
    """
    Exceção lançada quando o banco de dados está corrompido.

    Pode ocorrer quando:
    - Arquivo do banco foi corrompido
    - Estrutura do banco está inválida
    - Dados estão inconsistentes
    """

    def __init__(self, database_url: str, message: Optional[str] = None):
        msg = message or f"Banco de dados corrompido: {database_url}"
        super().__init__(msg, {"database_url": database_url})


class DatabaseLockedError(DatabaseError):
    """
    Exceção lançada quando o banco de dados está bloqueado.

    Pode ocorrer quando:
    - Múltiplas conexões simultâneas
    - Transação não foi finalizada
    - Banco está em uso por outro processo
    """

    def __init__(self, database_url: str, message: Optional[str] = None):
        msg = message or f"Banco de dados bloqueado: {database_url}"
        super().__init__(msg, {"database_url": database_url})


# ============================================
# EXCEÇÕES DE RECONHECIMENTO FACIAL
# ============================================

class RecognitionError(BioFaceError):
    """Exceção base para erros relacionados ao reconhecimento facial."""


class EmbeddingGenerationError(RecognitionError):
    """
    Exceção lançada quando falha ao gerar embedding facial.

    Pode ocorrer quando:
    - Face não detectada na imagem
    - Imagem inválida ou corrompida
    - MediaPipe falha ao processar
    """

    def __init__(self, message: Optional[str] = None, details: Optional[dict] = None):
        msg = message or "Falha ao gerar embedding facial"
        super().__init__(msg, details or {})


class FaceNotDetectedError(RecognitionError):
    """
    Exceção lançada quando nenhuma face é detectada.

    Diferente de EmbeddingGenerationError, esta ocorre quando
    o sistema não consegue detectar uma face na imagem fornecida.
    """

    def __init__(self, message: Optional[str] = None):
        msg = message or "Nenhuma face detectada na imagem"
        super().__init__(msg)


class AmbiguousRecognitionError(RecognitionError):
    """
    Exceção lançada quando há ambiguidade na identificação.

    Ocorre quando múltiplos usuários têm embeddings muito similares,
    tornando impossível determinar qual é a pessoa correta.
    """

    def __init__(
        self,
        user_ids: list,
        distances: list,
        message: Optional[str] = None
    ):
        msg = message or f"Ambiguidade na identificação entre usuários: {user_ids}"
        details = {
            "user_ids": user_ids,
            "distances": distances,
            "count": len(user_ids)
        }
        super().__init__(msg, details)


# ============================================
# EXCEÇÕES DE CLASSIFICAÇÃO DE EMOÇÕES
# ============================================

class EmotionError(BioFaceError):
    """Exceção base para erros relacionados à classificação de emoções."""


class EmotionClassificationError(EmotionError):
    """
    Exceção lançada quando falha ao classificar emoção.

    Pode ocorrer quando:
    - Face inválida ou corrompida
    - Modelo não disponível (DeepFace)
    - Erro no processamento
    """

    def __init__(self, message: Optional[str] = None, details: Optional[dict] = None):
        msg = message or "Falha ao classificar emoção"
        super().__init__(msg, details or {})


class ModelNotAvailableError(EmotionError):
    """
    Exceção lançada quando modelo de emoção não está disponível.

    Ocorre quando:
    - DeepFace não está instalado
    - TensorFlow não está disponível
    - Modelo não foi baixado
    """

    def __init__(self, model_name: str, message: Optional[str] = None):
        msg = message or f"Modelo de emoção não disponível: {model_name}"
        super().__init__(msg, {"model_name": model_name})


# ============================================
# EXCEÇÕES DE CONFIGURAÇÃO
# ============================================

class ConfigurationError(BioFaceError):
    """Exceção base para erros relacionados à configuração."""


class InvalidConfigurationError(ConfigurationError):
    """
    Exceção lançada quando configuração é inválida.

    Pode ocorrer quando:
    - Valores fora do range esperado
    - Tipos incorretos
    - Configurações conflitantes
    """

    def __init__(self, config_key: str, config_value: any, message: Optional[str] = None):
        msg = message or f"Configuração inválida: {config_key}={config_value}"
        super().__init__(
            msg, {"config_key": config_key, "config_value": config_value})


# ============================================
# EXCEÇÕES DE VALIDAÇÃO
# ============================================

class ValidationError(BioFaceError):
    """Exceção base para erros de validação."""


class InvalidInputError(ValidationError):
    """
    Exceção lançada quando entrada é inválida.

    Pode ocorrer quando:
    - Parâmetros obrigatórios faltando
    - Tipos incorretos
    - Valores fora do range esperado
    """

    def __init__(self, field: str, value: any, message: Optional[str] = None):
        msg = message or f"Entrada inválida para campo '{field}': {value}"
        super().__init__(msg, {"field": field, "value": value})


# ============================================
# UTILITÁRIOS
# ============================================

def handle_camera_error(error: Exception, camera_index: int) -> CameraError:
    """
    Converte exceções genéricas de câmera em exceções customizadas.

    Args:
        error: Exceção original
        camera_index: Índice da câmera

    Returns:
        CameraError: Exceção customizada apropriada
    """
    error_str = str(error).lower()

    if "not opened" in error_str or "cannot open" in error_str:
        return CameraNotOpenedError(camera_index)
    elif "disconnected" in error_str or "device not found" in error_str:
        return CameraDisconnectedError(camera_index)
    elif "read" in error_str or "frame" in error_str:
        return CameraReadError(camera_index)
    else:
        return CameraError(f"Erro na câmera {camera_index}: {error}", {"original_error": str(error)})


def handle_database_error(error: Exception, database_url: str) -> DatabaseError:
    """
    Converte exceções genéricas de banco em exceções customizadas.

    Args:
        error: Exceção original
        database_url: URL do banco de dados

    Returns:
        DatabaseError: Exceção customizada apropriada
    """
    error_str = str(error).lower()

    if "locked" in error_str or "database is locked" in error_str:
        return DatabaseLockedError(database_url)
    elif "corrupt" in error_str or "malformed" in error_str:
        return DatabaseCorruptedError(database_url)
    elif "connection" in error_str or "cannot connect" in error_str:
        return DatabaseConnectionError(database_url)
    else:
        return DatabaseError(f"Erro no banco de dados: {error}", {"database_url": database_url, "original_error": str(error)})
