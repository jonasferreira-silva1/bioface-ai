# Troubleshooting — BioFace AI

## Instalação

**Erro: NumPy incompatível**
```
ImportError: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x
```
```bash
pip install "numpy<2.0" --upgrade
```

**Erro: Protobuf incompatível**
```
ERROR: mediapipe requires protobuf<5
```
```bash
pip install "protobuf<5.0,>=4.25.3" --upgrade
```

**Erro: onnxruntime não instalado**
```bash
pip install onnxruntime
```

---

## Câmera

**Câmera não abre**
1. Feche Zoom, Teams, OBS ou qualquer app usando a câmera
2. Tente `CAMERA_INDEX=1` (ou 2) no `.env`
3. Verifique permissões de câmera no Windows (Configurações → Privacidade → Câmera)

**Câmera no Docker (Windows)**  
Docker Desktop no Windows não acessa webcam. Execute o pipeline diretamente no host:
```bash
python main-light.py
```

**Janela não aparece**  
Verifique a barra de tarefas — pode estar minimizada. Use `Alt+Tab` para encontrá-la.

---

## Reconhecimento facial

**Identifica como "Desconhecido"**
1. Verifique se está cadastrado: `python scripts/list_all_users.py`
2. Melhore a iluminação e aproxime-se da câmera
3. Re-cadastre: `python scripts/register_face.py --name "Seu Nome"`
4. Ajuste o threshold no `.env`: `RECOGNITION_DISTANCE_THRESHOLD=0.40`

**Identifica a pessoa errada**
1. Limpe e re-cadastre: `python scripts/delete_all_user_embeddings.py`
2. Torne o threshold mais restritivo: `RECOGNITION_DISTANCE_THRESHOLD=0.30`
3. Diagnostique: `python scripts/diagnose_recognition.py`

---

## Emoções

**Emoção não muda / fica presa**  
O sistema usa estabilização temporal (mediana de 6 frames). Sustente a expressão por ~1 segundo para a mudança ser detectada.

**Emoção oscila muito**  
Melhore a iluminação. Câmeras com pouca luz geram ruído nos landmarks.

**Modelo ONNX não baixa automaticamente**  
Baixe manualmente e salve em `models/emotion-ferplus-8.onnx`:  
https://github.com/onnx/models/raw/main/validated/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx

---

## Performance

**FPS baixo (< 15)**
```env
# .env
FRAME_SKIP=3        # processa 1 a cada 3 frames
CAMERA_WIDTH=320    # reduz resolução
CAMERA_HEIGHT=240
```

**Alto uso de memória**  
Certifique-se de estar usando `main-light.py` (sem TensorFlow). O uso esperado é ~300–500 MB.

---

## Docker

**Build falha**
```bash
# Rebuild sem cache
docker-compose build --no-cache
```

**API não responde**
```bash
# Verificar logs
docker-compose logs api

# Verificar health
curl http://localhost:8000/api/health
```

**Dashboard não conecta na API**  
Verifique se a API está saudável antes do Dashboard subir. O `depends_on` com `condition: service_healthy` garante isso, mas o healthcheck pode demorar até 90s na primeira vez.

---

## Verificar versões instaladas

```bash
python -c "import cv2, mediapipe, numpy, onnxruntime; print(f'OpenCV {cv2.__version__} | MediaPipe {mediapipe.__version__} | NumPy {numpy.__version__} | ONNX {onnxruntime.__version__}')"
```
