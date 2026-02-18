# 🏗️ Arquitetura Híbrida - BioFace AI

**Status:** ✅ Implementado

---

## 📋 Visão Geral

O BioFace AI utiliza uma **arquitetura híbrida** que combina:
- **Processamento Edge (Host)**: Pipeline de câmera roda nativamente
- **Serviços (Docker)**: API e Dashboard rodam em containers

Esta arquitetura oferece:
- ✅ **Acesso direto à câmera** (funciona no Windows)
- ✅ **Deploy fácil** (API/Dashboard containerizados)
- ✅ **Baixa latência** (processamento local)
- ✅ **Escalabilidade** (múltiplas câmeras → mesma API)

---

## 🎯 Por Que Arquitetura Híbrida?

### Problema Original
- Docker no Windows não acessa câmera diretamente (`/dev/video0` é Linux)
- Workarounds complexos (usbipd-win, WSL2) são difíceis de configurar

### Solução
- **Câmera no Host**: Pipeline roda nativamente, acessa câmera diretamente
- **Serviços no Docker**: API e Dashboard isolados, fáceis de deploy
- **Comunicação via HTTP/WebSocket**: Pipeline envia dados para API

---

## 📊 Diagrama da Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    HOST (Windows/Linux)                 │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Pipeline de Câmera (main_light.py)              │  │
│  │  - Acessa câmera diretamente                     │  │
│  │  - Processa frames                               │  │
│  │  - Reconhece faces                               │  │
│  │  - Detecta emoções                               │  │
│  │  - Salva no banco local                          │  │
│  │  └─── HTTP/WebSocket ────┐                      │  │
│  └──────────────────────────┼──────────────────────┘  │
│                              │                          │
└──────────────────────────────┼──────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────┐
│                    Docker Containers                     │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐  │
│  │   API FastAPI        │  │  Dashboard Streamlit  │  │
│  │   (Porta 8000)       │  │  (Porta 8501)        │  │
│  │                      │  │                      │  │
│  │  - Endpoints REST    │  │  - Visualizações     │  │
│  │  - WebSocket         │  │  - Gráficos          │  │
│  │  - Banco SQLite      │  │  - Estatísticas      │  │
│  └──────────────────────┘  └──────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Como Usar

### Modo 1: Standalone (Sem API)

Pipeline roda sozinho, salva tudo localmente:

```bash
python main-light.py
```

### Modo 2: Híbrido (Com API)

**Terminal 1: Inicia serviços Docker**
```bash
docker-compose -f docker-compose.services.yml up
```

**Terminal 2: Inicia pipeline (conectado à API)**
```bash
python main-light.py --api-url http://localhost:8000
```

O pipeline:
- ✅ Processa câmera localmente
- ✅ Salva no banco local
- ✅ Envia detecções para API via WebSocket
- ✅ API distribui para clientes conectados (Dashboard, etc.)

---

## 📁 Estrutura de Arquivos

```
bioface-ai/
├── docker-compose.services.yml  # Docker Compose para serviços
├── Dockerfile.api               # Container da API
├── Dockerfile.dashboard         # Container do Dashboard
├── requirements-api.txt         # Dependências da API
├── requirements-dashboard.txt   # Dependências do Dashboard
├── main-light.py                # Pipeline (roda no host)
├── run_api.py                   # Script para rodar API
├── dashboard.py                 # Dashboard Streamlit
└── src/
    ├── api/
    │   ├── client.py            # Cliente HTTP/WebSocket
    │   ├── main.py              # API FastAPI
    │   └── ...
    └── main_light.py            # Pipeline principal
```

---

## 🔧 Configuração

### Variáveis de Ambiente

**Pipeline (Host):**
```bash
# .env ou variáveis de ambiente
API_URL=http://localhost:8000  # Opcional: URL da API
```

**API (Docker):**
```yaml
# docker-compose.services.yml
environment:
  - DATABASE_URL=sqlite:///./bioface.db
  - CORS_ORIGINS=*
```

**Dashboard (Docker):**
```yaml
environment:
  - API_BASE_URL=http://api:8000
```

---

## 🌐 Comunicação

### HTTP REST
- Pipeline pode consultar API: `GET /api/users`, `GET /api/stats`
- Dashboard consulta API: Todas as rotas REST

### WebSocket
- Pipeline envia detecções: `WS /ws/detections`
- Pipeline envia emoções: `WS /ws/emotions`
- Dashboard pode conectar para receber atualizações em tempo real

### Banco de Dados
- Pipeline salva localmente: `bioface.db` (host)
- API acessa via volume: `./bioface.db:/app/bioface.db`

---

## ✅ Vantagens

1. **Funciona no Windows**: Câmera acessível sem workarounds
2. **Deploy Fácil**: API/Dashboard em containers
3. **Baixa Latência**: Processamento local
4. **Escalável**: Múltiplas câmeras → mesma API
5. **Flexível**: Pode rodar standalone ou conectado

---

## 📝 Notas

- **Banco de Dados**: Compartilhado via volume Docker
- **Rede**: Containers na mesma rede Docker (`bioface-network`)
- **Portas**: 
  - API: `8000`
  - Dashboard: `8501`
- **Performance**: WebSocket não bloqueia pipeline (assíncrono)

---

**Última atualização:** 2026-02-17

