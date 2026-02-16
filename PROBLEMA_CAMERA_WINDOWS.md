# 🎥 Problema: Câmera no Windows + Docker

## 🔴 O Que Aconteceu

O container ficou em **loop infinito** porque:

1. ✅ **Todas as dependências funcionam** (OpenCV, pydantic, etc.)
2. ❌ **Câmera não acessível**: No Windows, Docker não consegue acessar `/dev/video0` diretamente
3. 🔄 **Restart automático**: O `restart: unless-stopped` fazia o container reiniciar infinitamente

## ✅ Correção Aplicada

- Mudei `restart: unless-stopped` para `restart: no`
- Agora o container **para** quando encontra erro, em vez de reiniciar infinitamente

## 🎯 Soluções para Usar Câmera no Windows

### Opção 1: Executar Diretamente no Windows (Recomendado para Desenvolvimento)

```bash
# Instale as dependências localmente
pip install -r requirements-light.txt

# Execute diretamente
python main-light.py
```

**Vantagens:**
- ✅ Acesso direto à câmera
- ✅ Mais rápido para desenvolvimento
- ✅ Debug mais fácil

### Opção 2: Usar WSL2 + Docker Desktop

Se você tem WSL2 configurado:

1. Execute Docker dentro do WSL2
2. WSL2 pode acessar dispositivos USB/câmera do Windows
3. Configure o Docker para usar a câmera via WSL2

### Opção 3: Usar Arquivo de Vídeo para Testes

Modifique o código para aceitar arquivo de vídeo em vez de câmera:

```python
# Em vez de cv2.VideoCapture(0)
cap = cv2.VideoCapture("video_teste.mp4")
```

### Opção 4: Câmera Virtual (OBS Virtual Camera)

1. Instale OBS Studio
2. Configure "OBS Virtual Camera"
3. Use como fonte de vídeo para testes

## 🚀 Teste Agora

Com a correção aplicada, você pode:

```bash
# Inicia o container (vai parar se não encontrar câmera)
docker-compose up

# Ver os logs
docker-compose logs

# Parar manualmente
docker-compose down
```

O container **não vai mais ficar em loop infinito**.

## 📝 Próximos Passos

1. **Para desenvolvimento**: Execute diretamente no Windows (sem Docker)
2. **Para produção**: Configure WSL2 ou use servidor Linux
3. **Para testes**: Use arquivo de vídeo ou câmera virtual

---

**O sistema está funcionando corretamente! O problema é apenas o acesso à câmera no Windows via Docker.**

