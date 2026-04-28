#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# BioFace AI — Build dos containers Docker (Linux/Mac)
#
# Uso:
#   ./scripts/docker-build.sh           (builda API + Dashboard)
#   ./scripts/docker-build.sh api        (só API)
#   ./scripts/docker-build.sh dashboard  (só Dashboard)
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo ""
echo " BioFace AI - Docker Build"
echo " ─────────────────────────"
echo ""

if ! command -v docker &> /dev/null; then
    echo " ERRO: Docker não encontrado."
    echo " Instale: https://docs.docker.com/get-docker/"
    exit 1
fi

TARGET="${1:-all}"

build_api() {
    echo " [1/2] Buildando API (FastAPI)..."
    docker build -f Dockerfile.api -t bioface-api:latest .
    echo " OK - bioface-api:latest"
    echo ""
}

build_dashboard() {
    echo " [2/2] Buildando Dashboard (Streamlit)..."
    docker build -f Dockerfile.dashboard -t bioface-dashboard:latest .
    echo " OK - bioface-dashboard:latest"
    echo ""
}

case "$TARGET" in
    api)       build_api ;;
    dashboard) build_dashboard ;;
    all)       build_api; build_dashboard ;;
    *)
        echo " ERRO: opção inválida '$TARGET'"
        echo " Use: api, dashboard ou deixe em branco para buildar tudo."
        exit 1
        ;;
esac

echo ""
echo " Build concluído!"
echo ""
echo " Para subir os serviços:"
echo "   docker-compose up"
echo ""
echo " Para rodar o pipeline de câmera (em outro terminal):"
echo "   python main-light.py --api-url http://localhost:8000"
echo ""
echo " Acesse:"
echo "   API docs  → http://localhost:8000/docs"
echo "   Dashboard → http://localhost:8501"
echo ""
