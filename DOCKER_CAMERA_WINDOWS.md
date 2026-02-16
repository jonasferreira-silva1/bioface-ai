# 🎥 Docker + Câmera no Windows - Por Que Não Funciona

## ❌ O Problema

Docker no Windows **NÃO consegue acessar a câmera** porque:

1. **Docker roda em VM/WSL2**: Não tem acesso direto ao hardware do Windows
2. **`/dev/video0` não existe no Windows**: É um caminho Linux
3. **Câmera está no host**: O container não vê dispositivos USB/câmera

## ✅ Soluções

### Opção 1: Executar Diretamente no Windows (RECOMENDADO)

```bash
# Funciona perfeitamente!
python main-light.py
```

**Vantagens:**
- ✅ Acesso direto à câmera
- ✅ Mais rápido
- ✅ Debug mais fácil
- ✅ Sem problemas de compatibilidade

### Opção 2: Usar Arquivo de Vídeo no Docker

Modifique o código para aceitar arquivo de vídeo:

```python
# Em vez de cv2.VideoCapture(0)
cap = cv2.VideoCapture("video_teste.mp4")
```

### Opção 3: WSL2 + Docker Desktop (Avançado)

Se você tem WSL2 configurado:

1. Execute Docker dentro do WSL2
2. Configure acesso USB via WSL2
3. Mais complexo, mas pode funcionar

### Opção 4: Servidor de Streaming

1. Capture vídeo no Windows
2. Stream para o container via HTTP/RTSP
3. Container recebe o stream

## 🎯 Recomendação

**Para desenvolvimento**: Use `python main-light.py` diretamente no Windows

**Para produção**: Use servidor Linux ou configure WSL2 adequadamente

---

**Resumo**: Docker no Windows não acessa câmera. Use execução direta no Windows para desenvolvimento.

