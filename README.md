# BioFace AI

**Sistema de reconhecimento facial offline para controle de acesso e análise de presença — sem cloud, sem API externa, sem custo recorrente.**

Identifica pessoas cadastradas em tempo real via webcam, detecta emoções e registra tudo em banco de dados local. Ideal para controle de ponto, acesso a ambientes, monitoramento de presença e pesquisa em visão computacional.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-46%20passing-brightgreen.svg)]()

---

## Por que BioFace AI?

| | BioFace AI | APIs de nuvem (AWS Rekognition, Azure Face) |
|--|--|--|
| Custo | Gratuito | Por requisição |
| Privacidade | Dados ficam no seu servidor | Dados enviados para terceiros |
| Offline | Sim | Não |
| Customizável | Código aberto | Caixa preta |
| Latência | ~40ms local | 200ms+ (rede) |

---

## Performance

Medido em CPU Intel i5, 8GB RAM, webcam 720p, iluminação normal:

| Métrica | Valor |
|---------|-------|
| FPS (pipeline leve) | 25–30 FPS |
| Latência de detecção | ~40ms por frame |
| Latência de reconhecimento | +15ms (busca no banco) |
| Latência da API (health check) | < 10ms |
| Uso de RAM (pipeline) | ~300–500 MB |
| Acurácia de emoções (ONNX FER+) | ~72% em condições normais |
| Tamanho do modelo ONNX | 30 MB |

> Acurácia de emoções medida informalmente com expressões frontais e boa iluminação. Raiva e surpresa têm boost adicional via análise geométrica de landmarks.

---

## O que faz

- Detecta faces em tempo real (MediaPipe, 468 landmarks)
- Reconhece e identifica pessoas cadastradas via embeddings faciais (128D, distância cosseno)
- Classifica 5 emoções: Feliz, Triste, Raiva, Surpresa, Neutro
- Registra histórico de presenças e emoções em SQLite
- Expõe API REST + WebSocket (FastAPI) para integração com outros sistemas
- Dashboard web (Streamlit) com gráficos e gerenciamento de usuários

---

## Casos de uso

- **Controle de ponto** — registra entrada/saída de colaboradores automaticamente
- **Acesso a ambientes** — libera porta ou catraca ao reconhecer pessoa autorizada
- **Análise de presença** — monitora quem está presente em sala de aula ou reunião
- **Pesquisa** — base para experimentos em visão computacional e análise comportamental

---

## Arquitetura

O pipeline de câmera roda no host. API e Dashboard rodam em Docker.

```
Host (Windows / Linux / Mac)
└── main-light.py
      Webcam → MediaPipe (468 landmarks)
            → FaceRecognizer (embedding 128D)
            → EmotionClassifierONNX (FER+ + geométrico)
            → SQLite
            → HTTP POST → API

Docker Compose
├── bioface-api        → http://localhost:8000/docs  (FastAPI)
└── bioface-dashboard  → http://localhost:8501       (Streamlit)
```

> Docker no Windows não acessa webcam diretamente — por isso o pipeline fica no host. Veja [docs/ARQUITETURA_HIBRIDA.md](docs/ARQUITETURA_HIBRIDA.md).

---

## Instalação e execução

### Modo 1 — Standalone (só pipeline, sem Docker)

Use quando quiser apenas reconhecimento facial e emoções, sem API nem Dashboard.

```bash
# 1. Clone e entre na pasta
git clone https://github.com/jonasferreira-silva1/bioface-ai.git
cd bioface-ai

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements-light.txt

# 4. Execute — a janela da câmera abre automaticamente
python main-light.py
```

> Na primeira execução o modelo ONNX (~30 MB) é baixado automaticamente para `models/`. Aguarde o download antes da janela abrir.

---

### Modo 2 — Híbrido (pipeline + API + Dashboard)

Requer Docker instalado. São **3 passos obrigatórios em ordem**.

**Passo 1 — Sobe API e Dashboard em Docker** (aguarde até ver "Application startup complete")

```bash
docker-compose up --build
```

**Passo 2 — Em outro terminal, inicia o pipeline de câmera**

```bash
# Ative o venv primeiro (se ainda não estiver ativo)
venv\Scripts\activate

python main-light.py --api-url http://localhost:8000
```

**Passo 3 — Acesse no browser** (só funcionam após o Passo 1 estar rodando)

| Serviço | URL | O que é |
|---------|-----|---------|
| API + Swagger | http://localhost:8000/docs | Documentação interativa dos endpoints |
| Dashboard | http://localhost:8501 | Interface web com gráficos e usuários |

> ⚠️ As URLs acima **não funcionam** se o `docker-compose up` não estiver rodando. Elas ficam disponíveis apenas enquanto os containers estão ativos.

---

## Uso rápido

```bash
# Cadastrar pessoa
python scripts/register_face.py --name "Jonas Silva"

# Listar cadastrados
python scripts/list_all_users.py

# Testar detecção de emoções isoladamente
python scripts/test_emotion_detection.py
```

---

## Stack

| Camada | Tecnologia | Por quê |
|--------|-----------|---------|
| Detecção facial | MediaPipe Face Mesh | Leve, sem GPU, 468 landmarks |
| Reconhecimento | Embeddings 128D + cosseno | Sem TensorFlow, ~15ms |
| Emoções | ONNX Runtime (FER+) | 30MB, sem TensorFlow, ~25ms |
| Banco de dados | SQLite + SQLAlchemy | Zero configuração, portável |
| API | FastAPI + WebSocket | Async, Swagger automático |
| Dashboard | Streamlit + Plotly | Rápido de construir, interativo |
| Containers | Docker + Compose | Isolamento, deploy simples |
| Logging | Loguru | Rotação automática, colorido |

---

## Estrutura

```
bioface-ai/
├── src/
│   ├── ai/              # Reconhecimento + classificação de emoções (ONNX)
│   ├── api/             # FastAPI — rotas REST, WebSocket
│   ├── dashboard/       # Dashboard Streamlit
│   ├── database/        # Modelos SQLAlchemy + repositório
│   ├── vision/          # Câmera, detector, processador de faces
│   ├── utils/           # Config (Pydantic Settings) + Logger (Loguru)
│   ├── exceptions.py    # Hierarquia de exceções customizadas
│   └── main_light.py    # Pipeline principal
├── scripts/             # Cadastro, diagnóstico, limpeza de dados
├── tests/               # 46 testes com Pytest
├── docs/                # Instalação, uso, arquitetura, troubleshooting
├── models/              # Modelo ONNX (baixado automaticamente)
├── main-light.py        # Ponto de entrada
├── run_api.py           # Inicia API localmente (sem Docker)
├── docker-compose.yml
├── Dockerfile.api
└── Dockerfile.dashboard
```

---

## Testes

```bash
pytest tests/ -v
# 46 passed
```

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/INSTALL.md](docs/INSTALL.md) | Instalação detalhada e configuração |
| [docs/USAGE.md](docs/USAGE.md) | Como usar, scripts disponíveis, API |
| [docs/ARQUITETURA_HIBRIDA.md](docs/ARQUITETURA_HIBRIDA.md) | Diagrama e decisões de arquitetura |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Problemas comuns e soluções |

---

## Próximas features

- Rastreamento simultâneo de múltiplas faces
- Análise de micro-expressões
- Alertas configuráveis (webhook quando pessoa específica é detectada)
- Export de relatórios de presença em CSV/PDF

---

## Autor

**Jonas Ferreira da Silva**
- GitHub: [@jonasferreira-silva1](https://github.com/jonasferreira-silva1)
- LinkedIn: [jonas-silva01](https://www.linkedin.com/in/jonas-silva01/)

---

## Licença

MIT — veja [LICENSE](LICENSE).
