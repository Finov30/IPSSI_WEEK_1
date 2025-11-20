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

