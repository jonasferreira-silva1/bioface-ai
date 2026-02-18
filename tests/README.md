# 🧪 Testes - BioFace AI

**Status:** ✅ Implementado  
**Cobertura:** Em desenvolvimento

---

## 📋 Visão Geral

Suite completa de testes unitários e de integração para validar o funcionamento do BioFace AI, especialmente as **exceções customizadas** e sua integração nos componentes.

---

## 🚀 Executando os Testes

### Instalação de Dependências

```bash
pip install -r requirements.txt
```

### Executar Todos os Testes

```bash
pytest
```

### Executar Testes Específicos

```bash
# Testes de exceções
pytest tests/test_exceptions.py

# Testes de câmera
pytest tests/test_camera_exceptions.py

# Testes de banco de dados
pytest tests/test_database_exceptions.py

# Testes de reconhecimento facial
pytest tests/test_face_recognizer_exceptions.py
```

### Executar com Cobertura

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Isso gera:
- Relatório no terminal
- Relatório HTML em `htmlcov/index.html`

### Executar Testes Específicos por Marcador

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Testes que requerem banco de dados
pytest -m database
```

---

## 📁 Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures compartilhadas
├── test_exceptions.py             # Testes unitários de exceções
├── test_camera_exceptions.py      # Testes de integração - Câmera
├── test_database_exceptions.py   # Testes de integração - Banco
└── test_face_recognizer_exceptions.py  # Testes de integração - Reconhecimento
```

---

## 🧪 Tipos de Testes

### 1. Testes Unitários de Exceções (`test_exceptions.py`)

Valida que todas as exceções customizadas:
- ✅ Herdam corretamente de `BioFaceError`
- ✅ Têm mensagens apropriadas
- ✅ Armazenam detalhes corretamente
- ✅ Funcionam com funções utilitárias (`handle_camera_error`, etc.)

**Exemplo:**
```python
def test_camera_not_opened_error():
    error = CameraNotOpenedError(camera_index=0)
    assert isinstance(error, CameraError)
    assert error.details["camera_index"] == 0
```

### 2. Testes de Integração - Câmera (`test_camera_exceptions.py`)

Valida que exceções são lançadas corretamente em cenários reais:
- ✅ `CameraNotOpenedError` quando câmera não abre
- ✅ `CameraDisconnectedError` quando câmera desconecta
- ✅ `CameraReadError` quando falha ao ler frame
- ✅ Reconexão automática funciona

**Exemplo:**
```python
def test_camera_not_opened_error_on_init():
    with pytest.raises(CameraNotOpenedError):
        Camera(index=999)  # Índice inválido
```

### 3. Testes de Integração - Banco de Dados (`test_database_exceptions.py`)

Valida que exceções são lançadas corretamente:
- ✅ `DatabaseConnectionError` para conexões inválidas
- ✅ `DatabaseLockedError` para banco bloqueado
- ✅ `DatabaseCorruptedError` para banco corrompido
- ✅ Recuperação de backup funciona

**Exemplo:**
```python
def test_database_corrupted_error_detection():
    # Cria banco corrompido
    corrupted_db.write_bytes(b"INVALID DATA")
    
    with pytest.raises(DatabaseCorruptedError):
        repo = DatabaseRepository(database_url=corrupted_db)
```

### 4. Testes de Integração - Reconhecimento Facial (`test_face_recognizer_exceptions.py`)

Valida que exceções são lançadas corretamente:
- ✅ `FaceNotDetectedError` quando não há face
- ✅ `EmbeddingGenerationError` em falhas de processamento
- ✅ Embeddings são gerados corretamente com faces válidas

**Exemplo:**
```python
def test_face_not_detected_error_on_no_landmarks():
    no_face_image = np.random.randint(0, 255, (160, 160, 3))
    
    with pytest.raises(FaceNotDetectedError):
        recognizer.generate_embedding(no_face_image)
```

---

## 🔧 Fixtures Disponíveis

### `temp_database`
Cria um banco de dados temporário para testes.

```python
def test_something(temp_database):
    repo = DatabaseRepository(database_url=temp_database)
    # ... testes ...
```

### `sample_face_image`
Cria uma imagem de face sintética para testes.

```python
def test_embedding(sample_face_image):
    embedding = recognizer.generate_embedding(sample_face_image)
    assert embedding is not None
```

### `sample_embedding`
Cria um embedding de exemplo para testes.

```python
def test_comparison(sample_embedding):
    distance = recognizer.compare_embeddings(sample_embedding, sample_embedding)
    assert distance < 0.01
```

---

## 📊 Cobertura de Testes

### Status Atual

| Módulo | Cobertura | Status |
|--------|-----------|--------|
| `src/exceptions.py` | ~95% | ✅ Completo |
| `src/vision/camera.py` | ~60% | 🔄 Em progresso |
| `src/database/repository.py` | ~50% | 🔄 Em progresso |
| `src/ai/face_recognizer.py` | ~40% | 🔄 Em progresso |

### Meta
- **Cobertura Total:** > 80%
- **Exceções:** 100%
- **Componentes Críticos:** > 90%

---

## 🎯 Próximos Passos

1. **Expandir Testes de Integração**
   - [ ] Testes para `EmotionClassifier`
   - [ ] Testes para pipeline completo
   - [ ] Testes de performance

2. **Testes de Performance**
   - [ ] Benchmarks de FPS
   - [ ] Testes de carga
   - [ ] Testes de memória

3. **CI/CD**
   - [ ] GitHub Actions
   - [ ] Execução automática em PRs
   - [ ] Relatórios de cobertura

---

## 📝 Notas

- Testes usam **mocks** para evitar dependências externas (câmera real, etc.)
- Banco de dados usa arquivos temporários que são limpos automaticamente
- Testes são **isolados** - cada teste é independente

---

**Última atualização:** 2026-02-17

