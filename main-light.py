"""
Ponto de entrada para a versão leve do BioFace AI.

Não requer TensorFlow. Usa MediaPipe + ONNX para detecção facial e emoções.

Uso:
    python main-light.py
    python main-light.py --api-url http://localhost:8000
"""

from src.main_light import main

if __name__ == "__main__":
    exit(main())

