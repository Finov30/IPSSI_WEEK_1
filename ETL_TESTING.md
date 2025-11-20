# 🧪 Guide de Test ETL avec 100k.csv

## 📋 Vue d'ensemble

Ce guide explique comment tester le pipeline ETL avec le fichier `100k.csv` (100 000 lignes) avant de traiter le fichier complet de 42 millions de lignes.

## 🚀 Utilisation

### 1. Lancer le test ETL

```bash
make test-etl-100k
```

Cette commande va :
- ✅ Charger le fichier `old_dataset/100k.csv`
- ✅ Appliquer toutes les transformations (filtrage, nettoyage, normalisation)
- ✅ Créer des fichiers Parquet dans `data/processed/test_100k/`
- ✅ Afficher des statistiques détaillées
- ✅ Vérifier que les règles métier sont bien appliquées

### 2. Vérifier les résultats

```bash
make verify-etl
```

Cette commande affiche :
- Le nombre de fichiers Parquet créés
- Le nombre de lignes traitées
- Les vérifications de qualité (entreprises radiées, colonnes supprimées, etc.)
- Un aperçu des données

### 3. Tester les routes API avec les données de test

Une fois l'ETL testé, les données sont automatiquement utilisées par l'API si elles sont disponibles :

```bash
# Lancer l'API (si pas déjà lancée)
make run-api

# Dans un autre terminal, tester les endpoints
curl http://localhost:8000/health | jq
curl "http://localhost:8000/api/v1/usecase1/creations?year=2020" | jq '.[:5]'
```

## 📊 Ce qui est vérifié

Le script de test vérifie automatiquement :

### ✅ Règles métier
- **Entreprises radiées exclues** : Aucune entreprise avec `Etat_Administratif_Entreprise = 'C'` ne doit être présente
- **Colonnes supprimées** : Les colonnes inutiles sont bien supprimées :
  - `Enseigne_Etablissement`
  - `Denomination_Usuelle_Etablissement`
  - `Statut_Diffusion`
  - `Employeur_Entreprise`
  - `Prenom_Dirigeant`
  - `Nom_Dirigeant`
- **Gestion des nulls** : Les effectifs nulls sont remplacés par "NN"

### ✅ Qualité des données
- Taux de rétention (lignes valides / lignes initiales)
- Nombre de fichiers Parquet créés
- Statistiques sur les régions et codes APE

## 📁 Structure des fichiers

```
data/
└── processed/
    ├── test_100k/              # Données de test (100k.csv)
    │   ├── chunk_0001.parquet
    │   └── ...
    └── chunk_0001.parquet      # Données de production (fichier complet)
        └── ...
```

## 🔍 Exemple de sortie

```
================================================================================
TEST ETL AVEC 100K.CSV
================================================================================
Fichier source: old_dataset/100k.csv
Taille du fichier: 15.23 MB

--------------------------------------------------------------------------------
DÉBUT DU TRAITEMENT
--------------------------------------------------------------------------------

================================================================================
CHUNK 1
================================================================================
Lignes dans le chunk: 100,000
Entreprises radiées dans le chunk: 12,345
Transformation en cours...
Entreprises radiées exclues: 12,345
Validation en cours...
Métriques de qualité:
  - Total lignes: 87,655
  - Total colonnes: 22
  - Entreprises radiées restantes: 0

Sauvegarde vers: data/processed/test_100k/chunk_0001.parquet
✓ Fichier créé: 8.45 MB

================================================================================
RÉSUMÉ DU TEST ETL
================================================================================
Total lignes initiales: 100,000
Total lignes après filtrage: 87,655
Entreprises radiées exclues: 12,345
Taux de rétention: 87.66%
Fichiers Parquet créés: 1
Répertoire de sortie: data/processed/test_100k

--------------------------------------------------------------------------------
VÉRIFICATIONS
--------------------------------------------------------------------------------
✓ Aucune entreprise radiée dans les données finales
✓ Toutes les colonnes inutiles ont été supprimées
✓ Tous les effectifs nulls ont été remplacés par 'NN'

================================================================================
✓ TEST ETL TERMINÉ AVEC SUCCÈS
================================================================================
```

## ⚠️ Points d'attention

1. **Temps d'exécution** : Le test avec 100k.csv devrait prendre quelques secondes à quelques minutes selon votre machine
2. **Espace disque** : Les fichiers Parquet sont compressés, environ 8-10 MB pour 100k lignes
3. **Données de test** : Les données de test sont automatiquement utilisées par l'API si disponibles

## 🔄 Prochaines étapes

Une fois le test ETL validé :

1. ✅ **Tester les routes API** avec les données de test
2. ✅ **Vérifier les agrégations** pour chaque use case
3. ⏳ **Lancer l'ETL complet** sur le fichier de 42M lignes (plusieurs heures)
4. ⏳ **Créer le frontend** React pour visualiser les données

## 🐛 Dépannage

### Erreur : "Fichier de test introuvable"
```bash
# Vérifier que le fichier existe
ls -lh old_dataset/100k.csv

# Si absent, le créer depuis le fichier complet
# (voir get100K.py)
```

### Erreur : "Aucun fichier Parquet trouvé"
```bash
# Vérifier le répertoire
ls -lh data/processed/test_100k/

# Relancer le test
make test-etl-100k
```

### Les données ne sont pas chargées par l'API
```bash
# Vérifier que les fichiers existent
make verify-etl

# Redémarrer l'API
make run-api
```

## 📝 Notes

- Les données de test sont stockées dans `data/processed/test_100k/`
- L'API utilise automatiquement les données de test si disponibles
- Pour utiliser les données de production, supprimer le dossier `test_100k` ou lancer l'ETL complet

