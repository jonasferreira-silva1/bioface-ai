# 🐳 Guia Docker - BioFace AI

Este guia explica como usar Docker para executar o BioFace AI.

## 📋 Pré-requisitos

- Docker instalado ([Download](https://www.docker.com/get-started))
- Docker Compose (geralmente vem com Docker Desktop)
- Webcam conectada
- Permissões para acessar dispositivos de vídeo

## 🚀 Início Rápido

### Build da Imagem

```bash
docker build -t bioface-ai .
```

### Executar Container

```bash
# Modo básico
docker run -it --rm \
  --device=/dev/video0 \
  bioface-ai

# Com volumes para persistência
docker run -it --rm \
  --device=/dev/video0 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/models:/app/models \
  bioface-ai
```

### Usar Docker Compose

```bash
# Produção
docker-compose up

# Desenvolvimento
docker-compose -f docker-compose.dev.yml up

# Em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

## 🔧 Configuração

### Ajustar Índice da Câmera

Se sua câmera não for `/dev/video0`, ajuste no `docker-compose.yml`:

```yaml
devices:
  - /dev/video1:/dev/video0  # Mapeia video1 do host para video0 no container
```

Ou no comando Docker:

```bash
docker run -it --rm \
  --device=/dev/video1:/dev/video0 \
  bioface-ai
```

### Variáveis de Ambiente

Edite o arquivo `.env` ou passe via Docker:

```bash
docker run -it --rm \
  --device=/dev/video0 \
  -e CAMERA_INDEX=0 \
  -e FRAME_SKIP=3 \
  -e LOG_LEVEL=DEBUG \
  bioface-ai
```

## 🖥️ Suporte a GPU (NVIDIA)

### Pré-requisitos

1. Instale [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Build com suporte GPU:

```bash
# Use Dockerfile.gpu ou modifique Dockerfile
docker build -f Dockerfile.gpu -t bioface-ai:gpu .
```

3. Execute com GPU:

```bash
docker run -it --rm \
  --gpus all \
  --device=/dev/video0 \
  bioface-ai:gpu
```

### Docker Compose com GPU

Adicione ao `docker-compose.yml`:

```yaml
services:
  bioface-ai:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 📁 Volumes

### Estrutura de Volumes

```
./logs          → Logs do sistema
./models        → Modelos de IA
./data          → Dados processados
./.env          → Configurações
```

### Montar Volumes Customizados

```bash
docker run -it --rm \
  --device=/dev/video0 \
  -v /caminho/local/logs:/app/logs \
  -v /caminho/local/models:/app/models \
  bioface-ai
```

## 🪟 Windows - Limitações

### ⚠️ Câmera no Windows

**Docker no Windows NÃO consegue acessar a câmera** porque:
- Docker roda em VM/WSL2 (sem acesso direto ao hardware)
- `/dev/video0` não existe no Windows (é um caminho Linux)
- Câmera está no host (container não vê dispositivos USB)

**Solução Recomendada:**
```bash
# Execute diretamente no Windows (funciona perfeitamente!)
python main-light.py
```

**Alternativas:**
- Use arquivo de vídeo em vez de câmera
- Configure WSL2 + Docker Desktop (avançado)
- Use servidor de streaming

Para desenvolvimento no Windows, **use execução direta** em vez de Docker.

---

## 🐛 Solução de Problemas

### Erro: "Cannot find /dev/video0"

**Problema**: Câmera não encontrada

**Solução**:
1. Verifique se a câmera está conectada:
   ```bash
   ls -l /dev/video*
   ```

2. Liste dispositivos de vídeo:
   ```bash
   v4l2-ctl --list-devices
   ```

3. Ajuste o índice no docker-compose.yml

### Erro: "Permission denied" ao acessar câmera

**Solução**:
```bash
# Adicione usuário ao grupo video
sudo usermod -a -G video $USER

# Ou execute com privilégios (não recomendado para produção)
docker run -it --rm --privileged --device=/dev/video0 bioface-ai
```

### Erro: "No module named 'cv2'"

**Problema**: Dependências não instaladas

**Solução**:
```bash
# Rebuild a imagem
docker build --no-cache -t bioface-ai .
```

### Performance Lenta

**Soluções**:
1. Use GPU se disponível
2. Aumente `FRAME_SKIP` no `.env`
3. Reduza resolução da câmera
4. Limite recursos do container:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

## 🔍 Debugging

### Entrar no Container

```bash
# Container em execução
docker exec -it bioface-ai bash

# Novo container para debug
docker run -it --rm --device=/dev/video0 bioface-ai bash
```

### Ver Logs

```bash
# Logs do container
docker logs bioface-ai

# Logs em tempo real
docker logs -f bioface-ai

# Últimas 100 linhas
docker logs --tail 100 bioface-ai
```

### Inspecionar Imagem

```bash
# Ver camadas da imagem
docker history bioface-ai

# Ver tamanho
docker images bioface-ai

# Inspecionar configuração
docker inspect bioface-ai
```

## 🏗️ Build Avançado

### Build com Cache

```bash
# Build normal (usa cache)
docker build -t bioface-ai .

# Build sem cache
docker build --no-cache -t bioface-ai .

# Build com target específico
docker build --target dependencies -t bioface-ai:deps .
```

### Multi-stage Build

O Dockerfile usa multi-stage build para otimizar tamanho:

1. **base**: Imagem base com dependências do sistema
2. **dependencies**: Instala dependências Python
3. **app**: Aplicação final

### Otimizar Tamanho

```bash
# Build com compressão
docker build --compress -t bioface-ai .

# Ver tamanho de cada camada
docker history bioface-ai --human --format "{{.Size}}\t{{.CreatedBy}}"
```

## 🔐 Segurança

### Executar como Usuário Não-Root

O Dockerfile já cria usuário `bioface` (UID 1000) para segurança.

### Verificar

```bash
docker run -it --rm --device=/dev/video0 bioface-ai whoami
# Deve retornar: bioface
```

### Limitar Recursos

```yaml
services:
  bioface-ai:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## 📦 Publicar Imagem

### Tag da Imagem

```bash
docker tag bioface-ai:latest seu-usuario/bioface-ai:0.1.0
docker tag bioface-ai:latest seu-usuario/bioface-ai:latest
```

### Push para Registry

```bash
# Docker Hub
docker push seu-usuario/bioface-ai:latest

# GitHub Container Registry
docker tag bioface-ai:latest ghcr.io/seu-usuario/bioface-ai:latest
docker push ghcr.io/seu-usuario/bioface-ai:latest
```

## 🎯 Comandos Úteis

```bash
# Listar containers
docker ps -a

# Remover containers parados
docker container prune

# Remover imagens não usadas
docker image prune

# Limpar tudo
docker system prune -a

# Ver uso de recursos
docker stats bioface-ai
```

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)

---

**Dica**: Para desenvolvimento, use `docker-compose.dev.yml` que monta o código como volume, permitindo edições sem rebuild.


