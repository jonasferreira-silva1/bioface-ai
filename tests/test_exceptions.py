"""
Testes unitários para exceções customizadas do BioFace AI.

Valida que todas as exceções funcionam corretamente e têm
as propriedades esperadas.
"""

import pytest
from src.exceptions import (
    BioFaceError,
    CameraError,
    CameraNotOpenedError,
    CameraDisconnectedError,
    CameraReadError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseCorruptedError,
    DatabaseLockedError,
    RecognitionError,
    EmbeddingGenerationError,
    FaceNotDetectedError,
    AmbiguousRecognitionError,
    EmotionError,
    EmotionClassificationError,
    ModelNotAvailableError,
    ConfigurationError,
    InvalidConfigurationError,
    ValidationError,
    InvalidInputError,
    handle_camera_error,
    handle_database_error
)


class TestBioFaceError:
    """Testes para a exceção base BioFaceError."""
    
    def test_bioface_error_basic(self):
        """Testa criação básica de BioFaceError."""
        error = BioFaceError("Mensagem de erro")
        assert str(error) == "Mensagem de erro"
        assert error.message == "Mensagem de erro"
        assert error.details == {}
    
    def test_bioface_error_with_details(self):
        """Testa BioFaceError com detalhes adicionais."""
        details = {"key1": "value1", "key2": 123}
        error = BioFaceError("Mensagem", details=details)
        assert error.message == "Mensagem"
        assert error.details == details
        assert "key1=value1" in str(error)
        assert "key2=123" in str(error)


class TestCameraErrors:
    """Testes para exceções relacionadas à câmera."""
    
    def test_camera_error_inheritance(self):
        """Testa que CameraError herda de BioFaceError."""
        error = CameraError("Erro de câmera")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, CameraError)
    
    def test_camera_not_opened_error(self):
        """Testa CameraNotOpenedError."""
        camera_index = 0
        error = CameraNotOpenedError(camera_index)
        
        assert isinstance(error, CameraError)
        assert str(camera_index) in error.message
        assert error.details["camera_index"] == camera_index
    
    def test_camera_not_opened_error_custom_message(self):
        """Testa CameraNotOpenedError com mensagem customizada."""
        error = CameraNotOpenedError(1, "Câmera USB desconectada")
        assert error.message == "Câmera USB desconectada"
        assert error.details["camera_index"] == 1
    
    def test_camera_disconnected_error(self):
        """Testa CameraDisconnectedError."""
        camera_index = 2
        error = CameraDisconnectedError(camera_index)
        
        assert isinstance(error, CameraError)
        assert "desconectada" in error.message.lower()
        assert error.details["camera_index"] == camera_index
    
    def test_camera_read_error(self):
        """Testa CameraReadError."""
        camera_index = 0
        error = CameraReadError(camera_index)
        
        assert isinstance(error, CameraError)
        assert "ler frame" in error.message.lower()
        assert error.details["camera_index"] == camera_index


class TestDatabaseErrors:
    """Testes para exceções relacionadas ao banco de dados."""
    
    def test_database_error_inheritance(self):
        """Testa que DatabaseError herda de BioFaceError."""
        error = DatabaseError("Erro de banco")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, DatabaseError)
    
    def test_database_connection_error(self):
        """Testa DatabaseConnectionError."""
        db_url = "sqlite:///test.db"
        error = DatabaseConnectionError(db_url)
        
        assert isinstance(error, DatabaseError)
        assert db_url in error.message
        assert error.details["database_url"] == db_url
    
    def test_database_corrupted_error(self):
        """Testa DatabaseCorruptedError."""
        db_url = "sqlite:///corrupted.db"
        error = DatabaseCorruptedError(db_url)
        
        assert isinstance(error, DatabaseError)
        assert "corrompido" in error.message.lower()
        assert error.details["database_url"] == db_url
    
    def test_database_locked_error(self):
        """Testa DatabaseLockedError."""
        db_url = "sqlite:///locked.db"
        error = DatabaseLockedError(db_url)
        
        assert isinstance(error, DatabaseError)
        assert "bloqueado" in error.message.lower()
        assert error.details["database_url"] == db_url


class TestRecognitionErrors:
    """Testes para exceções relacionadas ao reconhecimento facial."""
    
    def test_recognition_error_inheritance(self):
        """Testa que RecognitionError herda de BioFaceError."""
        error = RecognitionError("Erro de reconhecimento")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, RecognitionError)
    
    def test_face_not_detected_error(self):
        """Testa FaceNotDetectedError."""
        error = FaceNotDetectedError()
        
        assert isinstance(error, RecognitionError)
        assert "face detectada" in error.message.lower()
    
    def test_face_not_detected_error_custom_message(self):
        """Testa FaceNotDetectedError com mensagem customizada."""
        error = FaceNotDetectedError("Nenhuma face encontrada na imagem")
        assert error.message == "Nenhuma face encontrada na imagem"
    
    def test_embedding_generation_error(self):
        """Testa EmbeddingGenerationError."""
        error = EmbeddingGenerationError()
        
        assert isinstance(error, RecognitionError)
        assert "gerar embedding" in error.message.lower()
    
    def test_embedding_generation_error_with_details(self):
        """Testa EmbeddingGenerationError com detalhes."""
        details = {"error_type": "MediaPipeError", "face_size": (160, 160)}
        error = EmbeddingGenerationError("Falha no MediaPipe", details=details)
        
        assert error.message == "Falha no MediaPipe"
        assert error.details == details
    
    def test_ambiguous_recognition_error(self):
        """Testa AmbiguousRecognitionError."""
        user_ids = [1, 2, 3]
        distances = [0.25, 0.26, 0.27]
        error = AmbiguousRecognitionError(user_ids, distances)
        
        assert isinstance(error, RecognitionError)
        assert "ambiguidade" in error.message.lower()
        assert error.details["user_ids"] == user_ids
        assert error.details["distances"] == distances
        assert error.details["count"] == 3


class TestEmotionErrors:
    """Testes para exceções relacionadas à classificação de emoções."""
    
    def test_emotion_error_inheritance(self):
        """Testa que EmotionError herda de BioFaceError."""
        error = EmotionError("Erro de emoção")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, EmotionError)
    
    def test_emotion_classification_error(self):
        """Testa EmotionClassificationError."""
        error = EmotionClassificationError()
        
        assert isinstance(error, EmotionError)
        assert "classificar emoção" in error.message.lower()
    
    def test_model_not_available_error(self):
        """Testa ModelNotAvailableError."""
        model_name = "DeepFace"
        error = ModelNotAvailableError(model_name)
        
        assert isinstance(error, EmotionError)
        assert model_name in error.message
        assert error.details["model_name"] == model_name


class TestConfigurationErrors:
    """Testes para exceções relacionadas à configuração."""
    
    def test_configuration_error_inheritance(self):
        """Testa que ConfigurationError herda de BioFaceError."""
        error = ConfigurationError("Erro de configuração")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, ConfigurationError)
    
    def test_invalid_configuration_error(self):
        """Testa InvalidConfigurationError."""
        config_key = "threshold"
        config_value = -1.0
        error = InvalidConfigurationError(config_key, config_value)
        
        assert isinstance(error, ConfigurationError)
        assert config_key in error.message
        assert error.details["config_key"] == config_key
        assert error.details["config_value"] == config_value


class TestValidationErrors:
    """Testes para exceções relacionadas à validação."""
    
    def test_validation_error_inheritance(self):
        """Testa que ValidationError herda de BioFaceError."""
        error = ValidationError("Erro de validação")
        assert isinstance(error, BioFaceError)
        assert isinstance(error, ValidationError)
    
    def test_invalid_input_error(self):
        """Testa InvalidInputError."""
        field = "user_id"
        value = None
        error = InvalidInputError(field, value)
        
        assert isinstance(error, ValidationError)
        assert field in error.message
        assert error.details["field"] == field
        assert error.details["value"] == value


class TestErrorHandlers:
    """Testes para funções utilitárias de tratamento de erros."""
    
    def test_handle_camera_error_not_opened(self):
        """Testa handle_camera_error para câmera não aberta."""
        original_error = Exception("Cannot open camera")
        error = handle_camera_error(original_error, camera_index=0)
        
        assert isinstance(error, CameraNotOpenedError)
        assert error.details["camera_index"] == 0
    
    def test_handle_camera_error_disconnected(self):
        """Testa handle_camera_error para câmera desconectada."""
        original_error = Exception("Device disconnected")
        error = handle_camera_error(original_error, camera_index=1)
        
        assert isinstance(error, CameraDisconnectedError)
        assert error.details["camera_index"] == 1
    
    def test_handle_camera_error_read(self):
        """Testa handle_camera_error para erro de leitura."""
        original_error = Exception("Failed to read frame")
        error = handle_camera_error(original_error, camera_index=2)
        
        assert isinstance(error, CameraReadError)
        assert error.details["camera_index"] == 2
    
    def test_handle_camera_error_generic(self):
        """Testa handle_camera_error para erro genérico."""
        original_error = Exception("Unknown error")
        error = handle_camera_error(original_error, camera_index=0)
        
        assert isinstance(error, CameraError)
        assert "original_error" in error.details
    
    def test_handle_database_error_locked(self):
        """Testa handle_database_error para banco bloqueado."""
        original_error = Exception("database is locked")
        db_url = "sqlite:///test.db"
        error = handle_database_error(original_error, db_url)
        
        assert isinstance(error, DatabaseLockedError)
        assert error.details["database_url"] == db_url
    
    def test_handle_database_error_corrupted(self):
        """Testa handle_database_error para banco corrompido."""
        original_error = Exception("database disk image is malformed")
        db_url = "sqlite:///test.db"
        error = handle_database_error(original_error, db_url)
        
        assert isinstance(error, DatabaseCorruptedError)
        assert error.details["database_url"] == db_url
    
    def test_handle_database_error_connection(self):
        """Testa handle_database_error para erro de conexão."""
        original_error = Exception("Cannot connect to database")
        db_url = "sqlite:///test.db"
        error = handle_database_error(original_error, db_url)
        
        assert isinstance(error, DatabaseConnectionError)
        assert error.details["database_url"] == db_url
    
    def test_handle_database_error_generic(self):
        """Testa handle_database_error para erro genérico."""
        original_error = Exception("Unknown database error")
        db_url = "sqlite:///test.db"
        error = handle_database_error(original_error, db_url)
        
        assert isinstance(error, DatabaseError)
        assert "original_error" in error.details

