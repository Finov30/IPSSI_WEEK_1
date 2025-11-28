"""Module d'agrégation des données par use case."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.fs as pafs

from src.config.settings import get_settings
from src.utils.ape_utils import get_secteur_from_ape
from src.utils.date_utils import extract_year

logger = logging.getLogger(__name__)


def _get_hdfs_filesystem() -> pafs.HadoopFileSystem | None:
    """
    Crée et retourne une connexion au système de fichiers HDFS.

    Returns:
        Instance de HadoopFileSystem ou None si la connexion échoue
    """
    settings = get_settings()
    try:
        fs = pafs.HadoopFileSystem(
            host=settings.hdfs_host,
            port=settings.hdfs_port,
            user="root",
        )
        return fs
    except Exception as e:
        logger.debug(f"Connexion HDFS non disponible: {e}")
        return None


def load_processed_data(data_path: str | None = None, use_test_data: bool = False) -> pd.DataFrame:
    """
    Charge les données traitées depuis HDFS UNIQUEMENT.

    Cette fonction ne fait PAS de fallback vers le stockage local.
    HDFS doit être disponible et les données doivent y être présentes.

    Args:
        data_path: Ignoré (conservé pour compatibilité). Les données viennent toujours de HDFS.
        use_test_data: Si True, charge les données de test (test_100k) en priorité.

    Returns:
        DataFrame avec toutes les données traitées depuis HDFS

    Raises:
        ConnectionError: Si HDFS n'est pas accessible
        FileNotFoundError: Si aucune donnée n'est trouvée dans HDFS
    """
    settings = get_settings()

    # Obtenir la connexion HDFS (obligatoire)
    fs = _get_hdfs_filesystem()
    if fs is None:
        error_msg = (
            "HDFS n'est pas accessible. "
            "Assurez-vous que HDFS est démarré: docker-compose up -d hdfs-namenode hdfs-datanode"
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg)

    # Déterminer le chemin HDFS
    hdfs_base_path = settings.hdfs_path
    if use_test_data:
        hdfs_path = f"{hdfs_base_path}/processed/test_100k"
    else:
        hdfs_path = f"{hdfs_base_path}/processed"

    logger.info(f"Chargement depuis HDFS: {hdfs_path}")

    try:
        # Lister les fichiers Parquet dans HDFS
        file_infos = fs.get_file_info(pafs.FileSelector(hdfs_path, recursive=True))
        parquet_files = [
            info.path
            for info in file_infos
            if info.is_file and info.path.endswith(".parquet")
        ]

        if not parquet_files:
            error_msg = (
                f"Aucun fichier Parquet trouvé dans HDFS: {hdfs_path}. "
                "Lancez 'make run-etl' pour traiter les données et les charger dans HDFS."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Trouvé {len(parquet_files)} fichiers Parquet dans HDFS")
        
        # Optimisation: charger en parallèle avec ThreadPoolExecutor pour accélérer
        from concurrent.futures import ThreadPoolExecutor, as_completed
        dfs = []
        loaded_count = 0
        
        def load_parquet_file(hdfs_file: str) -> tuple[str, pd.DataFrame | None]:
            """Charge un fichier Parquet depuis HDFS."""
            try:
                df = pd.read_parquet(hdfs_file, filesystem=fs)
                return hdfs_file, df
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {hdfs_file} depuis HDFS: {e}")
                return hdfs_file, None
        
        # Charger les fichiers en parallèle (max 10 workers pour éviter la surcharge)
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_file = {executor.submit(load_parquet_file, hdfs_file): hdfs_file for hdfs_file in parquet_files}
            
            for future in as_completed(future_to_file):
                hdfs_file, df = future.result()
                if df is not None:
                    dfs.append(df)
                    loaded_count += 1
                    if loaded_count % 50 == 0:
                        logger.info(f"Chargement en cours: {loaded_count}/{len(parquet_files)} fichiers...")

        if not dfs:
            error_msg = "Aucune donnée n'a pu être chargée depuis HDFS"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        result = pd.concat(dfs, ignore_index=True)
        logger.info(f"✓ Données chargées depuis HDFS: {len(result):,} lignes depuis {len(dfs)} fichiers")
        return result

    except (FileNotFoundError, ConnectionError):
        # Re-lancer les erreurs critiques
        raise
    except Exception as e:
        error_msg = f"Erreur lors de la lecture depuis HDFS: {e}"
        logger.error(error_msg, exc_info=True)
        raise ConnectionError(error_msg) from e


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

    # Normaliser les valeurs de sexe (M, F en majuscules, supprimer espaces)
    df_filtered["Sexe_Dirigeant"] = df_filtered["Sexe_Dirigeant"].astype(str).str.strip().str.upper()
    # Filtrer uniquement M et F valides
    df_filtered = df_filtered[df_filtered["Sexe_Dirigeant"].isin(["M", "F"])]

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

