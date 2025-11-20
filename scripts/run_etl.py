"""Script principal pour lancer le pipeline ETL."""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.logging import setup_logging
from src.config.settings import get_settings
from src.etl.extract import extract_csv_chunks
from src.etl.load import load_to_parquet
from src.etl.transform import transform_dataframe, validate_dataframe

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """Fonction principale du pipeline ETL."""
    settings = get_settings()

    logger.info("=" * 80)
    logger.info("DÉMARRAGE DU PIPELINE ETL")
    logger.info("=" * 80)

    # Paramètres
    chunk_size = 100000
    output_dir = Path(settings.data_processed_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Compteurs
    total_processed = 0
    total_valid = 0
    chunk_number = 0

    try:
        # Extraction et transformation par chunks
        for chunk in extract_csv_chunks(chunk_size=chunk_size):
            chunk_number += 1
            total_processed += len(chunk)

            logger.info(f"\n--- Traitement du chunk {chunk_number} ---")
            logger.info(f"Lignes dans le chunk: {len(chunk):,}")

            # Transformation
            chunk_transformed = transform_dataframe(chunk)

            # Validation
            metrics = validate_dataframe(chunk_transformed)
            logger.info(f"Métriques de qualité: {metrics}")

            total_valid += len(chunk_transformed)

            # Chargement vers Parquet
            output_file = output_dir / f"chunk_{chunk_number:04d}.parquet"
            load_to_parquet(chunk_transformed, str(output_file))

        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE ETL TERMINÉ")
        logger.info("=" * 80)
        logger.info(f"Total lignes traitées: {total_processed:,}")
        logger.info(f"Total lignes valides: {total_valid:,}")
        logger.info(f"Taux de rétention: {total_valid/total_processed*100:.2f}%")
        logger.info(f"Fichiers Parquet créés: {chunk_number}")
        logger.info(f"Répertoire de sortie: {output_dir}")

    except Exception as e:
        logger.error(f"Erreur critique dans le pipeline ETL: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

