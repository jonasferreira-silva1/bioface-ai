# 🚀 Guia Rápido de Início - BioFace AI

Este guia te ajudará a começar a usar o BioFace AI em poucos minutos.

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Webcam conectada
- 4GB+ RAM (8GB recomendado)
- GPU opcional (melhora performance significativamente)

## ⚡ Instalação Rápida

### 1. Clone o repositório (se aplicável)

```bash
git clone https://github.com/seu-usuario/bioface-ai.git
cd bioface-ai
```

### 2. Crie ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

**Nota:** A instalação do TensorFlow pode demorar alguns minutos.

### 4. Configure ambiente

```bash
# Executa script de setup (cria diretórios e .env)
python scripts/setup_env.py

# Ou manualmente:
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

### 5. Execute o sistema

```bash
python main.py
```

Pressione `q` para sair.

## 🎯 Primeiros Passos

### Verificar se a câmera está funcionando

```bash
python main.py --camera 0
```

### Ajustar performance

Se o sistema estiver lento, aumente o `FRAME_SKIP` no arquivo `.env`:

```env
FRAME_SKIP=3  # Processa 1 frame a cada 3 frames
```

### Modo debug

Para ver mais informações:

```bash
python main.py --log-level DEBUG
```

## 🐛 Solução de Problemas

### Erro: "Não foi possível abrir a câmera"

- Verifique se a webcam está conectada
- Tente outro índice: `--camera 1`
- Verifique se outra aplicação não está usando a câmera

### Erro: "ModuleNotFoundError"

- Certifique-se de que o ambiente virtual está ativado
- Reinstale dependências: `pip install -r requirements.txt`

### Performance baixa

- Aumente `FRAME_SKIP` no `.env
- Reduza resolução da câmera no `.env`:
  ```env
  CAMERA_WIDTH=320
  CAMERA_HEIGHT=240
  ```

### Modelo de emoção não funciona bem

O modelo padrão é apenas para demonstração. Para melhor precisão:

1. Baixe um modelo pré-treinado (veja `docs/MODELS.md`)
2. Coloque em `models/emotion/`
3. Configure no código ou via argumentos

## 📚 Próximos Passos

- Leia o [README.md](../README.md) completo
- Veja [MODELS.md](MODELS.md) para modelos pré-treinados
- Explore a [arquitetura](../README.md#-arquitetura)

## 💡 Dicas

- **Iluminação**: Boa iluminação melhora muito a detecção
- **Distância**: Fique a ~50cm da câmera para melhor resultado
- **Rosto frontal**: Funciona melhor com rosto voltado para a câmera
- **Performance**: Use GPU se disponível (TensorFlow detecta automaticamente)

## 🆘 Precisa de Ajuda?

- Abra uma [issue](https://github.com/seu-usuario/bioface-ai/issues)
- Consulte a documentação completa
- Verifique os logs em `logs/bioface.log`

---

**Boa sorte! 🎉**

