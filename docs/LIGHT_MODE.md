# 💡 Modo Leve - BioFace AI

Guia para usar a versão leve do BioFace AI que consome muito menos memória.

## 📊 Comparação de Uso de Memória

| Versão | Memória | Funcionalidades |
|--------|---------|-----------------|
| **Completa** | 2-4 GB | Detecção + Emoções + TensorFlow |
| **Leve** | 200-500 MB | Apenas Detecção de Faces |

## 🎯 Quando Usar Versão Leve

- ✅ Sistema com pouca RAM (< 4GB)
- ✅ Apenas precisa detectar faces (sem emoções)
- ✅ Quer economizar recursos
- ✅ Executar em hardware limitado

## 🚀 Como Usar

### Opção 1: Executar Diretamente (Mais Leve)

```bash
# Instale dependências leves
pip install -r requirements-light.txt

# Execute versão leve
python src/main-light.py
```

### Opção 2: Docker Leve

```bash
# Build imagem leve
docker build -f Dockerfile.light -t bioface-ai:light .

# Execute com limite de memória
docker run -it --rm \
  --memory="1g" \
  --device=/dev/video0 \
  bioface-ai:light
```

### Opção 3: Docker Compose Leve

```bash
docker-compose -f docker-compose.light.yml up
```

## 📋 O Que Foi Removido

### Dependências Removidas

- ❌ **TensorFlow** (~1.5-2GB RAM) - Principal culpado
- ❌ **Keras** - Depende do TensorFlow
- ❌ **scikit-learn** - Não usado no MVP
- ❌ **FastAPI** - Para fases futuras
- ❌ **Streamlit** - Para fases futuras
- ❌ **PostgreSQL drivers** - Para fases futuras

### Dependências Mantidas

- ✅ **OpenCV** (headless) - Essencial para visão
- ✅ **MediaPipe** - Detecção de faces
- ✅ **NumPy** - Operações matemáticas
- ✅ **Loguru** - Logging
- ✅ **python-dotenv** - Configurações

## 🔧 Otimizações Aplicadas

1. **OpenCV Headless**: Remove GUI, economiza ~100MB
2. **Sem TensorFlow**: Economiza 1.5-2GB
3. **Docker Multi-stage**: Imagem menor
4. **Limite de Memória**: Docker limita a 1GB
5. **Frame Skip Aumentado**: Processa menos frames

## 📝 Funcionalidades Disponíveis

### ✅ Funciona

- Detecção de faces em tempo real
- Extração de landmarks (468 pontos)
- Bounding boxes
- FPS tracking
- Logging

### ❌ Não Funciona (Versão Leve)

- Classificação de emoções (requer TensorFlow)
- Reconhecimento facial (requer modelos pesados)
- Análise de padrões (requer ML)

## 🎨 Adicionar Emoções Depois (Opcional)

Se quiser adicionar emoções sem TensorFlow completo:

### Opção 1: TensorFlow Lite (Mais Leve)

```bash
pip install tflite-runtime
```

### Opção 2: Modelo Simples

Use um modelo pré-treinado menor ou API externa.

### Opção 3: Instalar TensorFlow Separadamente

```bash
# Apenas quando necessário
pip install tensorflow
```

## 💾 Economia de Recursos

### Memória

- **Antes**: 2-4 GB
- **Depois**: 200-500 MB
- **Economia**: ~80-90%

### Disco

- **Antes**: ~2-3 GB (imagem Docker)
- **Depois**: ~500 MB
- **Economia**: ~75%

### CPU

- **Antes**: Alto (TensorFlow)
- **Depois**: Médio (apenas OpenCV + MediaPipe)
- **Economia**: ~50%

## 🐛 Solução de Problemas

### Ainda Consome Muita Memória

1. **Aumente FRAME_SKIP**:
   ```env
   FRAME_SKIP=5  # Processa 1 a cada 5 frames
   ```

2. **Reduza Resolução**:
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```

3. **Limite Docker**:
   ```bash
   docker run --memory="512m" ...
   ```

### Quer Emoções Mas Sem TensorFlow

Use uma API externa ou modelo mais leve (TensorFlow Lite).

## 📚 Arquivos da Versão Leve

- `requirements-light.txt` - Dependências mínimas
- `Dockerfile.light` - Dockerfile otimizado
- `docker-compose.light.yml` - Compose com limites
- `src/main-light.py` - Pipeline sem TensorFlow

## 🎯 Próximos Passos

1. **Teste a versão leve** primeiro
2. **Se precisar de emoções**, adicione TensorFlow Lite
3. **Ou use API externa** para classificação

---

**Dica**: Comece sempre com a versão leve. Adicione funcionalidades conforme necessário!


