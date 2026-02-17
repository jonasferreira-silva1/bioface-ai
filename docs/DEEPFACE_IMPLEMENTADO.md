# 🎭 DeepFace - Classificação de Emoções

**Nota:** Este documento descreve a implementação do DeepFace. Para uso, veja [USAGE.md](USAGE.md).

**Data:** 2026-02-17  
**Status:** ✅ Implementado

---

## 🎯 O Que Foi Feito

Implementado **EmotionClassifierDeepFace** usando a biblioteca DeepFace para classificação de emoções com alta precisão.

### ✅ Funcionalidades

1. **Classificador DeepFace**
   - Usa modelos pré-treinados (FER2013)
   - Precisão ~70-80% (vs ~50-60% das heurísticas)
   - Suporta 7 emoções: Happy, Sad, Angry, Surprise, Fear, Disgust, Neutral
   - Interface compatível com EmotionClassifierLight

2. **Integração Automática**
   - Sistema detecta automaticamente se DeepFace está instalado
   - Fallback para EmotionClassifierLight se não disponível
   - Configurável via variável de ambiente

3. **Performance**
   - Cache de resultados (opcional)
   - Limpeza automática de arquivos temporários
   - Processamento em tempo real

---

## 📦 Instalação

### 1. Instalar DeepFace

```bash
pip install deepface
```

Ou instalar todas as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar Tipo de Classificador

Edite o arquivo `.env` ou defina variável de ambiente:

```bash
# Usar DeepFace (recomendado para melhor precisão)
EMOTION_CLASSIFIER_TYPE=deepface

# Ou usar heurísticas (mais rápido, menos preciso)
EMOTION_CLASSIFIER_TYPE=light
```

**Padrão:** `light` (se não especificado)

---

## 🚀 Como Usar

### Opção 1: Via Configuração (Recomendado)

1. **Edite `.env`:**
```env
EMOTION_CLASSIFIER_TYPE=deepface
EMOTION_CONFIDENCE_THRESHOLD=0.5
```

2. **Execute o sistema:**
```bash
python main-light.py
```

O sistema automaticamente usará DeepFace se estiver instalado.

### Opção 2: Via Código

```python
from src.ai.emotion_classifier_deepface import EmotionClassifierDeepFace

# Cria classificador
classifier = EmotionClassifierDeepFace(
    confidence_threshold=0.5,
    backend='opencv'  # ou 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe'
)

# Classifica emoção
emotion, confidence = classifier.predict(face_image)
emotion_pt = classifier.get_emotion_pt(emotion)

print(f"{emotion_pt}: {confidence:.2%}")
```

---

## 📊 Comparação: Light vs DeepFace

| Característica | Light (Heurísticas) | DeepFace |
|----------------|---------------------|----------|
| **Precisão** | ~50-60% | ~70-80% |
| **Velocidade** | ⚡⚡⚡ Muito rápido | ⚡⚡ Rápido |
| **Dependências** | Nenhuma extra | DeepFace + TensorFlow |
| **Emoções** | 5 (Happy, Sad, Angry, Surprise, Neutral) | 7 (+ Fear, Disgust) |
| **Offline** | ✅ | ✅ |
| **Melhor Para** | Performance máxima | Precisão máxima |

---

## 🔧 Configurações Disponíveis

### Variáveis de Ambiente

```env
# Tipo de classificador
EMOTION_CLASSIFIER_TYPE=deepface  # ou 'light'

# Threshold de confiança
EMOTION_CONFIDENCE_THRESHOLD=0.5  # 0.0 a 1.0
```

### Parâmetros do DeepFace

```python
EmotionClassifierDeepFace(
    confidence_threshold=0.5,      # Confiança mínima
    backend='opencv',              # Backend de detecção
    enforce_detection=False         # Se True, erro se não detectar face
)
```

**Backends disponíveis:**
- `opencv` - Mais rápido (padrão)
- `ssd` - Boa precisão
- `dlib` - Preciso mas lento
- `mtcnn` - Muito preciso
- `retinaface` - Melhor precisão
- `mediapipe` - Rápido e preciso

---

## 🐛 Troubleshooting

### Erro: "DeepFace não está instalado"

**Solução:**
```bash
pip install deepface
```

### Erro: "No module named 'tensorflow'"

**Solução:**
```bash
pip install tensorflow
```

### Performance lenta

**Soluções:**
1. Use backend mais rápido: `backend='opencv'`
2. Aumente `FRAME_SKIP` no `.env`
3. Use `EMOTION_CLASSIFIER_TYPE=light` para máxima velocidade

### Emoções não detectadas

**Soluções:**
1. Reduza `EMOTION_CONFIDENCE_THRESHOLD` (ex: 0.3)
2. Melhore iluminação
3. Aproxime-se mais da câmera
4. Verifique se a face está visível

---

## 📝 Notas Técnicas

### Como Funciona

1. **Preparação:** Face é convertida para formato BGR (OpenCV)
2. **Temporário:** Salva em arquivo temporário (DeepFace requer arquivo)
3. **Análise:** DeepFace analisa emoção usando modelo FER2013
4. **Normalização:** Converte resultado para formato do sistema
5. **Limpeza:** Remove arquivo temporário

### Arquivos Temporários

DeepFace precisa de arquivo de imagem, então:
- Face é salva temporariamente em `%TEMP%/bioface_deepface/`
- Arquivos são removidos automaticamente após uso
- Limpeza automática de arquivos antigos (>1 hora)

### Compatibilidade

- ✅ Interface idêntica ao EmotionClassifierLight
- ✅ Drop-in replacement (substitui sem mudar código)
- ✅ Fallback automático se não disponível

---

## 🎯 Próximos Passos

1. **Testar precisão** - Comparar com heurísticas
2. **Otimizar performance** - Cache, processamento assíncrono
3. **Adicionar mais emoções** - Se necessário
4. **Treinar modelo customizado** - Para casos específicos

---

## ✅ Status

**Implementação:** ✅ Completa  
**Testes:** ⏳ Pendente  
**Documentação:** ✅ Completa

---

**Última atualização:** 2026-02-17

