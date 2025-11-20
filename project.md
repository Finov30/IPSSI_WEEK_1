# Extraire 100k lignes du fichier csv
_Exported on 11/20/2025 at 11:57:16 GMT+1 from Cursor (2.0.75)_

---

**User**

Recupére les premier 100 k premiere ligne du csv  et fait un autre fichier csv avec ces lignes tu lenomme 100k.csv .

---

**Cursor**

Recherche des fichiers CSV dans le projet.


Vérification de `get100K.py` pour identifier le fichier CSV cible :


Extraction des 100 000 premières lignes du CSV le plus volumineux. Vérification des tailles pour identifier le fichier cible :


Extraction des 100 000 premières lignes de `StockEtablissement_utf8.csv` (le plus volumineux) et création de `100k.csv` :


---

**User**

Tu dosi faire cela sur le fichier Sirene merged with region 

---

**Cursor**


Extraction des 100 000 premières lignes de `Sirene_merged_with_region.csv` et création de `100k.csv`.



Vérification que le fichier `100k.csv` a bien été créé et contient 100 000 lignes :



Extraction terminée. Le fichier `100k.csv` a été créé avec les 100 000 premières lignes de `Sirene_merged_with_region.csv`. Vérification : le fichier contient exactement 100 000 lignes.

---

**User**

Maintenant regarde le ficheir @roadmap.txt  je veux que tu comprenne le but du projet que tu me propose des axes d'amélioration que tu restrcture ems idée et que tu me propose des techno a utiliser et ensuite dans un second temp nous ferons notre archtiecture avec mermaid 

---

**Cursor**


Analyse du fichier roadmap et préparation d'une proposition structurée avec axes d'amélioration et technologies.



Analyse du projet et rédaction d'un document structuré avec axes d'amélioration et technologies.



Rédaction d'un document d'analyse structuré :


```markdown
# Analyse et Proposition d'Amélioration - Projet Sirene DataViz

## 📋 Compréhension du Projet

### Objectif Principal
Créer une plateforme de visualisation interactive de données Sirene (répertoire des entreprises françaises) avec des cartes de France interactives permettant d'analyser différents aspects des entreprises par région.

### Dataset
- **Source** : `Sirene_merged_with_region.csv` (~7.8 GB)
- **Contenu** : Données fusionnées des établissements et unités légales avec mapping régional
- **Volume** : Plusieurs millions d'enregistrements

### Use Cases Identifiés
1. **Évolution des créations d'entreprises** : Par année et secteur d'activité
2. **Répartition par sexe des dirigeants** : Selon les secteurs d'activité
3. **Répartition des effectifs** : Par secteurs et territoires
4. **Dominance sectorielle** : Par région
5. **Types juridiques et catégories** : Par secteur et région

### Règles Métier Identifiées
- **Filtrage obligatoire** : Exclure les entreprises avec `Etat_Administratif_Entreprise = 'C'` (radiées)
- **Colonnes à supprimer** : `Denomination_Usuelle_Etablissement`, `Enseigne_Etablissement`, `Status_Diffusion`
- **Gestion des nulls** : 
  - `Date_Creation_Entreprise` : Null acceptable (ne pas traiter dans use case 1 si null)
  - `Sexe_Dirigeant` : Null acceptable (ne pas traiter dans use case 2 si null)
  - `Effectifs_Entreprises` : Null = "NN" (Non renseigné)
- **Colonnes toujours vides** : `Employeur_Entreprise`, `Enseigne_Etablissement`, `Denomination_Usuelle_Etablissement`
- **Nom entreprise** : Soit `Denomination_Entreprise` soit `Nom_Entreprise` (mutuellement exclusif)

---

## 🎯 Axes d'Amélioration

### 1. Architecture & Infrastructure

#### Problèmes identifiés
- Pas de séparation claire entre ingestion, traitement et visualisation
- HDFS mentionné mais pas de stratégie de stockage intermédiaire
- Pas de mention de cache pour les visualisations

#### Améliorations proposées
- **Architecture en couches** : 
  - Layer 1 : Ingestion & Nettoyage (ETL)
  - Layer 2 : Stockage (HDFS + Parquet pour performance)
  - Layer 3 : Traitement & Agrégation (Spark/PySpark)
  - Layer 4 : API & Services (FastAPI/Flask)
  - Layer 5 : Frontend & Visualisation (Dash/Streamlit/React)
- **Cache stratégique** : Redis pour les agrégations fréquentes
- **Orchestration** : Airflow/Prefect pour les pipelines ETL

### 2. Traitement des Données

#### Problèmes identifiés
- Traitement par batch mais pas de validation de qualité
- Pas de gestion des doublons explicite
- Pas de normalisation des codes APE/NAF

#### Améliorations proposées
- **Pipeline de validation** : 
  - Schéma de données (Pydantic/Great Expectations)
  - Contrôles de cohérence (dates, codes postaux, etc.)
  - Détection d'anomalies
- **Normalisation** :
  - Codes APE/NAF vers libellés (mapping INSEE)
  - Normalisation des dates
  - Standardisation des effectifs
- **Déduplication** : Stratégie claire sur SIREN/SIRET

### 3. Performance & Scalabilité

#### Problèmes identifiés
- Fichier CSV volumineux (7.8 GB) - format non optimisé
- Pas de partitionnement mentionné
- Traitement séquentiel potentiellement lent

#### Améliorations proposées
- **Format de stockage** : 
  - Parquet (compression, colonnes, partitionnement)
  - Partitionnement par région/année pour requêtes rapides
- **Traitement distribué** : PySpark pour les agrégations
- **Indexation** : Sur colonnes fréquemment filtrées (région, secteur, année)

### 4. Visualisation & UX

#### Problèmes identifiés
- Pas de spécification de l'interactivité
- Pas de mention de filtres temporels
- Pas de gestion de la performance côté frontend

#### Améliorations proposées
- **Framework de visualisation** :
  - Dash/Plotly pour cartes interactives natives
  - Ou React + D3.js/Leaflet pour plus de contrôle
- **Fonctionnalités** :
  - Filtres multiples (année, secteur, région, type juridique)
  - Zoom/pan sur cartes
  - Tooltips avec détails
  - Export de données
  - Comparaisons temporelles (slider année)
- **Performance** :
  - Lazy loading des données
  - Agrégations pré-calculées
  - Pagination pour grandes listes

### 5. Qualité & Monitoring

#### Problèmes identifiés
- Pas de logging structuré
- Pas de métriques de qualité de données
- Pas de monitoring des pipelines

#### Améliorations proposées
- **Logging** : Structuré (JSON) avec niveaux appropriés
- **Métriques** : 
  - Taux de complétude par colonne
  - Nombre d'entreprises filtrées
  - Temps de traitement
- **Alertes** : Sur échecs de pipeline ou anomalies détectées

---

## 🔄 Restructuration des Idées

### Phase 1 : Ingestion & Nettoyage (ETL)
```
1. Lecture du CSV source
2. Application des règles de filtrage :
   - Suppression colonnes inutiles
   - Exclusion entreprises radiées (Etat = 'C')
   - Gestion des nulls selon règles métier
3. Validation & normalisation :
   - Validation schéma
   - Normalisation codes APE/NAF
   - Standardisation dates
4. Export format optimisé (Parquet) vers HDFS
```

### Phase 2 : Préparation & Agrégation
```
1. Chargement depuis HDFS
2. Création de vues agrégées par use case :
   - Use Case 1 : Créations par année/secteur/région
   - Use Case 2 : Dirigeants par sexe/secteur/région
   - Use Case 3 : Effectifs par secteur/région
   - Use Case 4 : Dominance sectorielle par région
   - Use Case 5 : Types juridiques par secteur/région
3. Stockage des agrégations (Parquet + Redis cache)
```

### Phase 3 : API & Services
```
1. API REST pour servir les données agrégées
2. Endpoints par use case
3. Filtres dynamiques (année, secteur, région)
4. Cache Redis pour performance
```

### Phase 4 : Frontend & Visualisation
```
1. Interface web interactive
2. Cartes de France avec visualisations
3. Filtres et contrôles utilisateur
4. Export et partage
```

---

## 🛠️ Technologies Proposées

### Stack Technique Recommandée

#### **Ingestion & ETL**
- **Python 3.11+** avec **UV** (gestionnaire de dépendances rapide)
- **Pandas** : Traitement initial et validation
- **PySpark** : Pour gros volumes et traitement distribué
- **Great Expectations** : Validation de qualité de données
- **Pydantic** : Validation de schémas

#### **Stockage**
- **HDFS** : Stockage distribué (comme demandé)
- **Parquet** : Format de stockage optimisé (compression, colonnes)
- **Redis** : Cache pour agrégations fréquentes
- **PostgreSQL/ClickHouse** (optionnel) : Pour requêtes analytiques rapides

#### **Orchestration & Pipelines**
- **Prefect** : Orchestration moderne et simple (alternative à Airflow)
- **Makefile** : Commandes de build et déploiement (comme demandé)

#### **API & Backend**
- **FastAPI** : API moderne, rapide, avec documentation auto
- **Pydantic** : Validation des requêtes/réponses
- **Redis** : Cache des résultats d'agrégation

#### **Visualisation & Frontend**
- **Option A (Rapide)** : 
  - **Dash/Plotly** : Framework Python pour dashboards interactifs
  - Avantages : Développement rapide, cartes intégrées, pas de frontend séparé
- **Option B (Flexible)** :
  - **React** : Framework frontend moderne
  - **Leaflet** ou **Mapbox GL JS** : Cartes interactives
  - **D3.js** : Visualisations avancées
  - **Recharts/Chart.js** : Graphiques
  - Avantages : Plus de contrôle, meilleure UX, scalable

#### **Infrastructure & Déploiement**
- **Docker** : Containerisation (comme demandé)
- **Docker Compose** : Orchestration locale
- **Hadoop/HDFS** : Stockage distribué
- **Spark** : Traitement distribué (si nécessaire)

#### **Outils de Développement**
- **UV** : Gestionnaire de dépendances Python (comme demandé)
- **Makefile** : Automatisation des tâches (comme demandé)
- **Pre-commit hooks** : Validation de code
- **Black/ruff** : Formatage et linting

### Architecture Technique Détaillée

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Visualisation)                  │
│  Option A: Dash/Plotly  |  Option B: React + Leaflet        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────┐
│                    API LAYER (FastAPI)                       │
│  - Endpoints par use case                                    │
│  - Validation Pydantic                                       │
│  - Cache Redis                                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              PROCESSING LAYER (PySpark/Pandas)               │
│  - Agrégations par use case                                  │
│  - Calculs de métriques                                      │
│  - Filtres dynamiques                                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼────────┐              ┌───────────▼──────────┐
│  HDFS/Parquet  │              │      Redis Cache     │
│  (Données)     │              │  (Agrégations)       │
└────────────────┘              └──────────────────────┘
        │
┌───────▼──────────────────────────────────────────────┐
│         ETL PIPELINE (Prefect)                        │
│  - Ingestion CSV                                       │
│  - Nettoyage & validation                             │
│  - Export Parquet                                      │
└───────────────────────────────────────────────────────┘
```

---

## 📊 Recommandations Spécifiques

### Pour les Use Cases

1. **Use Case 1 (Évolution créations)** :
   - Agrégation : `COUNT(*) GROUP BY année, secteur, région`
   - Visualisation : Carte choroplèthe + graphique temporel
   - Filtres : Année (slider), Secteur (multi-select)

2. **Use Case 2 (Sexe dirigeants)** :
   - Agrégation : `COUNT(*) GROUP BY sexe, secteur, région`
   - Visualisation : Carte avec proportions (pie charts par région)
   - Filtres : Secteur, Région

3. **Use Case 3 (Effectifs)** :
   - Agrégation : `SUM(effectifs) GROUP BY secteur, région`
   - Visualisation : Carte avec tailles de bulles proportionnelles
   - Filtres : Secteur, Tranche d'effectifs

4. **Use Case 4 (Dominance sectorielle)** :
   - Agrégation : Secteur dominant par région (TOP 1)
   - Visualisation : Carte avec couleurs par secteur dominant
   - Filtres : Année

5. **Use Case 5 (Types juridiques)** :
   - Agrégation : `COUNT(*) GROUP BY type_juridique, secteur, région`
   - Visualisation : Carte avec heatmap + tableau croisé
   - Filtres : Secteur, Type juridique

### Optimisations de Performance

- **Pré-agrégation** : Calculer les agrégations une fois, stocker en Parquet
- **Partitionnement** : Par année et région pour requêtes rapides
- **Cache** : Redis pour les requêtes fréquentes (ex: données 2024)
- **Lazy loading** : Charger les données à la demande dans le frontend
- **Compression** : Parquet avec compression Snappy ou Zstd

---

## 🚀 Prochaines Étapes

1. ✅ **Validation de cette analyse** avec vous
2. 🔄 **Création de l'architecture Mermaid** détaillée
3. 📁 **Structure du projet** avec dossiers et fichiers de base
4. 🐳 **Dockerfiles et docker-compose.yml**
5. 📝 **Makefile** avec commandes principales
6. ⚙️ **Configuration UV** (pyproject.toml)
7. 🔧 **Scripts ETL** de base avec règles métier
8. 🗺️ **Prototype de visualisation** (carte de base)

---

## ❓ Questions à Clarifier

1. **Volume de données** : Travailler sur le fichier complet (7.8 GB) ou un échantillon pour le développement ?
2. **Infrastructure** : HDFS disponible localement ou besoin de setup ?
3. **Visualisation** : Préférence pour Dash (rapide) ou React (plus flexible) ?
4. **Performance** : Temps de réponse acceptable pour les visualisations ?
5. **Déploiement** : Production prévue ou uniquement développement local ?

```


J'ai créé un document d'analyse structuré (`ANALYSE_PROJET.md`) qui comprend :

## Ce que j'ai fait :

1. **Compréhension du projet** : Objectifs, dataset, use cases et règles métier
2. **5 axes d'amélioration** :
   - Architecture & Infrastructure
   - Traitement des Données
   - Performance & Scalabilité
   - Visualisation & UX
   - Qualité & Monitoring
3. **Restructuration** : 4 phases (ETL → Agrégation → API → Frontend)
4. **Stack technique** :
   - **ETL** : Python + UV + Pandas + PySpark
   - **Stockage** : HDFS + Parquet + Redis
   - **Orchestration** : Prefect
   - **API** : FastAPI
   - **Frontend** : Dash/Plotly (rapide) ou React + Leaflet (flexible)
   - **Infrastructure** : Docker + Docker Compose

## Recommandations clés :

- Utiliser **Parquet** au lieu de CSV pour de meilleures performances
- **Pré-agrégation** des données par use case
- **Cache Redis** pour les requêtes fréquentes
- **Dash/Plotly** pour un développement rapide, ou **React** pour plus de flexibilité

Le document est prêt. Souhaitez-vous que je crée l'architecture Mermaid maintenant, ou préférez-vous d'abord revoir et ajuster cette analyse ?

---

**User**

Alors j'ai validé les techno je veux maintenant que tu lise le header du CSV pour mieux le comprendre que tu print le nombre de ligne pour comprendre la taille et que tu read les 1000 premiere, puis je veux aussi que tu note  que nous allons faire  project ordonné avec une bonne séparation des fichier je veux respecter les convention

---

**Cursor**


Analyse du CSV : lecture du header, comptage des lignes, puis lecture des 1000 premières lignes. Ensuite, préparation d'une structure de projet organisée selon les conventions.



Création d'un script Python pour analyser le CSV :


```python
"""Script temporaire pour analyser le fichier CSV Sirene"""
import pandas as pd
from tqdm import tqdm

CSV_FILE = 'Sirene_merged_with_region.csv'

print("=" * 80)
print("ANALYSE DU FICHIER CSV - Sirene_merged_with_region.csv")
print("=" * 80)

# 1. Lire le header
print("\n1. HEADER DU CSV")
print("-" * 80)
df_header = pd.read_csv(CSV_FILE, nrows=0)
print(f"Nombre de colonnes: {len(df_header.columns)}")
print("\nListe des colonnes:")
for i, col in enumerate(df_header.columns, 1):
    print(f"  {i:2d}. {col}")

# 2. Compter le nombre de lignes
print("\n2. COMPTAGE DES LIGNES")
print("-" * 80)
count = 0
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    next(f)  # Skip header
    for line in tqdm(f, desc="Comptage en cours"):
        count += 1
print(f"\nNombre total de lignes (sans header): {count:,}")

# 3. Lire les 1000 premières lignes
print("\n3. PREMIÈRES 1000 LIGNES")
print("-" * 80)
df_sample = pd.read_csv(CSV_FILE, nrows=1000)
print(f"\nShape: {df_sample.shape[0]} lignes x {df_sample.shape[1]} colonnes")
print("\nAperçu des premières lignes:")
print(df_sample.head(10).to_string())
print("\n...")
print(f"\nInformations sur les colonnes:")
print(df_sample.info())
print("\nStatistiques descriptives:")
print(df_sample.describe(include='all'))

```


Recherche du fichier CSV :



Mise à jour du script pour utiliser le bon chemin :


```python
"""Script temporaire pour analyser le fichier CSV Sirene"""
import pandas as pd
from tqdm import tqdm

CSV_FILE = 'dataset/Sirene_merged_with_region.csv'

print("=" * 80)
print("ANALYSE DU FICHIER CSV - Sirene_merged_with_region.csv")
print("=" * 80)

# 1. Lire le header
print("\n1. HEADER DU CSV")
print("-" * 80)
df_header = pd.read_csv(CSV_FILE, nrows=0)
print(f"Nombre de colonnes: {len(df_header.columns)}")
print("\nListe des colonnes:")
for i, col in enumerate(df_header.columns, 1):
    print(f"  {i:2d}. {col}")

# 2. Compter le nombre de lignes
print("\n2. COMPTAGE DES LIGNES")
print("-" * 80)
count = 0
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    next(f)  # Skip header
    for line in tqdm(f, desc="Comptage en cours"):
        count += 1
print(f"\nNombre total de lignes (sans header): {count:,}")

# 3. Lire les 1000 premières lignes
print("\n3. PREMIÈRES 1000 LIGNES")
print("-" * 80)
df_sample = pd.read_csv(CSV_FILE, nrows=1000)
print(f"\nShape: {df_sample.shape[0]} lignes x {df_sample.shape[1]} colonnes")
print("\nAperçu des premières lignes:")
print(df_sample.head(10).to_string())
print("\n...")
print(f"\nInformations sur les colonnes:")
print(df_sample.info())
print("\nStatistiques descriptives:")
print(df_sample.describe(include='all'))


```


Création d'un document récapitulatif et d'une structure de projet organisée selon les conventions :


```markdown
# Analyse du Dataset Sirene

## 📊 Informations Générales

- **Fichier** : `dataset/Sirene_merged_with_region.csv`
- **Taille** : ~7.8 GB
- **Nombre de lignes** : **42,151,993** (plus de 42 millions d'enregistrements)
- **Nombre de colonnes** : **28**

## 📋 Structure des Colonnes

### Colonnes Identifiées (28 au total)

1. `SIREN` - Numéro SIREN (int64)
2. `SIRET` - Numéro SIRET (int64)
3. `Effectifs_Etablissement` - Effectifs de l'établissement (object, valeurs "NN" pour non renseigné)
4. `Date_MAJ_Etablissement` - Date de mise à jour établissement (object, format ISO)
5. `Code_Postal` - Code postal (object)
6. `Ville` - Nom de la ville (object)
7. `Date_Debut_Activite_Etablissement` - Date début activité établissement (object, nullable)
8. `Etat_Administratif_Etablissement` - État administratif établissement (object: A, F, C)
9. `Enseigne_Etablissement` - Enseigne (object, **toujours vide** - à supprimer)
10. `Denomination_Usuelle_Etablissement` - Dénomination usuelle (object, **toujours vide** - à supprimer)
11. `Code_APE_Etablissement` - Code APE établissement (object, nullable)
12. `Employeur_Etablissement` - Caractère employeur établissement (object: N, O)
13. `Statut_Diffusion` - Statut de diffusion (object, **à supprimer**)
14. `Date_Creation_Entreprise` - Date création entreprise (object, nullable - important pour UC1)
15. `Sexe_Dirigeant` - Sexe du dirigeant (object: M, F, nullable - important pour UC2)
16. `Prenom_Dirigeant` - Prénom dirigeant (object, nullable - **non utilisé**)
17. `Effectifs_Entreprise` - Effectifs entreprise (object, valeurs "NN" pour null)
18. `Date_MAJ_Entreprise` - Date mise à jour entreprise (object)
19. `Categorie_Entreprise_PME_TPE` - Catégorie PME/TPE (object, nullable - **null si Etat = 'C'**)
20. `Date_Debut_Activite_Entreprise` - Date début activité entreprise (object, nullable)
21. `Etat_Administratif_Entreprise` - État administratif entreprise (object: A, F, C - **CRITIQUE: exclure 'C'**)
22. `Nom_Entreprise` - Nom entreprise (object, nullable - mutuellement exclusif avec Denomination_Entreprise)
23. `Nom_Dirigeant` - Nom dirigeant (object, nullable - **non utilisé**)
24. `Denomination_Entreprise` - Dénomination entreprise (object, nullable - mutuellement exclusif avec Nom_Entreprise)
25. `Categorie_Juridique` - Catégorie juridique (int64, code INSEE)
26. `Code_APE_Entreprise` - Code APE entreprise (object, nullable)
27. `Employeur_Entreprise` - Caractère employeur entreprise (float64, **toujours vide** - à supprimer)
28. `Region` - Région (object, nullable - important pour toutes les visualisations)

## 🔍 Observations sur l'Échantillon (1000 premières lignes)

### Taux de Complétude
- **Colonnes toujours remplies** : SIREN, SIRET, Effectifs_Etablissement, Date_MAJ_Etablissement, Code_Postal, Ville, Etat_Administratif_Etablissement, Statut_Diffusion, Effectifs_Entreprise, Date_MAJ_Entreprise, Etat_Administratif_Entreprise, Categorie_Juridique
- **Colonnes souvent vides** :
  - `Enseigne_Etablissement` : 2.3% rempli (23/1000)
  - `Denomination_Usuelle_Etablissement` : 1.2% rempli (12/1000)
  - `Employeur_Entreprise` : 0% rempli (0/1000) ⚠️
  - `Categorie_Entreprise_PME_TPE` : 11.6% rempli (116/1000)
  - `Date_Creation_Entreprise` : 58.9% rempli (589/1000)
  - `Sexe_Dirigeant` : 72.5% rempli (725/1000)
  - `Region` : 99.1% rempli (991/1000)

### Règles Métier Confirmées
- ✅ `Employeur_Entreprise` est toujours vide (0 non-null sur 1000)
- ✅ `Enseigne_Etablissement` est presque toujours vide (2.3% rempli)
- ✅ `Denomination_Usuelle_Etablissement` est presque toujours vide (1.2% rempli)
- ✅ `Nom_Entreprise` et `Denomination_Entreprise` sont mutuellement exclusifs
- ✅ `Etat_Administratif_Entreprise = 'C'` → `Categorie_Entreprise_PME_TPE` est null

### Types de Données
- **Numériques** : SIREN (int64), SIRET (int64), Categorie_Juridique (int64)
- **Textuelles** : La majorité des colonnes (object)
- **Dates** : Format ISO (ex: "2024-03-22T15:40:57")
- **Codes** : APE (ex: "32.12Z"), Effectifs (ex: "NN", codes INSEE)

## 📝 Actions de Nettoyage à Effectuer

### Colonnes à Supprimer
1. `Enseigne_Etablissement` - Toujours vide
2. `Denomination_Usuelle_Etablissement` - Toujours vide
3. `Statut_Diffusion` - Non utilisé
4. `Employeur_Entreprise` - Toujours vide
5. `Prenom_Dirigeant` - Non utilisé selon roadmap
6. `Nom_Dirigeant` - Non utilisé selon roadmap

### Filtres à Appliquer
1. **Exclure** toutes les lignes où `Etat_Administratif_Entreprise = 'C'` (radiées)
2. **Gérer les nulls** :
   - `Date_Creation_Entreprise` : Null acceptable (exclure de UC1 si null)
   - `Sexe_Dirigeant` : Null acceptable (exclure de UC2 si null)
   - `Effectifs_Entreprise` : Null → "NN"

### Normalisations à Effectuer
1. **Codes APE** : Extraire le secteur d'activité (2 premiers chiffres)
2. **Dates** : Convertir en format date standardisé
3. **Effectifs** : Standardiser les codes (NN, 00, 01, 02, 03, 11, 12, 21, 22, 31, 32, 41, 42, 51, 52, 53)
4. **Région** : Vérifier la complétude (99.1% rempli)

## 🎯 Impact sur les Use Cases

### Use Case 1 : Évolution créations par année/secteur
- **Colonnes nécessaires** : `Date_Creation_Entreprise`, `Code_APE_Entreprise`, `Region`
- **Filtre** : Exclure les nulls de `Date_Creation_Entreprise`
- **Agrégation** : GROUP BY année, secteur (APE), région

### Use Case 2 : Répartition par sexe dirigeants
- **Colonnes nécessaires** : `Sexe_Dirigeant`, `Code_APE_Entreprise`, `Region`
- **Filtre** : Exclure les nulls de `Sexe_Dirigeant`
- **Agrégation** : GROUP BY sexe, secteur (APE), région

### Use Case 3 : Répartition effectifs par secteurs/territoires
- **Colonnes nécessaires** : `Effectifs_Entreprise`, `Code_APE_Entreprise`, `Region`
- **Gestion nulls** : "NN" pour non renseigné
- **Agrégation** : GROUP BY effectifs, secteur (APE), région

### Use Case 4 : Dominance sectorielle par région
- **Colonnes nécessaires** : `Code_APE_Entreprise`, `Region`
- **Agrégation** : TOP 1 secteur par région

### Use Case 5 : Types juridiques par secteur/région
- **Colonnes nécessaires** : `Categorie_Juridique`, `Code_APE_Entreprise`, `Region`
- **Agrégation** : GROUP BY catégorie juridique, secteur (APE), région

## ⚠️ Points d'Attention

1. **Volume important** : 42+ millions de lignes nécessitent un traitement optimisé (PySpark, partitionnement)
2. **Taux de nulls variables** : Adapter les traitements selon le taux de complétude
3. **Format dates** : Format ISO à parser correctement
4. **Codes APE** : Nécessite un mapping vers libellés de secteurs
5. **Région** : 0.9% de nulls à gérer (peut-être mapper depuis code postal)

```

```markdown
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

```


Nettoyage du script temporaire et mise à jour de l'analyse du projet :



Ajout d'une section de référence dans l'analyse du projet :


```markdown
# Analyse et Proposition d'Amélioration - Projet Sirene DataViz

## 📋 Compréhension du Projet

### Objectif Principal
Créer une plateforme de visualisation interactive de données Sirene (répertoire des entreprises françaises) avec des cartes de France interactives permettant d'analyser différents aspects des entreprises par région.

### Dataset
- **Source** : `Sirene_merged_with_region.csv` (~7.8 GB)
- **Contenu** : Données fusionnées des établissements et unités légales avec mapping régional
- **Volume** : Plusieurs millions d'enregistrements

### Use Cases Identifiés
1. **Évolution des créations d'entreprises** : Par année et secteur d'activité
2. **Répartition par sexe des dirigeants** : Selon les secteurs d'activité
3. **Répartition des effectifs** : Par secteurs et territoires
4. **Dominance sectorielle** : Par région
5. **Types juridiques et catégories** : Par secteur et région

### Règles Métier Identifiées
- **Filtrage obligatoire** : Exclure les entreprises avec `Etat_Administratif_Entreprise = 'C'` (radiées)
- **Colonnes à supprimer** : `Denomination_Usuelle_Etablissement`, `Enseigne_Etablissement`, `Status_Diffusion`
- **Gestion des nulls** : 
  - `Date_Creation_Entreprise` : Null acceptable (ne pas traiter dans use case 1 si null)
  - `Sexe_Dirigeant` : Null acceptable (ne pas traiter dans use case 2 si null)
  - `Effectifs_Entreprises` : Null = "NN" (Non renseigné)
- **Colonnes toujours vides** : `Employeur_Entreprise`, `Enseigne_Etablissement`, `Denomination_Usuelle_Etablissement`
- **Nom entreprise** : Soit `Denomination_Entreprise` soit `Nom_Entreprise` (mutuellement exclusif)

---

## 🎯 Axes d'Amélioration

### 1. Architecture & Infrastructure

#### Problèmes identifiés
- Pas de séparation claire entre ingestion, traitement et visualisation
- HDFS mentionné mais pas de stratégie de stockage intermédiaire
- Pas de mention de cache pour les visualisations

#### Améliorations proposées
- **Architecture en couches** : 
  - Layer 1 : Ingestion & Nettoyage (ETL)
  - Layer 2 : Stockage (HDFS + Parquet pour performance)
  - Layer 3 : Traitement & Agrégation (Spark/PySpark)
  - Layer 4 : API & Services (FastAPI/Flask)
  - Layer 5 : Frontend & Visualisation (Dash/Streamlit/React)
- **Cache stratégique** : Redis pour les agrégations fréquentes
- **Orchestration** : Prefect pour les pipelines ETL

### 2. Traitement des Données

#### Problèmes identifiés
- Traitement par batch mais pas de validation de qualité
- Pas de gestion des doublons explicite
- Pas de normalisation des codes APE/NAF

#### Améliorations proposées
- **Pipeline de validation** : 
  - Schéma de données (Pydantic/Great Expectations)
  - Contrôles de cohérence (dates, codes postaux, etc.)
  - Détection d'anomalies
- **Normalisation** :
  - Codes APE/NAF vers libellés (mapping INSEE)
  - Normalisation des dates
  - Standardisation des effectifs
- **Déduplication** : Stratégie claire sur SIREN/SIRET

### 3. Performance & Scalabilité

#### Problèmes identifiés
- Fichier CSV volumineux (7.8 GB) - format non optimisé
- Pas de partitionnement mentionné
- Traitement séquentiel potentiellement lent

#### Améliorations proposées
- **Format de stockage** : 
  - Parquet (compression, colonnes, partitionnement)
  - Partitionnement par région/année pour requêtes rapides
- **Traitement distribué** : PySpark pour les agrégations
- **Indexation** : Sur colonnes fréquemment filtrées (région, secteur, année)

### 4. Visualisation & UX

#### Problèmes identifiés
- Pas de spécification de l'interactivité
- Pas de mention de filtres temporels
- Pas de gestion de la performance côté frontend

#### Améliorations proposées
- **Framework de visualisation** :
  - Dash/Plotly pour cartes interactives natives
  - Ou React + D3.js/Leaflet pour plus de contrôle
- **Fonctionnalités** :
  - Filtres multiples (année, secteur, région, type juridique)
  - Zoom/pan sur cartes
  - Tooltips avec détails
  - Export de données
  - Comparaisons temporelles (slider année)
- **Performance** :
  - Lazy loading des données
  - Agrégations pré-calculées
  - Pagination pour grandes listes

### 5. Qualité & Monitoring

#### Problèmes identifiés
- Pas de logging structuré
- Pas de métriques de qualité de données
- Pas de monitoring des pipelines

#### Améliorations proposées
- **Logging** : Structuré (JSON) avec niveaux appropriés
- **Métriques** : 
  - Taux de complétude par colonne
  - Nombre d'entreprises filtrées
  - Temps de traitement
- **Alertes** : Sur échecs de pipeline ou anomalies détectées

---

## 🔄 Restructuration des Idées

### Phase 1 : Ingestion & Nettoyage (ETL)
```
1. Lecture du CSV source
2. Application des règles de filtrage :
   - Suppression colonnes inutiles
   - Exclusion entreprises radiées (Etat = 'C')
   - Gestion des nulls selon règles métier
3. Validation & normalisation :
   - Validation schéma
   - Normalisation codes APE/NAF
   - Standardisation dates
4. Export format optimisé (Parquet) vers HDFS
```

### Phase 2 : Préparation & Agrégation
```
1. Chargement depuis HDFS
2. Création de vues agrégées par use case :
   - Use Case 1 : Créations par année/secteur/région
   - Use Case 2 : Dirigeants par sexe/secteur/région
   - Use Case 3 : Effectifs par secteur/région
   - Use Case 4 : Dominance sectorielle par région
   - Use Case 5 : Types juridiques par secteur/région
3. Stockage des agrégations (Parquet + Redis cache)
```

### Phase 3 : API & Services
```
1. API REST pour servir les données agrégées
2. Endpoints par use case
3. Filtres dynamiques (année, secteur, région)
4. Cache Redis pour performance
```

### Phase 4 : Frontend & Visualisation
```
1. Interface web interactive
2. Cartes de France avec visualisations
3. Filtres et contrôles utilisateur
4. Export et partage
```

---

## 🛠️ Technologies Proposées

### Stack Technique Recommandée

#### **Ingestion & ETL**
- **Python 3.11+** avec **UV** (gestionnaire de dépendances rapide) OK
- **Pandas** : Traitement initial et validation OK
- **PySpark** : Pour gros volumes et traitement distribué OK
- **Great Expectations** : Validation de qualité de données OK
- **Pydantic** : Validation de schémas OK

#### **Stockage**
- **HDFS** : Stockage distribué (comme demandé) OK
- **Parquet** : Format de stockage optimisé (compression, colonnes) OK
- **Redis** : Cache pour agrégations fréquentes OK
- **PostgreSQL/ClickHouse** (optionnel) : Pour requêtes analytiques rapides OK

#### **Orchestration & Pipelines**
- **Prefect** : Orchestration moderne et simple (alternative à Airflow) OK
- **Makefile** : Commandes de build et déploiement (comme demandé)

#### **API & Backend**
- **FastAPI** : API moderne, rapide, avec documentation auto OK
- **Pydantic** : Validation des requêtes/réponses OK
- **Redis** : Cache des résultats d'agrégation OK

#### **Visualisation & Frontend**
- **Option B (Flexible)** : OK
  - **React** : Framework frontend moderne OK
  - **Leaflet** ou **Mapbox GL JS** : Cartes interactives OK
  - **D3.js** : Visualisations avancées OK
  - **Recharts/Chart.js** : Graphiques OK
  - Avantages : Plus de contrôle, meilleure UX, scalable

#### **Infrastructure & Déploiement**
- **Docker** : Containerisation (comme demandé) OK
- **Docker Compose** : Orchestration locale OK
- **Hadoop/HDFS** : Stockage distribué OK
- **Spark** : Traitement distribué (si nécessaire) OK

#### **Outils de Développement**
- **UV** : Gestionnaire de dépendances Python (comme demandé) OK
- **Makefile** : Automatisation des tâches (comme demandé) OK
- **Pre-commit hooks** : Validation de code OK
- **Black/ruff** : Formatage et linting OK

### Architecture Technique Détaillée

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Visualisation)                  │
│  Option A: Dash/Plotly  |  Option B: React + Leaflet        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────┐
│                    API LAYER (FastAPI)                       │
│  - Endpoints par use case                                    │
│  - Validation Pydantic                                       │
│  - Cache Redis                                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              PROCESSING LAYER (PySpark/Pandas)               │
│  - Agrégations par use case                                  │
│  - Calculs de métriques                                      │
│  - Filtres dynamiques                                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼────────┐              ┌───────────▼──────────┐
│  HDFS/Parquet  │              │      Redis Cache     │
│  (Données)     │              │  (Agrégations)       │
└────────────────┘              └──────────────────────┘
        │
┌───────▼──────────────────────────────────────────────┐
│         ETL PIPELINE (Prefect)                        │
│  - Ingestion CSV                                       │
│  - Nettoyage & validation                             │
│  - Export Parquet                                      │
└───────────────────────────────────────────────────────┘
```

---

## 📊 Recommandations Spécifiques

### Pour les Use Cases

1. **Use Case 1 (Évolution créations)** :
   - Agrégation : `COUNT(*) GROUP BY année, secteur, région`
   - Visualisation : Carte choroplèthe + graphique temporel
   - Filtres : Année (slider), Secteur (multi-select)

2. **Use Case 2 (Sexe dirigeants)** :
   - Agrégation : `COUNT(*) GROUP BY sexe, secteur, région`
   - Visualisation : Carte avec proportions (pie charts par région)
   - Filtres : Secteur, Région

3. **Use Case 3 (Effectifs)** :
   - Agrégation : `SUM(effectifs) GROUP BY secteur, région`
   - Visualisation : Carte avec tailles de bulles proportionnelles
   - Filtres : Secteur, Tranche d'effectifs

4. **Use Case 4 (Dominance sectorielle)** :
   - Agrégation : Secteur dominant par région (TOP 1)
   - Visualisation : Carte avec couleurs par secteur dominant
   - Filtres : Année

5. **Use Case 5 (Types juridiques)** :
   - Agrégation : `COUNT(*) GROUP BY type_juridique, secteur, région`
   - Visualisation : Carte avec heatmap + tableau croisé
   - Filtres : Secteur, Type juridique

### Optimisations de Performance

- **Pré-agrégation** : Calculer les agrégations une fois, stocker en Parquet
- **Partitionnement** : Par année et région pour requêtes rapides
- **Cache** : Redis pour les requêtes fréquentes (ex: données 2024)
- **Lazy loading** : Charger les données à la demande dans le frontend
- **Compression** : Parquet avec compression Snappy ou Zstd

---

## 🚀 Prochaines Étapes

1. ✅ **Validation de cette analyse** avec vous
2. 🔄 **Création de l'architecture Mermaid** détaillée
3. 📁 **Structure du projet** avec dossiers et fichiers de base
4. 🐳 **Dockerfiles et docker-compose.yml**
5. 📝 **Makefile** avec commandes principales
6. ⚙️ **Configuration UV** (pyproject.toml)
7. 🔧 **Scripts ETL** de base avec règles métier
8. 🗺️ **Prototype de visualisation** (carte de base)

---

## 📚 Documents de Référence

- **`DATASET_ANALYSIS.md`** : Analyse détaillée du fichier CSV (structure, colonnes, observations)
- **`PROJECT_STRUCTURE.md`** : Architecture complète du projet avec structure de dossiers et conventions

## 📊 Informations Clés du Dataset

- **Volume** : 42,151,993 lignes (~7.8 GB)
- **Colonnes** : 28 colonnes
- **Format** : CSV avec encodage UTF-8
- **Localisation** : `dataset/Sirene_merged_with_region.csv`

Voir `DATASET_ANALYSIS.md` pour l'analyse complète.

## 🏗️ Structure du Projet

Le projet sera organisé selon les **conventions Python modernes** avec :
- Séparation claire des responsabilités (ETL, Processing, API, Frontend)
- Structure modulaire et maintenable
- Configuration centralisée
- Tests organisés

Voir `PROJECT_STRUCTURE.md` pour la structure détaillée.

---

## ❓ Questions à Clarifier

1. **Volume de données** : Travailler sur le fichier complet (7.8 GB) ou un échantillon pour le développement ?
2. **Infrastructure** : HDFS disponible localement ou besoin de setup ?
3. **Visualisation** : Préférence pour Dash (rapide) ou React (plus flexible) ?
4. **Performance** : Temps de réponse acceptable pour les visualisations ?
5. **Déploiement** : Production prévue ou uniquement développement local ?


```


## Analyse du CSV

- **Header** : 28 colonnes identifiées
- **Nombre de lignes** : **42,151,993** (plus de 42 millions)
- **1000 premières lignes** : analysées et documentées

## Documents créés

1. **`DATASET_ANALYSIS.md`** :
   - Structure des 28 colonnes
   - Observations sur l'échantillon (taux de complétude, types de données)
   - Règles métier confirmées
   - Actions de nettoyage à effectuer
   - Impact sur chaque use case

2. **`PROJECT_STRUCTURE.md`** :
   - Architecture du projet avec séparation des responsabilités
   - Structure de dossiers selon les conventions Python
   - Organisation modulaire (ETL, Processing, API, Frontend)
   - Conventions de nommage
   - Configuration (pyproject.toml, Makefile, Docker)

## Points importants identifiés

- **Volume** : 42+ millions de lignes → traitement distribué nécessaire (PySpark)
- **Colonnes à supprimer** : `Enseigne_Etablissement`, `Denomination_Usuelle_Etablissement`, `Statut_Diffusion`, `Employeur_Entreprise`
- **Filtre critique** : Exclure `Etat_Administratif_Entreprise = 'C'` (radiées)
- **Gestion des nulls** : Stratégie définie par use case

Le projet sera organisé avec une séparation claire des responsabilités et le respect des conventions Python modernes.

Souhaitez-vous que je commence à créer la structure de dossiers et les fichiers de base, ou préférez-vous d'abord créer l'architecture Mermaid ?

---

**User**

Tu peux commencer a coder 

---

**Cursor**


Création de la structure du projet et des fichiers de base selon les conventions définies.



Création des dossiers avec PowerShell :



Création des fichiers de configuration et des fichiers de base :


```toml
[project]
name = "sirene-dataviz"
version = "0.1.0"
description = "Visualisation interactive des données Sirene"
requires-python = ">=3.11"
readme = "README.md"
license = {text = "MIT"}

dependencies = [
    "pandas>=2.0.0",
    "pyspark>=3.5.0",
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "redis>=5.0.0",
    "great-expectations>=0.18.0",
    "pyarrow>=14.0.0",
    "python-dotenv>=1.0.0",
    "tqdm>=4.66.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

```

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv/
venv/
ENV/
env/

# UV
.uv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Data
data/
*.csv
*.parquet
*.json
!tests/fixtures/*.json

# Logs
logs/
*.log

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Docker
.dockerignore

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
temp_batches/
checkpoint.json

# HDFS
hdfs_data/

```

```makefile
.PHONY: help install setup run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Configuration terminée"

run-etl: ## Lance le pipeline ETL
	python scripts/run_etl.py

run-api: ## Lance l'API FastAPI
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: ## Lance les tests
	pytest tests/ -v --cov=src --cov-report=html

test-unit: ## Lance uniquement les tests unitaires
	pytest tests/unit/ -v

test-integration: ## Lance uniquement les tests d'intégration
	pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	ruff check src/ tests/
	black --check src/ tests/

format: ## Formate le code avec black et ruff
	black src/ tests/
	ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f

```

```markdown
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

# Installer les dépendances
make install

# Copier le fichier d'environnement
cp .env.example .env

# Lancer les services Docker
make docker-up

# Lancer l'ETL (première fois)
make run-etl

# Lancer l'API
make run-api

# Dans un autre terminal, lancer le frontend
make run-frontend
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

```


Création des fichiers de base pour chaque module :


```python
"""Sirene DataViz - Plateforme de visualisation interactive des données Sirene."""

__version__ = "0.1.0"

```

```python
"""Configuration du projet."""

from src.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]

```

```python
"""Configuration de l'application avec Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # HDFS Configuration
    hdfs_host: str = "localhost"
    hdfs_port: int = 9000
    hdfs_path: str = "/sirene_data"

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # Spark Configuration
    spark_master: str = "local[*]"
    spark_app_name: str = "sirene-dataviz"

    # Data Paths
    data_raw_path: str = "./data/raw"
    data_processed_path: str = "./data/processed"
    data_aggregated_path: str = "./data/aggregated"
    dataset_csv_path: str = "./dataset/Sirene_merged_with_region.csv"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def redis_url(self) -> str:
        """Retourne l'URL Redis."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def hdfs_url(self) -> str:
        """Retourne l'URL HDFS."""
        return f"hdfs://{self.hdfs_host}:{self.hdfs_port}{self.hdfs_path}"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings (singleton)."""
    return Settings()

```

```python
"""Configuration du logging."""

import json
import logging
import sys
from pathlib import Path
from typing import Any

from src.config.settings import get_settings


def setup_logging() -> None:
    """Configure le logging de l'application."""
    settings = get_settings()

    # Créer les dossiers de logs
    log_dirs = ["logs/etl", "logs/api", "logs/processing"]
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Configuration du format
    if settings.log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.log_level))

    # Configuration root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    root_logger.addHandler(console_handler)


class JsonFormatter(logging.Formatter):
    """Formatter JSON pour les logs structurés."""

    def format(self, record: logging.LogRecord) -> str:
        """Formate le log en JSON."""
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Ajouter les champs supplémentaires
        if hasattr(record, "module"):
            log_data["module"] = record.module
        if hasattr(record, "function"):
            log_data["function"] = record.function

        # Ajouter l'exception si présente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)

```

```python
"""Utilitaires partagés."""

from src.utils.ape_utils import get_secteur_from_ape, normalize_ape_code
from src.utils.date_utils import parse_date, extract_year
from src.utils.region_utils import normalize_region_name

__all__ = [
    "get_secteur_from_ape",
    "normalize_ape_code",
    "parse_date",
    "extract_year",
    "normalize_region_name",
]

```

```python
"""Utilitaires pour la manipulation des dates."""

from datetime import datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse une date depuis un string.

    Formats supportés:
    - ISO format: "2024-03-22T15:40:57"
    - Date simple: "2024-03-22"
    - Format Sirene: "2000-09-26"

    Args:
        date_str: String de date à parser

    Returns:
        Objet datetime ou None si parsing échoue
    """
    if not date_str or date_str == "NaN" or date_str == "null":
        return None

    try:
        # Essayer format ISO avec timestamp
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Essayer format date simple
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


def extract_year(date_str: Optional[str]) -> Optional[int]:
    """
    Extrait l'année depuis une date string.

    Args:
        date_str: String de date

    Returns:
        Année (int) ou None
    """
    date_obj = parse_date(date_str)
    if date_obj:
        return date_obj.year
    return None

```

```python
"""Utilitaires pour les codes APE/NAF."""

from typing import Optional


def normalize_ape_code(ape_code: Optional[str]) -> Optional[str]:
    """
    Normalise un code APE.

    Args:
        ape_code: Code APE (ex: "32.12Z", "3212Z")

    Returns:
        Code APE normalisé (ex: "32.12Z") ou None
    """
    if not ape_code or ape_code == "NaN" or ape_code == "null":
        return None

    # Nettoyer le code
    code = str(ape_code).strip().upper()

    # Si le code contient un point, le garder tel quel
    if "." in code:
        return code

    # Sinon, formater avec point (ex: "3212Z" -> "32.12Z")
    if len(code) >= 4:
        return f"{code[:2]}.{code[2:]}"

    return code


def get_secteur_from_ape(ape_code: Optional[str]) -> Optional[str]:
    """
    Extrait le secteur d'activité depuis un code APE.

    Le secteur correspond aux 2 premiers chiffres du code APE.

    Args:
        ape_code: Code APE (ex: "32.12Z")

    Returns:
        Code secteur (ex: "32") ou None
    """
    normalized = normalize_ape_code(ape_code)
    if not normalized:
        return None

    # Extraire les 2 premiers chiffres
    secteur = normalized.split(".")[0]
    if len(secteur) >= 2 and secteur[:2].isdigit():
        return secteur[:2]

    return None


# Mapping des secteurs APE vers libellés (exemple - à compléter)
SECTEUR_LIBELLES: dict[str, str] = {
    "01": "Culture et production animale, chasse et services annexes",
    "02": "Sylviculture et exploitation forestière",
    "03": "Pêche et aquaculture",
    "05": "Extraction de houille et de lignite",
    "06": "Extraction d'hydrocarbures",
    "07": "Extraction de minerais métalliques",
    "08": "Autres industries extractives",
    "09": "Services de soutien aux industries extractives",
    "10": "Industrie alimentaire",
    "11": "Fabrication de boissons",
    "12": "Fabrication de produits à base de tabac",
    "13": "Fabrication de textiles",
    "14": "Industrie de l'habillement",
    "15": "Industrie du cuir et de la chaussure",
    "16": "Travail du bois et fabrication d'articles en bois",
    "17": "Industrie du papier et du carton",
    "18": "Imprimerie et reproduction d'enregistrements",
    "19": "Cokéfaction et raffinage",
    "20": "Industrie chimique",
    "21": "Industrie pharmaceutique",
    "22": "Fabrication de produits en caoutchouc et en plastique",
    "23": "Fabrication d'autres produits minéraux non métalliques",
    "24": "Métallurgie",
    "25": "Fabrication de produits métalliques",
    "26": "Fabrication de produits informatiques, électroniques et optiques",
    "27": "Fabrication d'équipements électriques",
    "28": "Fabrication de machines et équipements n.c.a.",
    "29": "Industrie automobile",
    "30": "Fabrication d'autres matériels de transport",
    "31": "Fabrication de meubles",
    "32": "Autres industries manufacturières",
    "33": "Réparation et installation de machines et d'équipements",
    "35": "Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné",
    "36": "Captage, traitement et distribution d'eau",
    "37": "Collecte et traitement des eaux usées",
    "38": "Collecte, traitement et élimination des déchets",
    "39": "Dépollution et autres services de gestion des déchets",
    "41": "Construction de bâtiments",
    "42": "Génie civil",
    "43": "Travaux de construction spécialisés",
    "45": "Commerce et réparation d'automobiles et de motocycles",
    "46": "Commerce de gros",
    "47": "Commerce de détail",
    "49": "Transports terrestres et transport par conduites",
    "50": "Transports par eau",
    "51": "Transports aériens",
    "52": "Entreposage et services auxiliaires des transports",
    "53": "Activités de poste et courrier",
    "55": "Hébergement",
    "56": "Restauration",
    "58": "Édition",
    "59": "Production de films cinématographiques, de vidéo et de programmes de télévision",
    "60": "Programmation et diffusion",
    "61": "Télécommunications",
    "62": "Programmation, conseil et autres activités informatiques",
    "63": "Services d'information",
    "64": "Activités des services financiers",
    "65": "Assurance",
    "66": "Activités auxiliaires de services financiers et d'assurance",
    "68": "Activités immobilières",
    "69": "Activités juridiques et comptables",
    "70": "Activités des sièges sociaux",
    "71": "Activités d'architecture et d'ingénierie",
    "72": "Recherche-développement scientifique",
    "73": "Publicité et études de marché",
    "74": "Autres activités spécialisées, scientifiques et techniques",
    "75": "Activités vétérinaires",
    "77": "Activités de location et location-bail",
    "78": "Activités liées à l'emploi",
    "79": "Activités des agences de voyage",
    "80": "Enquêtes et sécurité",
    "81": "Services relatifs aux bâtiments et aménagement paysager",
    "82": "Activités administratives et de soutien de bureau",
    "84": "Administration publique",
    "85": "Enseignement",
    "86": "Activités pour la santé humaine",
    "87": "Hébergement médico-social et social",
    "88": "Action sociale sans hébergement",
    "90": "Activités créatives, artistiques et de spectacle",
    "91": "Bibliothèques, archives, musées et autres activités culturelles",
    "92": "Organisation de jeux de hasard et d'argent",
    "93": "Activités sportives, récréatives et de loisirs",
    "94": "Activités des organisations associatives",
    "95": "Réparation d'ordinateurs et de biens personnels et domestiques",
    "96": "Autres services personnels",
    "97": "Activités des ménages en tant qu'employeurs",
    "98": "Activités indifférenciées des ménages",
    "99": "Activités des organisations et organismes extraterritoriaux",
}


def get_secteur_libelle(ape_code: Optional[str]) -> Optional[str]:
    """
    Retourne le libellé du secteur depuis un code APE.

    Args:
        ape_code: Code APE

    Returns:
        Libellé du secteur ou None
    """
    secteur = get_secteur_from_ape(ape_code)
    if secteur:
        return SECTEUR_LIBELLES.get(secteur)
    return None

```

```python
"""Utilitaires pour les régions."""

from typing import Optional


def normalize_region_name(region: Optional[str]) -> Optional[str]:
    """
    Normalise le nom d'une région.

    Args:
        region: Nom de la région

    Returns:
        Nom de région normalisé ou None
    """
    if not region or region == "NaN" or region == "null":
        return None

    # Nettoyer et normaliser
    normalized = str(region).strip()

    # Gérer les cas particuliers (accents, etc.)
    # Exemple: "Provence-Alpes-Côte d'Azur" -> "Provence-Alpes-Cote d'Azur"
    # (à adapter selon les besoins)

    return normalized if normalized else None


# Liste des régions françaises (métropole + DOM)
REGIONS_FRANCE = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche-Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand Est",
    "Hauts-de-France",
    "Île-de-France",
    "Normandie",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Pays de la Loire",
    "Provence-Alpes-Côte d'Azur",
    "Guadeloupe",
    "Guyane",
    "La Réunion",
    "Martinique",
    "Mayotte",
]


def is_valid_region(region: Optional[str]) -> bool:
    """
    Vérifie si une région est valide.

    Args:
        region: Nom de la région

    Returns:
        True si la région est valide, False sinon
    """
    normalized = normalize_region_name(region)
    if not normalized:
        return False

    return normalized in REGIONS_FRANCE

```


Création des modules ETL de base :


```python
"""Module ETL (Extract, Transform, Load)."""

from src.etl.extract import extract_csv_chunks
from src.etl.load import load_to_parquet
from src.etl.transform import transform_dataframe

__all__ = ["extract_csv_chunks", "transform_dataframe", "load_to_parquet"]

```

```python
"""Module d'extraction des données CSV."""

import logging
from pathlib import Path
from typing import Iterator

import pandas as pd
from tqdm import tqdm

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def extract_csv_chunks(
    file_path: str | None = None,
    chunk_size: int = 100000,
) -> Iterator[pd.DataFrame]:
    """
    Extrait les données CSV par chunks pour gérer les gros volumes.

    Args:
        file_path: Chemin vers le fichier CSV. Si None, utilise le chemin des settings.
        chunk_size: Taille des chunks (nombre de lignes)

    Yields:
        DataFrames pandas par chunks
    """
    settings = get_settings()
    csv_path = file_path or settings.dataset_csv_path

    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Fichier CSV introuvable: {csv_path}")

    logger.info(f"Extraction du fichier CSV: {csv_path}")
    logger.info(f"Taille des chunks: {chunk_size:,} lignes")

    try:
        # Lecture par chunks avec types optimisés
        reader = pd.read_csv(
            csv_path,
            sep=",",
            encoding="utf-8",
            chunksize=chunk_size,
            low_memory=False,
            dtype={
                "SIREN": "str",
                "SIRET": "str",
                "Categorie_Juridique": "str",
            },
            on_bad_lines="skip",
            engine="c",
        )

        total_chunks = 0
        for chunk in tqdm(reader, desc="Extraction CSV"):
            total_chunks += 1
            logger.debug(f"Chunk {total_chunks} extrait: {len(chunk):,} lignes")
            yield chunk

        logger.info(f"Extraction terminée: {total_chunks} chunks traités")

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}", exc_info=True)
        raise

```

```python
"""Module de transformation et nettoyage des données."""

import logging
from typing import Any

import pandas as pd

from src.utils.ape_utils import normalize_ape_code
from src.utils.date_utils import extract_year, parse_date
from src.utils.region_utils import normalize_region_name

logger = logging.getLogger(__name__)

# Colonnes à supprimer selon le roadmap
COLUMNS_TO_DROP = [
    "Enseigne_Etablissement",
    "Denomination_Usuelle_Etablissement",
    "Statut_Diffusion",
    "Employeur_Entreprise",
    "Prenom_Dirigeant",
    "Nom_Dirigeant",
]


def transform_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme et nettoie un DataFrame selon les règles métier.

    Règles appliquées:
    1. Suppression des colonnes inutiles
    2. Exclusion des entreprises radiées (Etat_Administratif_Entreprise = 'C')
    3. Gestion des nulls selon règles métier
    4. Normalisation des données

    Args:
        df: DataFrame à transformer

    Returns:
        DataFrame transformé et nettoyé
    """
    logger.info(f"Transformation de {len(df):,} lignes")

    # Copie pour éviter les modifications in-place
    df_clean = df.copy()

    # 1. Supprimer les colonnes inutiles
    columns_to_drop = [col for col in COLUMNS_TO_DROP if col in df_clean.columns]
    if columns_to_drop:
        df_clean = df_clean.drop(columns=columns_to_drop)
        logger.debug(f"Colonnes supprimées: {columns_to_drop}")

    # 2. Filtrer les entreprises radiées (CRITIQUE)
    initial_count = len(df_clean)
    df_clean = df_clean[df_clean["Etat_Administratif_Entreprise"] != "C"]
    filtered_count = len(df_clean)
    excluded_count = initial_count - filtered_count

    if excluded_count > 0:
        logger.info(
            f"Entreprises radiées exclues: {excluded_count:,} "
            f"({excluded_count/initial_count*100:.2f}%)"
        )

    # 3. Gestion des nulls selon règles métier
    # Effectifs_Entreprise: null -> "NN"
    if "Effectifs_Entreprise" in df_clean.columns:
        df_clean["Effectifs_Entreprise"] = df_clean["Effectifs_Entreprise"].fillna("NN")

    # Effectifs_Etablissement: null -> "NN"
    if "Effectifs_Etablissement" in df_clean.columns:
        df_clean["Effectifs_Etablissement"] = df_clean["Effectifs_Etablissement"].fillna(
            "NN"
        )

    # 4. Normalisation des données
    # Normaliser les codes APE
    if "Code_APE_Entreprise" in df_clean.columns:
        df_clean["Code_APE_Entreprise"] = df_clean["Code_APE_Entreprise"].apply(
            normalize_ape_code
        )

    if "Code_APE_Etablissement" in df_clean.columns:
        df_clean["Code_APE_Etablissement"] = df_clean["Code_APE_Etablissement"].apply(
            normalize_ape_code
        )

    # Normaliser les régions
    if "Region" in df_clean.columns:
        df_clean["Region"] = df_clean["Region"].apply(normalize_region_name)

    # Extraire l'année de création pour faciliter les agrégations
    if "Date_Creation_Entreprise" in df_clean.columns:
        df_clean["Annee_Creation"] = df_clean["Date_Creation_Entreprise"].apply(
            extract_year
        )

    # 5. Créer une colonne nom entreprise unifiée
    # Soit Denomination_Entreprise soit Nom_Entreprise (mutuellement exclusif)
    if "Denomination_Entreprise" in df_clean.columns and "Nom_Entreprise" in df_clean.columns:
        df_clean["Nom_Entreprise_Unifie"] = df_clean["Denomination_Entreprise"].fillna(
            df_clean["Nom_Entreprise"]
        )

    logger.info(f"Transformation terminée: {len(df_clean):,} lignes valides")

    return df_clean


def validate_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Valide la qualité d'un DataFrame et retourne des métriques.

    Args:
        df: DataFrame à valider

    Returns:
        Dictionnaire avec les métriques de qualité
    """
    metrics = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "completeness_rate": (1 - df.isnull().sum() / len(df)).to_dict(),
    }

    # Vérifier qu'il n'y a pas d'entreprises radiées
    if "Etat_Administratif_Entreprise" in df.columns:
        radiées = (df["Etat_Administratif_Entreprise"] == "C").sum()
        metrics["entreprises_radiees"] = int(radiées)
        if radiées > 0:
            logger.warning(f"⚠ {radiées} entreprises radiées détectées dans le DataFrame")

    return metrics

```

```python
"""Module de chargement des données vers HDFS/Parquet."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def load_to_parquet(
    df: pd.DataFrame,
    output_path: str,
    partition_cols: Optional[list[str]] = None,
    compression: str = "snappy",
) -> None:
    """
    Charge un DataFrame vers un fichier Parquet.

    Args:
        df: DataFrame à sauvegarder
        output_path: Chemin de sortie (fichier ou dossier)
        partition_cols: Colonnes pour le partitionnement (optionnel)
        compression: Type de compression (snappy, gzip, zstd)
    """
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Chargement vers Parquet: {output_path}")
    logger.info(f"Nombre de lignes: {len(df):,}")

    try:
        # Convertir en table PyArrow
        table = pa.Table.from_pandas(df)

        # Écrire en Parquet
        if partition_cols:
            # Partitionnement
            pq.write_to_dataset(
                table,
                root_path=str(output),
                partition_cols=partition_cols,
                compression=compression,
                use_dictionary=True,
                write_statistics=True,
            )
            logger.info(f"Données partitionnées par: {partition_cols}")
        else:
            # Fichier unique
            pq.write_table(
                table,
                output_path,
                compression=compression,
                use_dictionary=True,
                write_statistics=True,
            )

        logger.info(f"✓ Données chargées avec succès: {output_path}")

    except Exception as e:
        logger.error(f"Erreur lors du chargement Parquet: {e}", exc_info=True)
        raise


def load_to_hdfs(
    df: pd.DataFrame,
    hdfs_path: str,
    partition_cols: Optional[list[str]] = None,
) -> None:
    """
    Charge un DataFrame vers HDFS en format Parquet.

    Note: Nécessite une connexion HDFS configurée.

    Args:
        df: DataFrame à sauvegarder
        hdfs_path: Chemin HDFS (ex: /sirene_data/processed)
        partition_cols: Colonnes pour le partitionnement
    """
    # TODO: Implémenter la connexion HDFS
    # Pour l'instant, on sauvegarde localement
    settings = get_settings()
    local_path = settings.data_processed_path

    logger.warning(
        "Chargement HDFS non implémenté, sauvegarde locale à la place: "
        f"{local_path}"
    )

    load_to_parquet(df, local_path, partition_cols)

```

```python
"""Script principal pour lancer le pipeline ETL."""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.logging import setup_logging
from src.config.settings import get_settings
from src.etl.extract import extract_csv_chunks
from src.etl.load import load_to_parquet
from src.etl.transform import transform_dataframe, validate_dataframe

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """Fonction principale du pipeline ETL."""
    settings = get_settings()

    logger.info("=" * 80)
    logger.info("DÉMARRAGE DU PIPELINE ETL")
    logger.info("=" * 80)

    # Paramètres
    chunk_size = 100000
    output_dir = Path(settings.data_processed_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Compteurs
    total_processed = 0
    total_valid = 0
    chunk_number = 0

    try:
        # Extraction et transformation par chunks
        for chunk in extract_csv_chunks(chunk_size=chunk_size):
            chunk_number += 1
            total_processed += len(chunk)

            logger.info(f"\n--- Traitement du chunk {chunk_number} ---")
            logger.info(f"Lignes dans le chunk: {len(chunk):,}")

            # Transformation
            chunk_transformed = transform_dataframe(chunk)

            # Validation
            metrics = validate_dataframe(chunk_transformed)
            logger.info(f"Métriques de qualité: {metrics}")

            total_valid += len(chunk_transformed)

            # Chargement vers Parquet
            output_file = output_dir / f"chunk_{chunk_number:04d}.parquet"
            load_to_parquet(chunk_transformed, str(output_file))

        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE ETL TERMINÉ")
        logger.info("=" * 80)
        logger.info(f"Total lignes traitées: {total_processed:,}")
        logger.info(f"Total lignes valides: {total_valid:,}")
        logger.info(f"Taux de rétention: {total_valid/total_processed*100:.2f}%")
        logger.info(f"Fichiers Parquet créés: {chunk_number}")
        logger.info(f"Répertoire de sortie: {output_dir}")

    except Exception as e:
        logger.error(f"Erreur critique dans le pipeline ETL: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

```


Création des Dockerfiles et du docker-compose.yml :


```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier les fichiers de configuration
COPY pyproject.toml ./
COPY uv.lock* ./

# Installer les dépendances
RUN uv sync --frozen

# Copier le code source
COPY src/ ./src/
COPY scripts/ ./scripts/

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Installer UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copier les fichiers de configuration
COPY pyproject.toml ./
COPY uv.lock* ./

# Installer les dépendances
RUN uv sync --frozen

# Copier le code source
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY dataset/ ./dataset/

# Créer les dossiers de données
RUN mkdir -p data/raw data/processed data/aggregated logs/etl

# Commande par défaut
CMD ["uv", "run", "python", "scripts/run_etl.py"]

```

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copier les fichiers de configuration
COPY src/frontend/package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code source
COPY src/frontend/ ./

# Build
RUN npm run build

# Stage de production
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=builder /app/build /usr/share/nginx/html

# Copier la configuration nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

```

```properties
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```

```dockercompose
version: '3.8'

services:
  # API FastAPI
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: sirene-api
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - HDFS_HOST=hdfs
      - ENVIRONMENT=development
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
    networks:
      - sirene-network

  # Frontend React
  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    container_name: sirene-frontend
    ports:
      - "3000:80"
    depends_on:
      - api
    networks:
      - sirene-network

  # Redis (Cache)
  redis:
    image: redis:7-alpine
    container_name: sirene-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - sirene-network

  # HDFS NameNode
  hdfs-namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: sirene-hdfs-namenode
    environment:
      - CLUSTER_NAME=sirene
    ports:
      - "9870:9870"  # Web UI
      - "9000:9000"  # HDFS
    volumes:
      - hdfs-namenode-data:/hadoop/dfs/name
    networks:
      - sirene-network

  # HDFS DataNode
  hdfs-datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: sirene-hdfs-datanode
    environment:
      - SERVICE_PRECONDITION=sirene-hdfs-namenode:9870
    ports:
      - "9864:9864"  # Web UI
    volumes:
      - hdfs-datanode-data:/hadoop/dfs/data
    depends_on:
      - hdfs-namenode
    networks:
      - sirene-network

  # Spark Master
  spark-master:
    image: bde2020/spark-master:3.0.0-hadoop3.2
    container_name: sirene-spark-master
    environment:
      - INIT_DAEMON_STEP=setup_spark
    ports:
      - "8080:8080"  # Web UI
      - "7077:7077"  # Spark
    volumes:
      - spark-master-data:/spark
    depends_on:
      - hdfs-namenode
    networks:
      - sirene-network

  # Spark Worker
  spark-worker:
    image: bde2020/spark-worker:3.0.0-hadoop3.2
    container_name: sirene-spark-worker
    environment:
      - SPARK_MASTER=spark://spark-master:7077
    ports:
      - "8081:8081"  # Web UI
    volumes:
      - spark-worker-data:/spark
    depends_on:
      - spark-master
    networks:
      - sirene-network

  # ETL Service (optionnel, pour lancer l'ETL via Docker)
  etl:
    build:
      context: .
      dockerfile: docker/Dockerfile.etl
    container_name: sirene-etl
    environment:
      - HDFS_HOST=hdfs-namenode
      - ENVIRONMENT=development
    volumes:
      - ./data:/app/data
      - ./dataset:/app/dataset
      - ./logs:/app/logs
    depends_on:
      - hdfs-namenode
      - redis
    networks:
      - sirene-network
    profiles:
      - etl  # Service optionnel, activé avec --profile etl

volumes:
  redis-data:
  hdfs-namenode-data:
  hdfs-datanode-data:
  spark-master-data:
  spark-worker-data:

networks:
  sirene-network:
    driver: bridge

```

```python
"""Module API FastAPI."""

```

```python
"""Application FastAPI principale."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.logging import setup_logging
from src.config.settings import get_settings

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="Sirene DataViz API",
    description="API pour la visualisation interactive des données Sirene",
    version="0.1.0",
)

# Configuration CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Événement au démarrage de l'application."""
    logger.info("Démarrage de l'API Sirene DataViz")
    logger.info(f"Environment: {settings.environment}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Événement à l'arrêt de l'application."""
    logger.info("Arrêt de l'API Sirene DataViz")


@app.get("/")
async def root() -> dict[str, str]:
    """Endpoint racine."""
    return {
        "message": "Sirene DataViz API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Endpoint de santé."""
    return {"status": "healthy"}

```


Ajout des fichiers `__init__.py` manquants et création d'un fichier de test basique :


```python
"""Module de traitement et agrégation des données."""

```

```python
"""Routers FastAPI par use case."""

```

```python
"""Modèles Pydantic pour l'API."""

```

```python
"""Services métier pour l'API."""

```

```python
"""Tests du projet."""

```

```python
"""Tests unitaires."""

```

```python
"""Tests d'intégration."""

```

```python
"""Tests unitaires pour les utilitaires."""

import pytest

from src.utils.ape_utils import get_secteur_from_ape, normalize_ape_code
from src.utils.date_utils import extract_year, parse_date
from src.utils.region_utils import normalize_region_name


class TestDateUtils:
    """Tests pour les utilitaires de dates."""

    def test_parse_date_iso(self):
        """Test parsing date ISO."""
        date_str = "2024-03-22T15:40:57"
        result = parse_date(date_str)
        assert result is not None
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 22

    def test_parse_date_simple(self):
        """Test parsing date simple."""
        date_str = "2024-03-22"
        result = parse_date(date_str)
        assert result is not None
        assert result.year == 2024

    def test_parse_date_none(self):
        """Test parsing date None."""
        assert parse_date(None) is None
        assert parse_date("NaN") is None
        assert parse_date("null") is None

    def test_extract_year(self):
        """Test extraction année."""
        assert extract_year("2024-03-22") == 2024
        assert extract_year("2024-03-22T15:40:57") == 2024
        assert extract_year(None) is None


class TestApeUtils:
    """Tests pour les utilitaires APE."""

    def test_normalize_ape_code(self):
        """Test normalisation code APE."""
        assert normalize_ape_code("32.12Z") == "32.12Z"
        assert normalize_ape_code("3212Z") == "32.12Z"
        assert normalize_ape_code(None) is None
        assert normalize_ape_code("NaN") is None

    def test_get_secteur_from_ape(self):
        """Test extraction secteur."""
        assert get_secteur_from_ape("32.12Z") == "32"
        assert get_secteur_from_ape("10.11A") == "10"
        assert get_secteur_from_ape(None) is None


class TestRegionUtils:
    """Tests pour les utilitaires régions."""

    def test_normalize_region_name(self):
        """Test normalisation nom région."""
        assert normalize_region_name("Île-de-France") == "Île-de-France"
        assert normalize_region_name("  Auvergne-Rhône-Alpes  ") == "Auvergne-Rhône-Alpes"
        assert normalize_region_name(None) is None
        assert normalize_region_name("NaN") is None

```

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

```


Vérification des erreurs de linting dans les fichiers créés :



Aucune erreur de linting. Création d'un fichier récapitulatif :


```markdown
# ✅ Setup du Projet - Terminé

## 📦 Ce qui a été créé

### Structure de dossiers
- ✅ Tous les dossiers selon `PROJECT_STRUCTURE.md`
- ✅ Organisation modulaire (ETL, Processing, API, Frontend)
- ✅ Dossiers de tests organisés

### Fichiers de configuration
- ✅ `pyproject.toml` - Configuration UV avec toutes les dépendances
- ✅ `Makefile` - Commandes automatisées (install, test, lint, format, docker)
- ✅ `.gitignore` - Fichiers à ignorer
- ✅ `.pre-commit-config.yaml` - Hooks de pré-commit
- ✅ `README.md` - Documentation principale
- ✅ `docker-compose.yml` - Orchestration Docker complète

### Modules ETL
- ✅ `src/etl/extract.py` - Extraction CSV par chunks
- ✅ `src/etl/transform.py` - Transformation et nettoyage selon règles métier
- ✅ `src/etl/load.py` - Chargement vers Parquet/HDFS
- ✅ `scripts/run_etl.py` - Script principal ETL

### Configuration
- ✅ `src/config/settings.py` - Settings Pydantic avec variables d'environnement
- ✅ `src/config/logging.py` - Configuration logging structuré (JSON)

### Utilitaires
- ✅ `src/utils/date_utils.py` - Parsing dates, extraction année
- ✅ `src/utils/ape_utils.py` - Normalisation codes APE, extraction secteurs
- ✅ `src/utils/region_utils.py` - Normalisation régions

### API
- ✅ `src/api/main.py` - Application FastAPI de base
- ✅ Structure pour routers, models, services

### Docker
- ✅ `docker/Dockerfile.api` - Container API
- ✅ `docker/Dockerfile.etl` - Container ETL
- ✅ `docker/Dockerfile.frontend` - Container Frontend
- ✅ `docker/nginx.conf` - Configuration Nginx
- ✅ `docker-compose.yml` - Services: API, Frontend, Redis, HDFS, Spark

### Tests
- ✅ `tests/unit/test_utils.py` - Tests unitaires pour les utilitaires
- ✅ Structure de tests organisée

## 🚀 Prochaines étapes

### 1. Installation des dépendances
```bash
make install
```

### 2. Configuration de l'environnement
```bash
# Créer un fichier .env (basé sur .env.example)
# Configurer les chemins et connexions
```

### 3. Lancer les services Docker
```bash
make docker-up
```

### 4. Tester l'ETL (sur un échantillon)
```bash
# Modifier le script pour utiliser 100k.csv en premier
make run-etl
```

### 5. Développer les modules manquants
- [ ] `src/processing/aggregations.py` - Agrégations par use case
- [ ] `src/api/routers/usecase*.py` - Routes API pour chaque use case
- [ ] `src/api/models/schemas.py` - Schémas Pydantic
- [ ] `src/api/services/data_service.py` - Service d'accès aux données
- [ ] `src/api/services/cache_service.py` - Service de cache Redis
- [ ] `src/frontend/` - Application React complète

## 📝 Notes importantes

### Règles métier implémentées
- ✅ Exclusion entreprises radiées (`Etat_Administratif_Entreprise = 'C'`)
- ✅ Suppression colonnes inutiles
- ✅ Gestion des nulls (Effectifs → "NN")
- ✅ Normalisation codes APE
- ✅ Normalisation régions
- ✅ Extraction année de création

### Architecture
- ✅ Séparation claire des responsabilités
- ✅ Configuration centralisée
- ✅ Logging structuré
- ✅ Tests organisés
- ✅ Docker prêt

### Performance
- ✅ Traitement par chunks (100k lignes)
- ✅ Format Parquet pour stockage optimisé
- ✅ Support partitionnement
- ✅ Compression Snappy

## 🔍 Vérifications

Pour vérifier que tout fonctionne :

```bash
# Vérifier la structure
tree src/ -I "__pycache__|*.pyc"

# Lancer les tests
make test

# Vérifier le linting
make lint

# Formater le code
make format
```

## 📚 Documentation

- `ANALYSE_PROJET.md` - Analyse complète du projet
- `DATASET_ANALYSIS.md` - Analyse du dataset
- `PROJECT_STRUCTURE.md` - Structure détaillée
- `README.md` - Guide d'utilisation

```


## Structure du projet créée

### Fichiers de configuration
- `pyproject.toml` - Configuration UV avec dépendances
- `Makefile` - Commandes automatisées
- `.gitignore` - Fichiers à ignorer
- `.pre-commit-config.yaml` - Hooks de pré-commit
- `docker-compose.yml` - Orchestration Docker (API, Frontend, Redis, HDFS, Spark)

### Modules ETL
- `src/etl/extract.py` - Extraction CSV par chunks (100k lignes)
- `src/etl/transform.py` - Transformation avec règles métier :
  - Exclusion entreprises radiées (Etat = 'C')
  - Suppression colonnes inutiles
  - Gestion des nulls
  - Normalisation des données
- `src/etl/load.py` - Chargement vers Parquet avec partitionnement
- `scripts/run_etl.py` - Script principal ETL

### Configuration et utilitaires
- `src/config/settings.py` - Settings Pydantic
- `src/config/logging.py` - Logging structuré JSON
- `src/utils/date_utils.py` - Utilitaires dates
- `src/utils/ape_utils.py` - Utilitaires codes APE avec mapping secteurs
- `src/utils/region_utils.py` - Utilitaires régions

### API de base
- `src/api/main.py` - Application FastAPI avec CORS
- Structure prête pour routers, models, services

### Docker
- Dockerfiles pour API, ETL, Frontend
- docker-compose.yml avec tous les services

### Tests
- Structure de tests organisée
- Tests unitaires pour les utilitaires

## Prochaines étapes

1. Installer les dépendances : `make install`
2. Configurer l'environnement : créer `.env`
3. Lancer les services : `make docker-up`
4. Tester l'ETL : `make run-etl`

Le projet est prêt pour le développement. La structure respecte les conventions Python et la séparation des responsabilités est en place.

Souhaitez-vous que je continue avec un module spécifique (par exemple les agrégations ou les routes API) ?

---

**User**

le .env ne peut pas se créer et se gérer avec uv dans le fichier make 

---

**Cursor**


Mise à jour du Makefile pour créer automatiquement le fichier `.env` depuis `.env.example` si nécessaire :



Création du fichier `.env.example` et mise à jour du Makefile pour créer automatiquement `.env` :



Création du fichier `.env.example` et mise à jour du Makefile :


```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Fichier .env créé depuis .env.example"; \
	else \
		echo "✓ Fichier .env existe déjà"; \
	fi

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: ## Lance le pipeline ETL
	python scripts/run_etl.py

run-api: ## Lance l'API FastAPI
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: ## Lance les tests
	pytest tests/ -v --cov=src --cov-report=html

test-unit: ## Lance uniquement les tests unitaires
	pytest tests/unit/ -v

test-integration: ## Lance uniquement les tests d'intégration
	pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	ruff check src/ tests/
	black --check src/ tests/

format: ## Formate le code avec black et ruff
	black src/ tests/
	ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Fichier .env créé depuis .env.example"; \
	else \
		echo "✓ Fichier .env existe déjà"; \
	fi

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: ## Lance les tests
	pytest tests/ -v --cov=src --cov-report=html

test-unit: ## Lance uniquement les tests unitaires
	pytest tests/unit/ -v

test-integration: ## Lance uniquement les tests d'intégration
	pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	ruff check src/ tests/
	black --check src/ tests/

format: ## Formate le code avec black et ruff
	black src/ tests/
	ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Fichier .env créé depuis .env.example"; \
	else \
		echo "✓ Fichier .env existe déjà"; \
	fi

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	ruff check src/ tests/
	black --check src/ tests/

format: ## Formate le code avec black et ruff
	black src/ tests/
	ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Fichier .env créé depuis .env.example"; \
	else \
		echo "✓ Fichier .env existe déjà"; \
	fi

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```


Vérification de la création de `.env.example` et adaptation du Makefile pour Windows :



Rendant le Makefile compatible Windows en utilisant Python pour créer le fichier `.env` :


```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@python -c "import os; import shutil; \
		if not os.path.exists('.env'): \
			if os.path.exists('.env.example'): \
				shutil.copy('.env.example', '.env'); \
				print('✓ Fichier .env créé depuis .env.example'); \
			else: \
				print('⚠ .env.example introuvable, création d\'un .env vide'); \
				open('.env', 'a').close(); \
		else: \
			print('✓ Fichier .env existe déjà')"

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```


Création d'un script Python pour gérer le fichier `.env` :


```python
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
        print("✓ Fichier .env existe déjà")
        return

    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
        print("✓ Fichier .env créé depuis .env.example")
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
        print("✓ Fichier .env créé avec les valeurs par défaut")


if __name__ == "__main__":
    try:
        create_env_file()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}", file=sys.stderr)
        sys.exit(1)

```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```


Correction du problème d'encodage dans le script :


```python
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
        print(f"❌ Erreur lors de la création du fichier .env: {e}", file=sys.stderr)
        sys.exit(1)


```

```python
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


```


Mise à jour du Makefile pour utiliser `uv run` de manière cohérente :


```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```


Mise à jour du README pour documenter cette fonctionnalité :


```markdown
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

# Lancer les services Docker
make docker-up

# Lancer l'ETL (première fois)
make run-etl

# Lancer l'API
make run-api

# Dans un autre terminal, lancer le frontend
make run-frontend
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


```


## Modifications apportées

### 1. Script de création du fichier `.env`
- **`scripts/create_env.py`** : Script Python qui :
  - Crée automatiquement `.env` depuis `.env.example` si ce dernier existe
  - Sinon, crée un `.env` avec les valeurs par défaut
  - Compatible Windows/Linux/Mac

### 2. Makefile mis à jour
- **Commande `env-file`** : Crée automatiquement le fichier `.env`
- **Intégration automatique** : `env-file` est appelé automatiquement avant :
  - `install` (et donc `setup`)
  - `run-etl`
  - `run-api`
  - `test`, `test-unit`, `test-integration`
- **Utilisation de UV** : Toutes les commandes Python utilisent `uv run` pour être cohérentes

### 3. README mis à jour
- Documentation mise à jour pour indiquer que le `.env` est créé automatiquement

## Utilisation

```bash
# Le .env sera créé automatiquement lors de l'installation
make setup

# Ou manuellement
make env-file

# Toutes les commandes créent automatiquement le .env si nécessaire
make install
make run-etl
make run-api
```

Le fichier `.env` est maintenant géré automatiquement via UV dans le Makefile.

```shellscript
# Le .env sera créé automatiquement lors de l'installation
make setup

# Ou manuellement
make env-file

# Toutes les commandes créent automatiquement le .env si nécessaire
make install
make run-etl
make run-api
```

---

**User**

je veux une commande make dev qui lance toutes les ressources 

---

**Cursor**


Ajout d'une commande `make dev` pour lancer toutes les ressources nécessaires au développement :


```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down dev dev-stop

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f


```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down dev dev-stop

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f

dev: env-file ## Lance toutes les ressources pour le développement (Docker + API + Frontend)
	@echo "=========================================="
	@echo "  Démarrage de l'environnement de dev"
	@echo "=========================================="
	@echo ""
	@echo "[1/3] Démarrage des services Docker..."
	@docker-compose up -d
	@echo "[OK] Services Docker démarrés"
	@echo ""
	@echo "[2/3] Attente de la disponibilité des services..."
	@sleep 5
	@echo "[OK] Services prêts"
	@echo ""
	@echo "[3/3] Démarrage de l'API et du Frontend..."
	@echo ""
	@echo "=========================================="
	@echo "  Services disponibles:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Redis: localhost:6379"
	@echo "  - HDFS NameNode: http://localhost:9870"
	@echo "  - Spark Master: http://localhost:8080"
	@echo "=========================================="
	@echo ""
	@echo "Pour arrêter: make dev-stop"
	@echo ""
	@echo "Démarrage de l'API en arrière-plan..."
	@uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "[OK] API démarrée (PID: $$!)"
	@echo ""
	@echo "Démarrage du Frontend..."
	@cd src/frontend && npm start

dev-stop: ## Arrête toutes les ressources de développement
	@echo "Arrêt de l'environnement de développement..."
	@docker-compose down
	@pkill -f "uvicorn src.api.main:app" || true
	@pkill -f "npm start" || true
	@echo "[OK] Toutes les ressources arrêtées"


```


Adaptation de la commande `make dev` pour lancer les services d'infrastructure en Docker et l'API/Frontend en local pour le développement :


```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down dev dev-stop

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f

dev: env-file ## Lance toutes les ressources pour le développement (Docker + API + Frontend)
	@echo "=========================================="
	@echo "  Démarrage de l'environnement de dev"
	@echo "=========================================="
	@echo ""
	@echo "[1/3] Démarrage des services Docker (Redis, HDFS, Spark)..."
	@docker-compose up -d redis hdfs-namenode hdfs-datanode spark-master spark-worker
	@echo "[OK] Services Docker démarrés"
	@echo ""
	@echo "[2/3] Attente de la disponibilité des services..."
	@echo "Attente de Redis..."
	@timeout 30 bash -c 'until docker exec sirene-redis redis-cli ping > /dev/null 2>&1; do sleep 1; done' || sleep 5
	@echo "[OK] Redis prêt"
	@sleep 3
	@echo "[OK] Services prêts"
	@echo ""
	@echo "[3/3] Démarrage de l'API et du Frontend en local..."
	@echo ""
	@echo "=========================================="
	@echo "  Services disponibles:"
	@echo "  - API: http://localhost:8000"
	@echo "  - Frontend: http://localhost:3000"
	@echo "  - Redis: localhost:6379"
	@echo "  - HDFS NameNode: http://localhost:9870"
	@echo "  - Spark Master: http://localhost:8080"
	@echo "=========================================="
	@echo ""
	@echo "Pour arrêter: make dev-stop"
	@echo ""
	@echo "Démarrage de l'API..."
	@uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "[OK] API démarrée"
	@echo ""
	@echo "Démarrage du Frontend..."
	@cd src/frontend && npm start

dev-stop: ## Arrête toutes les ressources de développement
	@echo "Arrêt de l'environnement de développement..."
	@docker-compose stop redis hdfs-namenode hdfs-datanode spark-master spark-worker
	@echo "[OK] Services Docker arrêtés"
	@echo "Arrêt de l'API et du Frontend..."
	@-pkill -f "uvicorn src.api.main:app" 2>/dev/null || true
	@-pkill -f "npm start" 2>/dev/null || true
	@-taskkill //F //IM node.exe 2>/dev/null || true
	@echo "[OK] Toutes les ressources arrêtées"


```


Création d'un script pour lancer tous les services de manière plus fiable :


```python
"""Script pour lancer l'environnement de développement complet."""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Exécute une commande."""
    print(f"[EXEC] {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def check_docker_service(service: str) -> bool:
    """Vérifie si un service Docker est en cours d'exécution."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return service in result.stdout
    except Exception:
        return False


def wait_for_redis(max_wait: int = 30) -> bool:
    """Attend que Redis soit disponible."""
    print("[WAIT] Attente de Redis...")
    for i in range(max_wait):
        try:
            result = subprocess.run(
                ["docker", "exec", "sirene-redis", "redis-cli", "ping"],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                print("[OK] Redis est prêt")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("[WARN] Redis n'est pas encore prêt, continuation...")
    return False


def main() -> None:
    """Fonction principale."""
    print("=" * 60)
    print("  Démarrage de l'environnement de développement")
    print("=" * 60)
    print()

    # Vérifier que Docker est disponible
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Docker n'est pas installé ou non disponible")
        sys.exit(1)

    # 1. Démarrer les services Docker
    print("[1/4] Démarrage des services Docker (Redis, HDFS, Spark)...")
    try:
        run_command(
            [
                "docker-compose",
                "up",
                "-d",
                "redis",
                "hdfs-namenode",
                "hdfs-datanode",
                "spark-master",
                "spark-worker",
            ]
        )
        print("[OK] Services Docker démarrés")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur lors du démarrage Docker: {e}")
        sys.exit(1)

    print()

    # 2. Attendre que les services soient prêts
    print("[2/4] Attente de la disponibilité des services...")
    wait_for_redis()
    time.sleep(3)  # Attendre un peu pour HDFS et Spark
    print("[OK] Services prêts")
    print()

    # 3. Afficher les informations
    print("[3/4] Informations des services:")
    print("=" * 60)
    print("  Services disponibles:")
    print("  - API: http://localhost:8000")
    print("  - Frontend: http://localhost:3000")
    print("  - Redis: localhost:6379")
    print("  - HDFS NameNode: http://localhost:9870")
    print("  - Spark Master: http://localhost:8080")
    print("=" * 60)
    print()

    # 4. Lancer l'API et le Frontend
    print("[4/4] Démarrage de l'API et du Frontend...")
    print()
    print("Pour arrêter: make dev-stop")
    print()

    # Lancer l'API
    print("[INFO] Démarrage de l'API sur http://localhost:8000")
    api_cmd = ["uv", "run", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    # Lancer le frontend si le dossier existe
    frontend_path = Path("src/frontend")
    if frontend_path.exists() and (frontend_path / "package.json").exists():
        print("[INFO] Démarrage du Frontend sur http://localhost:3000")
        print()
        print("⚠️  L'API et le Frontend doivent être lancés dans des terminaux séparés:")
        print()
        print("Terminal 1 (API):")
        print(f"  {' '.join(api_cmd)}")
        print()
        print("Terminal 2 (Frontend):")
        print("  cd src/frontend && npm start")
        print()
    else:
        print("[INFO] Frontend non trouvé, lancement de l'API uniquement")
        print()
        print("Pour lancer l'API, exécutez:")
        print(f"  {' '.join(api_cmd)}")
        print()

    # Option: lancer l'API directement
    try:
        print("[INFO] Lancement de l'API...")
        print("Appuyez sur Ctrl+C pour arrêter")
        print()
        run_command(api_cmd, check=False)
    except KeyboardInterrupt:
        print()
        print("[INFO] Arrêt demandé")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[INFO] Arrêt demandé")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Erreur: {e}", file=sys.stderr)
        sys.exit(1)

```

```makefile
.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down dev dev-stop

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f

dev: env-file ## Lance toutes les ressources pour le développement (Docker + API + Frontend)
	@uv run python scripts/dev.py || python scripts/dev.py

dev-stop: ## Arrête toutes les ressources de développement
	@echo "Arrêt de l'environnement de développement..."
	@docker-compose stop redis hdfs-namenode hdfs-datanode spark-master spark-worker
	@echo "[OK] Services Docker arrêtés"
	@echo "Arrêt de l'API et du Frontend..."
	@-pkill -f "uvicorn src.api.main:app" 2>/dev/null || true
	@-pkill -f "npm start" 2>/dev/null || true
	@-taskkill //F //IM node.exe 2>/dev/null || true
	@echo "[OK] Toutes les ressources arrêtées"


```


Mise à jour du README pour documenter la nouvelle commande :


```markdown
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


```


## Commande `make dev` créée

### Fonctionnalités

1. **Script Python** (`scripts/dev.py`) :
   - Lance les services Docker (Redis, HDFS, Spark)
   - Vérifie que les services sont prêts
   - Lance l'API en local (avec hot-reload)
   - Affiche les informations des services

2. **Commande `make dev`** :
   - Crée automatiquement le fichier `.env` si nécessaire
   - Lance tous les services d'infrastructure en Docker
   - Lance l'API en local pour le développement
   - Affiche les URLs des services

3. **Commande `make dev-stop`** :
   - Arrête tous les services Docker
   - Arrête l'API et le Frontend s'ils sont en cours d'exécution

### Utilisation

```bash
# Lancer tout l'environnement de développement
make dev

# Dans un autre terminal, lancer le frontend si nécessaire
cd src/frontend && npm start

# Pour arrêter tout
make dev-stop
```

### Services lancés

- **Redis** : `localhost:6379`
- **HDFS NameNode** : `http://localhost:9870`
- **HDFS DataNode** : `http://localhost:9864`
- **Spark Master** : `http://localhost:8080`
- **Spark Worker** : `http://localhost:8081`
- **API** : `http://localhost:8000` (en local avec hot-reload)
- **Frontend** : `http://localhost:3000` (à lancer manuellement)

La commande `make dev` est prête à l'emploi.

```shellscript
# Lancer tout l'environnement de développement
make dev

# Dans un autre terminal, lancer le frontend si nécessaire
cd src/frontend && npm start

# Pour arrêter tout
make dev-stop
```

