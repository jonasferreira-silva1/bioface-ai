# 📦 Guia de Instalação Completo - BioFace AI

Este guia detalha todos os passos para instalar e configurar o BioFace AI.

## 🔧 Requisitos do Sistema

### Mínimos
- **Python**: 3.9 ou superior
- **RAM**: 4GB
- **Espaço em disco**: 2GB
- **Webcam**: Qualquer webcam USB

### Recomendados
- **Python**: 3.10 ou 3.11
- **RAM**: 8GB ou mais
- **GPU**: NVIDIA com CUDA (opcional, mas melhora muito a performance)
- **CPU**: Multi-core (4+ cores)

## 📥 Instalação Passo a Passo

### 1. Clone ou Baixe o Projeto

```bash
# Se usar Git
git clone https://github.com/seu-usuario/bioface-ai.git
cd bioface-ai

# Ou baixe e extraia o ZIP
```

### 2. Crie Ambiente Virtual

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Atualize pip

```bash
python -m pip install --upgrade pip
```

### 4. Instale Dependências

```bash
pip install -r requirements.txt
```

**Nota**: A instalação pode demorar 5-10 minutos, especialmente o TensorFlow.

### 5. Configure Ambiente

**Opção A - Script Automático:**
```bash
python scripts/setup_env.py
```

**Opção B - Manual:**
```bash
# Cria diretórios
mkdir logs models data tests

# Copia .env.example para .env
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edite .env com suas configurações
```

### 6. Verifique Instalação

```bash
python -c "import cv2, mediapipe, tensorflow; print('OK!')"
```

Se não houver erros, a instalação foi bem-sucedida!

## 🎯 Primeira Execução

```bash
python main.py
```

Você deve ver:
- Janela com vídeo da webcam
- Detecção de faces
- Classificação de emoções
- FPS no canto superior

Pressione `q` para sair.

## ⚙️ Configuração Avançada

### Ajustar Câmera

Edite `.env`:
```env
CAMERA_INDEX=0  # Tente 1, 2, etc. se não funcionar
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

### Melhorar Performance

Se estiver lento, aumente o frame skip:
```env
FRAME_SKIP=3  # Processa 1 frame a cada 3
```

Ou reduza resolução:
```env
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
```

### Usar Modelo Pré-treinado

1. Baixe um modelo (veja `docs/MODELS.md`)
2. Coloque em `models/emotion/`
3. Modifique `src/ai/emotion_classifier.py` para usar o modelo

## 🐛 Solução de Problemas

### Erro: "pip install" falha

**Problema**: Dependências não instalam

**Solução**:
```bash
# Atualize pip
python -m pip install --upgrade pip setuptools wheel

# Instale uma por vez
pip install opencv-python
pip install mediapipe
pip install tensorflow
```

### Erro: "Não foi possível abrir a câmera"

**Solução**:
1. Verifique se webcam está conectada
2. Feche outras aplicações usando a câmera
3. Tente outro índice: `python main.py --camera 1`

### Erro: "ModuleNotFoundError"

**Solução**:
```bash
# Certifique-se que o venv está ativado
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstale dependências
pip install -r requirements.txt
```

### Performance Muito Lenta

**Soluções**:
1. Aumente `FRAME_SKIP` no `.env`
2. Reduza resolução da câmera
3. Use GPU (instale TensorFlow GPU)
4. Feche outras aplicações pesadas

### TensorFlow não usa GPU

**Para NVIDIA:**
1. Instale CUDA e cuDNN
2. Instale TensorFlow GPU:
   ```bash
   pip install tensorflow[and-cuda]
   ```

**Verificar se GPU está sendo usada:**
```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

## 🔍 Verificação Pós-Instalação

Execute este script para verificar tudo:

```python
# test_installation.py
import sys

print("Verificando instalação...")

try:
    import cv2
    print("✓ OpenCV:", cv2.__version__)
except ImportError:
    print("✗ OpenCV não instalado")

try:
    import mediapipe as mp
    print("✓ MediaPipe:", mp.__version__)
except ImportError:
    print("✗ MediaPipe não instalado")

try:
    import tensorflow as tf
    print("✓ TensorFlow:", tf.__version__)
    print("✓ GPU disponível:", len(tf.config.list_physical_devices('GPU')) > 0)
except ImportError:
    print("✗ TensorFlow não instalado")

try:
    import numpy as np
    print("✓ NumPy:", np.__version__)
except ImportError:
    print("✗ NumPy não instalado")

print("\nTeste completo!")
```

Salve como `test_installation.py` e execute:
```bash
python test_installation.py
```

## 📚 Próximos Passos

Após instalação bem-sucedida:

1. Leia o [Guia Rápido](docs/QUICKSTART.md)
2. Explore a [Documentação](README.md)
3. Veja [Modelos Disponíveis](docs/MODELS.md)
4. Comece a usar!

## 💡 Dicas

- **Primeira vez**: Use configurações padrão
- **Performance**: Ajuste `FRAME_SKIP` conforme necessário
- **Iluminação**: Boa iluminação melhora detecção
- **Logs**: Verifique `logs/bioface.log` para debug

## 🆘 Ainda com Problemas?

1. Verifique os logs em `logs/bioface.log`
2. Abra uma [issue](https://github.com/seu-usuario/bioface-ai/issues)
3. Consulte a documentação completa

---

**Boa sorte com a instalação! 🚀**


