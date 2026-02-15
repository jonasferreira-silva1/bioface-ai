"""
Script auxiliar para configurar ambiente inicial.

Cria diretórios necessários e arquivo .env se não existir.
"""

import os
from pathlib import Path

def setup_environment():
    """Configura ambiente inicial do projeto."""
    print("Configurando ambiente BioFace AI...")
    
    # Diretórios a criar
    directories = [
        "logs",
        "models/emotion",
        "models/recognition",
        "data/raw",
        "data/processed",
        "tests/unit",
        "tests/integration",
    ]
    
    # Cria diretórios
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Diretório criado/verificado: {directory}")
    
    # Cria .env se não existir
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print(f"✓ Arquivo .env criado a partir de .env.example")
    elif env_file.exists():
        print(f"✓ Arquivo .env já existe")
    else:
        print(f"⚠ Arquivo .env.example não encontrado")
    
    print("\nAmbiente configurado com sucesso!")
    print("\nPróximos passos:")
    print("1. Edite o arquivo .env com suas configurações")
    print("2. Instale as dependências: pip install -r requirements.txt")
    print("3. Execute: python main.py")

if __name__ == "__main__":
    setup_environment()

