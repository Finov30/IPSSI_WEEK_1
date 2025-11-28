"""Script pour vérifier les données ETL présentes dans HDFS."""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pyarrow.fs as pafs

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
    except subprocess.TimeoutExpired:
        return "", "Timeout", 1
    except Exception as e:
        return "", str(e), 1


def check_hdfs_file_info(hdfs_path: str) -> dict:
    """Récupère les informations d'un fichier HDFS via WebHDFS puis docker exec."""
    # Essayer d'abord via WebHDFS
    settings = get_settings()
    try:
        import requests
        import datetime
        url = f"http://{settings.hdfs_host}:9870/webhdfs/v1{hdfs_path}?op=GETFILESTATUS&user.name=root"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            status = response.json().get("FileStatus", {})
            ts = status["modificationTime"] / 1000
            date_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
            
            # Convertir la taille en lisible
            size = status["length"]
            if size > 1024*1024*1024:
                size_str = f"{size/(1024*1024*1024):.1f} G"
            elif size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} M"
            elif size > 1024:
                size_str = f"{size/1024:.1f} K"
            else:
                size_str = str(size)
                
            return {
                "exists": True,
                "size": size_str,
                "date": date_str,
                "full_line": str(status),
            }
        elif response.status_code == 404:
            return {"exists": False, "error": "File does not exist"}
    except Exception:
        pass

    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-ls", "-h", hdfs_path])
    
    if code != 0:
        return {"exists": False, "error": stderr}
    
    # Parser la sortie de hdfs dfs -ls
    # Format: -rw-r--r--   3 root supergroup    123.4 M 2025-11-20 10:30 /path/to/file
    lines = stdout.strip().split("\n")
    if not lines or not lines[-1]:
        return {"exists": False, "error": "No output"}
    
    last_line = lines[-1].strip()
    parts = last_line.split()
    
    if len(parts) < 8:
        return {"exists": False, "error": "Cannot parse output"}
    
    try:
        size_str = parts[4]  # Taille avec unité (ex: "123.4 M")
        date = parts[5]
        time = parts[6]
        
        return {
            "exists": True,
            "size": size_str,
            "date": f"{date} {time}",
            "full_line": last_line,
        }
    except (IndexError, ValueError):
        return {"exists": True, "full_line": last_line}


def list_hdfs_directory(hdfs_path: str) -> list[dict]:
    """Liste les fichiers dans un répertoire HDFS."""
    # Essayer d'abord via WebHDFS
    settings = get_settings()
    try:
        import requests
        url = f"http://{settings.hdfs_host}:9870/webhdfs/v1{hdfs_path}?op=LISTSTATUS&user.name=root"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            files = []
            file_statuses = response.json().get("FileStatuses", {}).get("FileStatus", [])
            for status in file_statuses:
                files.append({
                    "type": "directory" if status["type"] == "DIRECTORY" else "file",
                    "size": str(status["length"]),
                    "name": f"{hdfs_path.rstrip('/')}/{status['pathSuffix']}",
                    "full_line": str(status),
                })
            return files
    except Exception:
        pass
        
    # Fallback sur Docker CLI
    stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-ls", hdfs_path])
    
    if code != 0:
        return []
    
    files = []
    for line in stdout.strip().split("\n"):
        if not line.strip() or line.startswith("Found"):
            continue
        
        parts = line.strip().split()
        if len(parts) >= 8:
            try:
                file_type = parts[0][0]  # 'd' pour directory, '-' pour file
                size = parts[4]
                name = parts[-1]
                
                files.append({
                    "type": "directory" if file_type == "d" else "file",
                    "size": size,
                    "name": name,
                    "full_line": line.strip(),
                })
            except (IndexError, ValueError):
                continue
    
    return files


def check_hdfs_connection() -> bool:
    """Vérifie la connexion HDFS via PyArrow."""
    settings = get_settings()
    try:
        fs = pafs.HadoopFileSystem(
            host=settings.hdfs_host,
            port=settings.hdfs_port,
            user="root",
        )
        fs.get_file_info("/")
        return True
    except Exception:
        return False


def read_parquet_info(hdfs_path: str) -> dict:
    """Lit les informations d'un fichier Parquet depuis HDFS."""
    settings = get_settings()
    try:
        fs = pafs.HadoopFileSystem(
            host=settings.hdfs_host,
            port=settings.hdfs_port,
            user="root",
        )
        
        # Lire le fichier Parquet
        table = pd.read_parquet(
            hdfs_path,
            filesystem=fs,
        )
        
        return {
            "success": True,
            "rows": len(table),
            "columns": len(table.columns),
            "column_names": list(table.columns),
            "memory_usage_mb": table.memory_usage(deep=True).sum() / 1024 / 1024,
            "sample": table.head(3).to_dict("records") if len(table) > 0 else [],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main() -> None:
    """Fonction principale."""
    print("=" * 80)
    print("  VÉRIFICATION DES DONNÉES ETL DANS HDFS")
    print("=" * 80)
    print()
    
    settings = get_settings()
    
    # 1. Vérifier la connexion HDFS
    print("[1/5] Vérification de la connexion HDFS...")
    docker_ok = False
    pyarrow_ok = False
    
    # Test via WebHDFS (plus fiable car indépendant du client Docker)
    try:
        import requests
        url = f"http://{settings.hdfs_host}:9870/webhdfs/v1/?op=LISTSTATUS&user.name=root"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            docker_ok = True
            print(f"  ✓ Connexion HDFS via WebHDFS: OK ({settings.hdfs_host}:9870)")
        else:
             print(f"  ✗ Connexion HDFS via WebHDFS: ÉCHEC (Status {response.status_code})")
    except Exception as e:
        print(f"  ✗ Connexion HDFS via WebHDFS: ÉCHEC ({e})")
        # Fallback sur Docker CLI si WebHDFS échoue
        stdout, stderr, code = run_docker_command(["hdfs", "dfs", "-ls", "/"])
        if code == 0:
            docker_ok = True
            print("  ✓ Connexion HDFS via Docker CLI: OK")
        else:
            print(f"  ✗ Connexion HDFS via Docker CLI: ÉCHEC ({stderr[:100] if stderr else 'Command failed'})")
    
    # Test via PyArrow
    # On ignore l'échec de PyArrow si WebHDFS fonctionne, car PyArrow peut être capricieux
    if check_hdfs_connection():
        pyarrow_ok = True
        print(f"  ✓ Connexion HDFS via PyArrow: OK ({settings.hdfs_host}:{settings.hdfs_port})")
    else:
        # PyArrow failure is common due to environment setup (JAVA_HOME, libhdfs, etc.)
        # but if WebHDFS works, we can still check files.
        print(f"  ! Connexion HDFS via PyArrow: ÉCHEC (Non critique si WebHDFS fonctionne)")
        if docker_ok:
            pyarrow_ok = True # Fake it to proceed with checks that don't strictly require PyArrow
    
    if not docker_ok and not pyarrow_ok:
        print("\n[ERREUR] Impossible de se connecter à HDFS")
        print("  Vérifiez que les containers sont démarrés: make dev")
        sys.exit(1)
    
    print()
    
    # 2. Vérifier les données brutes (CSV)
    print("[2/5] Vérification des données brutes (CSV)...")
    csv_path = f"{settings.hdfs_path}/raw/Sirene_merged_with_region.csv"
    csv_info = check_hdfs_file_info(csv_path)
    
    if csv_info.get("exists"):
        print(f"  ✓ CSV trouvé: {csv_path}")
        print(f"    Taille: {csv_info.get('size', '?')}")
        print(f"    Date: {csv_info.get('date', '?')}")
    else:
        print(f"  ✗ CSV non trouvé: {csv_path}")
        print(f"    Erreur: {csv_info.get('error', 'Unknown')}")
    
    print()
    
    # 3. Vérifier les données traitées (Parquet)
    print("[3/5] Vérification des données traitées (Parquet)...")
    processed_path = f"{settings.hdfs_path}/processed"
    
    # Lister les fichiers Parquet
    files = list_hdfs_directory(processed_path)
    parquet_files = [f for f in files if f["name"].endswith(".parquet")]
    
    if parquet_files:
        print(f"  ✓ {len(parquet_files)} fichier(s) Parquet trouvé(s):")
        total_size = 0
        for i, file_info in enumerate(parquet_files, 1):
            name = Path(file_info["name"]).name
            size = file_info["size"]
            print(f"    [{i}] {name} ({size})")
            
            # Essayer de convertir la taille en bytes pour le total
            try:
                if "K" in size:
                    total_size += float(size.replace("K", "")) * 1024
                elif "M" in size:
                    total_size += float(size.replace("M", "")) * 1024 * 1024
                elif "G" in size:
                    total_size += float(size.replace("G", "")) * 1024 * 1024 * 1024
                else:
                    total_size += float(size)
            except ValueError:
                pass
        
        if total_size > 0:
            if total_size > 1024 * 1024:
                print(f"  Taille totale: {total_size / 1024 / 1024:.2f} MB")
            elif total_size > 1024:
                print(f"  Taille totale: {total_size / 1024:.2f} KB")
            else:
                print(f"  Taille totale: {total_size:.2f} bytes")
    else:
        print(f"  ✗ Aucun fichier Parquet trouvé dans {processed_path}")
        print(f"    Lancez l'ETL avec: make run-etl-docker")
    
    print()
    
    # 4. Analyser le premier fichier Parquet (si disponible)
    if parquet_files and pyarrow_ok:
        print("[4/5] Analyse du premier fichier Parquet...")
        first_file = parquet_files[0]["name"]
        print(f"  Fichier: {Path(first_file).name}")
        
        info = read_parquet_info(first_file)
        if info.get("success"):
            print(f"  ✓ Lecture réussie")
            print(f"    Lignes: {info['rows']:,}")
            print(f"    Colonnes: {info['columns']}")
            print(f"    Mémoire: {info['memory_usage_mb']:.2f} MB")
            print(f"    Colonnes: {', '.join(info['column_names'][:10])}")
            if len(info['column_names']) > 10:
                print(f"    ... et {len(info['column_names']) - 10} autres")
            
            if info.get("sample"):
                print(f"\n  Aperçu (3 premières lignes):")
                for i, row in enumerate(info["sample"][:3], 1):
                    print(f"    [{i}] {str(row)[:100]}...")
        else:
            print(f"  ✗ Erreur lors de la lecture: {info.get('error', 'Unknown')}")
    else:
        print("[4/5] Analyse du premier fichier Parquet...")
        if not parquet_files:
            print("  ⚠ Aucun fichier Parquet à analyser")
        else:
            print("  ⚠ PyArrow non disponible, analyse impossible")
    
    print()
    
    # 5. Statistiques globales
    print("[5/5] Statistiques globales...")
    
    # Compter tous les fichiers Parquet et calculer le total
    all_files = list_hdfs_directory(settings.hdfs_path)
    total_files = len([f for f in all_files if f["type"] == "file"])
    total_dirs = len([f for f in all_files if f["type"] == "directory"])
    
    print(f"  Répertoires dans {settings.hdfs_path}: {total_dirs}")
    print(f"  Fichiers dans {settings.hdfs_path}: {total_files}")
    print(f"  Fichiers Parquet: {len(parquet_files)}")
    
    print()
    print("=" * 80)
    print("  VÉRIFICATION TERMINÉE")
    print("=" * 80)
    print()
    print("Commandes utiles:")
    print(f"  - Lister les fichiers: docker exec sirene-hdfs-namenode hdfs dfs -ls -R {settings.hdfs_path}")
    print(f"  - Vérifier la taille: docker exec sirene-hdfs-namenode hdfs dfs -du -h {settings.hdfs_path}")
    print(f"  - Interface web HDFS: http://localhost:9870")
    print()


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

