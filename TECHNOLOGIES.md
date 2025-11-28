# Technologies utilisées dans Sirene DataViz

Ce document liste toutes les technologies, dépendances et outils utilisés dans le projet.

## 🔍 Vérification rapide

Pour vérifier l'état de toutes les technologies, exécutez :

```bash
make check-tech
```

ou directement :

```bash
python scripts/check_technologies.py
```

---

## 📋 Liste complète des technologies

### 🐍 Backend Python

#### Langage et runtime
- **Python 3.11+** : Langage de programmation principal
- **UV** : Gestionnaire de dépendances Python moderne et rapide

#### Framework et serveur web
- **FastAPI 0.104.0+** : Framework web moderne et performant pour créer l'API REST
- **Uvicorn 0.24.0+** : Serveur ASGI pour exécuter FastAPI
- **Pydantic 2.5.0+** : Validation de données et modèles de données
- **Pydantic Settings 2.1.0+** : Gestion des paramètres de configuration

#### Traitement de données
- **Pandas 2.0.0+** : Manipulation et analyse de données tabulaires
- **PySpark 3.5.0+** : Traitement distribué de données à grande échelle
- **PyArrow 14.0.0+** : Format Parquet pour le stockage optimisé des données
- **Great Expectations 0.18.0+** : Validation et qualité des données

#### Cache et stockage
- **Redis 5.0.0+** : Cache en mémoire pour améliorer les performances de l'API

#### Utilitaires
- **Python-dotenv 1.0.0+** : Gestion des variables d'environnement
- **TQDM 4.66.0+** : Barres de progression pour les opérations longues
- **HTTPX 0.25.0+** : Client HTTP asynchrone pour les tests et appels API

#### Build system
- **Hatchling** : Système de build pour les packages Python

---

### ⚛️ Frontend

#### Framework et langage
- **React 18.2.0** : Bibliothèque JavaScript pour construire l'interface utilisateur
- **TypeScript 5.3.3** : Superset typé de JavaScript pour une meilleure maintenabilité
- **Vite 7.2.4** : Build tool moderne et rapide pour le développement frontend

#### Visualisation de données
- **Leaflet 1.9.4** : Bibliothèque JavaScript pour les cartes interactives
- **React-Leaflet 4.2.1** : Intégration de Leaflet avec React
- **Recharts 2.10.3** : Bibliothèque de graphiques pour React

#### Navigation et HTTP
- **React Router DOM 6.20.0** : Routage côté client pour React
- **Axios 1.6.2** : Client HTTP pour les appels API

#### Types TypeScript
- **@types/leaflet 1.9.8** : Types TypeScript pour Leaflet
- **@types/react 18.2.43** : Types TypeScript pour React
- **@types/react-dom 18.2.17** : Types TypeScript pour React DOM

#### Outils de développement frontend
- **ESLint 8.54.0** : Linter JavaScript/TypeScript
- **@typescript-eslint/eslint-plugin 6.13.1** : Plugin ESLint pour TypeScript
- **@typescript-eslint/parser 6.13.1** : Parser ESLint pour TypeScript
- **eslint-plugin-react 7.33.2** : Plugin ESLint pour React
- **eslint-plugin-react-hooks 4.6.0** : Plugin ESLint pour les hooks React
- **eslint-plugin-react-refresh 0.4.4** : Plugin ESLint pour React Refresh
- **@vitejs/plugin-react 4.2.1** : Plugin Vite pour React

---

### 🐳 Infrastructure et conteneurisation

#### Conteneurisation
- **Docker** : Plateforme de conteneurisation pour isoler les services
- **Docker Compose** : Orchestration de conteneurs multi-services

#### Services conteneurisés
- **Redis 7-alpine** : Cache en mémoire (container)
- **HDFS (Hadoop 3.2.1)** : Système de fichiers distribué pour le stockage
  - **NameNode** : Gestionnaire de métadonnées HDFS
  - **DataNode** : Stockage des données HDFS
- **Spark 3.0.0** : Moteur de traitement distribué
  - **Spark Master** : Coordinateur du cluster Spark
  - **Spark Worker** : Nœuds de traitement Spark
- **Nginx** : Serveur web pour servir le frontend en production

---

### 🛠️ Outils de développement

#### Tests
- **Pytest 7.4.0+** : Framework de tests Python
- **Pytest-asyncio 0.21.0+** : Support des tests asynchrones
- **Pytest-cov 4.1.0+** : Couverture de code pour les tests

#### Qualité de code Python
- **Black 23.11.0+** : Formateur de code Python
- **Ruff 0.1.0+** : Linter Python ultra-rapide (remplace Flake8, isort, etc.)
- **MyPy 1.7.0+** : Vérificateur de types statique pour Python

#### Git hooks
- **Pre-commit 3.5.0+** : Framework de gestion des hooks Git
  - Hooks pour trailing whitespace, end-of-file
  - Vérification YAML, JSON, TOML
  - Black et Ruff automatiques

#### Automatisation
- **Make** : Automatisation des tâches via Makefile

---

### 📊 Formats de données

- **CSV** : Format d'entrée pour les données brutes (Sirene_merged_with_region.csv)
- **Parquet** : Format de sortie optimisé pour le stockage et la lecture rapide

---

## 🏗️ Architecture technique

### Backend
```
FastAPI (Uvicorn)
    ↓
Data Service (Pandas/PySpark)
    ↓
Cache Service (Redis)
    ↓
HDFS/Parquet (Stockage)
```

### Frontend
```
React (TypeScript)
    ↓
Vite (Build)
    ↓
Axios → FastAPI
    ↓
Leaflet (Cartes) + Recharts (Graphiques)
```

### Infrastructure
```
Docker Compose
    ├── Redis (Cache)
    ├── HDFS (Stockage)
    ├── Spark (Traitement)
    ├── API (FastAPI)
    └── Frontend (Nginx)
```

---

## 📦 Gestion des dépendances

### Python
Les dépendances Python sont gérées via `pyproject.toml` et installées avec **UV** :

```bash
uv sync  # Installe toutes les dépendances
```

### Frontend
Les dépendances frontend sont gérées via `package.json` et installées avec **npm** :

```bash
cd src/frontend
npm install  # Installe toutes les dépendances
```

---

## 🔄 Workflow de développement

1. **ETL** : Traitement des données CSV → Parquet (Pandas/PySpark)
2. **API** : Service FastAPI qui lit les données Parquet et les expose via REST
3. **Cache** : Redis met en cache les agrégations pour améliorer les performances
4. **Frontend** : React consomme l'API et affiche les visualisations

---

## 📝 Fichiers de configuration clés

- `pyproject.toml` : Configuration Python, dépendances, outils (Black, Ruff, MyPy)
- `package.json` : Dépendances frontend et scripts npm
- `docker-compose.yml` : Configuration des services Docker
- `Makefile` : Automatisation des tâches courantes
- `.pre-commit-config.yaml` : Configuration des hooks Git
- `tsconfig.json` : Configuration TypeScript
- `vite.config.ts` : Configuration Vite

---

## 🚀 Commandes utiles

```bash
# Vérifier toutes les technologies
make check-tech

# Installer les dépendances
make install

# Lancer l'ETL
make run-etl

# Lancer l'API
make run-api

# Lancer le frontend
make run-frontend

# Lancer l'environnement complet
make dev

# Tests
make test

# Formatage et linting
make format
make lint
```

---

## 📈 Versions et compatibilité

- **Python** : 3.11+ (requis)
- **Node.js** : Version LTS recommandée
- **Docker** : Version récente recommandée
- **UV** : Dernière version recommandée

---

## 🔍 Vérification automatique

Le script `scripts/check_technologies.py` vérifie automatiquement :
- ✅ Versions installées
- ✅ Disponibilité des commandes
- ✅ État des containers Docker
- ✅ Présence des fichiers de données
- ✅ Structure du projet

Génère un rapport JSON : `technology_report.json`

