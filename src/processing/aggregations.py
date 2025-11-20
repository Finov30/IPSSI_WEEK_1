"""Module d'agrégation des données par use case."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from src.config.settings import get_settings
from src.utils.ape_utils import get_secteur_from_ape
from src.utils.date_utils import extract_year

logger = logging.getLogger(__name__)


def load_processed_data(data_path: str | None = None, use_test_data: bool = False) -> pd.DataFrame:
    """
    Charge les données traitées depuis les fichiers Parquet.

    Args:
        data_path: Chemin vers les données traitées. Si None, utilise le chemin des settings.
        use_test_data: Si True, charge les données de test (test_100k) en priorité.

    Returns:
        DataFrame avec toutes les données traitées
    """
    settings = get_settings()
    base_path = Path(data_path or settings.data_processed_path)

    # Si use_test_data, chercher d'abord dans test_100k
    if use_test_data:
        test_path = base_path / "test_100k"
        if test_path.exists():
            processed_path = test_path
            logger.info(f"Chargement des données de test depuis: {processed_path}")
        else:
            processed_path = base_path
            logger.info(f"Données de test non trouvées, utilisation de: {processed_path}")
    else:
        processed_path = base_path

    if not processed_path.exists():
        logger.warning(f"Répertoire de données traitées introuvable: {processed_path}")
        return pd.DataFrame()

    # Charger tous les fichiers Parquet
    parquet_files = list(processed_path.glob("*.parquet"))
    if not parquet_files:
        logger.warning(f"Aucun fichier Parquet trouvé dans: {processed_path}")
        return pd.DataFrame()

    logger.info(f"Chargement de {len(parquet_files)} fichiers Parquet...")
    dfs = []
    for parquet_file in parquet_files:
        try:
            df = pd.read_parquet(parquet_file)
            dfs.append(df)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {parquet_file}: {e}")

    if not dfs:
        return pd.DataFrame()

    result = pd.concat(dfs, ignore_index=True)
    logger.info(f"Données chargées: {len(result):,} lignes")
    return result


def aggregate_usecase1_creations(
    df: pd.DataFrame,
    year: int | None = None,
    secteur: str | None = None,
    region: str | None = None,
) -> pd.DataFrame:
    """
    Use Case 1: Évolution des créations d'entreprises par année et secteur d'activité.

    Agrégation: COUNT(*) GROUP BY année, secteur, région

    Args:
        df: DataFrame avec les données traitées
        year: Filtre par année (optionnel)
        secteur: Filtre par secteur (optionnel)
        region: Filtre par région (optionnel)

    Returns:
        DataFrame agrégé avec colonnes: année, secteur, région, nombre_creations
    """
    logger.info("Agrégation Use Case 1: Évolution des créations")

    # Filtrer les données avec Date_Creation_Entreprise non null
    df_filtered = df[df["Date_Creation_Entreprise"].notna()].copy()

    if len(df_filtered) == 0:
        logger.warning("Aucune donnée avec Date_Creation_Entreprise valide")
        return pd.DataFrame(columns=["annee", "secteur", "region", "nombre_creations"])

    # Extraire l'année de création
    df_filtered["annee"] = df_filtered["Date_Creation_Entreprise"].apply(extract_year)
    df_filtered = df_filtered[df_filtered["annee"].notna()]

    # Extraire le secteur depuis Code_APE_Entreprise
    df_filtered["secteur"] = df_filtered["Code_APE_Entreprise"].apply(get_secteur_from_ape)

    # Appliquer les filtres
    if year is not None:
        df_filtered = df_filtered[df_filtered["annee"] == year]
    if secteur is not None:
        df_filtered = df_filtered[df_filtered["secteur"] == secteur]
    if region is not None:
        df_filtered = df_filtered[df_filtered["Region"] == region]

    # Agrégation
    result = (
        df_filtered.groupby(["annee", "secteur", "Region"], dropna=False)
        .size()
        .reset_index(name="nombre_creations")
    )
    result = result.rename(columns={"Region": "region"})

    logger.info(f"Agrégation terminée: {len(result)} groupes")
    return result


def aggregate_usecase2_sexe_dirigeants(
    df: pd.DataFrame,
    sexe: str | None = None,
    secteur: str | None = None,
    region: str | None = None,
) -> pd.DataFrame:
    """
    Use Case 2: Répartition par sexe des dirigeants selon les secteurs d'activité.

    Agrégation: COUNT(*) GROUP BY sexe, secteur, région

    Args:
        df: DataFrame avec les données traitées
        sexe: Filtre par sexe (M/F) (optionnel)
        secteur: Filtre par secteur (optionnel)
        region: Filtre par région (optionnel)

    Returns:
        DataFrame agrégé avec colonnes: sexe, secteur, région, nombre_entreprises
    """
    logger.info("Agrégation Use Case 2: Répartition par sexe dirigeants")

    # Filtrer les données avec Sexe_Dirigeant non null
    df_filtered = df[df["Sexe_Dirigeant"].notna()].copy()

    if len(df_filtered) == 0:
        logger.warning("Aucune donnée avec Sexe_Dirigeant valide")
        return pd.DataFrame(columns=["sexe", "secteur", "region", "nombre_entreprises"])

    # Extraire le secteur
    df_filtered["secteur"] = df_filtered["Code_APE_Entreprise"].apply(get_secteur_from_ape)

    # Appliquer les filtres
    if sexe is not None:
        df_filtered = df_filtered[df_filtered["Sexe_Dirigeant"] == sexe]
    if secteur is not None:
        df_filtered = df_filtered[df_filtered["secteur"] == secteur]
    if region is not None:
        df_filtered = df_filtered[df_filtered["Region"] == region]

    # Agrégation
    result = (
        df_filtered.groupby(["Sexe_Dirigeant", "secteur", "Region"], dropna=False)
        .size()
        .reset_index(name="nombre_entreprises")
    )
    result = result.rename(columns={"Sexe_Dirigeant": "sexe", "Region": "region"})

    logger.info(f"Agrégation terminée: {len(result)} groupes")
    return result


def aggregate_usecase3_effectifs(
    df: pd.DataFrame,
    secteur: str | None = None,
    region: str | None = None,
    effectif: str | None = None,
) -> pd.DataFrame:
    """
    Use Case 3: Répartition des effectifs par secteurs et territoires.

    Agrégation: COUNT(*) GROUP BY effectifs, secteur, région

    Args:
        df: DataFrame avec les données traitées
        secteur: Filtre par secteur (optionnel)
        region: Filtre par région (optionnel)
        effectif: Filtre par tranche d'effectifs (optionnel)

    Returns:
        DataFrame agrégé avec colonnes: effectifs, secteur, région, nombre_entreprises
    """
    logger.info("Agrégation Use Case 3: Répartition des effectifs")

    # Extraire le secteur
    df_filtered = df.copy()
    df_filtered["secteur"] = df_filtered["Code_APE_Entreprise"].apply(get_secteur_from_ape)

    # Appliquer les filtres
    if secteur is not None:
        df_filtered = df_filtered[df_filtered["secteur"] == secteur]
    if region is not None:
        df_filtered = df_filtered[df_filtered["Region"] == region]
    if effectif is not None:
        df_filtered = df_filtered[df_filtered["Effectifs_Entreprise"] == effectif]

    # Agrégation
    result = (
        df_filtered.groupby(["Effectifs_Entreprise", "secteur", "Region"], dropna=False)
        .size()
        .reset_index(name="nombre_entreprises")
    )
    result = result.rename(columns={"Effectifs_Entreprise": "effectifs", "Region": "region"})

    logger.info(f"Agrégation terminée: {len(result)} groupes")
    return result


def aggregate_usecase4_dominance_sectorielle(
    df: pd.DataFrame, year: int | None = None
) -> pd.DataFrame:
    """
    Use Case 4: Dominance sectorielle par région.

    Agrégation: TOP 1 secteur par région (le secteur avec le plus d'entreprises)

    Args:
        df: DataFrame avec les données traitées
        year: Filtre par année (optionnel)

    Returns:
        DataFrame avec colonnes: région, secteur_dominant, nombre_entreprises
    """
    logger.info("Agrégation Use Case 4: Dominance sectorielle")

    df_filtered = df.copy()

    # Filtrer par année si spécifié
    if year is not None:
        df_filtered["annee"] = df_filtered["Date_Creation_Entreprise"].apply(extract_year)
        df_filtered = df_filtered[df_filtered["annee"] == year]

    # Extraire le secteur
    df_filtered["secteur"] = df_filtered["Code_APE_Entreprise"].apply(get_secteur_from_ape)
    df_filtered = df_filtered[df_filtered["secteur"].notna()]

    # Compter par secteur et région
    counts = (
        df_filtered.groupby(["Region", "secteur"], dropna=False)
        .size()
        .reset_index(name="nombre_entreprises")
    )

    # Trouver le secteur dominant par région (TOP 1)
    result = (
        counts.sort_values("nombre_entreprises", ascending=False)
        .groupby("Region", dropna=False)
        .head(1)
        .reset_index(drop=True)
    )
    result = result.rename(columns={"Region": "region", "secteur": "secteur_dominant"})

    logger.info(f"Agrégation terminée: {len(result)} régions")
    return result


def aggregate_usecase5_types_juridiques(
    df: pd.DataFrame,
    secteur: str | None = None,
    region: str | None = None,
    categorie_juridique: int | None = None,
) -> pd.DataFrame:
    """
    Use Case 5: Types juridiques et catégories par secteur et région.

    Agrégation: COUNT(*) GROUP BY type_juridique, secteur, région

    Args:
        df: DataFrame avec les données traitées
        secteur: Filtre par secteur (optionnel)
        region: Filtre par région (optionnel)
        categorie_juridique: Filtre par catégorie juridique (optionnel)

    Returns:
        DataFrame agrégé avec colonnes: categorie_juridique, secteur, région, nombre_entreprises
    """
    logger.info("Agrégation Use Case 5: Types juridiques")

    df_filtered = df.copy()

    # Extraire le secteur
    df_filtered["secteur"] = df_filtered["Code_APE_Entreprise"].apply(get_secteur_from_ape)

    # Appliquer les filtres
    if secteur is not None:
        df_filtered = df_filtered[df_filtered["secteur"] == secteur]
    if region is not None:
        df_filtered = df_filtered[df_filtered["Region"] == region]
    if categorie_juridique is not None:
        df_filtered = df_filtered[df_filtered["Categorie_Juridique"] == categorie_juridique]

    # Agrégation
    result = (
        df_filtered.groupby(["Categorie_Juridique", "secteur", "Region"], dropna=False)
        .size()
        .reset_index(name="nombre_entreprises")
    )
    result = result.rename(
        columns={"Categorie_Juridique": "categorie_juridique", "Region": "region"}
    )

    logger.info(f"Agrégation terminée: {len(result)} groupes")
    return result

