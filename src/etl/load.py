"""Module de chargement des donnees vers HDFS en format Parquet via WebHDFS."""

import io
import logging
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def _get_webhdfs_base_url() -> str:
    """Retourne l'URL de base WebHDFS."""
    settings = get_settings()
    # WebHDFS utilise le port 9870 (Web UI) avec le endpoint /webhdfs/v1
    return f"http://{settings.hdfs_host}:9870/webhdfs/v1"


def _create_hdfs_directory(path: str) -> None:
    """Cree un repertoire dans HDFS via WebHDFS."""
    base_url = _get_webhdfs_base_url()
    url = f"{base_url}{path}?op=MKDIRS&user.name=root"
    response = requests.put(url, timeout=30)
    if response.status_code == 200:
        logger.info(f"Repertoire HDFS cree: {path}")
    else:
        logger.debug(f"Creation repertoire HDFS: {response.status_code} - {response.text}")


def _write_file_to_hdfs(hdfs_path: str, data: bytes) -> None:
    """Ecrit un fichier dans HDFS via WebHDFS (protocole en 2 etapes)."""
    base_url = _get_webhdfs_base_url()

    # Etape 1: Obtenir l'URL de redirection vers le DataNode
    create_url = f"{base_url}{hdfs_path}?op=CREATE&overwrite=true&user.name=root"
    response = requests.put(create_url, allow_redirects=False, timeout=30)

    if response.status_code == 307:
        # Etape 2: Ecrire les donnees vers le DataNode
        datanode_url = response.headers["Location"]
        write_response = requests.put(
            datanode_url,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
            timeout=120,
        )
        if write_response.status_code == 201:
            logger.info(f"Fichier ecrit dans HDFS: {hdfs_path}")
        else:
            raise RuntimeError(f"Erreur ecriture HDFS: {write_response.status_code} - {write_response.text}")
    else:
        raise RuntimeError(f"Erreur creation fichier HDFS: {response.status_code} - {response.text}")


def load_to_hdfs(
    df: pd.DataFrame,
    hdfs_path: str,
    partition_cols: Optional[list[str]] = None,
    compression: str = "snappy",
) -> None:
    """
    Charge un DataFrame vers HDFS en format Parquet via WebHDFS.

    Utilise l'API REST WebHDFS (HTTP) - pas besoin de librairies Hadoop natives.

    Args:
        df: DataFrame a sauvegarder
        hdfs_path: Chemin HDFS (ex: /sirene_data/processed/chunk_0001.parquet)
        partition_cols: Non supporte avec WebHDFS (ignore)
        compression: Type de compression (snappy, gzip, zstd)

    Raises:
        ConnectionError: Si HDFS n'est pas accessible
    """
    logger.info(f"Chargement vers HDFS (WebHDFS): {hdfs_path}")
    logger.info(f"Nombre de lignes: {len(df):,}")

    if partition_cols:
        logger.warning("Le partitionnement n'est pas supporte avec WebHDFS, ignore.")

    try:
        # Creer le repertoire parent
        parent_dir = "/".join(hdfs_path.split("/")[:-1]) if "/" in hdfs_path else "/"
        if parent_dir:
            _create_hdfs_directory(parent_dir)

        # Convertir le DataFrame en Parquet en memoire
        table = pa.Table.from_pandas(df)
        buffer = io.BytesIO()
        pq.write_table(
            table,
            buffer,
            compression=compression,
            use_dictionary=True,
            write_statistics=True,
        )
        parquet_data = buffer.getvalue()

        # S'assurer que le chemin se termine par .parquet
        if not hdfs_path.endswith(".parquet"):
            hdfs_path = f"{hdfs_path.rstrip('/')}.parquet"

        # Ecrire vers HDFS via WebHDFS
        _write_file_to_hdfs(hdfs_path, parquet_data)

        logger.info(f"Donnees chargees avec succes dans HDFS: {hdfs_path} ({len(parquet_data) / 1024 / 1024:.2f} MB)")

    except requests.exceptions.ConnectionError as e:
        error_msg = (
            "HDFS n'est pas accessible via WebHDFS. "
            "Assurez-vous que HDFS est demarre: docker-compose up -d hdfs-namenode hdfs-datanode"
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except Exception as e:
        logger.error(f"Erreur lors du chargement HDFS: {e}", exc_info=True)
        raise
