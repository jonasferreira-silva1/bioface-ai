@echo off
REM Script para build da imagem Docker do BioFace AI (Windows)

echo 🐳 Building BioFace AI Docker Image...
echo.

REM Verifica se Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado!
    echo    Instale Docker Desktop: https://www.docker.com/get-started
    exit /b 1
)

REM Opções
set BUILD_TYPE=%1
if "%BUILD_TYPE%"=="" set BUILD_TYPE=cpu

set IMAGE_NAME=bioface-ai
set TAG=%2
if "%TAG%"=="" set TAG=latest

if "%BUILD_TYPE%"=="cpu" (
    echo 📦 Building CPU image...
    docker build -t %IMAGE_NAME%:%TAG% .
    echo ✅ Build concluído: %IMAGE_NAME%:%TAG%
) else if "%BUILD_TYPE%"=="gpu" (
    echo 📦 Building GPU image...
    docker build -f Dockerfile.gpu -t %IMAGE_NAME%:gpu-%TAG% .
    echo ✅ Build concluído: %IMAGE_NAME%:gpu-%TAG%
) else (
    echo ❌ Tipo inválido: %BUILD_TYPE%
    echo    Use: cpu ou gpu
    exit /b 1
)

echo.
echo 🚀 Para executar:
if "%BUILD_TYPE%"=="cpu" (
    echo    docker run -it --rm --device=/dev/video0 %IMAGE_NAME%:%TAG%
) else (
    echo    docker run -it --rm --gpus all --device=/dev/video0 %IMAGE_NAME%:gpu-%TAG%
)


