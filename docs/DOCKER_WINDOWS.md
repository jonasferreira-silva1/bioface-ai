# 🪟 Docker no Windows - BioFace AI

Guia específico para usar Docker no Windows com BioFace AI.

## ⚠️ Limitações no Windows

No Windows, o acesso à câmera via Docker tem limitações:

1. **`/dev/video0` não existe** - Windows não usa o sistema de arquivos Linux
2. **`network_mode: host` não funciona** - Docker Desktop no Windows não suporta
3. **Acesso a dispositivos USB** - Requer configuração adicional

## 🎯 Soluções

### Opção 1: Executar Diretamente (Recomendado para Windows)

A forma mais simples no Windows é executar diretamente com Python:

```bash
# Instale dependências
pip install -r requirements.txt

# Execute
python main.py
```

### Opção 2: WSL2 (Recomendado para Docker)

Se você quer usar Docker, use WSL2:

1. **Instale WSL2**:
   ```powershell
   wsl --install
   ```

2. **Instale Docker no WSL2**:
   - Siga o guia: https://docs.docker.com/desktop/wsl/

3. **Execute no WSL2**:
   ```bash
   # No terminal WSL2
   docker-compose up
   ```

### Opção 3: Docker Desktop com WSL2 Backend

1. **Configure Docker Desktop**:
   - Settings → General → Use WSL 2 based engine
   - Settings → Resources → WSL Integration → Enable

2. **Execute no WSL2**:
   ```bash
   # No terminal WSL2
   docker-compose up
   ```

## 🔧 Configuração Alternativa

### Usar docker-compose.windows.yml

Criei um arquivo específico para Windows:

```bash
docker-compose -f docker-compose.windows.yml up
```

**Nota**: Este arquivo não inclui acesso à câmera, pois não é possível no Windows nativo.

## 📋 Comandos Úteis

### Verificar se WSL2 está instalado

```powershell
wsl --list --verbose
```

### Executar comando no WSL2

```powershell
wsl docker-compose up
```

### Acessar câmera no WSL2

No WSL2, você pode acessar dispositivos USB:

```bash
# Listar dispositivos de vídeo
ls -l /dev/video*

# Executar com device
docker run -it --rm --device=/dev/video0 bioface-ai
```

## 🐛 Solução de Problemas

### Erro: "devices is not supported"

**Problema**: Windows não suporta `devices:` no docker-compose

**Solução**: Use WSL2 ou execute diretamente com Python

### Erro: "network_mode: host is not supported"

**Problema**: Docker Desktop no Windows não suporta host network

**Solução**: Use port mapping ou WSL2

### Câmera não funciona no Docker

**Problema**: Windows não expõe câmera como `/dev/video0`

**Solução**: 
1. Use WSL2
2. Ou execute diretamente: `python main.py`

## 💡 Recomendações

Para Windows, recomendo:

1. **Desenvolvimento**: Execute diretamente com Python
   ```bash
   python main.py
   ```

2. **Produção/Deploy**: Use WSL2 + Docker
   ```bash
   wsl docker-compose up
   ```

3. **Testes**: Use ambiente virtual Python
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## 🔗 Links Úteis

- [WSL2 Installation](https://docs.microsoft.com/windows/wsl/install)
- [Docker Desktop WSL2](https://docs.docker.com/desktop/windows/wsl/)
- [USB Devices in WSL2](https://docs.microsoft.com/windows/wsl/connect-usb)

---

**Dica**: Para melhor experiência no Windows, use Python diretamente ou WSL2 para Docker.


