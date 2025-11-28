"""Script pour nettoyer les fichiers vides dans HDFS."""

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


def check_file_size(hdfs_path: str) -> int:
    """Vérifie la taille d'un fichier HDFS."""
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-du", hdfs_path])
    if code != 0:
        return -1
    
    try:
        size_str = stdout.strip().split()[0]
        return int(size_str)
    except (ValueError, IndexError):
        return -1


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
    print("  NETTOYAGE DES FICHIERS VIDES DANS HDFS")
    print("=" * 80)
    print()
    
    settings = get_settings()
    
    # 1. Vérifier le CSV
    print("[1/2] Vérification du CSV brut...")
    csv_path = f"{settings.hdfs_path}/raw/Sirene_merged_with_region.csv"
    csv_size = check_file_size(csv_path)
    
    if csv_size == 0:
        print(f"  ⚠ CSV vide détecté: {csv_path}")
        response = input("  Supprimer le CSV vide? [o/N]: ").strip().lower()
        if response in ["o", "oui", "y", "yes"]:
            stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-rm", "-f", csv_path])
            if code == 0:
                print(f"  ✓ CSV vide supprimé")
            else:
                print(f"  ✗ Erreur lors de la suppression: {stderr}")
        else:
            print("  → CSV vide conservé")
    elif csv_size > 0:
        print(f"  ✓ CSV valide: {csv_size:,} bytes")
    else:
        print(f"  ℹ CSV non trouvé")
    
    print()
    
    # 2. Vérifier les fichiers Parquet
    print("[2/2] Vérification des fichiers Parquet...")
    processed_dir = f"{settings.hdfs_path}/processed"
    parquet_files = list_parquet_files(processed_dir)
    
    if not parquet_files:
        print("  ℹ Aucun fichier Parquet trouvé")
    else:
        print(f"  {len(parquet_files)} fichier(s) Parquet trouvé(s)")
        
        empty_files = []
        valid_files = []
        
        for file_path in parquet_files:
            size = check_file_size(file_path)
            if size == 0:
                empty_files.append(file_path)
                print(f"    ⚠ {Path(file_path).name}: 0 bytes (VIDE)")
            elif size > 0:
                valid_files.append(file_path)
                print(f"    ✓ {Path(file_path).name}: {size:,} bytes")
            else:
                print(f"    ? {Path(file_path).name}: taille inconnue")
        
        if empty_files:
            print()
            print(f"  {len(empty_files)} fichier(s) vide(s) détecté(s)")
            response = input("  Supprimer les fichiers vides? [o/N]: ").strip().lower()
            if response in ["o", "oui", "y", "yes"]:
                for file_path in empty_files:
                    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-rm", "-f", file_path])
                    if code == 0:
                        print(f"  ✓ Supprimé: {Path(file_path).name}")
                    else:
                        print(f"  ✗ Erreur: {Path(file_path).name} - {stderr[:100]}")
            else:
                print("  → Fichiers vides conservés")
        else:
            print("  ✓ Tous les fichiers Parquet sont valides")
    
    print()
    print("=" * 80)
    print("  NETTOYAGE TERMINÉ")
    print("=" * 80)
    print()
    print("Pour réexécuter l'ETL après nettoyage:")
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

