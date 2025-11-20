# Sirene DataViz

Plateforme de visualisation interactive des données Sirene (répertoire des entreprises françaises) avec des cartes de France interactives.

## 📋 Description

Ce projet permet d'analyser différents aspects des entreprises françaises par région à travers 5 use cases :

1. **Évolution des créations d'entreprises** : Par année et secteur d'activité
2. **Répartition par sexe des dirigeants** : Selon les secteurs d'activité
3. **Répartition des effectifs** : Par secteurs et territoires
4. **Dominance sectorielle** : Par région
5. **Types juridiques et catégories** : Par secteur et région

## 🛠️ Technologies

- **Backend** : Python 3.11+, FastAPI, PySpark
- **Frontend** : React, TypeScript, Leaflet
- **Stockage** : HDFS, Parquet, Redis
- **Orchestration** : Prefect, Docker
- **Outils** : UV, Makefile

## 🚀 Installation

### Prérequis

- Python 3.11+
- UV (gestionnaire de dépendances)
- Docker & Docker Compose
- Node.js 18+ (pour le frontend)

### Setup

```bash
# Cloner le projet
git clone <repository-url>
cd IPSSI_19_11_2025

# Setup complet (installe les dépendances et crée le .env automatiquement)
make setup

# OU étape par étape :
# Installer les dépendances (crée aussi le .env automatiquement)
make install

# Lancer toutes les ressources pour le développement (recommandé)
make dev

# OU étape par étape :
# Lancer les services Docker
make docker-up

# Lancer l'ETL (première fois)
make run-etl

# Lancer l'API
make run-api

# Dans un autre terminal, lancer le frontend
make run-frontend

# Pour arrêter toutes les ressources
make dev-stop
```

## 📁 Structure du Projet

Voir `PROJECT_STRUCTURE.md` pour la structure détaillée.

## 📊 Dataset

- **Source** : `dataset/Sirene_merged_with_region.csv`
- **Volume** : ~42 millions de lignes (~7.8 GB)
- **Colonnes** : 28 colonnes

Voir `DATASET_ANALYSIS.md` pour l'analyse complète du dataset.

## 🧪 Tests

```bash
# Tous les tests
make test

# Tests unitaires uniquement
make test-unit

# Tests d'intégration
make test-integration
```

## 🔧 Développement

```bash
# Formater le code
make format

# Vérifier le code
make lint

# Nettoyer les fichiers temporaires
make clean
```

## 📚 Documentation

- `ANALYSE_PROJET.md` : Analyse et proposition d'amélioration
- `DATASET_ANALYSIS.md` : Analyse du dataset
- `PROJECT_STRUCTURE.md` : Structure du projet
- `roadmap.txt` : Roadmap du projet

## 📝 License

MIT

