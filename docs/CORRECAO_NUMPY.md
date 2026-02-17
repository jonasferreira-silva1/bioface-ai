# 🔧 Correção: Incompatibilidade NumPy 2.x

**Data:** 2026-02-17  
**Problema:** NumPy 2.4.2 incompatível com MediaPipe

---

## 🐛 Problema

O sistema estava com **NumPy 2.4.2** instalado, mas:
- **MediaPipe** requer **NumPy < 2.0**
- **OpenCV** versões antigas requerem **NumPy < 2.0**

**Erro:**
```
ImportError: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.2
```

---

## ✅ Solução Aplicada

### 1. **Downgrade do NumPy**

```bash
pip install "numpy<2.0" --upgrade
```

**Versão instalada:** NumPy 1.26.4

### 2. **Ajuste do OpenCV**

Downgrade para versão compatível:
```bash
pip install opencv-python==4.8.1.78
```

### 3. **Ajuste do Protobuf**

MediaPipe requer protobuf < 5.0:
```bash
pip install "protobuf<5.0,>=4.25.3"
```

**Versão instalada:** Protobuf 4.25.8

---

## ⚠️ Conflito TensorFlow vs MediaPipe

**Problema conhecido:**
- **TensorFlow** requer `protobuf>=5.28.0`
- **MediaPipe** requer `protobuf<5.0`

**Solução temporária:**
- TensorFlow foi marcado como **opcional** no `requirements.txt`
- Sistema principal funciona **sem TensorFlow**
- TensorFlow só é necessário se usar **DeepFace**

---

## 📝 Versões Finais

| Pacote | Versão | Nota |
|--------|--------|------|
| NumPy | 1.26.4 | Compatível com MediaPipe |
| OpenCV | 4.8.1.78 | Compatível com NumPy < 2.0 |
| Protobuf | 4.25.8 | Compatível com MediaPipe |
| MediaPipe | 0.10.7 | Funciona com NumPy 1.x |
| TensorFlow | Opcional | Apenas se usar DeepFace |

---

## 🚀 Como Usar

### Sistema Principal (sem TensorFlow)

```bash
# Instalar dependências principais
pip install -r requirements.txt

# Executar sistema
python main-light.py
```

### Com DeepFace (requer TensorFlow)

```bash
# Instalar TensorFlow e DeepFace
pip install tensorflow==2.15.0 deepface==0.0.79

# Configurar .env
EMOTION_CLASSIFIER_TYPE=deepface

# Executar sistema
python main-light.py
```

**Nota:** Se usar DeepFace, pode haver conflito de protobuf. Nesse caso, considere usar `EmotionClassifierLight` (sem TensorFlow).

---

## ✅ Status

**Correção:** ✅ Aplicada  
**NumPy:** ✅ 1.26.4 (compatível)  
**MediaPipe:** ✅ Funcionando  
**TensorFlow:** ⚠️ Opcional (conflito com protobuf)

---

**Última atualização:** 2026-02-17

