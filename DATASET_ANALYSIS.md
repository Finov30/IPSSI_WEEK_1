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
