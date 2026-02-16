# 🤖 Modelos de IA - BioFace AI

Este documento explica como usar modelos pré-treinados no BioFace AI.

## 📦 Modelos de Emoção

O sistema suporta modelos de classificação de emoções. Por padrão, um modelo de demonstração é criado automaticamente, mas para melhor precisão, use modelos pré-treinados.

### Modelos Recomendados

#### 1. FER-2013 (Dataset padrão)
- **7 emoções**: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral
- **Formato**: TensorFlow/Keras (.h5)
- **Tamanho de entrada**: 48x48 grayscale

#### 2. FERPlus
- **Melhor precisão** que FER-2013
- **8 emoções** (inclui Contempt)
- Disponível em: [Hugging Face](https://huggingface.co/models?search=fer)

#### 3. AffectNet
- **Dataset maior** e mais diverso
- **8 emoções**
- Disponível em: [AffectNet](http://mohammadmahoor.com/affectnet/)

### Como Usar Modelos Pré-treinados

#### Opção 1: Baixar e Colocar Manualmente

1. Baixe um modelo pré-treinado (formato .h5 ou SavedModel)
2. Coloque em `models/emotion/`
3. Modifique `src/ai/emotion_classifier.py`:

```python
classifier = EmotionClassifier(
    model_path="models/emotion/fer_model.h5"
)
```

#### Opção 2: Usar Hugging Face

```python
from transformers import pipeline

# Carrega modelo do Hugging Face
emotion_pipeline = pipeline(
    "image-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)
```

#### Opção 3: Treinar Seu Próprio Modelo

1. Baixe o dataset FER-2013
2. Treine usando o código em `src/ai/emotion_classifier.py`
3. Salve o modelo treinado

## 🎭 Modelos de Reconhecimento Facial

Para a Fase 2 (Identificação), você precisará de modelos de embeddings faciais.

### Modelos Recomendados

#### 1. FaceNet
- **Embeddings de 128 dimensões**
- **Alta precisão**
- Disponível em: [FaceNet Paper](https://arxiv.org/abs/1503.03832)

#### 2. ArcFace
- **Melhor que FaceNet** em alguns benchmarks
- **Embeddings de 512 dimensões**
- Disponível em: [ArcFace GitHub](https://github.com/deepinsight/insightface)

#### 3. MediaPipe Face Embedder
- **Já integrado** com MediaPipe
- **Rápido** e otimizado
- Usa o mesmo pipeline de detecção

### Como Usar

```python
from src.ai.face_recognizer import FaceRecognizer

recognizer = FaceRecognizer(
    model_path="models/recognition/facenet.h5"
)
```

## 📥 Onde Baixar Modelos

### Repositórios Recomendados

1. **Hugging Face Model Hub**
   - URL: https://huggingface.co/models
   - Busque por: "emotion recognition", "facial expression"

2. **TensorFlow Hub**
   - URL: https://tfhub.dev/
   - Busque por: "face recognition", "emotion"

3. **GitHub**
   - Muitos projetos open-source disponíveis
   - Exemplo: https://github.com/atulapra/Emotion-detection

4. **Kaggle**
   - Competições e datasets com modelos
   - URL: https://www.kaggle.com/

## 🔧 Estrutura de Diretórios

```
models/
├── emotion/
│   ├── fer_model.h5          # Modelo FER-2013
│   └── ferplus_model.h5      # Modelo FERPlus
└── recognition/
    ├── facenet.h5            # Modelo FaceNet
    └── arcface.h5            # Modelo ArcFace
```

## ⚙️ Configuração

No arquivo `.env`, você pode configurar:

```env
# Caminho do modelo de emoção
EMOTION_MODEL_PATH=models/emotion/fer_model.h5

# Caminho do modelo de reconhecimento
RECOGNITION_MODEL_PATH=models/recognition/facenet.h5
```

## 📊 Comparação de Modelos

| Modelo | Precisão | Velocidade | Tamanho |
|--------|----------|------------|---------|
| FER-2013 (demo) | ~60% | Rápido | ~5MB |
| FERPlus | ~75% | Médio | ~15MB |
| AffectNet | ~80% | Lento | ~50MB |

## 🚀 Performance

### Otimizações

1. **Quantização**: Reduz tamanho e acelera
   ```python
   import tensorflow as tf
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   tflite_model = converter.convert()
   ```

2. **GPU**: TensorFlow detecta GPU automaticamente
   - NVIDIA: Requer CUDA
   - AMD: Requer ROCm

3. **Batch Processing**: Processa múltiplas faces de uma vez

## 📝 Notas Importantes

- **Licenças**: Verifique licenças dos modelos antes de usar comercialmente
- **Compatibilidade**: Modelos devem ser compatíveis com TensorFlow 2.x
- **Formato**: Prefira .h5 ou SavedModel para fácil carregamento
- **Tamanho**: Modelos grandes podem ser lentos em CPUs

## 🔗 Links Úteis

- [TensorFlow Model Zoo](https://github.com/tensorflow/models)
- [Hugging Face Models](https://huggingface.co/models)
- [Papers With Code](https://paperswithcode.com/)

---

**Dica**: Comece com modelos pequenos para testar, depois migre para modelos maiores conforme necessário.


