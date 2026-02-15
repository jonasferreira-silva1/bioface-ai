# 🧠 BioFace AI – Real-Time Behavioral Intelligence System

> Sistema inteligente de análise comportamental em tempo real através de reconhecimento facial e classificação de emoções.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Decisões de Arquitetura](#-decisões-de-arquitetura)
- [Considerações Éticas](#-considerações-éticas)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Visão Geral

O **BioFace AI** é um sistema completo de análise comportamental que combina:

- ✅ **Detecção facial em tempo real** usando MediaPipe
- ✅ **Classificação de emoções** com modelos de Deep Learning
- ✅ **Reconhecimento facial** via embeddings (FaceNet)
- ✅ **Análise temporal** de padrões comportamentais
- ✅ **Dashboard interativo** para visualização
- ✅ **Motor de regras** para automação baseada em eventos
- ✅ **Conformidade ética** e LGPD

### Problema que Resolve

Sistemas tradicionais de análise comportamental são:
- Caros e complexos
- Não oferecem insights em tempo real
- Não são facilmente customizáveis
- Não consideram aspectos éticos

**BioFace AI** resolve isso oferecendo uma solução open-source, modular e ética.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────┐
│         Video Capture Layer              │
│  (OpenCV - Async Frame Capture)         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Vision Processing Pipeline         │
│  - MediaPipe (Face Detection)          │
│  - Face Normalization                   │
│  - Frame Skipping (Performance)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         AI Models Layer                  │
│  - Emotion Classifier (Pre-trained)     │
│  - Face Recognition (Embeddings)        │
│  - Landmark Extraction                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Event Engine (Rules)               │
│  - Configurable Rules Engine           │
│  - Action Triggers                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Data Layer (SQLite → PostgreSQL)   │
│  - Encrypted Embeddings                 │
│  - Time-series Data                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      API Layer (FastAPI)                │
│  - REST Endpoints                        │
│  - WebSocket (Real-time)                │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Dashboard (Streamlit/React)        │
│  - Real-time Visualization              │
│  - Analytics                            │
└─────────────────────────────────────────┘
```

### Fluxo de Dados

1. **Captura**: Webcam captura frames continuamente
2. **Detecção**: MediaPipe detecta faces e extrai landmarks
3. **Normalização**: Face é recortada e normalizada
4. **IA**: Modelos processam emoção e identidade
5. **Eventos**: Motor de regras avalia condições
6. **Persistência**: Dados são salvos no banco
7. **Visualização**: Dashboard atualiza em tempo real

---

## 🛠️ Stack Tecnológico

### Visão Computacional
- **OpenCV**: Captura e processamento de vídeo
- **MediaPipe**: Detecção facial e landmarks (468 pontos)

### Machine Learning
- **TensorFlow/Keras**: Modelos de Deep Learning
- **scikit-learn**: Utilitários de ML

### Backend
- **FastAPI**: API REST moderna e rápida
- **WebSockets**: Comunicação em tempo real
- **SQLAlchemy**: ORM para banco de dados

### Banco de Dados
- **SQLite**: Desenvolvimento (MVP)
- **PostgreSQL**: Produção

### Frontend
- **Streamlit**: Dashboard rápido (MVP)
- **React + Chart.js**: Dashboard avançado (futuro)

### Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração local

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- Webcam conectada
- 4GB+ RAM recomendado
- GPU opcional (melhora performance)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/bioface-ai.git
cd bioface-ai
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o ambiente**
```bash
# Copie o arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edite o .env conforme necessário
```

5. **Baixe os modelos de IA** (se necessário)
```bash
# Os modelos serão baixados automaticamente na primeira execução
# ou você pode baixá-los manualmente para a pasta models/
```

---

## 💻 Uso

### Execução Básica

```bash
python main.py
```

### Modos de Operação

#### Modo Desenvolvimento
```bash
python main.py --mode dev
```

#### Modo Produção
```bash
python main.py --mode prod
```

#### Modo Anônimo (sem identificação)
```bash
python main.py --anonymous
```

### Parâmetros de Linha de Comando

```bash
python main.py --help

# Exemplos:
python main.py --camera 0 --fps 30
python main.py --skip-frames 3
python main.py --log-level DEBUG
```

---

## 📁 Estrutura do Projeto

```
bioface-ai/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada principal
│   │
│   ├── vision/                 # Camada de Visão Computacional
│   │   ├── __init__.py
│   │   ├── camera.py           # Captura de vídeo
│   │   ├── face_detector.py    # Detecção de faces (MediaPipe)
│   │   └── face_processor.py   # Normalização e pré-processamento
│   │
│   ├── ai/                     # Camada de IA
│   │   ├── __init__.py
│   │   ├── emotion_classifier.py  # Classificação de emoções
│   │   ├── face_recognizer.py     # Reconhecimento facial
│   │   └── models/                # Modelos pré-treinados
│   │
│   ├── engine/                 # Motor de Regras
│   │   ├── __init__.py
│   │   ├── event_engine.py     # Processamento de eventos
│   │   └── rules/              # Regras configuráveis
│   │
│   ├── database/               # Camada de Dados
│   │   ├── __init__.py
│   │   ├── models.py           # Modelos SQLAlchemy
│   │   ├── repository.py       # Acesso a dados
│   │   └── migrations/         # Migrações de banco
│   │
│   ├── api/                    # API Backend
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── routes/              # Endpoints REST
│   │   └── websocket.py        # WebSocket handlers
│   │
│   ├── dashboard/              # Dashboard
│   │   ├── __init__.py
│   │   └── app.py              # Streamlit app
│   │
│   └── utils/                  # Utilitários
│       ├── __init__.py
│       ├── config.py           # Configurações
│       ├── logger.py           # Sistema de logging
│       └── security.py         # Criptografia e segurança
│
├── models/                     # Modelos de IA
│   ├── emotion/                # Modelos de emoção
│   └── recognition/            # Modelos de reconhecimento
│
├── data/                       # Dados
│   ├── raw/                    # Dados brutos
│   └── processed/              # Dados processados
│
├── tests/                      # Testes
│   ├── unit/                   # Testes unitários
│   └── integration/            # Testes de integração
│
├── logs/                       # Logs do sistema
│
├── docs/                       # Documentação adicional
│
├── .env                        # Configurações (não versionado)
├── .env.example               # Exemplo de configurações
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🏛️ Decisões de Arquitetura

### Por que MediaPipe?
- **Performance**: Otimizado para tempo real
- **Precisão**: 468 landmarks faciais
- **Cross-platform**: Funciona em múltiplas plataformas
- **Open-source**: Mantido pelo Google

### Por que SQLite primeiro?
- **Simplicidade**: Zero configuração
- **Rápido**: Perfeito para MVP
- **Migração fácil**: SQLAlchemy facilita mudança para PostgreSQL

### Por que FastAPI?
- **Performance**: Uma das APIs Python mais rápidas
- **Async**: Suporte nativo a async/await
- **Documentação automática**: Swagger/OpenAPI
- **Type hints**: Melhor experiência de desenvolvimento

### Por que modelos pré-treinados?
- **Velocidade**: Não precisa treinar do zero
- **Qualidade**: Modelos já validados
- **Foco**: Concentrar esforço em integração, não em treinamento

---

## ⚖️ Considerações Éticas

### Princípios

1. **Consentimento Explícito**
   - Usuário deve consentir antes de usar o sistema
   - Modo anônimo disponível (sem identificação)

2. **Privacidade**
   - Embeddings são criptografados no banco
   - Imagens não são armazenadas (apenas embeddings)
   - Dados podem expirar automaticamente

3. **Transparência**
   - Código open-source
   - Documentação clara do funcionamento
   - Logs de todas as operações

4. **Não Comercial**
   - Projeto educacional/demonstrativo
   - Não coleta dados para venda
   - Não compartilha dados com terceiros

### LGPD Compliance

- ✅ Consentimento explícito
- ✅ Finalidade específica
- ✅ Retenção limitada
- ✅ Segurança dos dados
- ✅ Direito ao esquecimento (deletar dados)

### Modo Anônimo

O sistema pode operar em modo anônimo onde:
- Apenas emoções são detectadas
- Nenhuma identificação é feita
- Nenhum dado pessoal é armazenado

---

## 🗺️ Roadmap

### ✅ Fase 1 - Core Pipeline (Atual)
- [x] Estrutura do projeto
- [x] Captura de vídeo
- [x] Detecção de faces
- [x] Classificação de emoções
- [ ] Pipeline assíncrono completo

### 🔄 Fase 2 - Identificação + Persistência
- [ ] Sistema de embeddings
- [ ] Banco de dados
- [ ] Registro de faces
- [ ] Comparação e identificação

### 📅 Fase 3 - Backend + Dashboard
- [ ] API FastAPI
- [ ] WebSocket para tempo real
- [ ] Dashboard Streamlit
- [ ] Visualizações

### 🚀 Fase 4 - Automação + Deploy
- [ ] Event Engine configurável
- [ ] Métricas avançadas
- [ ] Docker + Deploy
- [ ] Testes completos

### 🔮 Futuro
- [ ] Multi-face tracking
- [ ] Análise de micro-expressões
- [ ] Estimativa de frequência cardíaca (rPPG)
- [ ] Dashboard React avançado
- [ ] Mobile app

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
- GitHub: [@seu-usuario](https://github.com/jonasferreira-silva1)
- LinkedIn: [Seu Perfil](https://www.linkedin.com/in/jonas-silva01/)

---


**⭐ Se este projeto foi útil, considere dar uma estrela!**

