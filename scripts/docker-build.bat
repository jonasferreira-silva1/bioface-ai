@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM BioFace AI — Build dos containers Docker (Windows)
REM
REM Uso:
REM   scripts\docker-build.bat          (builda API + Dashboard)
REM   scripts\docker-build.bat api       (só API)
REM   scripts\docker-build.bat dashboard (só Dashboard)
REM ─────────────────────────────────────────────────────────────────────────────

@echo off
setlocal

echo.
echo  BioFace AI - Docker Build
echo  ─────────────────────────
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo  ERRO: Docker nao encontrado.
    echo  Instale Docker Desktop: https://www.docker.com/get-started
    exit /b 1
)

set TARGET=%1
if "%TARGET%"=="" set TARGET=all

if "%TARGET%"=="api" goto build_api
if "%TARGET%"=="dashboard" goto build_dashboard
if "%TARGET%"=="all" goto build_all

echo  ERRO: opcao invalida "%TARGET%"
echo  Use: api, dashboard ou deixe em branco para buildar tudo.
exit /b 1

:build_all
call :build_api
call :build_dashboard
goto done

:build_api
echo  [1/2] Buildando API (FastAPI)...
docker build -f Dockerfile.api -t bioface-api:latest .
if errorlevel 1 ( echo  ERRO no build da API & exit /b 1 )
echo  OK - bioface-api:latest
echo.
goto :eof

:build_dashboard
echo  [2/2] Buildando Dashboard (Streamlit)...
docker build -f Dockerfile.dashboard -t bioface-dashboard:latest .
if errorlevel 1 ( echo  ERRO no build do Dashboard & exit /b 1 )
echo  OK - bioface-dashboard:latest
echo.
goto :eof

:done
echo.
echo  Build concluido!
echo.
echo  Para subir os servicos:
echo    docker-compose up
echo.
echo  Para rodar o pipeline de camera (em outro terminal):
echo    python main-light.py --api-url http://localhost:8000
echo.
echo  Acesse:
echo    API docs  -^> http://localhost:8000/docs
echo    Dashboard -^> http://localhost:8501
echo.
