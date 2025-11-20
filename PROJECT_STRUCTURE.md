# Structure du Projet Sirene DataViz

## 📁 Architecture du Projet

Ce projet suit les **conventions Python modernes** et une **séparation claire des responsabilités**.

```
IPSSI_19_11_2025/
├── .env.example                 # Variables d'environnement exemple
├── .gitignore                   # Fichiers à ignorer
├── .pre-commit-config.yaml      # Configuration pre-commit hooks
├── docker-compose.yml           # Orchestration Docker
├── Makefile                     # Commandes automatisées
├── pyproject.toml               # Configuration UV/Python (dépendances)
├── README.md                    # Documentation principale
│
├── dataset/                     # Données brutes
│   ├── Sirene_merged_with_region.csv
│   └── regions-france.csv
│
├── src/                         # Code source principal
│   ├── __init__.py
│   │
│   ├── etl/                     # Pipeline ETL
│   │   ├── __init__.py
│   │   ├── extract.py           # Extraction depuis CSV
│   │   ├── transform.py          # Transformation & nettoyage
│   │   ├── load.py              # Chargement vers HDFS/Parquet
│   │   └── validators.py        # Validation de qualité (Great Expectations)
│   │
│   ├── processing/              # Traitement & Agrégation
│   │   ├── __init__.py
│   │   ├── aggregations.py      # Agrégations par use case
│   │   ├── spark_jobs.py        # Jobs PySpark
│   │   └── normalizers.py       # Normalisation données
│   │
│   ├── api/                     # API FastAPI
│   │   ├── __init__.py
│   │   ├── main.py              # Application FastAPI
│   │   ├── routers/             # Routes par use case
│   │   │   ├── __init__.py
│   │   │   ├── usecase1.py     # Évolution créations
│   │   │   ├── usecase2.py     # Sexe dirigeants
│   │   │   ├── usecase3.py     # Effectifs
│   │   │   ├── usecase4.py     # Dominance sectorielle
│   │   │   └── usecase5.py     # Types juridiques
│   │   ├── models/              # Modèles Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py      # Schémas de requêtes/réponses
│   │   │   └── filters.py       # Modèles de filtres
│   │   └── services/            # Services métier
│   │       ├── __init__.py
│   │       ├── data_service.py  # Accès aux données
│   │       └── cache_service.py # Gestion cache Redis
│   │
│   ├── frontend/                # Application React
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── public/
│   │   └── src/
│   │       ├── components/      # Composants React
│   │       │   ├── Map/         # Composant carte
│   │       │   ├── Filters/    # Composants filtres
│   │       │   └── Charts/     # Graphiques
│   │       ├── services/        # Services API
│   │       ├── hooks/          # Custom hooks
│   │       ├── utils/          # Utilitaires
│   │       └── App.tsx
│   │
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py         # Settings Pydantic
│   │   └── logging.py           # Configuration logging
│   │
│   └── utils/                   # Utilitaires partagés
│       ├── __init__.py
│       ├── date_utils.py        # Utilitaires dates
│       ├── ape_utils.py         # Utilitaires codes APE
│       └── region_utils.py      # Utilitaires régions
│
├── tests/                       # Tests
│   ├── __init__.py
│   ├── unit/                    # Tests unitaires
│   │   ├── test_etl/
│   │   ├── test_processing/
│   │   └── test_api/
│   ├── integration/             # Tests d'intégration
│   └── fixtures/                # Données de test
│
├── scripts/                     # Scripts utilitaires
│   ├── setup_hdfs.sh           # Setup HDFS
│   ├── run_etl.py              # Script ETL
│   └── generate_aggregations.py # Génération agrégations
│
├── docker/                      # Dockerfiles
│   ├── Dockerfile.api
│   ├── Dockerfile.etl
│   ├── Dockerfile.frontend
│   └── Dockerfile.spark
│
├── docs/                        # Documentation
│   ├── architecture.md         # Architecture détaillée
│   ├── api.md                  # Documentation API
│   └── deployment.md           # Guide déploiement
│
├── data/                        # Données traitées (gitignored)
│   ├── raw/                    # Données brutes
│   ├── processed/              # Données nettoyées (Parquet)
│   └── aggregated/             # Agrégations pré-calculées
│
└── logs/                        # Logs (gitignored)
    ├── etl/
    ├── api/
    └── processing/
```

## 🎯 Principes de Séparation

### 1. **ETL (Extract, Transform, Load)**
- **Responsabilité** : Ingestion, nettoyage, validation
- **Technologies** : Pandas, PySpark, Great Expectations
- **Output** : Parquet sur HDFS

### 2. **Processing (Traitement)**
- **Responsabilité** : Agrégations, calculs métier
- **Technologies** : PySpark, Pandas
- **Output** : Agrégations pré-calculées (Parquet + Redis)

### 3. **API (Backend)**
- **Responsabilité** : Service des données, validation, cache
- **Technologies** : FastAPI, Pydantic, Redis
- **Output** : JSON via REST API

### 4. **Frontend (Visualisation)**
- **Responsabilité** : Interface utilisateur, cartes interactives
- **Technologies** : React, TypeScript, Leaflet, D3.js
- **Output** : Application web

## 📋 Conventions de Nommage

### Fichiers Python
- **Modules** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions/Variables** : `snake_case`
- **Constantes** : `UPPER_SNAKE_CASE`

### Fichiers Frontend
- **Composants** : `PascalCase.tsx`
- **Hooks** : `useCamelCase.ts`
- **Services** : `camelCase.ts`
- **Utils** : `camelCase.ts`

### Structure des Modules

```python
# src/etl/extract.py
"""Module d'extraction des données CSV."""

from typing import Iterator
import pandas as pd

def extract_csv_chunks(file_path: str, chunk_size: int = 100000) -> Iterator[pd.DataFrame]:
    """Extrait les données CSV par chunks."""
    ...
```

## 🔧 Configuration

### pyproject.toml (UV)
```toml
[project]
name = "sirene-dataviz"
version = "0.1.0"
description = "Visualisation interactive des données Sirene"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "pyspark>=3.5.0",
    "fastapi>=0.104.0",
    ...
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    ...
]
```

### Makefile
```makefile
.PHONY: install setup run-etl run-api run-frontend test lint format

install:
	uv sync

setup:
	make install
	docker-compose up -d

run-etl:
	python scripts/run_etl.py

run-api:
	uvicorn src.api.main:app --reload

run-frontend:
	cd src/frontend && npm start

test:
	pytest tests/

lint:
	ruff check src/
	black --check src/

format:
	black src/
	ruff check --fix src/
```

## 🐳 Docker

### Séparation des Services
- **etl** : Container pour pipeline ETL
- **api** : Container pour API FastAPI
- **frontend** : Container pour application React
- **spark** : Container pour jobs Spark
- **hdfs** : Container pour HDFS
- **redis** : Container pour cache

## 📝 Logging

### Structure des Logs
- **Format** : JSON structuré
- **Niveaux** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation** : Par jour, conservation 30 jours
- **Séparation** : Par module (etl, api, processing)

## ✅ Checklist de Conformité

- [x] Structure modulaire claire
- [x] Séparation des responsabilités
- [x] Conventions de nommage Python
- [x] Configuration centralisée
- [x] Dockerfiles séparés
- [x] Tests organisés
- [x] Documentation structurée
- [x] Logging structuré
- [x] Gestion des dépendances (UV)
- [x] Makefile pour automatisation
