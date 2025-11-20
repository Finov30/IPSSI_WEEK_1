"""Module d'extraction des données CSV."""

import logging
from pathlib import Path
from typing import Iterator

import pandas as pd
from tqdm import tqdm

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def extract_csv_chunks(
    file_path: str | None = None,
    chunk_size: int = 100000,
) -> Iterator[pd.DataFrame]:
    """
    Extrait les données CSV par chunks pour gérer les gros volumes.

    Args:
        file_path: Chemin vers le fichier CSV. Si None, utilise le chemin des settings.
        chunk_size: Taille des chunks (nombre de lignes)

    Yields:
        DataFrames pandas par chunks
    """
    settings = get_settings()
    csv_path = file_path or settings.dataset_csv_path

    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Fichier CSV introuvable: {csv_path}")

    logger.info(f"Extraction du fichier CSV: {csv_path}")
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
        for chunk in tqdm(reader, desc="Extraction CSV"):
            total_chunks += 1
            logger.debug(f"Chunk {total_chunks} extrait: {len(chunk):,} lignes")
            yield chunk

        logger.info(f"Extraction terminée: {total_chunks} chunks traités")

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction: {e}", exc_info=True)
        raise

