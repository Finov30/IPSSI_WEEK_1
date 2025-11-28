"""Script de test pour l'ETL avec le fichier 100k.csv."""

import logging
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.logging import setup_logging
from src.config.settings import get_settings
from src.etl.extract import extract_csv_chunks
from src.etl.transform import transform_dataframe, validate_dataframe


def save_to_local_parquet(df: pd.DataFrame, output_path: str) -> None:
    """Sauvegarde un DataFrame vers un fichier Parquet local (pour les tests)."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, output_path, compression="snappy")

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def test_etl_100k() -> None:
    """Test du pipeline ETL avec le fichier 100k.csv."""
    settings = get_settings()

    # Utiliser le fichier 100k.csv pour le test
    test_csv_path = Path("old_dataset/100k.csv")
    if not test_csv_path.exists():
        logger.error(f"Fichier de test introuvable: {test_csv_path}")
        logger.info("Assurez-vous que le fichier 100k.csv existe dans old_dataset/")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("TEST ETL AVEC 100K.CSV")
    logger.info("=" * 80)
    logger.info(f"Fichier source: {test_csv_path}")
    logger.info(f"Taille du fichier: {test_csv_path.stat().st_size / 1024 / 1024:.2f} MB")

    # Répertoire de sortie pour le test
    output_dir = Path(settings.data_processed_path) / "test_100k"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Nettoyer les anciens fichiers de test
    for old_file in output_dir.glob("*.parquet"):
        old_file.unlink()
        logger.info(f"Fichier supprimé: {old_file}")

    # Paramètres
    chunk_size = 100000
    total_processed = 0
    total_valid = 0
    chunk_number = 0

    # Statistiques détaillées
    stats = {
        "total_lignes_initiales": 0,
        "lignes_apres_filtrage_radiees": 0,
        "lignes_finales": 0,
        "entreprises_radiees_exclues": 0,
        "colonnes_supprimees": 0,
        "fichiers_parquet_crees": 0,
    }

    try:
        # Extraction et transformation par chunks
        logger.info("\n" + "-" * 80)
        logger.info("DÉBUT DU TRAITEMENT")
        logger.info("-" * 80)

        for chunk in extract_csv_chunks(file_path=str(test_csv_path), chunk_size=chunk_size):
            chunk_number += 1
            total_processed += len(chunk)
            stats["total_lignes_initiales"] += len(chunk)

            logger.info(f"\n{'='*80}")
            logger.info(f"CHUNK {chunk_number}")
            logger.info(f"{'='*80}")
            logger.info(f"Lignes dans le chunk: {len(chunk):,}")

            # Vérifier les entreprises radiées avant transformation
            if "Etat_Administratif_Entreprise" in chunk.columns:
                radiees_avant = (chunk["Etat_Administratif_Entreprise"] == "C").sum()
                logger.info(f"Entreprises radiées dans le chunk: {radiees_avant:,}")

            # Transformation
            logger.info("Transformation en cours...")
            chunk_transformed = transform_dataframe(chunk)
            stats["lignes_finales"] += len(chunk_transformed)
            total_valid += len(chunk_transformed)

            # Calculer les statistiques
            if "Etat_Administratif_Entreprise" in chunk.columns:
                radiees_exclues = len(chunk) - len(chunk_transformed)
                stats["entreprises_radiees_exclues"] += radiees_exclues
                logger.info(f"Entreprises radiées exclues: {radiees_exclues:,}")

            # Validation
            logger.info("Validation en cours...")
            metrics = validate_dataframe(chunk_transformed)
            logger.info(f"Métriques de qualité:")
            logger.info(f"  - Total lignes: {metrics['total_rows']:,}")
            logger.info(f"  - Total colonnes: {metrics['total_columns']}")
            logger.info(f"  - Entreprises radiées restantes: {metrics.get('entreprises_radiees', 0)}")

            # Vérifier quelques colonnes importantes
            if len(chunk_transformed) > 0:
                logger.info("\nAperçu des données transformées:")
                logger.info(f"  - Colonnes: {list(chunk_transformed.columns)[:5]}...")
                logger.info(f"  - Régions uniques: {chunk_transformed['Region'].nunique() if 'Region' in chunk_transformed.columns else 'N/A'}")
                logger.info(
                    f"  - Codes APE uniques: {chunk_transformed['Code_APE_Entreprise'].nunique() if 'Code_APE_Entreprise' in chunk_transformed.columns else 'N/A'}"
                )

            # Chargement vers Parquet
            output_file = output_dir / f"chunk_{chunk_number:04d}.parquet"
            logger.info(f"\nSauvegarde vers: {output_file}")
            save_to_local_parquet(chunk_transformed, str(output_file))
            stats["fichiers_parquet_crees"] += 1

            # Vérifier le fichier créé
            file_size = output_file.stat().st_size / 1024 / 1024
            logger.info(f"✓ Fichier créé: {file_size:.2f} MB")

        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("RÉSUMÉ DU TEST ETL")
        logger.info("=" * 80)
        logger.info(f"Total lignes initiales: {stats['total_lignes_initiales']:,}")
        logger.info(f"Total lignes après filtrage: {stats['lignes_finales']:,}")
        logger.info(f"Entreprises radiées exclues: {stats['entreprises_radiees_exclues']:,}")
        logger.info(f"Taux de rétention: {stats['lignes_finales']/stats['total_lignes_initiales']*100:.2f}%")
        logger.info(f"Fichiers Parquet créés: {stats['fichiers_parquet_crees']}")
        logger.info(f"Répertoire de sortie: {output_dir}")

        # Vérifications supplémentaires
        logger.info("\n" + "-" * 80)
        logger.info("VÉRIFICATIONS")
        logger.info("-" * 80)

        # Vérifier qu'aucune entreprise radiée n'est présente
        all_data = pd.concat([pd.read_parquet(f) for f in output_dir.glob("*.parquet")], ignore_index=True)
        if "Etat_Administratif_Entreprise" in all_data.columns:
            radiees_restantes = (all_data["Etat_Administratif_Entreprise"] == "C").sum()
            if radiees_restantes == 0:
                logger.info("✓ Aucune entreprise radiée dans les données finales")
            else:
                logger.warning(f"⚠ {radiees_restantes} entreprises radiées encore présentes!")

        # Vérifier les colonnes supprimées
        colonnes_a_supprimer = [
            "Enseigne_Etablissement",
            "Denomination_Usuelle_Etablissement",
            "Statut_Diffusion",
            "Employeur_Entreprise",
            "Prenom_Dirigeant",
            "Nom_Dirigeant",
        ]
        colonnes_presentes = [col for col in colonnes_a_supprimer if col in all_data.columns]
        if not colonnes_presentes:
            logger.info("✓ Toutes les colonnes inutiles ont été supprimées")
        else:
            logger.warning(f"⚠ Colonnes non supprimées: {colonnes_presentes}")

        # Vérifier la gestion des nulls
        if "Effectifs_Entreprise" in all_data.columns:
            nulls_effectifs = all_data["Effectifs_Entreprise"].isna().sum()
            if nulls_effectifs == 0:
                logger.info("✓ Tous les effectifs nulls ont été remplacés par 'NN'")
            else:
                logger.warning(f"⚠ {nulls_effectifs} effectifs nulls restants")

        # Statistiques sur les données
        logger.info("\n" + "-" * 80)
        logger.info("STATISTIQUES SUR LES DONNÉES FINALES")
        logger.info("-" * 80)
        logger.info(f"Total lignes: {len(all_data):,}")
        logger.info(f"Total colonnes: {len(all_data.columns)}")
        if "Region" in all_data.columns:
            logger.info(f"Régions uniques: {all_data['Region'].nunique()}")
            logger.info(f"Régions: {sorted(all_data['Region'].dropna().unique())[:5]}...")
        if "Code_APE_Entreprise" in all_data.columns:
            logger.info(f"Codes APE uniques: {all_data['Code_APE_Entreprise'].nunique()}")

        logger.info("\n" + "=" * 80)
        logger.info("✓ TEST ETL TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 80)
        logger.info(f"\nLes données traitées sont disponibles dans: {output_dir}")
        logger.info("Vous pouvez maintenant tester les routes API avec ces données.")

    except Exception as e:
        logger.error(f"Erreur critique dans le test ETL: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    test_etl_100k()

