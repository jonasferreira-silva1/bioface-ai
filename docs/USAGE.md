# Como Usar — BioFace AI

## Iniciar o sistema

```bash
# Modo standalone (sem API)
python main-light.py

# Modo híbrido (envia dados para a API em Docker)
python main-light.py --api-url http://localhost:8000
```

A janela de vídeo abre automaticamente. Pressione `Q` para fechar.

---

## Cadastrar uma pessoa

```bash
python scripts/register_face.py --name "Jonas Silva"
```

1. Uma janela da câmera abre
2. Posicione o rosto na frente da câmera
3. Pressione `ESPAÇO` para capturar
4. Pressione `ESC` para cancelar

O sistema impede cadastros duplicados automaticamente.

---

## Gerenciar usuários

```bash
# Listar todos os usuários cadastrados
python scripts/list_all_users.py

# Deletar um usuário pelo ID
python scripts/delete_user.py --id 3

# Deletar todos os embeddings de um usuário (mantém o cadastro)
python scripts/delete_all_user_embeddings.py --id 3

# Mesclar dois usuários (útil quando a mesma pessoa foi cadastrada duas vezes)
python scripts/merge_users.py --source 4 --target 2

# Limpar embeddings órfãos (sem usuário associado)
python scripts/cleanup_orphan_embeddings.py
```

---

## Testar detecção de emoções

```bash
python scripts/test_emotion_detection.py
```

Mostra as métricas geométricas em tempo real no canto da tela — útil para entender o que o sistema está detectando.

---

## Diagnosticar problemas de reconhecimento

```bash
python scripts/diagnose_recognition.py
python scripts/debug_recognition.py
```

---

## Emoções detectadas

| Emoção | Ícone | Cor |
|--------|-------|-----|
| Feliz | `:)` | Verde |
| Triste | `:(` | Azul |
| Raiva | `>:(` | Vermelho |
| Surpresa | `:O` | Amarelo |
| Neutro | `:\|` | Cinza |

A detecção usa um modelo ONNX (FER+) combinado com análise geométrica dos landmarks do MediaPipe para maior precisão em raiva e surpresa.

---

## Banco de dados

O banco SQLite (`bioface.db`) é criado automaticamente na raiz do projeto.

```bash
# Consultar diretamente (requer sqlite3 instalado)
sqlite3 bioface.db "SELECT id, name, created_at FROM users;"
```

Para backup:
```bash
copy bioface.db bioface_backup.db   # Windows
cp bioface.db bioface_backup.db     # Linux/Mac
```

---

## API REST

Com os serviços Docker rodando (`docker-compose up`), a API fica disponível em `http://localhost:8000`.

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/health` | Status do sistema |
| `GET` | `/api/users` | Lista usuários |
| `POST` | `/api/users` | Cria usuário |
| `GET` | `/api/users/{id}` | Detalhes do usuário |
| `DELETE` | `/api/users/{id}` | Deleta usuário |
| `GET` | `/api/emotions/history` | Histórico de emoções |
| `GET` | `/api/stats` | Estatísticas gerais |
| `WS` | `/ws/detections` | Stream de detecções em tempo real |
| `WS` | `/ws/emotions` | Stream de emoções em tempo real |

Documentação interativa (Swagger): http://localhost:8000/docs

### Exemplos rápidos

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
