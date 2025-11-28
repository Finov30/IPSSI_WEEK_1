"""Module d'agrégation des données avec PySpark pour HDFS.

Ce module utilise PySpark pour lire directement depuis HDFS et effectuer
les agrégations sans charger toutes les données en mémoire.
"""

import logging
from typing import Any

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import udf, upper, trim
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql.window import Window

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# Singleton SparkSession
_spark_session: SparkSession | None = None


def get_spark_session() -> SparkSession:
    """
    Crée et retourne une session Spark (singleton).
    
    Returns:
        SparkSession configurée pour HDFS
    """
    global _spark_session
    
    if _spark_session is None:
        settings = get_settings()
        
        # Configuration Spark pour HDFS
        # Utiliser le port RPC (8020) pour HDFS, pas le port externe (9000)
        hdfs_rpc_port = 8020 if settings.hdfs_port == 9000 else settings.hdfs_port
        hdfs_url = f"hdfs://{settings.hdfs_host}:{hdfs_rpc_port}"
        
        spark_builder = SparkSession.builder \
            .appName("sirene-dataviz") \
            .config("spark.master", "local[*]") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.hadoop.fs.defaultFS", hdfs_url) \
            .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
            .config("spark.sql.parquet.enableVectorizedReader", "true") \
            .config("spark.sql.parquet.mergeSchema", "false") \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.maxResultSize", "2g") \
            .config("spark.sql.shuffle.partitions", "100") \
            .config("spark.memory.fraction", "0.8") \
            .config("spark.memory.storageFraction", "0.3") \
            .config("spark.sql.autoBroadcastJoinThreshold", "-1")
        
        _spark_session = spark_builder.getOrCreate()
        logger.info("Session Spark créée pour HDFS")
    
    return _spark_session


def load_processed_data_spark(use_test_data: bool = False) -> Any:
    """
    Charge les données Parquet depuis HDFS avec Spark (lazy evaluation).
    
    Args:
        use_test_data: Si True, charge depuis test_100k
        
    Returns:
        DataFrame Spark (lazy, pas encore chargé en mémoire)
    """
    settings = get_settings()
    spark = get_spark_session()
    
    # Déterminer le chemin HDFS (utiliser le port RPC 8020)
    hdfs_rpc_port = 8020 if settings.hdfs_port == 9000 else settings.hdfs_port
    hdfs_base_path = settings.hdfs_path
    if use_test_data:
        hdfs_path = f"hdfs://{settings.hdfs_host}:{hdfs_rpc_port}{hdfs_base_path}/processed/test_100k"
    else:
        hdfs_path = f"hdfs://{settings.hdfs_host}:{hdfs_rpc_port}{hdfs_base_path}/processed"
    
    logger.info(f"Chargement Spark depuis HDFS: {hdfs_path}")
    
    try:
        # Lire tous les fichiers Parquet (Spark les lit en lazy, pas en mémoire)
        # Ne pas appeler count() ici car cela déclencherait une action et chargerait tout en mémoire
        df = spark.read.parquet(hdfs_path)
        logger.info(f"✓ DataFrame Spark créé depuis HDFS (lazy evaluation)")
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement Spark depuis HDFS: {e}")
        raise


def aggregate_usecase1_creations_spark(
    df: Any,
    year: int | None = None,
    secteur: str | None = None,
    region: str | None = None,
) -> list[dict[str, Any]]:
    """
    Use Case 1: Évolution des créations avec Spark.
    
    Args:
        df: DataFrame Spark
        year: Filtre par année
        secteur: Filtre par secteur
        region: Filtre par région
        
    Returns:
        Liste de dictionnaires avec les résultats agrégés
    """
    logger.info("Agrégation Spark Use Case 1: Évolution des créations")
    
    from src.utils.date_utils import extract_year as extract_year_func
    from src.utils.ape_utils import get_secteur_from_ape as get_secteur_func
    
    # Filtrer les données avec Date_Creation_Entreprise non null
    df_filtered = df.filter(F.col("Date_Creation_Entreprise").isNotNull())
    
    # Extraire l'année (UDF Python pour compatibilité)
    extract_year_udf = udf(lambda x: extract_year_func(x) if x else None, IntegerType())
    get_secteur_udf = udf(lambda x: get_secteur_func(x) if x else None, StringType())
    
    df_filtered = df_filtered.withColumn("annee", extract_year_udf(F.col("Date_Creation_Entreprise")))
    df_filtered = df_filtered.filter(F.col("annee").isNotNull())
    
    # Extraire le secteur
    df_filtered = df_filtered.withColumn("secteur", get_secteur_udf(F.col("Code_APE_Entreprise")))
    
    # Appliquer les filtres
    if year is not None:
        df_filtered = df_filtered.filter(F.col("annee") == year)
    if secteur is not None:
        df_filtered = df_filtered.filter(F.col("secteur") == secteur)
    if region is not None:
        df_filtered = df_filtered.filter(F.col("Region") == region)
    
    # Agrégation avec Spark (exécutée directement dans HDFS)
    result_df = df_filtered.groupBy("annee", "secteur", "Region") \
        .count() \
        .withColumnRenamed("count", "nombre_creations") \
        .withColumnRenamed("Region", "region") \
        .orderBy("annee", "secteur", "region")
    
    # Collecter seulement les résultats agrégés (petit volume)
    results = result_df.collect()
    
    # Convertir en liste de dictionnaires
    result_list = [
        {
            "annee": row.annee,
            "secteur": row.secteur,
            "region": row.region,
            "nombre_creations": row.nombre_creations,
        }
        for row in results
    ]
    
    logger.info(f"Agrégation Spark terminée: {len(result_list)} groupes")
    return result_list


def aggregate_usecase2_sexe_dirigeants_spark(
    df: Any,
    sexe: str | None = None,
    secteur: str | None = None,
    region: str | None = None,
) -> list[dict[str, Any]]:
    """
    Use Case 2: Répartition par sexe dirigeants avec Spark.
    
    Args:
        df: DataFrame Spark
        sexe: Filtre par sexe (M/F)
        secteur: Filtre par secteur
        region: Filtre par région
        
    Returns:
        Liste de dictionnaires avec les résultats agrégés
    """
    logger.info("Agrégation Spark Use Case 2: Répartition par sexe dirigeants")
    
    from src.utils.ape_utils import get_secteur_from_ape as get_secteur_func
    
    # Filtrer les données avec Sexe_Dirigeant non null
    df_filtered = df.filter(F.col("Sexe_Dirigeant").isNotNull())
    
    # Normaliser le sexe (M/F en majuscules)
    df_filtered = df_filtered.withColumn("Sexe_Dirigeant", upper(trim(F.col("Sexe_Dirigeant"))))
    df_filtered = df_filtered.filter(F.col("Sexe_Dirigeant").isin(["M", "F"]))
    
    # Extraire le secteur
    get_secteur_udf = udf(lambda x: get_secteur_func(x) if x else None, StringType())
    df_filtered = df_filtered.withColumn("secteur", get_secteur_udf(F.col("Code_APE_Entreprise")))
    
    # Appliquer les filtres
    if sexe is not None:
        df_filtered = df_filtered.filter(F.col("Sexe_Dirigeant") == sexe.upper())
    if secteur is not None:
        df_filtered = df_filtered.filter(F.col("secteur") == secteur)
    if region is not None:
        df_filtered = df_filtered.filter(F.col("Region") == region)
    
    # Agrégation
    result_df = df_filtered.groupBy("Sexe_Dirigeant", "secteur", "Region") \
        .count() \
        .withColumnRenamed("count", "nombre_entreprises") \
        .withColumnRenamed("Sexe_Dirigeant", "sexe") \
        .withColumnRenamed("Region", "region") \
        .orderBy("sexe", "secteur", "region")
    
    results = result_df.collect()
    result_list = [
        {
            "sexe": row.sexe,
            "secteur": row.secteur,
            "region": row.region,
            "nombre_entreprises": row.nombre_entreprises,
        }
        for row in results
    ]
    
    logger.info(f"Agrégation Spark terminée: {len(result_list)} groupes")
    return result_list


def aggregate_usecase3_effectifs_spark(
    df: Any,
    secteur: str | None = None,
    region: str | None = None,
    effectif: str | None = None,
) -> list[dict[str, Any]]:
    """
    Use Case 3: Répartition des effectifs avec Spark.
    
    Args:
        df: DataFrame Spark
        secteur: Filtre par secteur
        region: Filtre par région
        effectif: Filtre par tranche d'effectifs
        
    Returns:
        Liste de dictionnaires avec les résultats agrégés
    """
    logger.info("Agrégation Spark Use Case 3: Répartition des effectifs")
    
    from src.utils.ape_utils import get_secteur_from_ape as get_secteur_func
    
    # Extraire le secteur
    get_secteur_udf = udf(lambda x: get_secteur_func(x) if x else None, StringType())
    df_filtered = df.withColumn("secteur", get_secteur_udf(F.col("Code_APE_Entreprise")))
    
    # Appliquer les filtres
    if secteur is not None:
        df_filtered = df_filtered.filter(F.col("secteur") == secteur)
    if region is not None:
        df_filtered = df_filtered.filter(F.col("Region") == region)
    if effectif is not None:
        df_filtered = df_filtered.filter(F.col("Effectifs_Entreprise") == effectif)
    
    # Agrégation
    result_df = df_filtered.groupBy("Effectifs_Entreprise", "secteur", "Region") \
        .count() \
        .withColumnRenamed("count", "nombre_entreprises") \
        .withColumnRenamed("Effectifs_Entreprise", "effectifs") \
        .withColumnRenamed("Region", "region") \
        .orderBy("effectifs", "secteur", "region")
    
    results = result_df.collect()
    result_list = [
        {
            "effectifs": row.effectifs,
            "secteur": row.secteur,
            "region": row.region,
            "nombre_entreprises": row.nombre_entreprises,
        }
        for row in results
    ]
    
    logger.info(f"Agrégation Spark terminée: {len(result_list)} groupes")
    return result_list


def aggregate_usecase4_dominance_sectorielle_spark(
    df: Any,
    year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Use Case 4: Dominance sectorielle avec Spark.
    
    Args:
        df: DataFrame Spark
        year: Filtre par année
        
    Returns:
        Liste de dictionnaires avec les résultats agrégés
    """
    logger.info("Agrégation Spark Use Case 4: Dominance sectorielle")
    
    from src.utils.date_utils import extract_year as extract_year_func
    from src.utils.ape_utils import get_secteur_from_ape as get_secteur_func
    
    df_filtered = df
    
    # Filtrer par année si spécifié
    if year is not None:
        extract_year_udf = udf(lambda x: extract_year_func(x) if x else None, IntegerType())
        df_filtered = df_filtered.withColumn("annee", extract_year_udf(F.col("Date_Creation_Entreprise")))
        df_filtered = df_filtered.filter(F.col("annee") == year)
    
    # Extraire le secteur
    get_secteur_udf = udf(lambda x: get_secteur_func(x) if x else None, StringType())
    df_filtered = df_filtered.withColumn("secteur", get_secteur_udf(F.col("Code_APE_Entreprise")))
    df_filtered = df_filtered.filter(F.col("secteur").isNotNull())
    
    # Compter par secteur et région
    counts = df_filtered.groupBy("Region", "secteur") \
        .count() \
        .withColumnRenamed("count", "nombre_entreprises")
    
    # Trouver le secteur dominant par région (TOP 1)
    window = Window.partitionBy("Region").orderBy(F.desc("nombre_entreprises"))
    result_df = counts.withColumn("rank", F.row_number().over(window)) \
        .filter(F.col("rank") == 1) \
        .drop("rank") \
        .withColumnRenamed("Region", "region") \
        .withColumnRenamed("secteur", "secteur_dominant") \
        .orderBy("region")
    
    results = result_df.collect()
    result_list = [
        {
            "region": row.region,
            "secteur_dominant": row.secteur_dominant,
            "nombre_entreprises": row.nombre_entreprises,
        }
        for row in results
    ]
    
    logger.info(f"Agrégation Spark terminée: {len(result_list)} régions")
    return result_list


def aggregate_usecase5_types_juridiques_spark(
    df: Any,
    secteur: str | None = None,
    region: str | None = None,
    categorie_juridique: int | None = None,
) -> list[dict[str, Any]]:
    """
    Use Case 5: Types juridiques avec Spark.
    
    Args:
        df: DataFrame Spark
        secteur: Filtre par secteur
        region: Filtre par région
        categorie_juridique: Filtre par catégorie juridique
        
    Returns:
        Liste de dictionnaires avec les résultats agrégés
    """
    logger.info("Agrégation Spark Use Case 5: Types juridiques")
    
    from src.utils.ape_utils import get_secteur_from_ape as get_secteur_func
    
    # Extraire le secteur
    get_secteur_udf = udf(lambda x: get_secteur_func(x) if x else None, StringType())
    df_filtered = df.withColumn("secteur", get_secteur_udf(F.col("Code_APE_Entreprise")))
    
    # Appliquer les filtres
    if secteur is not None:
        df_filtered = df_filtered.filter(F.col("secteur") == secteur)
    if region is not None:
        df_filtered = df_filtered.filter(F.col("Region") == region)
    if categorie_juridique is not None:
        df_filtered = df_filtered.filter(F.col("Categorie_Juridique") == categorie_juridique)
    
    # Agrégation
    result_df = df_filtered.groupBy("Categorie_Juridique", "secteur", "Region") \
        .count() \
        .withColumnRenamed("count", "nombre_entreprises") \
        .withColumnRenamed("Categorie_Juridique", "categorie_juridique") \
        .withColumnRenamed("Region", "region") \
        .orderBy("categorie_juridique", "secteur", "region")
    
    results = result_df.collect()
    result_list = [
        {
            "categorie_juridique": row.categorie_juridique,
            "secteur": row.secteur,
            "region": row.region,
            "nombre_entreprises": row.nombre_entreprises,
        }
        for row in results
    ]
    
    logger.info(f"Agrégation Spark terminée: {len(result_list)} groupes")
    return result_list

