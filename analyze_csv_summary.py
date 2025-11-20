#!/usr/bin/env python3
"""Résumé de l'analyse du dataset Sirene"""

import pandas as pd

print("=" * 60)
print("RÉSUMÉ DE L'ANALYSE DU DATASET SIRENE")
print("=" * 60)

# Informations générales
print(f"\n📊 VOLUME DE DONNÉES")
print(f"  - Total d'enregistrements: {42151993:,} lignes (~42 millions)")
print(f"  - Nombre de colonnes: 28")
print(f"  - Taille estimée: ~7.8 GB")

# Analyse des 1000 premières lignes
df = pd.read_csv('dataset/Sirene_merged_with_region.csv', nrows=1000)

print(f"\n🔍 ANALYSE DE L'ÉCHANTILLON (1000 premières lignes)")
print(f"  - Entreprises radiées (Etat_Administratif_Entreprise='C'): {(df['Etat_Administratif_Entreprise'] == 'C').sum()} ({((df['Etat_Administratif_Entreprise'] == 'C').sum()/len(df)*100):.1f}%)")
print(f"  - Dates création renseignées: {df['Date_Creation_Entreprise'].notna().sum()} ({df['Date_Creation_Entreprise'].notna().sum()/len(df)*100:.1f}%)")
print(f"  - Sexe dirigeant renseigné: {df['Sexe_Dirigeant'].notna().sum()} ({df['Sexe_Dirigeant'].notna().sum()/len(df)*100:.1f}%)")
print(f"  - Enseigne_Etablissement renseigné: {df['Enseigne_Etablissement'].notna().sum()} ({df['Enseigne_Etablissement'].notna().sum()/len(df)*100:.1f}%)")
print(f"  - Denomination_Usuelle_Etablissement renseigné: {df['Denomination_Usuelle_Etablissement'].notna().sum()} ({df['Denomination_Usuelle_Etablissement'].notna().sum()/len(df)*100:.1f}%)")

print(f"\n⚠️ RÈGLES DE FILTRAGE À APPLIQUER")
print(f"  - Exclure: Etat_Administratif_Entreprise = 'C' (~16% des données)")
print(f"  - Supprimer colonnes: Enseigne_Etablissement, Denomination_Usuelle_Etablissement, Statut_Diffusion")
print(f"  - Ignorer colonnes vides: Employeur_Entreprise")

print(f"\n✅ DOCUMENTS CRÉÉS")
print(f"  - DATASET_ANALYSIS.md: Analyse détaillée du dataset")
print(f"  - PROJECT_STRUCTURE.md: Structure et conventions du projet")

print(f"\n📋 COLONNES PAR CATÉGORIE")
print(f"  Identifiants: SIREN, SIRET")
print(f"  Établissement: 11 colonnes (Effectifs, Dates, Localisation, etc.)")
print(f"  Entreprise: 13 colonnes (Dates, Dirigeant, Catégories, etc.)")
print(f"  Géographie: Region")

print("\n" + "=" * 60)

