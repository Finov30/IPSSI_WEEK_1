"""Module d'extraction des données CSV."""

import logging
from pathlib import Path
from typing import Iterator

import pandas as pd
import pyarrow.fs as pafs
from tqdm import tqdm

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def extract_csv_chunks(
    file_path: str | None = None,
    chunk_size: int = 100000,
    prefer_hdfs: bool = True,
) -> Iterator[pd.DataFrame]:
    """
    Extrait les données CSV par chunks pour gérer les gros volumes.

    Essaie d'abord de lire depuis HDFS si disponible, sinon depuis le système de fichiers local.

    Args:
        file_path: Chemin vers le fichier CSV. Si None, utilise le chemin des settings.
        chunk_size: Taille des chunks (nombre de lignes)
        prefer_hdfs: Si True, essaie de lire depuis HDFS en priorité

    Yields:
        DataFrames pandas par chunks
    """
    settings = get_settings()
    csv_path = file_path or settings.dataset_csv_path
    csv_filename = Path(csv_path).name

    # Essayer de lire depuis HDFS si demandé
    if prefer_hdfs:
        try:
            fs = pafs.HadoopFileSystem(
                host=settings.hdfs_host,
                port=settings.hdfs_port,
                user="root",
            )
            hdfs_csv_path = f"{settings.hdfs_path}/raw/{csv_filename}"

            # Vérifier si le fichier existe dans HDFS
            try:
                file_info = fs.get_file_info(hdfs_csv_path)
                if file_info.is_file:
                    logger.info(f"Extraction depuis HDFS: {hdfs_csv_path}")
                    logger.info(f"Taille: {file_info.size:,} bytes")
                    logger.info(f"Taille des chunks: {chunk_size:,} lignes")

                    # Lire depuis HDFS - télécharger temporairement ou utiliser l'URL HDFS
                    # Note: pandas ne peut pas lire directement depuis HDFS, on utilise l'URL
                    import io
                    with fs.open_input_file(hdfs_csv_path) as hdfs_file:
                        # Lire le contenu par chunks pour éviter de charger tout en mémoire
                        buffer = io.BytesIO()
                        while True:
                            chunk_data = hdfs_file.read(1024 * 1024)  # 1MB chunks
                            if not chunk_data:
                                break
                            buffer.write(chunk_data)
                        buffer.seek(0)
                        
                        # Convertir en StringIO pour pandas
                        text_buffer = io.TextIOWrapper(buffer, encoding='utf-8')
                        
                        reader = pd.read_csv(
                            text_buffer,
                            sep=",",
                            encoding="utf-8",
                            chunksize=chunk_size,
                            low_memory=False,
                            dtype={
                                "SIREN": "str",
                                "SIRET": "str",
                                "Categorie_Juridique": "str",
                            },
                            on_bad_lines="skip",
                            engine="python",  # Utiliser python engine pour StringIO
                        )

                        total_chunks = 0
                        for chunk in tqdm(reader, desc="Extraction CSV depuis HDFS"):
                            total_chunks += 1
                            logger.debug(f"Chunk {total_chunks} extrait: {len(chunk):,} lignes")
                            yield chunk

                        logger.info(f"Extraction depuis HDFS terminée: {total_chunks} chunks traités")
                        return
            except Exception as e:
                logger.debug(f"CSV non trouvé dans HDFS ({hdfs_csv_path}), tentative locale: {e}")
        except Exception as e:
            logger.debug(f"HDFS non accessible, utilisation du fichier local: {e}")

    # Fallback vers fichier local (nécessaire pour la première ingestion)
    if not Path(csv_path).exists():
        raise FileNotFoundError(
            f"Fichier CSV introuvable: {csv_path}. "
            "Assurez-vous que le fichier existe localement ou qu'il est dans HDFS."
        )

    logger.info(f"Extraction du fichier CSV local: {csv_path}")
    logger.info(f"Taille des chunks: {chunk_size:,} lignes")

    try:
        # Lecture par chunks avec types optimisés
        reader = pd.read_csv(
            csv_path,
            sep=",",
            encoding="utf-8",
            chunksize=chunk_size,
            low_memory=False,
            dtype={
                "SIREN": "str",
                "SIRET": "str",
                "Categorie_Juridique": "str",
            },
            on_bad_lines="skip",
            engine="c",
        )

        total_chunks = 0
        for chunk in tqdm(reader, desc="Extraction CSV local"):
            total_chunks += 1
            logger.debug(f"Chunk {total_chunks} extrait: {len(chunk):,} lignes")
            yield chunk

        logger.info(f"Extraction terminée: {total_chunks} chunks traités")

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}", exc_info=True)
        raise

