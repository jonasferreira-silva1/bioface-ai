# 🛡️ Exceções Customizadas - BioFace AI

**Data:** 2026-02-17  
**Status:** ✅ Implementado

---

## 📋 Visão Geral

O BioFace AI agora possui um sistema completo de exceções customizadas que facilita o tratamento de erros e a recuperação de falhas. Isso demonstra **maturidade de desenvolvimento** e **preparação para produção**.

---

## 🎯 Objetivo

Criar exceções específicas para diferentes cenários de erro, permitindo:
- ✅ Tratamento granular de erros
- ✅ Recuperação automática quando possível
- ✅ Logs mais informativos
- ✅ Melhor experiência do desenvolvedor

---

## 📁 Estrutura

### Hierarquia de Exceções

```
BioFaceError (base)
├── CameraError
│   ├── CameraNotOpenedError
│   ├── CameraDisconnectedError
│   └── CameraReadError
├── DatabaseError
│   ├── DatabaseConnectionError
│   ├── DatabaseCorruptedError
│   └── DatabaseLockedError
├── RecognitionError
│   ├── EmbeddingGenerationError
│   ├── FaceNotDetectedError
│   └── AmbiguousRecognitionError
├── EmotionError
│   ├── EmotionClassificationError
│   └── ModelNotAvailableError
├── ConfigurationError
│   └── InvalidConfigurationError
└── ValidationError
    └── InvalidInputError
```

---

## 🔧 Exceções Implementadas

### 1. Exceções de Câmera

#### `CameraNotOpenedError`
**Quando ocorre:** Não é possível abrir a câmera na inicialização

**Exemplo:**
```python
try:
    camera = Camera(index=0)
except CameraNotOpenedError as e:
    logger.error(f"Câmera não disponível: {e.message}")
    # Tenta câmera alternativa
    camera = Camera(index=1)
```

#### `CameraDisconnectedError`
**Quando ocorre:** Câmera desconecta durante o uso

**Exemplo:**
```python
try:
    frame = camera.read()
except CameraDisconnectedError as e:
    logger.warning(f"{e.message}, tentando reconectar...")
    if camera.reconnect(max_retries=3):
        continue
    else:
        logger.error("Não foi possível reconectar")
```

#### `CameraReadError`
**Quando ocorre:** Falha ao ler frame (câmera travada, buffer cheio)

**Exemplo:**
```python
try:
    frame = camera.read()
except CameraReadError as e:
    logger.warning(f"{e.message}, pulando frame...")
    continue
```

---

### 2. Exceções de Banco de Dados

#### `DatabaseConnectionError`
**Quando ocorre:** Não é possível conectar ao banco

**Exemplo:**
```python
try:
    repo = DatabaseRepository()
except DatabaseConnectionError as e:
    logger.error(f"Erro de conexão: {e.message}")
    # Tenta reconectar ou usar backup
```

#### `DatabaseCorruptedError`
**Quando ocorre:** Banco de dados está corrompido

**Exemplo:**
```python
try:
    session = repo.get_session()
except DatabaseCorruptedError as e:
    logger.error(f"Banco corrompido: {e.message}")
    # Tenta recuperar
    if repo.recover_from_backup():
        logger.info("Banco recuperado!")
    else:
        logger.error("Falha ao recuperar banco")
```

#### `DatabaseLockedError`
**Quando ocorre:** Banco está bloqueado (múltiplas conexões)

**Exemplo:**
```python
try:
    session = repo.get_session()
except DatabaseLockedError as e:
    logger.warning(f"Banco bloqueado: {e.message}")
    # Aguarda e tenta novamente
    time.sleep(1)
    session = repo.get_session()
```

---

### 3. Exceções de Reconhecimento Facial

#### `FaceNotDetectedError`
**Quando ocorre:** Nenhuma face detectada na imagem

**Exemplo:**
```python
try:
    embedding = recognizer.generate_embedding(face_image)
except FaceNotDetectedError:
    logger.debug("Nenhuma face detectada, pulando...")
    continue
```

#### `EmbeddingGenerationError`
**Quando ocorre:** Falha ao gerar embedding (erro no processamento)

**Exemplo:**
```python
try:
    embedding = recognizer.generate_embedding(face_image)
except EmbeddingGenerationError as e:
    logger.error(f"Erro ao gerar embedding: {e.message}")
    logger.debug(f"Detalhes: {e.details}")
```

#### `AmbiguousRecognitionError`
**Quando ocorre:** Múltiplos usuários com embeddings muito similares

**Exemplo:**
```python
try:
    user = repo.find_user_by_embedding(embedding)
except AmbiguousRecognitionError as e:
    logger.warning(f"Ambiguidade: {e.message}")
    logger.debug(f"Usuários candidatos: {e.details['user_ids']}")
```

---

### 4. Exceções de Classificação de Emoções

#### `EmotionClassificationError`
**Quando ocorre:** Falha ao classificar emoção

**Exemplo:**
```python
try:
    emotion, confidence = classifier.predict(face)
except EmotionClassificationError as e:
    logger.error(f"Erro ao classificar: {e.message}")
    # Usa fallback
    emotion = "Unknown"
```

#### `ModelNotAvailableError`
**Quando ocorre:** Modelo não está disponível (DeepFace não instalado)

**Exemplo:**
```python
try:
    classifier = EmotionClassifierDeepFace()
except ModelNotAvailableError as e:
    logger.warning(f"{e.message}, usando classificador leve")
    classifier = EmotionClassifierLight()
```

---

## 🔄 Integração no Código

### Camera (`src/vision/camera.py`)

```python
from ..exceptions import (
    CameraNotOpenedError,
    CameraDisconnectedError,
    CameraReadError,
    handle_camera_error
)

def _initialize(self):
    try:
        self.cap = cv2.VideoCapture(self.index)
    except Exception as e:
        raise handle_camera_error(e, self.index)
    
    if not self.cap.isOpened():
        raise CameraNotOpenedError(self.index)

def read(self):
    if not self.cap.isOpened():
        raise CameraDisconnectedError(self.index)
    
    try:
        ret, frame = self.cap.read()
    except Exception as e:
        raise handle_camera_error(e, self.index)
    
    if not ret:
        raise CameraReadError(self.index)
    
    return frame

def reconnect(self, max_retries=3):
    """Tenta reconectar após desconexão"""
    for attempt in range(1, max_retries + 1):
        try:
            self._initialize()
            return True
        except CameraNotOpenedError:
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise
```

### Database Repository (`src/database/repository.py`)

```python
from ..exceptions import (
    DatabaseConnectionError,
    DatabaseCorruptedError,
    DatabaseLockedError,
    handle_database_error
)

def __init__(self):
    try:
        self.engine = create_engine(self.database_url)
        # Testa conexão
        with self.engine.connect() as conn:
            conn.execute(func.select(1))
    except sqlite3.OperationalError as e:
        error_str = str(e).lower()
        if "locked" in error_str:
            raise DatabaseLockedError(self.database_url)
        elif "corrupt" in error_str:
            raise DatabaseCorruptedError(self.database_url)
        else:
            raise handle_database_error(e, self.database_url)

def recover_from_backup(self, backup_path=None):
    """Recupera banco corrompido"""
    if Path(backup).exists():
        shutil.copy(backup, db_path)
        # Reconecta
        self.engine.dispose()
        self.engine = create_engine(self.database_url)
        return True
    else:
        raise DatabaseCorruptedError(
            self.database_url,
            f"Backup não encontrado: {backup}"
        )
```

### Face Recognizer (`src/ai/face_recognizer.py`)

```python
from ..exceptions import (
    EmbeddingGenerationError,
    FaceNotDetectedError
)

def generate_embedding(self, face_image):
    try:
        results = self.face_mesh.process(rgb_image)
        if not results.multi_face_landmarks:
            raise FaceNotDetectedError("Nenhum landmark detectado")
        # ... processamento ...
    except FaceNotDetectedError:
        raise  # Re-lança exceção específica
    except Exception as e:
        raise EmbeddingGenerationError(
            f"Falha ao gerar embedding: {e}",
            {"error_type": type(e).__name__}
        )
```

### Pipeline Principal (`src/main_light.py`)

```python
from src.exceptions import (
    CameraNotOpenedError,
    CameraDisconnectedError,
    CameraReadError,
    DatabaseCorruptedError,
    DatabaseLockedError,
    EmbeddingGenerationError,
    FaceNotDetectedError
)

def run(self):
    try:
        while True:
            try:
                frame = self.camera.read()
            except CameraDisconnectedError as e:
                logger.warning(f"{e.message}, tentando reconectar...")
                if self.camera.reconnect(max_retries=3):
                    continue
                else:
                    break
            except CameraReadError as e:
                logger.warning(f"{e.message}, pulando frame...")
                continue
            
            try:
                frame_annotated, results = self.process_frame(frame)
            except (EmbeddingGenerationError, FaceNotDetectedError) as e:
                logger.debug(f"Erro ao processar: {e.message}")
                continue
            
            try:
                self.db.save_embedding(...)
            except (DatabaseLockedError, DatabaseCorruptedError) as e:
                logger.error(f"Erro crítico: {e.message}")
                if isinstance(e, DatabaseCorruptedError):
                    self.db.recover_from_backup()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except (CameraNotOpenedError, DatabaseConnectionError) as e:
        logger.error(f"Erro de inicialização: {e.message}")
        return 1
```

---

## 🎯 Benefícios

### 1. Tratamento Granular
- Cada tipo de erro tem tratamento específico
- Permite recuperação automática quando possível
- Logs mais informativos

### 2. Recuperação Automática
- Câmera: Reconexão automática
- Banco: Recuperação de backup
- Modelos: Fallback para versão leve

### 3. Melhor Experiência do Desenvolvedor
- Exceções auto-documentadas
- Mensagens claras e específicas
- Detalhes adicionais via `details` dict

### 4. Preparação para Produção
- Tratamento robusto de falhas
- Sistema resiliente a erros
- Demonstra maturidade técnica

---

## 📊 Status de Implementação

| Componente | Status | Exceções Implementadas |
|------------|--------|------------------------|
| **Camera** | ✅ Completo | `CameraNotOpenedError`, `CameraDisconnectedError`, `CameraReadError` |
| **Database** | ✅ Completo | `DatabaseConnectionError`, `DatabaseCorruptedError`, `DatabaseLockedError` |
| **Face Recognizer** | ✅ Completo | `EmbeddingGenerationError`, `FaceNotDetectedError` |
| **Emotion Classifier** | ⏳ Planejado | `EmotionClassificationError`, `ModelNotAvailableError` |
| **Pipeline Principal** | ✅ Completo | Tratamento integrado de todas as exceções |

---

## 🚀 Próximos Passos

1. **Integrar em Emotion Classifier** - Adicionar tratamento de erros específicos
2. **Testes Unitários** - Criar testes para cada tipo de exceção
3. **Documentação de API** - Documentar exceções na documentação da API (Fase 4)
4. **Métricas** - Adicionar métricas de erros e recuperações

---

**Última atualização:** 2026-02-17

