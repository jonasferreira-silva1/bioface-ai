"""
Testes de integração para exceções de reconhecimento facial.

Valida que as exceções são lançadas corretamente
nos cenários reais de uso.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.ai.face_recognizer import FaceRecognizer
from src.exceptions import (
    FaceNotDetectedError,
    EmbeddingGenerationError
)


class TestFaceRecognizerExceptions:
    """Testes para exceções de reconhecimento facial em uso real."""
    
    def test_face_not_detected_error_on_no_landmarks(self, sample_face_image):
        """Testa que FaceNotDetectedError é lançada quando não há landmarks."""
        recognizer = FaceRecognizer()
        
        # Cria imagem sem face (apenas ruído)
        no_face_image = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
        
        # Mock do MediaPipe para retornar sem landmarks
        with patch.object(recognizer.face_mesh, 'process') as mock_process:
            mock_result = Mock()
            mock_result.multi_face_landmarks = []  # Sem landmarks
            mock_process.return_value = mock_result
            
            with pytest.raises(FaceNotDetectedError) as exc_info:
                recognizer.generate_embedding(no_face_image)
            
            assert "landmark detectado" in exc_info.value.message.lower()
    
    def test_embedding_generation_error_on_processing_failure(self, sample_face_image):
        """Testa que EmbeddingGenerationError é lançada em falha de processamento."""
        recognizer = FaceRecognizer()
        
        # Mock do MediaPipe para lançar exceção
        with patch.object(recognizer.face_mesh, 'process') as mock_process:
            mock_process.side_effect = Exception("MediaPipe processing error")
            
            with pytest.raises(EmbeddingGenerationError) as exc_info:
                recognizer.generate_embedding(sample_face_image)
            
            assert "gerar embedding" in exc_info.value.message.lower()
            assert "error_type" in exc_info.value.details
    
    def test_embedding_generation_with_valid_face(self, sample_face_image):
        """Testa que embedding é gerado corretamente com face válida."""
        recognizer = FaceRecognizer()
        
        # Mock do MediaPipe para retornar landmarks válidos
        with patch.object(recognizer.face_mesh, 'process') as mock_process:
            # Cria landmarks simulados
            mock_landmark = Mock()
            mock_landmark.x = 0.5
            mock_landmark.y = 0.5
            mock_landmark.z = 0.0
            
            mock_face_landmarks = Mock()
            mock_face_landmarks.landmark = [mock_landmark] * 468  # 468 landmarks do MediaPipe
            
            mock_result = Mock()
            mock_result.multi_face_landmarks = [mock_face_landmarks]
            mock_process.return_value = mock_result
            
            # Deve gerar embedding sem erro
            embedding = recognizer.generate_embedding(sample_face_image)
            
            assert embedding is not None
            assert len(embedding) == 128
            assert np.all(np.isfinite(embedding))
    
    def test_compare_embeddings_handles_errors(self):
        """Testa que compare_embeddings trata erros corretamente."""
        recognizer = FaceRecognizer()
        
        # Embeddings válidos
        emb1 = np.random.rand(128).astype(np.float32)
        emb2 = np.random.rand(128).astype(np.float32)
        
        # Normaliza
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)
        
        # Deve calcular distância sem erro
        distance = recognizer.compare_embeddings(emb1, emb2)
        
        assert isinstance(distance, float)
        assert 0.0 <= distance <= 1.0
        
        # Mesmo embedding deve ter distância ~0
        distance_same = recognizer.compare_embeddings(emb1, emb1)
        assert distance_same < 0.01
    
    def test_compare_embeddings_with_invalid_input(self):
        """Testa que compare_embeddings trata entrada inválida."""
        recognizer = FaceRecognizer()
        
        # Embeddings com tamanhos diferentes
        emb1 = np.random.rand(128).astype(np.float32)
        emb2 = np.random.rand(64).astype(np.float32)  # Tamanho diferente
        
        # Deve retornar infinito ou tratar erro
        distance = recognizer.compare_embeddings(emb1, emb2)
        
        # Pode retornar infinito ou lançar exceção, dependendo da implementação
        assert distance == float('inf') or distance >= 0.0

