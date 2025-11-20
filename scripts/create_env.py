"""Script pour créer le fichier .env depuis .env.example."""

import os
import shutil
import sys
from pathlib import Path


def create_env_file() -> None:
    """Crée le fichier .env depuis .env.example si il n'existe pas."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if env_path.exists():
        print("[OK] Fichier .env existe deja")
        return

    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("[OK] Fichier .env cree depuis .env.example")
    else:
        # Créer un fichier .env vide avec les valeurs par défaut
        default_env = """# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# HDFS Configuration
HDFS_HOST=localhost
HDFS_PORT=9000
HDFS_PATH=/sirene_data

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Spark Configuration
SPARK_MASTER=local[*]
SPARK_APP_NAME=sirene-dataviz

# Data Paths
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed
DATA_AGGREGATED_PATH=./data/aggregated
DATASET_CSV_PATH=./dataset/Sirene_merged_with_region.csv

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=development
"""
        env_path.write_text(default_env, encoding="utf-8")
        print("[OK] Fichier .env cree avec les valeurs par defaut")


if __name__ == "__main__":
    try:
        create_env_file()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Erreur lors de la creation du fichier .env: {e}", file=sys.stderr)
        sys.exit(1)

