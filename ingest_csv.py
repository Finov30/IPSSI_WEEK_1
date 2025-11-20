import pandas as pd
import os
import json
from tqdm import tqdm
import traceback

# Chemins vers vos fichiers CSV (à adapter)
fichier_unite_legale = r"C:\IPSSI_19_11_2025\StockUniteLegale_utf8.csv"
fichier_etablissement = r"C:\IPSSI_19_11_2025\StockEtablissement_utf8.csv"
fichier_codepostal_region = r"C:\IPSSI_19_11_2025\regions-france.csv"  # Fichier mapping code postal → region

# Paramètres de batch
TAILLE_BATCH = 100000  # Nombre de lignes par batch (augmenté pour meilleures performances)
DOSSIER_TEMP = r"C:\IPSSI_19_11_2025\temp_batches"
FICHIER_CHECKPOINT = r"C:\IPSSI_19_11_2025\checkpoint.json"
fichier_sortie = r"C:\Users\samua\Desktop\Google\Sirene_merged_with_region.csv"

# Créer le dossier temporaire si nécessaire
os.makedirs(DOSSIER_TEMP, exist_ok=True)

# Colonnes à garder dans chaque fichier
colonnes_unite = [
    'siren',
    'categorieJuridiqueUniteLegale',
    'activitePrincipaleUniteLegale',
    'nomUniteLegale',
    'denominationUniteLegale',
    'prenom1UniteLegale',
    'nomUsageUniteLegale',
    'sexeUniteLegale',
    'trancheEffectifsUniteLegale',
    'dateCreationUniteLegale',
    'dateDernierTraitementUniteLegale',
    'statutDiffusionUniteLegale',
    'categorieEntreprise',
    'caractereEmployeurUniteLegale',
    'etatAdministratifUniteLegale',
    'dateDebut'
]

colonnes_etab = [
    'siren',
    'siret',
    'activitePrincipaleEtablissement',
    'codePostalEtablissement',
    'libelleCommuneEtablissement',
    'caractereEmployeurEtablissement',
    'trancheEffectifsEtablissement',
    'dateDernierTraitementEtablissement',
    'denominationUsuelleEtablissement',
    'enseigne1Etablissement',
    'etatAdministratifEtablissement',
    'dateDebut'
]

def charger_checkpoint():
    """Charge le checkpoint pour reprendre où on s'est arrêté"""
    if os.path.exists(FICHIER_CHECKPOINT):
        with open(FICHIER_CHECKPOINT, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'batch_etab_actuel': 0, 'batches_completes': []}

def sauvegarder_checkpoint(checkpoint):
    """Sauvegarde l'état actuel du traitement"""
    with open(FICHIER_CHECKPOINT, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2)

def get_departement_from_code_postal_vectorized(series_cp):
    """Extrait le département depuis une série de codes postaux (vectorisé avec gestion d'erreurs)"""
    try:
        # Convertir en string et zfill (gérer les NaN et valeurs invalides)
        cp_str = series_cp.astype(str)
        # Remplacer 'nan' et valeurs invalides par chaîne vide (utiliser replace avec dict)
        cp_str = cp_str.replace({'nan': '', 'None': '', 'null': '', 'NaN': '', 'NaT': ''})
        cp_str = cp_str.str.zfill(5)
        
        # Initialiser avec les 2 premiers chiffres
        dept = cp_str.str[:2]
        
        # Cas DOM-TOM (971, 972, 973, 974, 976)
        mask_dom = cp_str.str.startswith('97')
        dept = dept.where(~mask_dom, cp_str.str[:3])
        
        # Cas spécial pour la Corse (20000-20189 -> 2A, 20190-20999 -> 2B)
        mask_corse = cp_str.str.startswith('20')
        if mask_corse.any():
            cp_numeric = pd.to_numeric(cp_str, errors='coerce')
            mask_2a = mask_corse & (cp_numeric >= 20000) & (cp_numeric <= 20189)
            mask_2b = mask_corse & (cp_numeric >= 20190) & (cp_numeric <= 20999)
            dept = dept.where(~mask_2a, '2A')
            dept = dept.where(~mask_2b, '2B')
        
        # Remplacer les valeurs vides par None
        dept = dept.replace('', None)
        
        return dept
    except Exception as e:
        print(f"⚠ Erreur lors de l'extraction du département: {e}")
        print(f"  Types de données: {series_cp.dtype}")
        print(f"  Exemple de valeurs: {series_cp.head()}")
        # Retourner une série de None en cas d'erreur
        return pd.Series([None] * len(series_cp), index=series_cp.index)

def traiter_batch(df_etab_batch, df_unite_indexed, mapping_dept_nom_region):
    """Traite un batch d'établissements (optimisé avec gestion d'erreurs)"""
    try:
        # Jointure sur siren entre établissement et unité légale (avec index pour performance)
        try:
            # Utiliser left_on avec right_index=True pour éviter l'ambiguïté index/colonne
            df_merged = df_etab_batch.merge(df_unite_indexed, left_on='siren', right_index=True, 
                                          how='left', suffixes=('_etab', '_unite'))
        except Exception as e:
            print(f"⚠ Erreur lors de la jointure SIREN: {e}")
            print(f"  Colonnes disponibles dans df_etab_batch: {df_etab_batch.columns.tolist()}")
            print(f"  Colonnes disponibles dans df_unite_indexed: {df_unite_indexed.columns.tolist()}")
            # Essayer avec une jointure plus simple en retirant l'index
            try:
                # reset_index() sans drop pour récupérer siren comme colonne depuis l'index
                df_unite_reset = df_unite_indexed.reset_index()
                df_merged = df_etab_batch.merge(df_unite_reset, on='siren', how='left', suffixes=('_etab', '_unite'))
            except Exception as e2:
                print(f"⚠ Erreur lors de la jointure alternative: {e2}")
                # Dernière tentative : copier et faire une jointure basique
                df_merged = df_etab_batch.copy()
                # Ajouter des colonnes vides pour les colonnes manquantes depuis df_unite_indexed
                # Note: siren est l'index, donc on récupère toutes les colonnes
                df_unite_cols = df_unite_indexed.columns.tolist()
                for col in df_unite_cols:
                    if col not in df_merged.columns:
                        df_merged[col] = None
        
        # Nettoyage code postal au format chaîne (vectorisé avec gestion d'erreurs)
        try:
            if 'codePostalEtablissement' in df_merged.columns:
                # Gérer les valeurs NaN et invalides
                df_merged['codePostalEtablissement'] = df_merged['codePostalEtablissement'].fillna('').astype(str)
                df_merged['codePostalEtablissement'] = df_merged['codePostalEtablissement'].replace(['nan', 'None', 'null', 'NaN'], '')
                df_merged['codePostalEtablissement'] = df_merged['codePostalEtablissement'].str.zfill(5)
                # Remplacer les codes vides par None
                df_merged.loc[df_merged['codePostalEtablissement'] == '00000', 'codePostalEtablissement'] = None
        except Exception as e:
            print(f"⚠ Erreur lors du nettoyage du code postal: {e}")
            if 'codePostalEtablissement' not in df_merged.columns:
                df_merged['codePostalEtablissement'] = None
        
        # Mapping code postal → région en utilisant le département (vectorisé)
        try:
            if 'codePostalEtablissement' in df_merged.columns:
                df_merged['departement'] = get_departement_from_code_postal_vectorized(df_merged['codePostalEtablissement'])
                df_merged['region'] = df_merged['departement'].map(mapping_dept_nom_region)
            else:
                df_merged['departement'] = None
                df_merged['region'] = None
        except Exception as e:
            print(f"⚠ Erreur lors du mapping département → région: {e}")
            df_merged['departement'] = None
            df_merged['region'] = None
        
        # Supprimer la colonne département temporaire
        df_merged.drop(columns=['departement'], inplace=True, errors='ignore')
        
        df_final = df_merged
        
        # Renommage colonnes pour clarté et suppression du doublon code_postal (avec gestion d'erreurs)
        try:
            df_final = df_final.rename(columns={
                'siren': 'SIREN',
                'siret': 'SIRET',
                'activitePrincipaleUniteLegale': 'Code_APE_Entreprise',
                'activitePrincipaleEtablissement': 'Code_APE_Etablissement',
                'nomUniteLegale': 'Nom_Entreprise',
                'denominationUniteLegale': 'Denomination_Entreprise',
                'prenom1UniteLegale': 'Prenom_Dirigeant',
                'nomUsageUniteLegale': 'Nom_Dirigeant',
                'sexeUniteLegale': 'Sexe_Dirigeant',
                'categorieJuridiqueUniteLegale': 'Categorie_Juridique',
                'trancheEffectifsUniteLegale': 'Effectifs_Entreprise',
                'trancheEffectifsEtablissement': 'Effectifs_Etablissement',
                'codePostalEtablissement': 'Code_Postal',
                'libelleCommuneEtablissement': 'Ville',
                'dateCreationUniteLegale': 'Date_Creation_Entreprise',
                'dateDernierTraitementUniteLegale': 'Date_MAJ_Entreprise',
                'dateDernierTraitementEtablissement': 'Date_MAJ_Etablissement',
                'statutDiffusionUniteLegale': 'Statut_Diffusion',
                'categorieEntreprise': 'Categorie_Entreprise_PME_TPE',
                'caractereEmployeurUniteLegale': 'Employeur_Entreprise',
                'caractereEmployeurEtablissement': 'Employeur_Etablissement',
                'denominationUsuelleEtablissement': 'Denomination_Usuelle_Etablissement',
                'enseigne1Etablissement': 'Enseigne_Etablissement',
                'etatAdministratifUniteLegale': 'Etat_Administratif_Entreprise',
                'etatAdministratifEtablissement': 'Etat_Administratif_Etablissement',
                'dateDebut_unite': 'Date_Debut_Activite_Entreprise',
                'dateDebut_etab': 'Date_Debut_Activite_Etablissement',
                'region': 'Region'  # champ de la table code postal → région
            })
        except Exception as e:
            print(f"⚠ Erreur lors du renommage des colonnes: {e}")
            print(f"  Colonnes disponibles: {df_final.columns.tolist()}")
            # Continuer même si le renommage échoue
        
        # Supprimer colonnes superflues (optionnel)
        try:
            df_final.drop(columns=['dateDebut_unite', 'dateDebut_etab'], inplace=True, errors='ignore')
        except Exception as e:
            print(f"⚠ Erreur lors de la suppression des colonnes: {e}")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Erreur critique lors du traitement du batch: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        # Retourner un DataFrame vide plutôt que de crasher
        return pd.DataFrame()

def fusionner_batches_completes(fichiers_batches):
    """Fusionne tous les batches traités en un seul fichier final (optimisé)"""
    print(f"\nFusion de {len(fichiers_batches)} batches...")
    dfs = []
    for fichier_batch in tqdm(fichiers_batches, desc="  Chargement des batches", unit="batch"):
        # Charger avec types optimisés
        df = pd.read_csv(fichier_batch, encoding='utf-8', low_memory=False)
        dfs.append(df)
    
    print("  Concaténation des données...")
    df_final = pd.concat(dfs, ignore_index=True, sort=False)
    
    print(f"  Sauvegarde du fichier final ({len(df_final):,} lignes)...")
    # Utiliser compression et optimisations pour la sauvegarde
    df_final.to_csv(fichier_sortie, index=False, encoding='utf-8', 
                    chunksize=100000, compression=None)
    print(f"✓ Fichier fusionné créé : {fichier_sortie}")
    
    # Nettoyage des fichiers temporaires
    print("\nNettoyage des fichiers temporaires...")
    for fichier_batch in fichiers_batches:
        try:
            os.remove(fichier_batch)
        except Exception as e:
            print(f"  Erreur lors de la suppression de {fichier_batch}: {e}")
    
    # Suppression du checkpoint et du dossier temp
    try:
        if os.path.exists(FICHIER_CHECKPOINT):
            os.remove(FICHIER_CHECKPOINT)
        if os.path.exists(DOSSIER_TEMP) and not os.listdir(DOSSIER_TEMP):
            os.rmdir(DOSSIER_TEMP)
    except Exception as e:
        print(f"  Erreur lors du nettoyage: {e}")

# Chargement fichier de correspondance codes postaux → région (petit fichier, chargé une fois)
print("Chargement du fichier de correspondance codes postaux → région...")
df_region_codes = pd.read_csv(fichier_codepostal_region, sep=',', encoding='utf-8')

# S'assurer que les codes région sont en string avec zéro devant si nécessaire
# Convertir d'abord en string, puis zfill pour gérer les cas où c'est déjà un string ou un int
df_region_codes['code_region'] = df_region_codes['code_region'].astype(str)
# Si le code a moins de 2 caractères, ajouter un zéro devant
df_region_codes['code_region'] = df_region_codes['code_region'].apply(lambda x: x.zfill(2) if len(x) < 2 else x)

# Créer un mapping département → nom de région
# Les 2 premiers chiffres du code postal correspondent généralement au département
# Mapping des départements vers les codes région, puis vers les noms
mapping_dept_code_region = {
    # Guadeloupe (971)
    '971': '01',
    # Martinique (972)
    '972': '02',
    # Guyane (973)
    '973': '03',
    # La Réunion (974)
    '974': '04',
    # Mayotte (976)
    '976': '06',
    # Île-de-France (75, 77, 78, 91, 92, 93, 94, 95)
    '75': '11', '77': '11', '78': '11', '91': '11', '92': '11', '93': '11', '94': '11', '95': '11',
    # Centre-Val de Loire (18, 28, 36, 37, 41, 45)
    '18': '24', '28': '24', '36': '24', '37': '24', '41': '24', '45': '24',
    # Bourgogne-Franche-Comté (21, 25, 39, 58, 70, 71, 89, 90)
    '21': '27', '25': '27', '39': '27', '58': '27', '70': '27', '71': '27', '89': '27', '90': '27',
    # Normandie (14, 27, 50, 61, 76)
    '14': '28', '27': '28', '50': '28', '61': '28', '76': '28',
    # Hauts-de-France (02, 59, 60, 62, 80)
    '02': '32', '59': '32', '60': '32', '62': '32', '80': '32',
    # Grand Est (08, 10, 51, 52, 54, 55, 57, 67, 68, 88)
    '08': '44', '10': '44', '51': '44', '52': '44', '54': '44', '55': '44', '57': '44', '67': '44', '68': '44', '88': '44',
    # Pays de la Loire (44, 49, 53, 72, 85)
    '44': '52', '49': '52', '53': '52', '72': '52', '85': '52',
    # Bretagne (22, 29, 35, 56)
    '22': '53', '29': '53', '35': '53', '56': '53',
    # Nouvelle-Aquitaine (16, 17, 19, 23, 24, 33, 40, 47, 64, 79, 86, 87)
    '16': '75', '17': '75', '19': '75', '23': '75', '24': '75', '33': '75', '40': '75', '47': '75', '64': '75', '79': '75', '86': '75', '87': '75',
    # Occitanie (09, 11, 12, 30, 31, 32, 34, 46, 48, 65, 66, 81, 82)
    '09': '76', '11': '76', '12': '76', '30': '76', '31': '76', '32': '76', '34': '76', '46': '76', '48': '76', '65': '76', '66': '76', '81': '76', '82': '76',
    # Auvergne-Rhône-Alpes (01, 03, 07, 15, 26, 38, 42, 43, 63, 69, 73, 74)
    '01': '84', '03': '84', '07': '84', '15': '84', '26': '84', '38': '84', '42': '84', '43': '84', '63': '84', '69': '84', '73': '84', '74': '84',
    # Provence-Alpes-Côte d'Azur (04, 05, 06, 13, 83, 84)
    '04': '93', '05': '93', '06': '93', '13': '93', '83': '93', '84': '93',
    # Corse (2A, 2B)
    '2A': '94', '2B': '94'
}

# Créer un dictionnaire code_region -> nom_region
# S'assurer que les codes sont en string avec zéro devant
dict_code_region_nom = {}
for idx, row in df_region_codes.iterrows():
    code = str(row['code_region']).strip()
    # Normaliser le code (ajouter zéro devant si nécessaire)
    if len(code) < 2:
        code = code.zfill(2)
    nom = str(row['nom_region']).strip()
    dict_code_region_nom[code] = nom

# Afficher le dictionnaire pour debug
print(f"  Codes région chargés depuis CSV: {sorted(dict_code_region_nom.keys())}")

# Créer un mapping département -> nom de région
mapping_dept_nom_region = {}
codes_manquants = []
for dept, code_region in mapping_dept_code_region.items():
    # S'assurer que le code région est en string avec zéro devant
    code_region_str = str(code_region).strip()
    if len(code_region_str) < 2:
        code_region_str = code_region_str.zfill(2)
    
    if code_region_str in dict_code_region_nom:
        mapping_dept_nom_region[dept] = dict_code_region_nom[code_region_str]
    else:
        codes_manquants.append((dept, code_region_str))

if codes_manquants:
    print(f"  ⚠ {len(codes_manquants)} codes région non trouvés (premiers exemples): {codes_manquants[:5]}")

print(f"✓ Mapping département → région créé ({len(mapping_dept_nom_region)} départements)\n")

# Chargement du fichier unité légale (chargé une fois en mémoire pour les jointures)
print("Chargement du fichier unité légale...")

# Estimer le nombre total de lignes pour la barre de progression
print("  Estimation du nombre de lignes...")
with open(fichier_unite_legale, 'rb') as f:
    sample_size = min(1024 * 1024, os.path.getsize(fichier_unite_legale))  # 1MB ou taille du fichier
    sample = f.read(sample_size)
    lines_in_sample = sample.count(b'\n')
    if lines_in_sample > 0:
        file_size = os.path.getsize(fichier_unite_legale)
        total_lignes_unite_estime = int((file_size / sample_size) * lines_in_sample)
    else:
        total_lignes_unite_estime = 0

chunk_size = 200000  # Chunks plus grands pour meilleures performances
estimated_chunks = max((total_lignes_unite_estime // chunk_size) + 1, 1)

# Charger directement avec types optimisés et indexer sur siren pour accélérer les jointures
chunks_unite = []
total_lignes_chargees = 0
try:
    reader_unite = pd.read_csv(fichier_unite_legale, sep=',', encoding='utf-8', 
                              chunksize=chunk_size, low_memory=False, usecols=colonnes_unite,
                              dtype={'siren': 'str'},  # siren en string pour éviter les problèmes de type
                              on_bad_lines='skip',  # Ignorer les lignes mal formées
                              engine='c')  # Utiliser le parser C plus rapide
    
    # Barre de progression améliorée avec informations détaillées
    pbar_unite = tqdm(reader_unite, total=estimated_chunks, 
                     desc="  Chargement unités légales", 
                     unit=" chunk",
                     bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]')
    
    for chunk in pbar_unite:
        try:
            total_lignes_chargees += len(chunk)
            # Optimiser les types de données
            for col in chunk.columns:
                try:
                    if chunk[col].dtype == 'object':
                        # Convertir en category si peu de valeurs uniques (gain mémoire et performance)
                        unique_ratio = chunk[col].nunique() / len(chunk)
                        if unique_ratio < 0.5 and chunk[col].nunique() < 10000:
                            chunk[col] = chunk[col].astype('category')
                except Exception as e:
                    pass  # Ignorer les erreurs d'optimisation silencieusement
            chunks_unite.append(chunk)
            # Mettre à jour la description avec le nombre de lignes chargées
            pbar_unite.set_postfix({"lignes": f"{total_lignes_chargees:,}"})
        except Exception as e:
            print(f"\n⚠ Erreur lors du traitement d'un chunk: {e}")
            print(f"  Continuation du chargement...")
            continue
    
    pbar_unite.close()
    
    if chunks_unite:
        print("  Concaténation des chunks...")
        df_unite = pd.concat(chunks_unite, ignore_index=True, sort=False)
        print("  Indexation sur SIREN...")
        # Indexer sur siren pour accélérer les jointures (CRITIQUE pour performance)
        # Utiliser drop=True pour éviter d'avoir siren à la fois en index et en colonne
        df_unite_indexed = df_unite.set_index('siren', drop=True)
        print(f"✓ {len(df_unite):,} unités légales chargées et indexées\n")
    else:
        raise ValueError("Aucun chunk n'a pu être chargé")
except Exception as e:
    print(f"❌ Erreur critique lors du chargement des unités légales: {e}")
    print(f"  Traceback: {traceback.format_exc()}")
    raise

# Chargement du checkpoint
checkpoint = charger_checkpoint()
batch_etab_actuel = checkpoint['batch_etab_actuel']
batches_completes = checkpoint['batches_completes']

print(f"\n{'='*60}")
print(f"Traitement par batches (taille: {TAILLE_BATCH} lignes)")
if batch_etab_actuel > 0:
    print(f"✓ Reprise depuis le batch {batch_etab_actuel} ({len(batches_completes)} batches déjà complétés)")
else:
    print("✓ Démarrage du traitement")
print(f"{'='*60}\n")

# Traitement du fichier établissement par batches
try:
    # Estimer le nombre total de lignes rapidement
    print("Estimation du nombre total de lignes...")
    # Utiliser une méthode rapide : compter seulement les premières lignes pour estimer
    with open(fichier_etablissement, 'rb') as f:
        # Lire un échantillon pour estimer
        sample_size = min(1024 * 1024, os.path.getsize(fichier_etablissement))  # 1MB ou taille du fichier
        sample = f.read(sample_size)
        lines_in_sample = sample.count(b'\n')
        if lines_in_sample > 0:
            file_size = os.path.getsize(fichier_etablissement)
            total_lignes_estime = int((file_size / sample_size) * lines_in_sample)
        else:
            total_lignes_estime = 0
    print(f"Estimation: ~{total_lignes_estime:,} lignes à traiter\n")
    
    # Calculer le nombre total de batches (sera ajusté dynamiquement)
    total_batches = max((total_lignes_estime // TAILLE_BATCH) + 1, 100)  # Minimum 100 pour la barre de progression
    
    # Lecture par chunks avec types optimisés et gestion d'erreurs
    reader_etab = pd.read_csv(fichier_etablissement, sep=',', encoding='utf-8', 
                              chunksize=TAILLE_BATCH, low_memory=False, usecols=colonnes_etab,
                              dtype={'siren': 'str', 'siret': 'str'},  # Types optimisés
                              on_bad_lines='skip',  # Ignorer les lignes mal formées
                              engine='c')  # Utiliser le parser C plus rapide
    
    # Barre de progression pour les batches
    pbar = tqdm(enumerate(reader_etab), total=total_batches, desc="Traitement des batches", unit="batch")
    
    for batch_num, df_etab_batch in pbar:
        try:
            # Si ce batch a déjà été traité, on le saute
            if batch_num < batch_etab_actuel:
                pbar.set_postfix({"status": f"Batch {batch_num + 1} déjà traité"})
                continue
            
            pbar.set_postfix({"status": f"Traitement batch {batch_num + 1}"})
            
            # Traitement du batch avec gestion d'erreurs
            try:
                df_final_batch = traiter_batch(df_etab_batch, df_unite_indexed, mapping_dept_nom_region)
                
                # Vérifier que le batch n'est pas vide
                if df_final_batch.empty:
                    print(f"⚠ Batch {batch_num + 1} est vide après traitement, passage au suivant...")
                    continue
            except Exception as e:
                print(f"⚠ Erreur lors du traitement du batch {batch_num + 1}: {e}")
                print(f"  Nombre de lignes dans le batch: {len(df_etab_batch)}")
                print(f"  Colonnes: {df_etab_batch.columns.tolist()}")
                # Continuer avec le batch suivant
                continue
            
            # Sauvegarde du batch traité (optimisée avec gestion d'erreurs)
            try:
                fichier_batch = os.path.join(DOSSIER_TEMP, f"batch_{batch_num:06d}.csv")
                df_final_batch.to_csv(fichier_batch, index=False, encoding='utf-8', 
                                     chunksize=50000, errors='replace')  # Écrire par chunks pour grandes données
            except Exception as e:
                print(f"⚠ Erreur lors de la sauvegarde du batch {batch_num + 1}: {e}")
                print(f"  Tentative de sauvegarde alternative...")
                try:
                    # Essayer une sauvegarde sans chunksize
                    df_final_batch.to_csv(fichier_batch, index=False, encoding='utf-8', errors='replace')
                except Exception as e2:
                    print(f"❌ Impossible de sauvegarder le batch {batch_num + 1}: {e2}")
                    continue
            
            # Mise à jour du checkpoint
            try:
                batches_completes.append(fichier_batch)
                checkpoint['batch_etab_actuel'] = batch_num + 1
                checkpoint['batches_completes'] = batches_completes
                sauvegarder_checkpoint(checkpoint)
            except Exception as e:
                print(f"⚠ Erreur lors de la sauvegarde du checkpoint: {e}")
            
            lignes_traitees = (batch_num + 1) * TAILLE_BATCH
            if lignes_traitees > total_lignes_estime:
                lignes_traitees = total_lignes_estime
            pourcentage = (lignes_traitees / total_lignes_estime) * 100 if total_lignes_estime > 0 else 0
            pbar.set_postfix({"status": f"✓ Batch {batch_num + 1} sauvegardé ({pourcentage:.1f}%)"})
            
        except Exception as e:
            print(f"❌ Erreur inattendue dans le batch {batch_num + 1}: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            print(f"  Continuation du traitement...")
            continue
    
    pbar.close()
    
    # Tous les batches sont traités, fusion finale
    print(f"{'='*60}")
    print("Tous les batches sont traités. Fusion en cours...")
    print(f"{'='*60}")
    fusionner_batches_completes(batches_completes)
    
except KeyboardInterrupt:
    print("\n\n⚠ Interruption par l'utilisateur. Le traitement peut être repris plus tard.")
    print(f"Checkpoint sauvegardé: {FICHIER_CHECKPOINT}")
    print(f"Batches complétés: {len(batches_completes)}")
    
except Exception as e:
    print(f"\n\n❌ Erreur lors du traitement: {e}")
    print(f"Checkpoint sauvegardé: {FICHIER_CHECKPOINT}")
    print(f"Batches complétés: {len(batches_completes)}")
    print("Vous pouvez relancer le script pour reprendre où il s'est arrêté.")
    raise
