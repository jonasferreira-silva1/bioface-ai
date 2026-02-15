"""
Script de setup do BioFace AI.

Facilita a instalação e configuração inicial do projeto.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lê o README para usar como descrição longa
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="bioface-ai",
    version="0.1.0",
    description="Real-Time Behavioral Intelligence System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BioFace AI Team",
    author_email="",
    url="https://github.com/seu-usuario/bioface-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "numpy>=1.24.0",
        "tensorflow>=2.15.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "bioface=src.main:main",
        ],
    },
)

