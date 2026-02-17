# 🐛 Troubleshooting - BioFace AI

Guia de solução de problemas comuns.

---

## 🔧 Problemas de Instalação

### Erro: NumPy incompatível

**Erro:**
```
ImportError: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.2
```

**Solução:**
```bash
pip install "numpy<2.0" --upgrade
```

**Causa:** MediaPipe requer NumPy < 2.0.

---

### Erro: Protobuf incompatível

**Erro:**
```
ERROR: mediapipe requires protobuf<5,>=4.25.3, but you have protobuf 6.33.5
```

**Solução:**
```bash
pip install "protobuf<5.0,>=4.25.3" --upgrade
```

**Nota:** TensorFlow requer protobuf>=5.28.0, causando conflito. Se usar DeepFace, pode ser necessário escolher entre MediaPipe ou TensorFlow.

---

### Erro: TensorFlow vs MediaPipe

**Problema:** Conflito entre TensorFlow (protobuf>=5.28.0) e MediaPipe (protobuf<5.0).

**Solução:**
- **Sistema principal funciona sem TensorFlow** (use `python main-light.py`)
- **DeepFace requer TensorFlow** (opcional, apenas se usar classificação de emoções com DeepFace)
- **Recomendação:** Use `EMOTION_CLASSIFIER_TYPE=light` (não requer TensorFlow)

---

## 🎥 Problemas com Câmera

### Câmera não abre

**Sintomas:**
- Erro: "Cannot open camera"
- Janela não aparece
- Sistema trava

**Soluções:**
1. Feche outros programas usando a câmera (Zoom, Teams, Skype, etc.)
2. Verifique permissões da câmera no Windows
3. Tente outro índice: `CAMERA_INDEX=1` no `.env`
4. Reinicie o programa
5. Reinicie o computador (último recurso)

---

### Câmera no Docker (Windows)

**Problema:** Docker no Windows não acessa câmera.

**Solução:** Execute diretamente no Windows:
```bash
python main-light.py
```

Veja [DOCKER.md](DOCKER.md) para mais detalhes.

---

## 👤 Problemas de Reconhecimento

### Identifica como "DESCONHECIDO"

**Sintomas:**
- Sistema não identifica pessoa cadastrada
- Mostra "DESCONHECIDO" mesmo após cadastro

**Soluções:**
1. **Verifique se está cadastrado:**
   ```bash
   python scripts/list_all_users.py
   ```

2. **Re-cadastre-se:**
   ```bash
   python scripts/register_face.py --name "Seu Nome"
   ```

3. **Melhore condições:**
   - Boa iluminação
   - Aproxime-se da câmera
   - Olhe diretamente para a câmera
   - Remova óculos/máscara se possível

4. **Limpe embeddings antigos:**
   ```bash
   python scripts/delete_all_user_embeddings.py
   # Depois re-cadastre
   ```

---

### Identifica pessoa errada

**Sintomas:**
- Jonas identificado como Eliza
- Identificação incorreta

**Soluções:**
1. **Limpe embeddings problemáticos:**
   ```bash
   python scripts/delete_all_user_embeddings.py
   # Re-cadastre todas as pessoas
   ```

2. **Verifique ambiguidade:**
   ```bash
   python scripts/diagnose_recognition.py
   ```

3. **Ajuste threshold no `.env`:**
   ```env
   RECOGNITION_DISTANCE_THRESHOLD=0.30  # Mais restritivo
   ```

---

### Cadastro duplicado

**Sintomas:**
- Sistema impede cadastro dizendo que pessoa já existe

**Solução:** Isso é **correto** - o sistema impede duplicatas. Se quiser re-cadastrar:
```bash
# Delete embeddings antigos
python scripts/delete_all_user_embeddings.py

# Depois cadastre novamente
python scripts/register_face.py --name "Seu Nome"
```

---

## 😊 Problemas com Emoções

### Emoção não muda

**Sintomas:**
- Sistema mostra "Feliz" mesmo quando está bravo
- Emoção fica "fixada"

**Soluções:**
1. **Use DeepFace (mais preciso):**
   ```bash
   pip install deepface tensorflow
   # Configure .env: EMOTION_CLASSIFIER_TYPE=deepface
   ```

2. **Ajuste threshold:**
   ```env
   EMOTION_CONFIDENCE_THRESHOLD=0.3  # Mais sensível
   ```

3. **Melhore iluminação** - ajuda muito na detecção

---

### Emoção oscila na tela

**Sintomas:**
- Emoção pisca/muda rapidamente
- Não fica fixa

**Solução:** Já implementado - sistema usa estabilização temporal. Se ainda oscilar:
1. Aumente `FRAME_SKIP` no `.env` (reduz processamento)
2. Melhore iluminação
3. Aproxime-se mais da câmera

---

## 🖥️ Problemas de Performance

### Sistema muito lento

**Sintomas:**
- FPS baixo (< 10)
- Lag na interface
- CPU alto

**Soluções:**
1. **Aumente frame skip:**
   ```env
   FRAME_SKIP=3  # Processa 1 frame a cada 3
   ```

2. **Reduza resolução:**
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```

3. **Use modo leve:**
   ```bash
   python main-light.py  # Sem TensorFlow
   ```

4. **Feche outras aplicações pesadas**

5. **Use GPU** (se disponível)

---

### Alto uso de memória

**Sintomas:**
- Sistema usa muita RAM (> 2GB)
- Computador fica lento

**Soluções:**
1. **Use modo leve:**
   ```bash
   python main-light.py  # ~200-500MB
   ```

2. **Não use DeepFace** (requer TensorFlow, usa mais memória)

3. **Limite histórico:**
   - Sistema já otimizado, mas pode reduzir `history_size` no código

---

## 🪟 Problemas no Windows

### Janela não aparece

**Sintomas:**
- Sistema inicia mas janela não aparece
- Logs mostram que está rodando

**Soluções:**
1. Verifique barra de tarefas (pode estar minimizada)
2. Use `Alt+Tab` para encontrar a janela
3. Verifique se há outras janelas cobrindo
4. Tente redimensionar: `cv2.namedWindow(..., cv2.WINDOW_NORMAL)`

---

### Erro: "libGL.so" (Linux/WSL)

**Erro:**
```
ImportError: libGL.so.1: cannot open shared object file
```

**Solução (Linux):**
```bash
sudo apt-get update
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

**Solução (WSL):**
```bash
sudo apt-get install libgl1-mesa-glx
```

---

## 🔍 Debug

### Ver logs detalhados

**Configure `.env`:**
```env
LOG_LEVEL=DEBUG
```

**Ou via código:**
```python
from src.utils.logger import get_logger
logger = get_logger(__name__)
logger.setLevel("DEBUG")
```

---

### Testar componentes isoladamente

**Testar câmera:**
```python
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print("Câmera OK!" if ret else "Erro na câmera")
```

**Testar MediaPipe:**
```python
import mediapipe as mp
mp_face = mp.solutions.face_mesh.FaceMesh()
print("MediaPipe OK!")
```

**Testar banco de dados:**
```bash
python scripts/list_all_users.py
```

---

## 📞 Ainda com Problemas?

1. **Verifique logs:** `logs/bioface.log`
2. **Consulte documentação:** [docs/README.md](README.md)
3. **Verifique versões:**
   ```bash
   python -c "import cv2, mediapipe, numpy; print(f'OpenCV: {cv2.__version__}, MediaPipe: {mediapipe.__version__}, NumPy: {numpy.__version__}')"
   ```

---

**Última atualização:** 2026-02-17

