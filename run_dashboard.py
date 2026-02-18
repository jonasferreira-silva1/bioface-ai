"""
Script para executar o Dashboard Streamlit do BioFace AI.

Uso:
    python run_dashboard.py
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    dashboard_path = Path(__file__).parent / "dashboard.py"
    
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(dashboard_path),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])

