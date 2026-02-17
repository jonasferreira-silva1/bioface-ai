# 🎭 Como Usar DeepFace para Detecção de Emoções

**Data:** 2026-02-17  
**Status:** Implementado ✅

---

## 📦 Instalação

### 1. Instalar DeepFace

```bash
pip install deepface
```

Ou atualize o `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Verificar Instalação

```python
from deepface import DeepFace
print("DeepFace instalado com sucesso!")
```

---

## ⚙️ Configuração

### Opção 1: Variável de Ambiente (Recomendado)

Crie ou edite o arquivo `.env` na raiz do projeto:

```env
# Usar DeepFace para classificação de emoções
EMOTION_CLASSIFIER_TYPE=deepface

# Threshold de confiança (opcional)
EMOTION_CONFIDENCE_THRESHOLD=0.5
```

### Opção 2: Código

O sistema detecta automaticamente se DeepFace está disponível. Se não estiver, usa `EmotionClassifierLight` como fallback.

---

## 🚀 Uso

### Executar com DeepFace

```bash
# Com variável de ambiente
export EMOTION_CLASSIFIER_TYPE=deepface
python main-light.py

# Ou no Windows
set EMOTION_CLASSIFIER_TYPE=deepface
python main-light.py
```

### Executar com Classificador Leve (padrão)

```bash
# Não precisa fazer nada, já é o padrão
python main-light.py
```

---

## 📊 Comparação

| Característica | Light (Heurísticas) | DeepFace |
|----------------|---------------------|----------|
| **Precisão** | ~50-60% | ~70-80% |
| **Velocidade** | ⚡⚡⚡ Muito rápido | ⚡⚡ Rápido |
| **Dependências** | Nenhuma extra | DeepFace + TensorFlow |
| **Emoções** | 5 (Happy, Sad, Angry, Surprise, Neutral) | 7 (inclui Fear, Disgust) |
| **Offline** | ✅ | ✅ |

---

## 🎯 Emoções Detectadas

### DeepFace detecta 7 emoções:

1. **Happy** (Feliz)
2. **Sad** (Triste)
3. **Angry** (Raiva)
4. **Surprise** (Surpresa)
5. **Fear** (Medo) - *novo*
6. **Disgust** (Nojo) - *novo*
7. **Neutral** (Neutro)

### Mapeamento para Compatibilidade

O sistema mapeia automaticamente as 7 emoções do DeepFace para as 5 do classificador leve:
- `Fear` → `Surprise`
- `Disgust` → `Neutral`

---

## 🔧 Ajustes

### Threshold de Confiança

Ajuste no `.env`:

```env
# Mais restritivo (só mostra emoções muito confiantes)
EMOTION_CONFIDENCE_THRESHOLD=0.7

# Mais permissivo (mostra mais emoções)
EMOTION_CONFIDENCE_THRESHOLD=0.3
```

### Backend do DeepFace

Por padrão, usa `opencv` (mais rápido). Você pode mudar no código:

```python
classifier = EmotionClassifierDeepFace(backend="mtcnn")  # Mais preciso, mais lento
```

Backends disponíveis:
- `opencv` - Mais rápido (padrão)
- `ssd` - Balanceado
- `dlib` - Mais preciso, mais lento
- `mtcnn` - Muito preciso, muito lento
- `retinaface` - Mais preciso, mais lento

---

## 🐛 Troubleshooting

### Erro: "DeepFace não está instalado"

```bash
pip install deepface
```

### Erro: "TensorFlow não encontrado"

DeepFace requer TensorFlow. Instale:

```bash
pip install tensorflow
```

### Performance Lenta

1. Use `backend="opencv"` (padrão)
2. Aumente `FRAME_SKIP` no `.env`:
   ```env
   FRAME_SKIP=3  # Processa 1 frame a cada 3
   ```

### Primeira Execução Lenta

Na primeira execução, DeepFace baixa modelos (~100MB). Isso acontece apenas uma vez.

---

## 📝 Exemplo de Código

```python
from src.ai import EmotionClassifierDeepFace
import cv2

# Inicializa classificador
classifier = EmotionClassifierDeepFace(
    confidence_threshold=0.5,
    backend="opencv"
)

# Carrega face
face = cv2.imread("face.jpg")

# Classifica emoção
emotion, confidence = classifier.predict(face)
emotion_pt = classifier.get_emotion_pt(emotion)

print(f"Emoção: {emotion_pt} ({confidence:.2%})")

# Libera recursos
classifier.release()
```

---

## ✅ Status

**Implementação:** ✅ Completa  
**Testes:** Pronto para testar  
**Documentação:** ✅ Completa

---

**Última atualização:** 2026-02-17

