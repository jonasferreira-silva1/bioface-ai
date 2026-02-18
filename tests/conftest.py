"""
Configuração do Pytest para testes do BioFace AI.

Define fixtures compartilhadas e configurações globais.
"""

import pytest
import sys
from pathlib import Path

# Adiciona diretório raiz ao path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Configurações do Pytest
pytest_plugins = []


@pytest.fixture
def temp_database(tmp_path):
    """
    Cria um banco de dados temporário para testes.

    Returns:
        str: Caminho do banco de dados temporário
    """
    db_path = tmp_path / "test_bioface.db"
    return f"sqlite:///{db_path}"


@pytest.fixture
def sample_face_image():
    """
    Cria uma imagem de face de exemplo para testes.

    Returns:
        np.ndarray: Imagem de face (160x160, BGR)
    """
    import numpy as np
    import cv2

    # Cria imagem sintética de face
    face = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)

    # Adiciona alguns padrões que simulam uma face
    cv2.rectangle(face, (50, 50), (110, 80), (200, 180, 150), -1)  # Rosto
    cv2.circle(face, (70, 65), 5, (0, 0, 0), -1)  # Olho esquerdo
    cv2.circle(face, (90, 65), 5, (0, 0, 0), -1)  # Olho direito
    cv2.ellipse(face, (80, 90), (15, 8), 0, 0, 180, (100, 50, 50), 2)  # Boca

    return face


@pytest.fixture
def sample_embedding():
    """
    Cria um embedding de exemplo para testes.

    Returns:
        np.ndarray: Embedding de 128 dimensões
    """
    import numpy as np
    embedding = np.random.rand(128).astype(np.float32)
    # Normaliza
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    return embedding
