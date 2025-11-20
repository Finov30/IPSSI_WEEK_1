"""Script pour lancer l'environnement de développement complet."""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Exécute une commande."""
    print(f"[EXEC] {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def check_docker_service(service: str) -> bool:
    """Vérifie si un service Docker est en cours d'exécution."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={service}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return service in result.stdout
    except Exception:
        return False


def wait_for_redis(max_wait: int = 30) -> bool:
    """Attend que Redis soit disponible."""
    print("[WAIT] Attente de Redis...")
    for i in range(max_wait):
        try:
            result = subprocess.run(
                ["docker", "exec", "sirene-redis", "redis-cli", "ping"],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                print("[OK] Redis est prêt")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("[WARN] Redis n'est pas encore prêt, continuation...")
    return False


def main() -> None:
    """Fonction principale."""
    print("=" * 60)
    print("  Démarrage de l'environnement de développement")
    print("=" * 60)
    print()

    # Vérifier que Docker est disponible
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Docker n'est pas installé ou non disponible")
        sys.exit(1)

    # 1. Démarrer les services Docker
    print("[1/4] Démarrage des services Docker (Redis, HDFS, Spark)...")
    
    # Liste des conteneurs à vérifier
    containers_to_check = [
        "sirene-hdfs-namenode",
        "sirene-hdfs-datanode",
        "sirene-spark-master",
        "sirene-spark-worker",
        "sirene-redis",
    ]
    
    try:
        # Arrêter tous les conteneurs liés à ce projet (y compris les orphelins)
        print("[INFO] Nettoyage des conteneurs existants...")
        subprocess.run(
            ["docker-compose", "down", "--remove-orphans"],
            capture_output=True,
            check=False,
        )
        
        # Vérifier et supprimer les conteneurs orphelins qui pourraient utiliser les ports
        for container_name in containers_to_check:
            # Vérifier si le conteneur existe (en cours d'exécution ou arrêté)
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if container_name in result.stdout:
                print(f"[INFO] Suppression du conteneur {container_name}...")
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    capture_output=True,
                    check=False,
                )
        
        time.sleep(2)
        
        run_command(
            [
                "docker-compose",
                "up",
                "-d",
                "redis",
                "hdfs-namenode",
                "hdfs-datanode",
                "spark-master",
                "spark-worker",
            ]
        )
        print("[OK] Services Docker démarrés")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur lors du démarrage Docker: {e}")
        print("[INFO] Tentative de nettoyage complet...")
        subprocess.run(
            ["docker-compose", "down", "--remove-orphans"],
            capture_output=True,
            check=False,
        )
        # Supprimer les conteneurs orphelins manuellement
        for container_name in containers_to_check:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                check=False,
            )
        print("[INFO] Veuillez vérifier les ports utilisés et réessayer")
        print("[INFO] Vous pouvez vérifier avec: docker ps -a | grep sirene")
        sys.exit(1)

    print()

    # 2. Attendre que les services soient prêts
    print("[2/4] Attente de la disponibilité des services...")
    wait_for_redis()
    time.sleep(3)  # Attendre un peu pour HDFS et Spark
    print("[OK] Services prêts")
    print()

    # 3. Afficher les informations
    print("[3/4] Informations des services:")
    print("=" * 60)
    print("  Services disponibles:")
    print("  - API: http://localhost:8000")
    print("  - Frontend: http://localhost:3000")
    print("  - Redis: localhost:6379")
    print("  - HDFS NameNode: http://localhost:9870")
    print("  - Spark Master: http://localhost:8080")
    print("=" * 60)
    print()

    # 4. Lancer l'API et le Frontend
    print("[4/4] Démarrage de l'API et du Frontend...")
    print()
    print("Pour arrêter: make dev-stop")
    print()

    # Lancer l'API
    print("[INFO] Démarrage de l'API sur http://localhost:8000")
    api_cmd = ["uv", "run", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    # Lancer le frontend si le dossier existe
    frontend_path = Path("src/frontend")
    if frontend_path.exists() and (frontend_path / "package.json").exists():
        print("[INFO] Démarrage du Frontend sur http://localhost:3000")
        print()
        print("⚠️  L'API et le Frontend doivent être lancés dans des terminaux séparés:")
        print()
        print("Terminal 1 (API):")
        print(f"  {' '.join(api_cmd)}")
        print()
        print("Terminal 2 (Frontend):")
        print("  cd src/frontend && npm start")
        print()
    else:
        print("[INFO] Frontend non trouvé, lancement de l'API uniquement")
        print()
        print("Pour lancer l'API, exécutez:")
        print(f"  {' '.join(api_cmd)}")
        print()

    # Option: lancer l'API directement
    try:
        print("[INFO] Lancement de l'API...")
        print("Appuyez sur Ctrl+C pour arrêter")
        print()
        run_command(api_cmd, check=False)
    except KeyboardInterrupt:
        print()
        print("[INFO] Arrêt demandé")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[INFO] Arrêt demandé")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Erreur: {e}", file=sys.stderr)
        sys.exit(1)

