# Architecture - Sirene DataViz

## Vue d'ensemble

Sirene DataViz est une plateforme de visualisation des donnees d'entreprises francaises (Sirene).
L'architecture est basee sur HDFS comme source de verite pour les donnees.

```
+------------------+     +------------------+     +------------------+
|    Frontend      |     |      API         |     |      Redis       |
|    (React)       |<--->|    (FastAPI)     |<--->|     (Cache)      |
|    Port 3000     |     |    Port 8000     |     |    Port 6379     |
+------------------+     +------------------+     +------------------+
                                  |
                                  v
                         +------------------+
                         |      HDFS        |
                         |  (Hadoop 3.2.1)  |
                         |  NameNode: 9870  |
                         |  DataNode: 9864  |
                         +------------------+
                                  ^
                                  |
                         +------------------+
                         |       ETL        |
                         |  (Python/Pandas) |
                         |  (Docker profile)|
                         +------------------+
```

## Composants

### 1. Frontend (React + TypeScript)

- **Technologie**: React 18, TypeScript, Vite, Leaflet
- **Port**: 3000
- **Role**: Interface utilisateur pour la visualisation des donnees
- **Fonctionnalites**:
  - Carte interactive de France
  - 5 cas d'usage de visualisation
  - Filtres dynamiques

### 2. API (FastAPI)

- **Technologie**: Python 3.11, FastAPI, Uvicorn
- **Port**: 8000
- **Role**: API REST pour servir les donnees agregees
- **Endpoints**: `/api/v1/usecase{1-5}`
- **Cache**: Redis pour les requetes frequentes

### 3. HDFS (Hadoop Distributed File System)

- **Technologie**: Hadoop 3.2.1 (bde2020 images)
- **Ports**: 9870 (Web UI), 9000 (RPC)
- **Role**: Stockage distribue des donnees
- **Structure**:
  ```
  /sirene_data/
    /raw/                 # CSV source
    /processed/           # Parquet traite
  ```

### 4. Redis (Cache)

- **Technologie**: Redis 7 Alpine
- **Port**: 6379
- **Role**: Cache des agregations API
- **Persistence**: AOF active

### 5. ETL (Extract-Transform-Load)

- **Technologie**: Python 3.11, Pandas, PyArrow
- **Execution**: Docker (profile: etl)
- **Role**: Traitement des donnees CSV vers Parquet
- **Pipeline**:
  1. Extract: Lecture CSV par chunks
  2. Transform: Nettoyage et filtrage
  3. Load: Ecriture Parquet vers HDFS

## Flux de donnees

```
1. Ingestion:
   CSV (7.8 GB) --> ETL --> Parquet --> HDFS

2. Requete utilisateur:
   Frontend --> API --> [Cache?] --> HDFS --> Response
```

## Structure du code

```
src/
  api/                    # API FastAPI
    main.py               # Point d'entree
    routers/              # Endpoints par use case
    services/             # Logique metier
      data_service.py     # Agregations
      cache_service.py    # Cache Redis
    models/               # Schemas Pydantic

  etl/                    # Pipeline ETL
    extract.py            # Lecture CSV
    transform.py          # Nettoyage
    load.py               # Ecriture HDFS

  config/                 # Configuration
    settings.py           # Pydantic Settings

  frontend/               # Application React
    src/
      pages/              # Pages par use case
      components/         # Composants UI
      services/           # Client API

scripts/                  # Scripts utilitaires
  dev.py                  # Demarrage dev
  run_etl.py              # Lancement ETL
  check_hdfs_data.py      # Verification HDFS

docker/                   # Dockerfiles
  Dockerfile.api
  Dockerfile.etl
  Dockerfile.frontend
```

## Services Docker

| Service | Image | Role |
|---------|-------|------|
| redis | redis:7-alpine | Cache |
| hdfs-namenode | bde2020/hadoop-namenode | HDFS Master |
| hdfs-datanode | bde2020/hadoop-datanode | HDFS Storage |
| api | custom | API FastAPI |
| frontend | custom | React App |
| etl | custom (profile) | Pipeline ETL |

## Commandes principales

```bash
# Demarrer l'environnement
make dev

# Executer l'ETL
make run-etl-docker

# Verifier les donnees HDFS
make check-hdfs-data-docker

# Lister les fichiers HDFS
make list-hdfs

# Arreter l'environnement
make dev-stop
```

## Technologies utilisees

| Categorie | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python | 3.11+ |
| Framework API | FastAPI | 0.104+ |
| Frontend | React | 18 |
| Build Frontend | Vite | - |
| Stockage | HDFS | 3.2.1 |
| Cache | Redis | 7 |
| Format donnees | Parquet | - |
| Containerisation | Docker | - |
| Package Manager | UV | - |

## Decisions d'architecture

1. **HDFS obligatoire**: Source de verite unique pour les donnees, pas de fallback local.

2. **ETL dans Docker**: S'execute dans le meme reseau Docker que HDFS pour la connectivite.

3. **Cache Redis**: Reduit la charge sur HDFS pour les requetes frequentes.

4. **Format Parquet**: Format colonnaire optimise pour les agregations analytiques.

5. **Pas de Spark**: Le volume de donnees actuel est gerable avec Pandas. Spark peut etre ajoute plus tard si necessaire.
