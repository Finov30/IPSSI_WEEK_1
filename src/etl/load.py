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

