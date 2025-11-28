"""Script principal pour lancer le pipeline ETL."""

import logging
import subprocess
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.logging import setup_logging
from src.config.settings import get_settings
from src.etl.extract import extract_csv_chunks
from src.etl.hdfs_utils import check_hdfs_connection, wait_for_datanode, wait_for_safemode_exit
from src.etl.load import load_to_hdfs
from src.etl.transform import transform_dataframe, validate_dataframe

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


def run_docker_command(cmd: list[str], timeout: int = 30) -> tuple[str, str, int]:
    """Exécute une commande dans le container HDFS NameNode."""
    try:
        full_cmd = ["docker", "exec", "sirene-hdfs-namenode"] + cmd
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def list_parquet_files(hdfs_dir: str) -> list[str]:
    """Liste les fichiers Parquet dans un répertoire HDFS."""
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-ls", hdfs_dir])
    if code != 0:
        return []
    
    files = []
    for line in stdout.strip().split("\n"):
        if not line.strip() or line.startswith("Found"):
            continue
        
        parts = line.strip().split()
        if len(parts) >= 8 and parts[-1].endswith(".parquet"):
            files.append(parts[-1])
    
    return files


def clean_processed_directory(hdfs_path: str) -> bool:
    """Nettoie le répertoire processed dans HDFS."""
    processed_dir = f"{hdfs_path}/processed"
    
    logger.info(f"Nettoyage du répertoire {processed_dir}...")
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-rm", "-r", "-f", processed_dir])
    
    if code != 0:
        logger.error(f"Erreur lors de la suppression: {stderr}")
        return False
    
    # Recréer le répertoire vide
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-mkdir", "-p", processed_dir])
    
    if code == 0:
        logger.info(f"✓ Répertoire {processed_dir} nettoyé avec succès")
        return True
    else:
        logger.warning(f"⚠ Répertoire peut-être déjà existant: {stderr}")
        return True  # Considéré comme succès si le répertoire existe déjà


def ask_clean_processed(hdfs_path: str) -> bool:
    """Demande à l'utilisateur s'il veut nettoyer le répertoire processed."""
    processed_dir = f"{hdfs_path}/processed"
    parquet_files = list_parquet_files(processed_dir)
    
    if not parquet_files:
        logger.info(f"Aucun fichier trouvé dans {processed_dir}")
        return False
    
    logger.info("=" * 80)
    logger.info(f"⚠️  ATTENTION: {len(parquet_files)} fichier(s) Parquet trouvé(s) dans {processed_dir}")
    logger.info("=" * 80)
    
    # Afficher quelques exemples
    for file_path in parquet_files[:5]:
        logger.info(f"  - {Path(file_path).name}")
    if len(parquet_files) > 5:
        logger.info(f"  ... et {len(parquet_files) - 5} autre(s) fichier(s)")
    
    logger.info("")
    logger.info("Si vous relancez l'ETL sans nettoyer, les fichiers avec le même nom seront écrasés,")
    logger.info("mais les fichiers orphelins (si le nouveau run a moins de chunks) resteront.")
    logger.info("")
    
    # Demander confirmation (utiliser print pour que ce soit visible même avec logging)
    print("")
    print("=" * 80)
    print(f"  {len(parquet_files)} fichier(s) existant(s) dans processed/")
    print("=" * 80)
    print("")
    print("Voulez-vous nettoyer le répertoire processed avant de relancer l'ETL ?")
    print("  → Cela supprimera TOUS les fichiers existants dans processed/")
    print("")
    response = input("Nettoyer processed/ avant de continuer ? [O/n]: ").strip().lower()
    
    if response in ["", "o", "oui", "y", "yes"]:
        return True
    else:
        logger.info("Nettoyage annulé. L'ETL va continuer avec les fichiers existants.")
        return False


def main() -> None:
    """Fonction principale du pipeline ETL."""
    settings = get_settings()

    logger.info("=" * 80)
    logger.info("DÉMARRAGE DU PIPELINE ETL")
    logger.info("=" * 80)

    # Vérifier la connexion HDFS
    logger.info("Vérification de la connexion HDFS...")
    if not check_hdfs_connection():
        logger.error(
            "HDFS n'est pas accessible. "
            "Assurez-vous que HDFS est démarré: docker-compose up -d hdfs-namenode hdfs-datanode"
        )
        sys.exit(1)

    # Attendre que le DataNode soit enregistré
    if not wait_for_datanode():
        logger.error("Le DataNode n'est pas disponible. Vérifiez les logs du container hdfs-datanode.")
        sys.exit(1)
        
    # Attendre la sortie du Safe Mode
    if not wait_for_safemode_exit():
        logger.warning("HDFS semble être en Safe Mode. L'écriture pourrait échouer.")
        # On continue quand même au cas où, l'erreur sera capturée plus tard

    # Vérifier et demander si on doit nettoyer le répertoire processed
    logger.info("Vérification des fichiers existants dans processed/...")
    if ask_clean_processed(settings.hdfs_path):
        if not clean_processed_directory(settings.hdfs_path):
            logger.error("Échec du nettoyage. Arrêt de l'ETL.")
            sys.exit(1)
        logger.info("")

    # Note: La copie du CSV brut vers HDFS est désactivée car:
    # 1. Le fichier est très gros et consomme beaucoup de mémoire/temps
    # 2. L'ETL lit le CSV localement par chunks, pas besoin de le copier d'abord
    # 3. Les données transformées en Parquet seront stockées dans HDFS
    csv_path = Path(settings.dataset_csv_path)
    if not csv_path.exists():
        logger.error(f"Fichier CSV source introuvable: {csv_path}")
        sys.exit(1)
    logger.info(f"Fichier CSV source: {csv_path} ({csv_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Paramètres
    chunk_size = 100000
    hdfs_base_path = settings.hdfs_path

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

            # Chargement vers HDFS
            hdfs_output_path = f"{hdfs_base_path}/processed/chunk_{chunk_number:04d}.parquet"
            load_to_hdfs(chunk_transformed, hdfs_output_path)

        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE ETL TERMINÉ")
        logger.info("=" * 80)
        logger.info(f"Total lignes traitées: {total_processed:,}")
        logger.info(f"Total lignes valides: {total_valid:,}")
        logger.info(f"Taux de rétention: {total_valid/total_processed*100:.2f}%")
        logger.info(f"Fichiers Parquet créés: {chunk_number}")
        logger.info(f"Chemin HDFS: {hdfs_base_path}/processed")

    except Exception as e:
        logger.error(f"Erreur critique dans le pipeline ETL: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

