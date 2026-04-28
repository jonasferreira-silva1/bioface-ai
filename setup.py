"""
Setup do BioFace AI.
"""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="bioface-ai",
    version="1.0.0",
    description="Real-Time Facial Recognition and Emotion Analysis System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jonas Ferreira da Silva",
    url="https://github.com/jonasferreira-silva1/bioface-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "opencv-python-headless>=4.8.0",
        "mediapipe>=0.10.0",
        "numpy>=1.26.0,<2.0",
        "onnxruntime>=1.16.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    extras_require={
        "api": ["fastapi>=0.104.0", "uvicorn>=0.24.0", "websockets>=12.0"],
        "dashboard": ["streamlit>=1.28.0", "plotly>=5.18.0", "requests>=2.31.0"],
        "deepface": ["deepface>=0.0.79", "tensorflow>=2.15.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    entry_points={
        "console_scripts": [
            "bioface=src.main_light:main",
        ],
    },
)
