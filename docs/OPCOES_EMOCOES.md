# 🎭 Opções para Melhorar Detecção de Emoções

**Data:** 2026-02-17  
**Status:** Análise de alternativas

---

## 📊 Situação Atual

Atualmente, o sistema usa **heurísticas baseadas em landmarks** do MediaPipe:
- ✅ Funciona sem dependências pesadas
- ✅ Rápido e leve
- ❌ Precisão limitada (especialmente para "Angry")
- ❌ Depende de regras manuais

---

## 🎯 Opções Disponíveis

### 1. **DeepFace** (Recomendado) ⭐

**Vantagens:**
- ✅ Modelos pré-treinados (FER2013, VGGFace)
- ✅ Alta precisão (~70-80%)
- ✅ Fácil integração
- ✅ Gratuito e open source
- ✅ Suporta 7 emoções: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral

**Desvantagens:**
- ⚠️ Requer TensorFlow (pode ser pesado)
- ⚠️ Mais lento que heurísticas (mas ainda em tempo real)

**Instalação:**
```bash
pip install deepface
```

**Uso:**
```python
from deepface import DeepFace

result = DeepFace.analyze(
    img_path=face_image,
    actions=['emotion'],
    enforce_detection=False
)
emotion = result['dominant_emotion']
```

---

### 2. **Modelo ONNX (FER2013)** ⭐⭐

**Vantagens:**
- ✅ Muito leve (modelo < 5MB)
- ✅ Rápido (ONNX Runtime)
- ✅ Não requer TensorFlow
- ✅ Alta precisão (~65-75%)
- ✅ Funciona offline

**Desvantagens:**
- ⚠️ Precisa baixar modelo pré-treinado
- ⚠️ Requer ONNX Runtime

**Instalação:**
```bash
pip install onnxruntime
# Baixar modelo FER2013 (disponível no GitHub)
```

**Uso:**
```python
import onnxruntime as ort
import numpy as np

# Carrega modelo
session = ort.InferenceSession('fer2013_model.onnx')

# Prepara input (48x48 grayscale)
input_data = preprocess_face(face_image)

# Predição
outputs = session.run(None, {'input': input_data})
emotion_idx = np.argmax(outputs[0])
emotion = EMOTIONS[emotion_idx]
```

---

### 3. **Affectiva (Affdex)** ❌

**Vantagens:**
- ✅ Alta precisão comercial
- ✅ SDK profissional

**Desvantagens:**
- ❌ **Requer licença comercial** (custo)
- ❌ **API key necessária**
- ❌ SDK proprietário
- ❌ Não é open source

**Conclusão:** Não recomendado para projeto open source/gratuito.

---

## 🚀 Recomendação

### Opção 1: **DeepFace** (Mais Fácil)

**Por quê?**
- Integração simples
- Modelos já treinados
- Alta precisão
- Documentação completa

**Implementação:**
- Substituir `EmotionClassifierLight` por `EmotionClassifierDeepFace`
- Manter mesma interface
- Adicionar cache para performance

### Opção 2: **ONNX FER2013** (Mais Leve)

**Por quê?**
- Muito leve e rápido
- Não requer TensorFlow
- Funciona offline
- Boa precisão

**Implementação:**
- Criar `EmotionClassifierONNX`
- Baixar modelo FER2013
- Usar ONNX Runtime

---

## 📝 Próximos Passos

1. **Escolher opção** (DeepFace ou ONNX)
2. **Implementar novo classificador**
3. **Manter compatibilidade** com código atual
4. **Testar precisão**
5. **Substituir ou manter como alternativa**

---

## 🔧 Comparação Rápida

| Característica | Heurísticas Atuais | DeepFace | ONNX FER2013 | Affectiva |
|----------------|-------------------|----------|-------------|-----------|
| **Precisão** | ~50-60% | ~70-80% | ~65-75% | ~85-90% |
| **Velocidade** | ⚡⚡⚡ Muito rápido | ⚡⚡ Rápido | ⚡⚡⚡ Muito rápido | ⚡⚡ Rápido |
| **Peso** | Muito leve | Pesado (TF) | Leve | Médio |
| **Custo** | Gratuito | Gratuito | Gratuito | **Pago** |
| **Offline** | ✅ | ✅ | ✅ | ❌ (API) |
| **Fácil Integração** | ✅ | ✅ | ✅ | ⚠️ |

---

**Qual você prefere implementar?**

1. **DeepFace** - Mais fácil, alta precisão
2. **ONNX FER2013** - Mais leve, boa precisão
3. **Manter atual** - Melhorar heurísticas

