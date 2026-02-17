# 🛣️ Roadmap Técnico Detalhado - BioFace AI

**Versão:** 1.0  
**Data:** 2026-02-16

---

## 📋 Visão Geral

Este documento detalha as tarefas técnicas específicas para completar o projeto BioFace AI, organizadas por fases e prioridades.

---

## ✅ Fase 2: Reconhecimento Facial (COMPLETA)

### Tarefas Concluídas

- [x] Implementar `FaceRecognizer` com geração de embeddings
- [x] Criar modelos de banco de dados (User, FaceEmbedding)
- [x] Implementar repositório de dados com CRUD completo
- [x] Integrar reconhecimento no pipeline principal
- [x] Criar script de cadastro de faces
- [x] Implementar estabilização temporal de identificação
- [x] Otimizar geração de embeddings (múltiplas características)
- [x] Mudar de distância euclidiana para cosseno
- [x] Implementar validação de ambiguidade inteligente
- [x] Priorizar usuários com nome sobre anônimos
- [x] Prevenir cadastros duplicados
- [x] Criar scripts de gerenciamento de usuários
- [x] Limpar embeddings órfãos
- [x] Melhorar lógica de estabilização temporal

---

## 🔄 Fase 3: Classificação de Emoções (PRÓXIMA)

### Prioridade: ALTA

### Tarefas Técnicas

#### 3.1 Preparação do Ambiente

- [ ] **Escolher modelo de emoções**
  - [ ] Pesquisar modelos pré-treinados disponíveis
  - [ ] Avaliar: FER2013, AffectNet, EmotiW
  - [ ] Decidir formato: ONNX, TensorFlow Lite, ou PyTorch
  - [ ] Testar performance e precisão

- [ ] **Configurar dependências**
  - [ ] Adicionar bibliotecas necessárias ao `requirements.txt`
  - [ ] Criar `requirements-full.txt` (com TensorFlow/ONNX)
  - [ ] Documentar instalação

#### 3.2 Implementação do Classificador

- [ ] **Criar módulo `EmotionClassifier`**
  - [ ] Classe base em `src/ai/emotion_classifier.py`
  - [ ] Carregar modelo pré-treinado
  - [ ] Pré-processamento de imagens (normalização)
  - [ ] Método `predict(face_image)` → (emotion, confidence)
  - [ ] Mapeamento de emoções (EN → PT)

- [ ] **Integrar com pipeline**
  - [ ] Adicionar classificação em `main_light.py`
  - [ ] Processar emoção após detecção facial
  - [ ] Exibir emoção na tela
  - [ ] Salvar emoção no banco (`EmotionLog`)

#### 3.3 Banco de Dados

- [ ] **Atualizar modelo `EmotionLog`**
  - [ ] Adicionar campos necessários
  - [ ] Criar migração de banco
  - [ ] Índices para consultas rápidas

- [ ] **Implementar repositório**
  - [ ] Método `save_emotion(user_id, emotion, confidence)`
  - [ ] Método `get_emotion_history(user_id, start_date, end_date)`
  - [ ] Método `get_emotion_stats(user_id)`

#### 3.4 Visualização

- [ ] **Exibir emoção na tela**
  - [ ] Adicionar texto com emoção detectada
  - [ ] Cores diferentes por emoção
  - [ ] Ícones ou emojis (opcional)

- [ ] **Gráficos de emoções**
  - [ ] Gráfico de linha (emoções ao longo do tempo)
  - [ ] Gráfico de pizza (distribuição de emoções)
  - [ ] Estatísticas por usuário

#### 3.5 Otimizações

- [ ] **Performance**
  - [ ] Processar emoção a cada N frames (não todos)
  - [ ] Cache de resultados recentes
  - [ ] Processamento assíncrono (opcional)

- [ ] **Configuração**
  - [ ] Adicionar flags no `.env`:
    - `ENABLE_EMOTION_CLASSIFICATION=true/false`
    - `EMOTION_PROCESSING_INTERVAL=5` (frames)

### Estimativa: 2-3 semanas

---

## 🔄 Fase 4: API e Dashboard (MÉDIO PRAZO)

### Prioridade: MÉDIA

### Tarefas Técnicas

#### 4.1 API REST (FastAPI)

- [ ] **Estrutura base**
  - [ ] Criar `src/api/` directory
  - [ ] `main.py`: Aplicação FastAPI
  - [ ] `routes/`: Endpoints organizados
  - [ ] `models.py`: Modelos Pydantic
  - [ ] `dependencies.py`: Dependências (DB, etc)

- [ ] **Endpoints de Usuários**
  - [ ] `GET /api/users` - Listar usuários
  - [ ] `GET /api/users/{id}` - Detalhes do usuário
  - [ ] `POST /api/users` - Criar usuário
  - [ ] `PUT /api/users/{id}` - Atualizar usuário
  - [ ] `DELETE /api/users/{id}` - Deletar usuário

- [ ] **Endpoints de Reconhecimento**
  - [ ] `POST /api/recognize` - Reconhecer face (upload imagem)
  - [ ] `GET /api/recognize/history` - Histórico de reconhecimentos

- [ ] **Endpoints de Emoções**
  - [ ] `GET /api/emotions/{user_id}` - Histórico de emoções
  - [ ] `GET /api/emotions/{user_id}/stats` - Estatísticas
  - [ ] `GET /api/emotions/{user_id}/chart` - Dados para gráfico

- [ ] **Autenticação**
  - [ ] JWT tokens
  - [ ] Login/logout
  - [ ] Proteção de rotas

- [ ] **Documentação**
  - [ ] Swagger UI automático
  - [ ] Documentação de cada endpoint

#### 4.2 WebSocket

- [ ] **Conexão WebSocket**
  - [ ] Endpoint `/ws` para conexão
  - [ ] Broadcast de detecções em tempo real
  - [ ] Notificações de eventos

- [ ] **Mensagens**
  - [ ] Tipo: `face_detected`
  - [ ] Tipo: `person_identified`
  - [ ] Tipo: `emotion_detected`

#### 4.3 Dashboard Web

- [ ] **Escolher tecnologia**
  - [ ] Opção 1: Streamlit (rápido, Python)
  - [ ] Opção 2: React (mais flexível)
  - [ ] Decisão baseada em requisitos

- [ ] **Páginas principais**
  - [ ] Dashboard principal (visão geral)
  - [ ] Lista de usuários
  - [ ] Detalhes do usuário
  - [ ] Gráficos de emoções
  - [ ] Configurações

- [ ] **Componentes**
  - [ ] Player de vídeo em tempo real
  - [ ] Gráficos interativos (Chart.js ou similar)
  - [ ] Tabelas de dados
  - [ ] Formulários de cadastro

#### 4.4 Banco de Dados

- [ ] **Migração para PostgreSQL** (opcional)
  - [ ] Configurar PostgreSQL
  - [ ] Migrar dados do SQLite
  - [ ] Atualizar `DATABASE_URL`

### Estimativa: 4-6 semanas

---

## 🔄 Fase 5: Motor de Regras (LONGO PRAZO)

### Prioridade: BAIXA

### Tarefas Técnicas

#### 5.1 Sistema de Regras

- [ ] **Estrutura base**
  - [ ] Criar `src/rules/` directory
  - [ ] `rule_engine.py`: Motor de regras
  - [ ] `rule_parser.py`: Parser de regras (YAML/JSON)
  - [ ] `actions.py`: Ações executáveis

- [ ] **Tipos de Regras**
  - [ ] Regra: "Se pessoa X detectada → ação Y"
  - [ ] Regra: "Se emoção Z detectada → ação Y"
  - [ ] Regra: "Se padrão temporal → ação Y"

- [ ] **Ações**
  - [ ] Enviar notificação
  - [ ] Salvar log
  - [ ] Chamar webhook
  - [ ] Enviar email/SMS

#### 5.2 Integrações

- [ ] **Webhooks**
  - [ ] Configurar URLs de webhook
  - [ ] Enviar payload JSON

- [ ] **Email**
  - [ ] SMTP configurável
  - [ ] Templates de email

- [ ] **SMS** (opcional)
  - [ ] Integração com Twilio ou similar

### Estimativa: 3-4 semanas

---

## 🔄 Fase 6: Melhorias Contínuas

### Prioridade: CONTÍNUA

### Tarefas Técnicas

#### 6.1 Modelos Mais Robustos

- [ ] **FaceNet via ONNX**
  - [ ] Pesquisar modelo FaceNet em ONNX
  - [ ] Integrar ONNX Runtime
  - [ ] Comparar precisão com atual
  - [ ] Migrar se melhor

- [ ] **Modelos de Emoção Melhores**
  - [ ] Pesquisar modelos state-of-the-art
  - [ ] Treinar modelo customizado (opcional)
  - [ ] Ensemble de modelos

#### 6.2 Performance

- [ ] **Otimização de Banco**
  - [ ] Adicionar índices nas colunas de busca
  - [ ] Otimizar queries de embedding
  - [ ] Implementar cache de resultados

- [ ] **Processamento Paralelo**
  - [ ] Múltiplas faces simultâneas
  - [ ] Threading para I/O
  - [ ] Processamento assíncrono

- [ ] **GPU Acceleration** (opcional)
  - [ ] Suporte a CUDA
  - [ ] TensorRT para modelos

#### 6.3 Múltiplas Faces

- [ ] **Detecção Simultânea**
  - [ ] Processar todas as faces detectadas
  - [ ] Identificar cada pessoa
  - [ ] Rastrear pessoas entre frames

- [ ] **Análise de Interações**
  - [ ] Detectar proximidade
  - [ ] Análise de grupos

#### 6.4 Segurança e Privacidade

- [ ] **Criptografia**
  - [ ] Criptografar embeddings no banco
  - [ ] Chaves de criptografia configuráveis

- [ ] **LGPD**
  - [ ] Anonimização de dados
  - [ ] Direito ao esquecimento
  - [ ] Exportação de dados

- [ ] **Controle de Acesso**
  - [ ] Roles e permissões
  - [ ] Auditoria de ações

#### 6.5 Interface de Usuário

- [ ] **GUI para Cadastro**
  - [ ] Tkinter ou PyQt
  - [ ] Interface visual para cadastro
  - [ ] Visualização de embeddings

- [ ] **Configurações Visuais**
  - [ ] Painel de configurações
  - [ ] Ajuste de thresholds
  - [ ] Visualização de estatísticas

### Estimativa: Contínua

---

## 📊 Priorização

### 🔴 Crítico (Fazer Agora)

1. Finalizar estabilização de identificação
2. Testes extensivos com múltiplos usuários
3. Documentação completa

### 🟡 Importante (Próximas 2-4 Semanas)

1. Fase 3: Classificação de Emoções
2. Melhorias de performance
3. GUI para cadastro

### 🟢 Desejável (1-3 Meses)

1. Fase 4: API e Dashboard
2. Múltiplas faces
3. Modelos mais robustos

### ⚪ Opcional (Longo Prazo)

1. Fase 5: Motor de Regras
2. GPU acceleration
3. Análise de interações

---

## 📝 Notas de Implementação

### Padrões de Código

- Seguir PEP 8
- Type hints em todas as funções
- Docstrings em todas as classes/métodos
- Logging estruturado
- Tratamento de erros robusto

### Testes

- Unit tests para cada módulo
- Integration tests para pipeline
- Testes de performance
- Testes com dados reais

### Documentação

- Atualizar README.md
- Documentar cada nova funcionalidade
- Criar tutoriais
- Manter este roadmap atualizado

---

## 🎯 Milestones

### Milestone 1: Reconhecimento Estável ✅
**Data:** 2026-02-16  
**Status:** Completo

### Milestone 2: Emoções Funcionais
**Data Alvo:** 2026-03-15  
**Status:** Planejado

### Milestone 3: API Completa
**Data Alvo:** 2026-04-30  
**Status:** Planejado

### Milestone 4: Dashboard Interativo
**Data Alvo:** 2026-05-31  
**Status:** Planejado

### Milestone 5: Produção
**Data Alvo:** 2026-07-31  
**Status:** Planejado

---

**Última atualização:** 2026-02-16  
**Próxima revisão:** Semanalmente ou após cada milestone

