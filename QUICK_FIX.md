# ⚡ Solução Rápida - Versão Leve

## 🚀 Executar Versão Leve (Sem Docker)

A forma mais rápida e leve:

```bash
# 1. Instale apenas dependências leves
pip install -r requirements-light.txt

# 2. Execute versão leve
python main-light.py
```

**Uso de memória**: ~200-500 MB (vs 2-4 GB da versão completa)

## 🐳 Executar Versão Leve no Docker

```bash
# Build
docker build -f Dockerfile.light -t bioface-ai:light .

# Run (com limite de memória)
docker run -it --rm --memory="1g" bioface-ai:light
```

## 📊 O Que Foi Removido

- ❌ TensorFlow (economiza ~1.5-2 GB)
- ❌ Keras
- ❌ FastAPI, Streamlit (futuro)
- ❌ PostgreSQL drivers

## ✅ O Que Funciona

- ✅ Detecção de faces
- ✅ Landmarks (468 pontos)
- ✅ Visualização em tempo real
- ✅ FPS tracking

## ❌ O Que NÃO Funciona

- ❌ Classificação de emoções (requer TensorFlow)

## 💡 Se Precisar de Emoções Depois

Instale TensorFlow Lite (mais leve):
```bash
pip install tflite-runtime
```

Ou adicione TensorFlow completo quando necessário:
```bash
pip install tensorflow
```

---

**Use a versão leve primeiro! É muito mais eficiente em recursos.**


