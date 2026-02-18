"""
Módulo de reconhecimento facial do BioFace AI.

Gera embeddings faciais para identificação de pessoas.
Usa MediaPipe Face Embedder (leve, sem TensorFlow).
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple
import mediapipe as mp

from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)


class FaceRecognizer:
    """
    Classe para reconhecimento facial usando embeddings.

    Gera vetores de características (embeddings) de faces detectadas
    para comparação e identificação de pessoas.

    Attributes:
        embedding_size: Tamanho do embedding (dimensões)
        mp_face_detection: MediaPipe Face Detection
        mp_face_mesh: MediaPipe Face Mesh

    Example:
        >>> recognizer = FaceRecognizer()
        >>> embedding = recognizer.generate_embedding(face_image)
        >>> if embedding is not None:
        ...     print(f"Embedding: {len(embedding)} dimensões")
    """

    def __init__(
        self,
        embedding_size: int = 128,
        min_detection_confidence: float = 0.5
    ):
        """
        Inicializa o reconhecedor facial.

        Args:
            embedding_size: Tamanho do embedding (128 ou 512)
            min_detection_confidence: Confiança mínima para detecção
        """
        logger.info("Inicializando Face Recognizer...")

        self.embedding_size = embedding_size
        self.min_detection_confidence = min_detection_confidence

        # MediaPipe Face Detection (para localizar faces)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0 = short-range, 1 = full-range
            min_detection_confidence=min_detection_confidence
        )

        # MediaPipe Face Mesh (para landmarks)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )

        logger.info(
            f"Face Recognizer inicializado (embedding_size={embedding_size})")

    def generate_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Gera embedding de uma face usando múltiplas características robustas.

        Combina landmarks, características de textura e histograma para criar
        um embedding mais robusto a variações de ângulo e iluminação.

        Args:
            face_image: Imagem da face (BGR, normalizada 160x160)

        Returns:
            np.ndarray: Embedding de 128 dimensões, ou None se falhar
        """
        try:
            # Converte BGR para RGB (MediaPipe usa RGB)
            rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Converte para escala de cinza para processamento
            gray_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

            # Processa com Face Mesh para obter landmarks
            results = self.face_mesh.process(rgb_image)

            if not results.multi_face_landmarks:
                raise FaceNotDetectedError("Nenhum landmark detectado para gerar embedding")

            # Extrai landmarks
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = []

            # Extrai apenas landmarks importantes (pontos-chave do rosto)
            # Índices dos pontos mais importantes: olhos, nariz, boca, contorno
            important_indices = set([
                10, 151, 9, 175,  # Contorno superior
                33, 7, 163, 144,  # Olhos
                1, 2, 5, 4,  # Nariz
                61, 291, 39, 181,  # Bochechas
                13, 14, 15, 16, 17, 18,  # Queixo
            ])
            
            # Extrai todos os landmarks, mas dá peso maior aos importantes
            for i, landmark in enumerate(face_landmarks.landmark):
                if i in important_indices:
                    # Landmarks importantes: peso 1.0
                    landmarks.extend([landmark.x, landmark.y, landmark.z])
                else:
                    # Landmarks menos importantes: peso 0.5
                    landmarks.extend([landmark.x * 0.5, landmark.y * 0.5, landmark.z * 0.5])

            landmarks_array = np.array(landmarks, dtype=np.float32)

            # Características de textura (histograma)
            hist = cv2.calcHist([gray_image], [0], None, [32], [0, 256])
            hist = hist.flatten() / (hist.sum() + 1e-8)  # Normaliza

            # Características de gradiente (detecta bordas/contornos)
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            gradient_features = np.histogram(gradient_magnitude.flatten(), bins=16, range=(0, 255))[0]
            gradient_features = gradient_features / (gradient_features.sum() + 1e-8)

            # Combina todas as características
            combined_features = np.concatenate([
                landmarks_array,
                hist,
                gradient_features
            ])

            # Reduz para o tamanho desejado usando PCA simples (média de blocos)
            if len(combined_features) >= self.embedding_size:
                # Divide em blocos e calcula média de cada bloco
                block_size = len(combined_features) // self.embedding_size
                embedding = []
                for i in range(self.embedding_size):
                    start_idx = i * block_size
                    end_idx = start_idx + block_size if i < self.embedding_size - 1 else len(combined_features)
                    embedding.append(np.mean(combined_features[start_idx:end_idx]))
                embedding = np.array(embedding, dtype=np.float32)
            else:
                # Interpola se tiver menos dimensões
                embedding = np.interp(
                    np.linspace(0, len(combined_features) - 1, self.embedding_size),
                    np.arange(len(combined_features)),
                    combined_features
                )

            # Normaliza o embedding (L2 normalization)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding.astype(np.float32)

        except FaceNotDetectedError:
            raise  # Re-lança exceção específica
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise EmbeddingGenerationError(
                f"Falha ao gerar embedding: {e}",
                {"error_type": type(e).__name__}
            )

    def generate_embedding_from_bbox(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """
        Gera embedding a partir de um bounding box no frame.

        Args:
            frame: Frame completo (BGR)
            bbox: (x, y, width, height) do bounding box

        Returns:
            np.ndarray: Embedding ou None
        """
        try:
            x, y, w, h = bbox

            # Extrai região da face
            face_roi = frame[y:y+h, x:x+w]

            if face_roi.size == 0:
                logger.warning("Região da face vazia")
                return None

            # Redimensiona para tamanho padrão (160x160)
            face_normalized = cv2.resize(face_roi, (160, 160))

            # Gera embedding
            return self.generate_embedding(face_normalized)

        except Exception as e:
            logger.error(f"Erro ao gerar embedding de bbox: {e}")
            return None

    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compara dois embeddings usando distância cosseno (melhor para embeddings normalizados).

        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding

        Returns:
            float: Distância cosseno (0.0 = idênticos, 1.0 = completamente diferentes)
        """
        try:
            # Garante que são arrays numpy
            emb1 = np.array(embedding1, dtype=np.float32)
            emb2 = np.array(embedding2, dtype=np.float32)

            # Normaliza
            emb1 = emb1 / (np.linalg.norm(emb1) + 1e-8)
            emb2 = emb2 / (np.linalg.norm(emb2) + 1e-8)

            # Calcula distância cosseno (1 - similaridade cosseno)
            # Similaridade cosseno = produto escalar de vetores normalizados
            cosine_similarity = np.dot(emb1, emb2)
            cosine_distance = 1.0 - cosine_similarity

            return float(cosine_distance)

        except Exception as e:
            logger.error(f"Erro ao comparar embeddings: {e}")
            return float('inf')

    def release(self):
        """Libera recursos."""
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        logger.info("Face Recognizer liberado")
