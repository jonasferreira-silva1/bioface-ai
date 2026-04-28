# Instalação — BioFace AI

## Requisitos

| Item | Mínimo | Recomendado |
|------|--------|-------------|
| Python | 3.9+ | 3.11 |
| RAM | 4 GB | 8 GB |
| Webcam | Qualquer USB | 720p+ |
| Docker | Opcional | Docker Desktop |

---

## Instalação do Pipeline (host)

O pipeline de câmera roda diretamente no host — não em Docker.

```bash
# 1. Clone o repositório
git clone https://github.com/jonasferreira-silva1/bioface-ai.git
cd bioface-ai

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements-light.txt

# 4. Execute
python main-light.py
```

Na primeira execução o modelo ONNX de emoções (~30 MB) é baixado automaticamente para `models/`.

---

## Instalação dos Serviços (Docker)

API e Dashboard rodam em containers.

```bash
# Sobe API (porta 8000) + Dashboard (porta 8501)
docker-compose up --build
```

Acesse:
- API + Swagger → http://localhost:8000/docs
- Dashboard → http://localhost:8501

---

## Configuração (opcional)

Crie um arquivo `.env` na raiz para sobrescrever os padrões:

```env
# Câmera
CAMERA_INDEX=0          # tente 1 ou 2 se a câmera não abrir
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Performance
FRAME_SKIP=2            # processa 1 frame a cada N

# Reconhecimento
RECOGNITION_DISTANCE_THRESHOLD=0.35

# Emoções
EMOTION_CONFIDENCE_THRESHOLD=0.0

# API (modo híbrido)
API_URL=http://localhost:8000
```

---

## Problemas comuns

**Câmera não abre**
- Feche Zoom, Teams ou qualquer app usando a câmera
- Tente `CAMERA_INDEX=1` no `.env`

**Conflito de dependências (NumPy / protobuf)**
```bash
pip install "numpy<2.0" "protobuf<5.0,>=4.25.3" --upgrade
```

**Modelo ONNX não baixa**  
Baixe manualmente e salve em `models/emotion-ferplus-8.onnx`:  
https://github.com/onnx/models/raw/main/validated/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx

Para mais problemas, veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
