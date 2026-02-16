# BioFace AI - Dockerfile
# 
# Versão otimizada para baixo uso de memória.
# Remove TensorFlow e dependências pesadas.
# 
# Build:
#   docker build -t bioface-ai .
#
# Run:
#   docker run -it --rm --device=/dev/video0 --memory="1g" bioface-ai

# ============================================
# Estágio 1: Base Image
# ============================================
FROM python:3.11-slim AS base

LABEL maintainer="BioFace AI Team"
LABEL description="BioFace AI - Versão Leve"
LABEL version="0.1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    QT_QPA_PLATFORM=offscreen \
    DISPLAY=:99

# Instala dependências do sistema
# SOLUÇÃO: Instala pacotes OpenGL que funcionam em qualquer Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependências básicas
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    # OpenGL - Pacotes que funcionam em Bookworm e Trixie
    libgl1 \
    libglx0 \
    libglu1 \
    # Mesa DRI (fornece libGL.so.1)
    libgl1-mesa-dri \
    # Codecs
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && ldconfig \
    # Verifica libGL.so.1
    && echo "=== Verificando libGL.so.1 ===" && \
    find /usr -name "libGL.so*" 2>/dev/null && \
    echo "✓ libGL.so.1 encontrado" || \
    (echo "✗ libGL.so.1 NÃO encontrado!" && \
     echo "Bibliotecas GL disponíveis:" && \
     find /usr -name "*GL*" -o -name "*gl*" 2>/dev/null | head -20 && \
     exit 1)

# ============================================
# Estágio 2: Dependências Python
# ============================================
FROM base AS dependencies

WORKDIR /app

COPY requirements-light.txt .

# Instala Python packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-light.txt && \
    # Atualiza cache ANTES de testar OpenCV
    ldconfig && \
    # Testa OpenCV
    python -c "import cv2; print(f'✓ OpenCV {cv2.__version__} funcionando')" || \
    (echo "✗ ERRO ao importar OpenCV" && \
     echo "=== Debug Info ===" && \
     echo "Python version:" && python --version && \
     echo "libGL.so.1:" && find /usr -name "libGL.so*" 2>/dev/null && \
     echo "LD_LIBRARY_PATH:" && echo $LD_LIBRARY_PATH && \
     ldconfig -p | grep -i gl | head -10 && \
     exit 1)

# ============================================
# Estágio 3: Aplicação
# ============================================
FROM dependencies AS app

RUN useradd -m -u 1000 bioface && \
    chown -R bioface:bioface /app

COPY --chown=bioface:bioface src/ /app/src/
COPY --chown=bioface:bioface main-light.py /app/

RUN mkdir -p /app/logs /app/models /app/data && \
    chown -R bioface:bioface /app/logs /app/models /app/data

USER bioface
WORKDIR /app
ENV MODE=light

CMD ["python", "main-light.py"]
