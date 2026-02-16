#!/bin/bash
# Script para build da imagem Docker do BioFace AI

set -e

echo "🐳 Building BioFace AI Docker Image..."
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "   Instale Docker: https://www.docker.com/get-started"
    exit 1
fi

# Opções
BUILD_TYPE="${1:-cpu}"  # cpu ou gpu
IMAGE_NAME="bioface-ai"
TAG="${2:-latest}"

case $BUILD_TYPE in
    cpu)
        echo "📦 Building CPU image..."
        docker build -t ${IMAGE_NAME}:${TAG} .
        echo "✅ Build concluído: ${IMAGE_NAME}:${TAG}"
        ;;
    gpu)
        echo "📦 Building GPU image..."
        docker build -f Dockerfile.gpu -t ${IMAGE_NAME}:gpu-${TAG} .
        echo "✅ Build concluído: ${IMAGE_NAME}:gpu-${TAG}"
        ;;
    *)
        echo "❌ Tipo inválido: $BUILD_TYPE"
        echo "   Use: cpu ou gpu"
        exit 1
        ;;
esac

echo ""
echo "🚀 Para executar:"
if [ "$BUILD_TYPE" = "cpu" ]; then
    echo "   docker run -it --rm --device=/dev/video0 ${IMAGE_NAME}:${TAG}"
else
    echo "   docker run -it --rm --gpus all --device=/dev/video0 ${IMAGE_NAME}:gpu-${TAG}"
fi


