# 🧠 BioFace AI – Real-Time Facial Recognition System

> Sistema inteligente de reconhecimento facial e análise comportamental em tempo real.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Instalação Rápida](#-instalação-rápida)
- [Uso](#-uso)
- [Documentação](#-documentação)
- [Roadmap](#-roadmap)
- [Áreas de Desenvolvimento](#-áreas-de-desenvolvimento-e-melhorias-futuras)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

### A História

Em um mundo onde a tecnologia de reconhecimento facial está cada vez mais presente, percebemos uma grande lacuna: **soluções acessíveis e transparentes são raras**. As opções disponíveis no mercado são:

- 🔒 **Proprietárias e caras** - Custos proibitivos para projetos pessoais e educacionais
- ⚫ **Caixas pretas** - Não sabemos como funcionam internamente
- 🏢 **Orientadas a grandes empresas** - Não atendem necessidades específicas
- 🔐 **Sem controle total** - Dependência de serviços externos e APIs

**BioFace AI nasceu da necessidade de ter um sistema de reconhecimento facial:**
- ✅ **Completamente open-source** - Você vê e controla todo o código
- ✅ **Leve e eficiente** - Funciona em computadores comuns
- ✅ **Modular e extensível** - Fácil de customizar para suas necessidades
- ✅ **Transparente e ético** - Você sabe exatamente o que está acontecendo
- ✅ **Sem dependências externas** - Funciona offline, sem APIs de terceiros

### Por Que Estamos Trabalhando Nisso?

Este projeto foi desenvolvido com o objetivo de:

1. **Democratizar a tecnologia** - Tornar reconhecimento facial acessível para todos
2. **Educação e aprendizado** - Servir como referência de implementação completa
3. **Controle e privacidade** - Dados ficam no seu ambiente, sem enviar para nuvem
4. **Customização** - Adaptar o sistema para necessidades específicas
5. **Base para projetos maiores** - Fundação para sistemas mais complexos

### O Intuito Final

O **BioFace AI** visa ser uma **solução completa e profissional** de reconhecimento facial que:

- 🎓 **Educa** - Código bem documentado e estruturado para aprendizado
- 🛠️ **Empodera** - Dá controle total sobre a tecnologia
- 🚀 **Evolui** - Base sólida para projetos futuros (análise comportamental, segurança, automação)
- 🌍 **Contribui** - Open-source para a comunidade crescer e melhorar

**Em resumo:** Queremos provar que tecnologia avançada pode ser **acessível, transparente e controlada por você**.

---

## 📖 Sobre o Projeto

### A História por Trás do BioFace AI

Em um mundo onde a tecnologia de reconhecimento facial está cada vez mais presente em nosso dia a dia, identificamos uma lacuna significativa: **a falta de soluções acessíveis, transparentes e controláveis**.

#### O Problema que Observamos

Sistemas tradicionais de reconhecimento facial no mercado apresentam desafios reais:

- 💰 **Custos Proibitivos** - Licenças caras que impedem projetos pessoais, educacionais e de pequeno porte
- ⚫ **Caixas Pretas** - Funcionamento interno desconhecido, sem transparência sobre como os dados são processados
- 🏢 **Orientação Corporativa** - Soluções focadas apenas em grandes empresas, ignorando necessidades específicas
- 🔐 **Dependência Externa** - APIs de terceiros que podem mudar políticas, aumentar custos ou descontinuar serviços
- 🚫 **Falta de Customização** - Impossibilidade de adaptar o sistema para casos de uso específicos

#### Nossa Missão

O **BioFace AI** foi criado para quebrar essas barreiras, oferecendo uma alternativa que é:

- ✅ **Completamente Open-Source** - Todo o código está disponível para inspeção, aprendizado e modificação
- ✅ **Leve e Eficiente** - Funciona em computadores comuns, sem necessidade de hardware especializado
- ✅ **Modular e Extensível** - Arquitetura pensada para facilitar customizações e extensões
- ✅ **Transparente e Ético** - Você sabe exatamente o que está acontecendo em cada etapa do processo
- ✅ **Independente** - Funciona completamente offline, sem dependência de serviços externos ou APIs

#### Por Que Estamos Trabalhando Nisso?

Este projeto nasceu de necessidades reais:

1. **Democratização da Tecnologia** - Tornar reconhecimento facial acessível para estudantes, pesquisadores e desenvolvedores
2. **Educação e Aprendizado** - Servir como referência completa de implementação, com código bem documentado e estruturado
3. **Controle e Privacidade** - Garantir que os dados permaneçam no seu ambiente, sem envio para nuvens de terceiros
4. **Flexibilidade** - Permitir adaptação do sistema para necessidades específicas (segurança, automação, análise comportamental)
5. **Base Sólida** - Criar uma fundação robusta para projetos maiores e mais complexos

#### O Intuito Final

Nosso objetivo é construir uma **solução completa e profissional** que:

- 🎓 **Educa** - Código documentado e estruturado serve como material de aprendizado para a comunidade
- 🛠️ **Empodera** - Dá controle total sobre a tecnologia, permitindo entender e modificar cada componente
- 🚀 **Evolui** - Serve como base sólida para projetos futuros (análise comportamental avançada, sistemas de segurança, automação residencial)
- 🌍 **Contribui** - Open-source permite que a comunidade cresça, melhore e adapte o projeto para suas necessidades

**Em essência:** Queremos provar que tecnologia avançada de reconhecimento facial pode ser **acessível, transparente, controlável e construída pela comunidade**.

---

## 🎯 Visão Geral

**🏗️ Arquitetura baseada em microsserviços com API FastAPI + Dashboard Streamlit, containerizados com Docker e orquestrados via Docker Compose.**

O **BioFace AI** é um sistema completo de reconhecimento facial que combina:

- ✅ **Detecção facial em tempo real** usando MediaPipe
- ✅ **Reconhecimento facial** via embeddings (128 dimensões)
- ✅ **Classificação de emoções** (opcional, com DeepFace ou heurísticas)
- ✅ **Banco de dados SQLite** para armazenamento
- ✅ **Interface visual** em tempo real
- ✅ **Scripts de gerenciamento** para cadastro e consulta
- ✅ **API REST FastAPI** com documentação automática (Swagger)
- ✅ **Dashboard Streamlit** para visualização e gerenciamento
- ✅ **Arquitetura baseada em microsserviços** com API FastAPI + Dashboard Streamlit, containerizados com Docker e orquestrados via Docker Compose

---

## ✨ Funcionalidades

### Core
- **Detecção facial** com MediaPipe Face Mesh (468 landmarks)
- **Reconhecimento facial** usando embeddings robustos
- **Estabilização temporal** (evita oscilação)
- **Prevenção de duplicatas** (não permite cadastros duplicados)

### Classificação de Emoções
- **Modo Light**: Heurísticas baseadas em landmarks (rápido, sem TensorFlow)
- **Modo DeepFace**: Modelos pré-treinados (mais preciso, requer TensorFlow)

### Gerenciamento
- Cadastro de pessoas com nome
- Listagem de usuários cadastrados
- Mesclagem de usuários
- Limpeza de embeddings órfãos
- Diagnóstico de problemas

### API e Dashboard
- **API REST FastAPI** com endpoints para usuários, emoções e estatísticas
- **WebSocket** para streaming em tempo real de detecções e emoções
- **Dashboard Streamlit** com visualizações interativas
- **Documentação automática** (Swagger/OpenAPI) em `/docs`
- **Arquitetura híbrida**: Pipeline no host, API/Dashboard em Docker

---

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.9+
- Webcam conectada
- 4GB+ RAM (8GB recomendado)
- Docker (opcional, para API e Dashboard)

### Modo Standalone (Recomendado para Windows)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/bioface-ai.git
cd bioface-ai

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute pipeline
python main-light.py
```

### Modo Híbrido (API + Dashboard em Docker)

**Terminal 1: Inicia serviços Docker**
```bash
docker-compose -f docker-compose.services.yml up
```

**Terminal 2: Inicia pipeline conectado à API**
```bash
python main-light.py --api-url http://localhost:8000
```

**Acesse:**
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

> **📝 Arquitetura de Microsserviços:** O BioFace AI utiliza uma **arquitetura baseada em microsserviços** com API FastAPI + Dashboard Streamlit, containerizados com Docker e orquestrados via Docker Compose.
>
> **Características da arquitetura:**
> - **Modo API/Dashboard**: 100% Dockerizado para fácil deploy e escalabilidade
> - **Modo Processamento (Edge)**: Recomenda-se execução nativa (Python direto no host) para acesso direto à câmera, garantindo a menor latência possível no processamento de frames
> - **Comunicação**: HTTP REST e WebSocket para streaming em tempo real
> - **Orquestração**: Docker Compose para gerenciamento simplificado dos serviços
>
> Esta arquitetura funciona perfeitamente no Windows, onde Docker não acessa câmera diretamente. Veja [docs/ARQUITETURA_HIBRIDA.md](docs/ARQUITETURA_HIBRIDA.md) para detalhes.

**⚠️ Importante:** O sistema requer **NumPy < 2.0** e **protobuf < 5.0**. Se houver conflitos, consulte [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

Para instalação detalhada, veja [docs/INSTALL.md](docs/INSTALL.md).

---

## 💻 Uso

### Executar Sistema

```bash
# Versão leve (recomendada, sem TensorFlow)
python main-light.py

# Versão completa (requer TensorFlow)
python main.py
```

### Cadastrar Pessoa

```bash
python scripts/register_face.py --name "Jonas Silva"
```

### Listar Usuários

```bash
python scripts/list_all_users.py
```

### Mais Comandos

Veja [docs/USAGE.md](docs/USAGE.md) para guia completo de uso.

---

## 📚 Documentação

Toda a documentação está na pasta [`docs/`](docs/):

- **[docs/README.md](docs/README.md)** - Índice da documentação
- **[docs/INSTALL.md](docs/INSTALL.md)** - Instalação completa
- **[docs/USAGE.md](docs/USAGE.md)** - Como usar o sistema
- **[docs/CADASTRO_E_CONSULTA.md](docs/CADASTRO_E_CONSULTA.md)** - Cadastro e consulta
- **[docs/STATUS.md](docs/STATUS.md)** - Status atual e roadmap
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solução de problemas
- **[docs/DOCKER.md](docs/DOCKER.md)** - Setup com Docker

---

## 🗺️ Roadmap

### ✅ Fase 1 - Core Pipeline (COMPLETA)
- [x] Detecção facial
- [x] Pipeline de processamento
- [x] Interface visual

### ✅ Fase 2 - Reconhecimento Facial (COMPLETA)
- [x] Sistema de embeddings
- [x] Banco de dados
- [x] Cadastro e identificação
- [x] Estabilização temporal

### ✅ Fase 3 - Classificação de Emoções (COMPLETA)
- [x] Classificador leve (heurísticas)
- [x] Integração com DeepFace (opcional)
- [x] Estabilização de emoções

### ✅ Fase 4 - Backend + Dashboard (COMPLETA)
- [x] API FastAPI com endpoints REST
- [x] WebSocket para tempo real
- [x] Dashboard Streamlit
- [x] Visualizações e estatísticas
- [x] Arquitetura híbrida (Docker + Host)
- [x] Documentação automática (Swagger)

### 🔮 Futuro
- [ ] Multi-face tracking
- [ ] Análise de micro-expressões
- [ ] Dashboard React avançado

Veja [docs/STATUS.md](docs/STATUS.md) para detalhes completos.

---

## 🛠️ Stack Tecnológico

### Visão Computacional
- **OpenCV**: Captura e processamento de vídeo
- **MediaPipe**: Detecção facial e landmarks (468 pontos)

### Machine Learning
- **NumPy**: Computação numérica
- **DeepFace** (opcional): Classificação de emoções
- **TensorFlow** (opcional): Apenas se usar DeepFace

### Banco de Dados
- **SQLite**: Banco de dados leve
- **SQLAlchemy**: ORM

### Backend e API
- **FastAPI**: Framework web moderno e rápido
- **WebSockets**: Streaming em tempo real
- **Pydantic**: Validação de dados e configurações
- **Uvicorn**: Servidor ASGI de alta performance

### Dashboard
- **Streamlit**: Framework para dashboards interativos
- **HTTPX**: Cliente HTTP assíncrono

### Utilitários
- **Loguru**: Sistema de logging
- **Docker**: Containerização de serviços
- **Docker Compose**: Orquestração de containers

---

## 📁 Estrutura do Projeto

```
bioface-ai/
├── src/
│   ├── main_light.py          # Pipeline principal (leve)
│   ├── vision/                # Visão computacional
│   ├── ai/                    # IA (reconhecimento + emoções)
│   ├── database/              # Banco de dados
│   ├── api/                   # API FastAPI
│   │   ├── main.py            # Aplicação FastAPI
│   │   ├── routes/            # Rotas da API
│   │   ├── websocket_manager.py
│   │   └── client.py          # Cliente HTTP/WebSocket
│   ├── exceptions.py          # Exceções customizadas
│   └── utils/                 # Utilitários
├── tests/                     # Testes unitários e de integração
│   ├── test_exceptions.py     # Testes de exceções
│   ├── test_camera_exceptions.py
│   ├── test_database_exceptions.py
│   └── test_face_recognizer_exceptions.py
├── scripts/                   # Scripts de gerenciamento
├── docs/                      # Documentação completa
├── dashboard.py               # Dashboard Streamlit
├── run_api.py                 # Script para rodar API
├── docker-compose.services.yml # Docker Compose (serviços)
├── Dockerfile.api             # Container da API
├── Dockerfile.dashboard       # Container do Dashboard
├── requirements.txt           # Dependências principais
├── requirements-api.txt       # Dependências da API
├── requirements-dashboard.txt # Dependências do Dashboard
├── pytest.ini                 # Configuração do Pytest
└── README.md                  # Este arquivo
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👤 Autor

**JONAS FERREIRA DA SILVA**
- GitHub: [@jonasferreira-silva1](https://github.com/jonasferreira-silva1)
- LinkedIn: [Seu Perfil](https://www.linkedin.com/in/jonas-silva01/)

---

## 🎯 Áreas de Desenvolvimento e Melhorias Futuras

Este projeto está em desenvolvimento ativo. Identificamos áreas críticas para elevar o BioFace AI ao nível de **projeto production-ready** que impressiona recrutadores técnicos.

### ✅ O Que Já Temos (Fundação Sólida)

- ✅ **Sistema de Logging Robusto** - Loguru com rotação, compressão e níveis configuráveis
- ✅ **Tratamento de Erros Básico** - Try/except em operações críticas (banco de dados, câmera)
- ✅ **Validação de Dados** - Pydantic para configurações e validação de tipos
- ✅ **Arquitetura Modular** - Código organizado e separado por responsabilidades
- ✅ **Documentação Completa** - Guias, troubleshooting e documentação técnica

### 🚧 O Que Estamos Trabalhando (Próximas Prioridades)

#### 1. 🧪 Testes Unitários e de Integração ✅ **IMPLEMENTADO**

**Status:** ✅ **Implementado** - Estrutura completa criada

**O que foi implementado:**
- ✅ Estrutura completa de testes com Pytest (`tests/` directory)
- ✅ Testes unitários para exceções customizadas (`test_exceptions.py`)
- ✅ Testes de integração para componentes críticos:
  - ✅ `Camera` - Exceções de câmera e reconexão
  - ✅ `DatabaseRepository` - Exceções de banco e recuperação
  - ✅ `FaceRecognizer` - Exceções de reconhecimento facial
- ✅ Fixtures compartilhadas (`conftest.py`)
- ✅ Configuração do Pytest (`pytest.ini`)
- ✅ Documentação de testes (`tests/README.md`)

**Cobertura atual:**
- `src/exceptions.py`: ~95% ✅
- Componentes críticos: Em progresso 🔄

**Próximos passos:**
- [ ] Expandir testes para `EmotionClassifier`
- [ ] Testes de integração do pipeline completo
- [ ] Atingir cobertura > 80%
- [ ] CI/CD com testes automáticos

**Como executar:**
```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_exceptions.py
```

Veja [tests/README.md](tests/README.md) para documentação completa.

**Impacto:** ✅ Valida que exceções funcionam exatamente como documentado!

---

#### 2. 🛡️ Tratamento de Erros Avançado 🔄

**Status:** Parcialmente implementado - **Melhorias necessárias**

**O que já temos:**
- ✅ Try/except em operações de banco de dados
- ✅ Logging de erros com contexto
- ✅ Validação de entrada de dados
- ✅ Tratamento básico de câmera

**O que falta (cenários críticos):**
- [ ] **Desconexão de câmera** - Reconexão automática
- [ ] **Corrupção de banco SQLite** - Recuperação e backup
- [ ] **Retry logic** - Para operações críticas com backoff exponencial
- [ ] **Exceções customizadas** - `CameraDisconnectedError`, `DatabaseCorruptedError`
- [ ] **Health checks** - Monitoramento periódico de componentes
- [ ] **Circuit breaker** - Para componentes opcionais (DeepFace, TensorFlow)

**Exemplo do que implementaremos:**
```python
# Tratamento robusto de desconexão de câmera
try:
    frame = camera.read()
except CameraDisconnectedError:
    logger.warning("Câmera desconectada, tentando reconectar...")
    camera.reconnect(max_retries=3)
    continue
except DatabaseCorruptedError:
    logger.error("Banco corrompido, tentando recuperar...")
    database.recover_from_backup()
```

**Por que é importante:** Demonstra maturidade e preparação para cenários reais de produção.

---

#### 3. 🌐 API REST e Dashboard (Fase 4) ✅ **IMPLEMENTADO**

**Status:** ✅ **Implementado** - Sistema completo de API e Dashboard

**O que foi implementado:**

**API FastAPI:**
- ✅ `GET /api/users` - Listar usuários cadastrados
- ✅ `POST /api/users` - Cadastrar novo usuário
- ✅ `GET /api/users/{id}` - Detalhes do usuário
- ✅ `DELETE /api/users/{id}` - Deletar usuário
- ✅ `GET /api/emotions` - Histórico de emoções
- ✅ `GET /api/stats` - Estatísticas e métricas
- ✅ `GET /api/health` - Health check do sistema
- ✅ Documentação automática (Swagger/OpenAPI) em `/docs`

**WebSocket para Tempo Real:**
- ✅ `/ws/detections` - Streaming de detecções em tempo real
- ✅ `/ws/emotions` - Streaming de emoções
- ✅ Notificações de eventos (nova identificação, mudança de emoção)

**Dashboard Streamlit:**
- ✅ Interface interativa para visualização
- ✅ Visualização em tempo real de detecções
- ✅ Gráficos de emoções ao longo do tempo
- ✅ Estatísticas e analytics
- ✅ Gerenciamento de usuários via interface

**Arquitetura:**
- ✅ **Arquitetura baseada em microsserviços** com API FastAPI + Dashboard Streamlit
- ✅ Containerizados com Docker e orquestrados via Docker Compose
- ✅ Arquitetura híbrida: Pipeline no host, serviços em containers
- ✅ Comunicação via HTTP REST e WebSocket

**Impacto:** ✅ Projeto agora demonstra habilidades fullstack completas!

---

#### 4. 📊 Métricas de Performance 📊

**Status:** Coletando dados - **Documentação em desenvolvimento**

**Benchmarks Atuais (estimativas baseadas em testes):**

| Versão | FPS Médio | Uso de RAM | CPU | Precisão Reconhecimento | Latência |
|--------|-----------|------------|-----|------------------------|----------|
| **Light** (sem TensorFlow) | ~25-30 FPS | ~200-400 MB | Baixo | ~85-90% | ~40-50ms |
| **DeepFace** (com TensorFlow) | ~15-20 FPS | ~800-1200 MB | Médio | ~90-95% | ~60-80ms |

**Condições de teste:**
- CPU: Intel i5/i7 ou equivalente
- RAM: 8GB
- Webcam: 720p
- Iluminação: Boa (condições ideais)
- Rosto: Frontal, sem obstruções

**Próximos passos:**
- [ ] Script automatizado de benchmark (`scripts/benchmark.py`)
- [ ] Gráficos de performance no README
- [ ] Comparação com outras soluções (OpenFace, FaceNet)
- [ ] Métricas de latência e throughput
- [ ] Testes em diferentes condições (iluminação, ângulo, distância)

**Por que é importante:** Demonstra orientação a dados e capacidade de otimização baseada em métricas.

---

### 📈 Roadmap de Qualidade

Para tornar o projeto **production-ready** e impressionar recrutadores técnicos:

#### Prioridade Alta (Impacto Imediato)
1. **Testes Unitários** ⏳
   - Implementar suite completa com Pytest
   - Atingir cobertura > 80%
   - CI/CD com testes automáticos

2. **Tratamento de Erros Avançado** 🔄
   - Exceções customizadas
   - Recuperação automática de falhas
   - Health checks e monitoramento

#### Prioridade Média (Transforma em Produto)
3. **API e Dashboard** ✅ **IMPLEMENTADO**
   - FastAPI com endpoints REST
   - WebSocket para tempo real
   - Dashboard profissional
   - Arquitetura de microsserviços com Docker

4. **Métricas Documentadas** 📊
   - Benchmarks automatizados
   - Gráficos e comparações
   - Otimizações baseadas em dados

---

### 💡 Transparência e Honestidade

Este projeto está em **desenvolvimento ativo**. Estamos cientes das áreas que precisam de melhoria e temos um plano claro para implementá-las. Acreditamos que **transparência sobre o estado atual** e **direção clara para o futuro** demonstram maturidade profissional.

**Nossa abordagem:**
- ✅ Código funcional e bem estruturado
- ✅ Documentação completa e honesta
- ✅ Roadmap claro de melhorias
- ✅ Foco em qualidade e profissionalismo

Para detalhes completos sobre melhorias futuras, veja [docs/MELHORIAS_FUTURAS.md](docs/MELHORIAS_FUTURAS.md).

---

## 🆘 Precisa de Ajuda?

1. Consulte [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para problemas comuns
2. Veja [docs/USAGE.md](docs/USAGE.md) para dúvidas de uso
3. Leia [docs/STATUS.md](docs/STATUS.md) para entender o estado atual

---

## 💡 Contribuindo com Melhorias

Se você quer ajudar a tornar o BioFace AI ainda melhor, considere contribuir com:

- 🧪 **Testes** - Ajude a criar testes unitários e de integração
- 🐛 **Tratamento de Erros** - Melhore a robustez do sistema
- 📊 **Métricas** - Adicione benchmarks e comparações
- 🚀 **API** - Implemente endpoints REST ou WebSocket
- 📝 **Documentação** - Melhore guias e exemplos

Veja [docs/STATUS.md](docs/STATUS.md) para mais detalhes sobre o roadmap.

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
