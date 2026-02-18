# 🚀 API e Dashboard - BioFace AI

**Fase 4 Implementada!** ✅

---

## 📋 Visão Geral

A Fase 4 adiciona uma **API REST completa** (FastAPI) e um **Dashboard web** (Streamlit) ao BioFace AI, transformando o projeto de "script Python" para **"produto completo"**.

---

## 🚀 Como Executar

### 1. Iniciar a API

```bash
python run_api.py
```

A API estará disponível em:
- **URL:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs (Swagger UI)
- **Documentação Alternativa:** http://localhost:8000/redoc

### 2. Iniciar o Dashboard

Em outro terminal:

```bash
python run_dashboard.py
```

O dashboard estará disponível em:
- **URL:** http://localhost:8501

---

## 📡 Endpoints da API

### Usuários

- `GET /api/users` - Lista usuários cadastrados
- `POST /api/users` - Cria novo usuário
- `GET /api/users/{id}` - Detalhes de um usuário
- `DELETE /api/users/{id}` - Deleta usuário

### Emoções

- `GET /api/emotions/history` - Histórico de emoções
- `GET /api/emotions/users/{id}/emotions` - Emoções de um usuário

### Estatísticas

- `GET /api/stats` - Estatísticas gerais do sistema

### Health Check

- `GET /api/health` - Status do sistema

### WebSocket

- `WS /ws/detections` - Streaming de detecções em tempo real
- `WS /ws/emotions` - Streaming de emoções em tempo real

---

## 🎨 Dashboard

O dashboard Streamlit oferece:

1. **📊 Visão Geral**
   - Status do sistema
   - Estatísticas gerais
   - Distribuição de emoções
   - Atividade recente

2. **👥 Usuários**
   - Lista de usuários cadastrados
   - Criar novo usuário
   - Detalhes de usuário
   - Contagem de embeddings

3. **😊 Emoções**
   - Histórico de emoções
   - Filtros por usuário
   - Gráficos temporais
   - Distribuição de emoções

4. **📈 Estatísticas**
   - Métricas detalhadas
   - Gráficos interativos
   - Análise de atividade

---

## 🔌 Integração com Pipeline

Para integrar o pipeline principal com a API (enviar dados via WebSocket), você pode:

1. **Modificar `src/main_light.py`** para enviar detecções para a API
2. **Usar a API diretamente** para consultar dados
3. **Conectar via WebSocket** para receber atualizações em tempo real

**Exemplo de integração futura:**

```python
# No pipeline principal, após detectar face:
if websocket_manager:
    await websocket_manager.broadcast_detection({
        "user_id": user_id,
        "user_name": user_name,
        "emotion": emotion,
        "confidence": confidence,
        "bbox": bbox
    })
```

---

## 📚 Documentação da API

A documentação interativa está disponível em:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Testando a API

### Com cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Listar usuários
curl http://localhost:8000/api/users

# Criar usuário
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Jonas Silva"}'

# Estatísticas
curl http://localhost:8000/api/stats
```

### Com Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Listar usuários
response = requests.get("http://localhost:8000/api/users")
print(response.json())

# Criar usuário
response = requests.post(
    "http://localhost:8000/api/users",
    json={"name": "Jonas Silva"}
)
print(response.json())
```

---

## 🎯 Próximos Passos

1. **Integrar pipeline com WebSocket** - Enviar detecções em tempo real
2. **Autenticação** - Adicionar segurança à API
3. **Exportação de dados** - CSV, JSON, etc.
4. **Filtros avançados** - No dashboard e API
5. **Notificações** - Alertas quando eventos ocorrem

---

**Status:** ✅ Fase 4 Implementada!

