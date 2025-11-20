# 🚀 Prochaines Étapes - Projet Sirene DataViz

## ✅ Ce qui est fait

1. **Infrastructure** ✅
   - Docker Compose avec Redis, HDFS, Spark
   - API FastAPI fonctionnelle
   - Services de cache Redis
   - Services de données

2. **Modules de traitement** ✅
   - `src/processing/aggregations.py` : 5 fonctions d'agrégation pour chaque use case
   - `src/api/services/data_service.py` : Service d'accès aux données avec cache
   - `src/api/services/cache_service.py` : Service de cache Redis

3. **Routes API** ✅
   - `/api/v1/usecase1/creations` : Évolution des créations
   - `/api/v1/usecase2/sexe-dirigeants` : Répartition par sexe dirigeants
   - `/api/v1/usecase3/effectifs` : Répartition des effectifs
   - `/api/v1/usecase4/dominance-sectorielle` : Dominance sectorielle
   - `/api/v1/usecase5/types-juridiques` : Types juridiques

## 📋 À faire maintenant

### 1. Tester l'ETL avec 100k.csv (PRIORITÉ)

```bash
# Option 1: Modifier temporairement le chemin dans .env
# DATASET_CSV_PATH=./old_dataset/100k.csv

# Option 2: Créer un script de test
make run-etl
```

**Vérifier que :**
- Les données sont transformées correctement
- Les entreprises radiées (Etat='C') sont exclues
- Les fichiers Parquet sont créés dans `data/processed/`

### 2. Tester les routes API

Une fois l'ETL terminé, tester les endpoints :

```bash
# Vérifier que l'API fonctionne
curl http://localhost:8000/health

# Tester Use Case 1
curl "http://localhost:8000/api/v1/usecase1/creations?year=2020"

# Tester Use Case 2
curl "http://localhost:8000/api/v1/usecase2/sexe-dirigeants?secteur=10"

# Voir la documentation interactive
# Ouvrir http://localhost:8000/docs dans un navigateur
```

### 3. Créer le Frontend React

**Structure à créer :**
```
src/frontend/
├── package.json
├── tsconfig.json
├── public/
└── src/
    ├── components/
    │   ├── Map/
    │   │   ├── FranceMap.tsx
    │   │   └── RegionLayer.tsx
    │   ├── Filters/
    │   │   ├── YearFilter.tsx
    │   │   ├── SectorFilter.tsx
    │   │   └── RegionFilter.tsx
    │   └── Charts/
    │       └── BarChart.tsx
    ├── services/
    │   └── api.ts
    ├── hooks/
    │   └── useData.ts
    └── App.tsx
```

**Technologies :**
- React 18+
- TypeScript
- Leaflet pour les cartes
- Recharts pour les graphiques
- Axios ou fetch pour les appels API

### 4. Implémenter les visualisations

Pour chaque use case, créer :
- Une carte de France interactive (Leaflet)
- Des filtres dynamiques
- Des graphiques complémentaires
- Des tooltips avec détails

## 🧪 Tests à effectuer

### Test ETL
```bash
# Lancer l'ETL sur 100k.csv
make run-etl

# Vérifier les fichiers créés
ls -lh data/processed/

# Vérifier le contenu d'un fichier Parquet
python -c "import pandas as pd; df = pd.read_parquet('data/processed/chunk_0001.parquet'); print(df.head()); print(f'Shape: {df.shape}')"
```

### Test API
```bash
# Vérifier que les données sont chargées
curl http://localhost:8000/health | jq

# Tester chaque use case
curl "http://localhost:8000/api/v1/usecase1/creations" | jq '.[:5]'
curl "http://localhost:8000/api/v1/usecase2/sexe-dirigeants" | jq '.[:5]'
curl "http://localhost:8000/api/v1/usecase3/effectifs" | jq '.[:5]'
curl "http://localhost:8000/api/v1/usecase4/dominance-sectorielle" | jq
curl "http://localhost:8000/api/v1/usecase5/types-juridiques" | jq '.[:5]'
```

## 📊 Endpoints API disponibles

### Use Case 1: Évolution des créations
```
GET /api/v1/usecase1/creations
Query params:
  - year: int (optionnel)
  - secteur: str (optionnel, code 2 chiffres)
  - region: str (optionnel)
```

### Use Case 2: Répartition par sexe dirigeants
```
GET /api/v1/usecase2/sexe-dirigeants
Query params:
  - sexe: str (optionnel, M ou F)
  - secteur: str (optionnel)
  - region: str (optionnel)
```

### Use Case 3: Répartition des effectifs
```
GET /api/v1/usecase3/effectifs
Query params:
  - secteur: str (optionnel)
  - region: str (optionnel)
  - effectif: str (optionnel)
```

### Use Case 4: Dominance sectorielle
```
GET /api/v1/usecase4/dominance-sectorielle
Query params:
  - year: int (optionnel)
```

### Use Case 5: Types juridiques
```
GET /api/v1/usecase5/types-juridiques
Query params:
  - secteur: str (optionnel)
  - region: str (optionnel)
  - categorie_juridique: int (optionnel)
```

## 🔍 Documentation API

Une fois l'API lancée, accéder à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## ⚠️ Points d'attention

1. **Données manquantes** : Les routes API retourneront une liste vide si les données ne sont pas chargées
2. **Cache Redis** : Le cache est automatiquement désactivé si Redis n'est pas disponible
3. **Performance** : Pour le fichier complet (42M lignes), prévoir plusieurs heures pour l'ETL

## 🎯 Ordre recommandé

1. ✅ **Tester l'ETL** avec 100k.csv
2. ✅ **Tester les routes API** avec les données traitées
3. ⏳ **Créer le frontend** React de base
4. ⏳ **Implémenter les cartes** interactives
5. ⏳ **Ajouter les filtres** et graphiques
6. ⏳ **Tester l'intégration** complète

## 📝 Notes

- Les données sont chargées en mémoire au premier appel API (lazy loading)
- Le cache Redis améliore les performances pour les requêtes répétées
- Les agrégations sont calculées à la volée (pourrait être optimisé avec pré-agrégation)

