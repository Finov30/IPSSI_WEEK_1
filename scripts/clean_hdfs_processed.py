"""Script pour nettoyer le répertoire processed dans HDFS avant de relancer l'ETL."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings


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


def main() -> None:
    """Fonction principale."""
    print("=" * 80)
    print("  NETTOYAGE DU RÉPERTOIRE PROCESSED DANS HDFS")
    print("=" * 80)
    print()
    
    settings = get_settings()
    processed_dir = f"{settings.hdfs_path}/processed"
    
    # Lister les fichiers existants
    print(f"Vérification du répertoire: {processed_dir}")
    parquet_files = list_parquet_files(processed_dir)
    
    if not parquet_files:
        print("  ℹ Aucun fichier Parquet trouvé dans processed/")
        print("  → Aucun nettoyage nécessaire")
        return
    
    print(f"  {len(parquet_files)} fichier(s) Parquet trouvé(s):")
    for file_path in parquet_files[:10]:  # Afficher les 10 premiers
        print(f"    - {Path(file_path).name}")
    if len(parquet_files) > 10:
        print(f"    ... et {len(parquet_files) - 10} autre(s) fichier(s)")
    
    print()
    print("⚠️  ATTENTION: Cette opération va supprimer TOUS les fichiers dans processed/")
    print("   Cela est recommandé avant de relancer l'ETL pour éviter les fichiers orphelins.")
    print()
    
    response = input("Supprimer tous les fichiers dans processed/? [o/N]: ").strip().lower()
    
    if response not in ["o", "oui", "y", "yes"]:
        print("  → Opération annulée")
        return
    
    # Supprimer le répertoire processed (et tout son contenu)
    print()
    print("Suppression en cours...")
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-rm", "-r", "-f", processed_dir])
    
    if code == 0:
        print(f"  ✓ Répertoire {processed_dir} supprimé avec succès")
        print(f"  ✓ {len(parquet_files)} fichier(s) supprimé(s)")
    else:
        print(f"  ✗ Erreur lors de la suppression: {stderr}")
        sys.exit(1)
    
    # Recréer le répertoire vide
    print()
    print("Recréation du répertoire processed/...")
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-mkdir", "-p", processed_dir])
    
    if code == 0:
        print(f"  ✓ Répertoire {processed_dir} recréé")
    else:
        print(f"  ⚠ Répertoire peut-être déjà existant: {stderr}")
    
    print()
    print("=" * 80)
    print("  NETTOYAGE TERMINÉ")
    print("=" * 80)
    print()
    print("Vous pouvez maintenant relancer l'ETL:")
    print("  make run-etl-docker")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Arrêt demandé")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERREUR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

