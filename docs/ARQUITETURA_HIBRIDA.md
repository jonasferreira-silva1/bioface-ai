# Arquitetura Híbrida — BioFace AI

## Visão Geral

O BioFace AI usa uma **arquitetura híbrida** que separa responsabilidades entre o host e containers Docker:

```
┌─────────────────────────────────────────────────────────────┐
│  HOST (Windows / Linux / Mac)                               │
│                                                             │
│  ┌──────────────────────────────────────┐                   │
│  │  Pipeline de Câmera  (main-light.py) │                   │
│  │                                      │                   │
│  │  Webcam → MediaPipe → FaceRecognizer │                   │
│  │       → EmotionClassifier (ONNX)     │                   │
│  │       → HTTP POST → API              │                   │
│  └──────────────────────────────────────┘                   │
│                        │                                    │
│                        │ HTTP / WebSocket                   │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Docker Compose                                     │    │
│  │                                                     │    │
│  │  ┌─────────────────┐    ┌──────────────────────┐   │    │
│  │  │  API (FastAPI)  │◄───│  Dashboard           │   │    │
│  │  │  :8000          │    │  (Streamlit)  :8501  │   │    │
│  │  │                 │    │                      │   │    │
│  │  │  REST + WS      │    │  Gráficos, stats,    │   │    │
│  │  │  SQLite         │    │  gerenciamento       │   │    │
│  │  └─────────────────┘    └──────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Por que essa separação?

### Pipeline no host
- Docker no Windows **não acessa webcam** diretamente (limitação do Docker Desktop)
- Rodar no host garante **latência mínima** no processamento de frames
- MediaPipe e OpenCV funcionam melhor com acesso direto ao hardware

### API e Dashboard em Docker
- **Isolamento**: dependências da API não conflitam com as do pipeline
- **Portabilidade**: qualquer máquina com Docker sobe os serviços com um comando
- **Deploy fácil**: em produção, basta fazer push das imagens para um registry

## Como usar

### 1. Sobe os serviços (API + Dashboard)
```bash
docker-compose up --build
```

### 2. Inicia o pipeline de câmera
```bash
# Modo conectado à API (envia dados em tempo real)
python main-light.py --api-url http://localhost:8000

# Modo standalone (sem API)
python main-light.py
```

### 3. Acesse
| Serviço   | URL                          |
|-----------|------------------------------|
| API docs  | http://localhost:8000/docs   |
| Dashboard | http://localhost:8501        |

## Estrutura dos containers

| Container          | Imagem               | Porta | Responsabilidade              |
|--------------------|----------------------|-------|-------------------------------|
| `bioface-api`      | `bioface-api:latest` | 8000  | REST API + WebSocket + SQLite |
| `bioface-dashboard`| `bioface-dashboard:latest` | 8501 | Interface visual Streamlit |

## Comunicação entre componentes

```
Pipeline (host)  ──POST /api/emotions──►  API (Docker)
Pipeline (host)  ──POST /api/users────►  API (Docker)
Dashboard        ──GET  /api/stats────►  API (Docker)
Dashboard        ──WS   /ws/emotions──►  API (Docker)
```

## Build manual

```bash
# Windows
scripts\docker-build.bat

# Linux / Mac
./scripts/docker-build.sh
```
