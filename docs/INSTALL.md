# 📦 Instalação - BioFace AI

Guia completo de instalação do BioFace AI.

---

## 🔧 Requisitos do Sistema

### Mínimos
- **Python**: 3.9 ou superior
- **RAM**: 4GB
- **Espaço em disco**: 2GB
- **Webcam**: Qualquer webcam USB

### Recomendados
- **Python**: 3.10 ou 3.11
- **RAM**: 8GB ou mais
- **GPU**: NVIDIA com CUDA (opcional, melhora performance)
- **CPU**: Multi-core (4+ cores)

---

## 📥 Instalação Passo a Passo

### 1. Clone ou Baixe o Projeto

```bash
git clone https://github.com/seu-usuario/bioface-ai.git
cd bioface-ai
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

### 3. Instale Dependências

```bash
# Atualize pip primeiro
python -m pip install --upgrade pip

# Instale dependências
pip install -r requirements.txt
```

**⚠️ Importante:** O sistema requer **NumPy < 2.0** e **protobuf < 5.0** para compatibilidade com MediaPipe. Se houver conflitos, consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### 4. Configure Ambiente

```bash
# Copie .env.example para .env
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edite .env com suas configurações (opcional)
```

### 5. Verifique Instalação

```bash
python -c "import cv2, mediapipe, numpy; print('✓ Instalação OK!')"
```

---

## 🚀 Primeira Execução

```bash
# Versão leve (recomendada)
python main-light.py

# Ou versão completa (requer TensorFlow)
python main.py
```

Você deve ver:
- Janela com vídeo da webcam
- Detecção de faces
- Identificação de pessoas cadastradas
- Classificação de emoções (se habilitado)

**Pressione `Q` para sair.**

---

## ⚙️ Configuração

### Ajustar Câmera

Edite `.env`:
```env
CAMERA_INDEX=0  # Tente 1, 2, etc. se não funcionar
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

### Melhorar Performance

Se estiver lento:
```env
FRAME_SKIP=3  # Processa 1 frame a cada 3
```

Ou reduza resolução:
```env
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
```

### Classificador de Emoções

```env
# Usar heurísticas (rápido, menos preciso)
EMOTION_CLASSIFIER_TYPE=light

# Ou usar DeepFace (mais preciso, requer TensorFlow)
EMOTION_CLASSIFIER_TYPE=deepface
```

---

## 🐛 Problemas Comuns

### Erro: NumPy incompatível

**Solução:**
```bash
pip install "numpy<2.0" --upgrade
```

### Erro: Protobuf incompatível

**Solução:**
```bash
pip install "protobuf<5.0,>=4.25.3" --upgrade
```

### Erro: Câmera não abre

**Soluções:**
1. Feche outras aplicações usando a câmera
2. Tente outro índice: `CAMERA_INDEX=1` no `.env`
3. Verifique permissões da câmera

### Performance lenta

**Soluções:**
1. Aumente `FRAME_SKIP` no `.env`
2. Reduza resolução da câmera
3. Use modo leve: `python main-light.py`

Para mais problemas, consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## 📚 Próximos Passos

Após instalação:
1. Leia [USAGE.md](USAGE.md) para aprender a usar
2. Veja [CADASTRO_E_CONSULTA.md](CADASTRO_E_CONSULTA.md) para cadastrar pessoas
3. Consulte [STATUS.md](STATUS.md) para entender o estado do projeto

---

**Última atualização:** 2026-02-17

