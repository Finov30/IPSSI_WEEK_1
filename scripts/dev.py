"""Script pour lancer l'environnement de developpement complet."""

import subprocess
import sys
import time
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Execute une commande."""
    print(f"[EXEC] {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def check_docker_service(service: str) -> bool:
    """Verifie si un service Docker est en cours d'execution."""
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
                print("[OK] Redis est pret")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("[WARN] Redis n'est pas encore pret, continuation...")
    return False


def wait_for_hdfs(max_wait: int = 60) -> bool:
    """Attend que HDFS soit disponible."""
    print("[WAIT] Attente de HDFS...")

    for i in range(max_wait):
        try:
            # Verifier que le container NameNode est en cours d'execution
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=sirene-hdfs-namenode", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if "Up" not in result.stdout:
                time.sleep(2)
                continue

            # Tester une operation HDFS simple
            test_cmd = [
                "docker", "exec", "sirene-hdfs-namenode",
                "hdfs", "dfs", "-ls", "/"
            ]
            test_result = subprocess.run(test_cmd, capture_output=True, check=False, timeout=10)

            if test_result.returncode == 0:
                # Verifier que le DataNode est enregistre
                report_cmd = [
                    "docker", "exec", "sirene-hdfs-namenode",
                    "hdfs", "dfsadmin", "-report"
                ]
                report_result = subprocess.run(
                    report_cmd, capture_output=True, text=True, check=False, timeout=10
                )
                if report_result.returncode == 0 and "Live datanodes" in report_result.stdout:
                    print("[OK] HDFS est pret")
                    return True

        except Exception:
            pass

        if i % 10 == 0 and i > 0:
            print(f"[WAIT] HDFS: initialisation... ({i}/{max_wait}s)")

        time.sleep(2)

    print("[WARN] HDFS n'est pas encore completement pret, continuation...")
    return False


def main() -> None:
    """Fonction principale."""
    print("=" * 60)
    print("  Demarrage de l'environnement de developpement")
    print("=" * 60)
    print()

    # Verifier que Docker est disponible
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Docker n'est pas installe ou non disponible")
        sys.exit(1)

    # 1. Demarrer les services Docker
    print("[1/4] Demarrage des services Docker (Redis, HDFS, Frontend)...")

    try:
        run_command([
            "docker-compose", "up", "-d", "--build",
            "redis", "hdfs-namenode", "hdfs-datanode", "frontend"
        ])
        print("[OK] Services Docker demarres")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erreur lors du demarrage Docker: {e}")
        sys.exit(1)

    print()

    # 2. Attendre que les services soient prets
    print("[2/4] Attente de la disponibilite des services...")
    wait_for_redis()
    wait_for_hdfs()
    time.sleep(3)
    print("[OK] Services prets")
    print()

    # 3. Verifier que le frontend est demarre
    print("[3/4] Verification du frontend...")
    if check_docker_service("sirene-frontend"):
        print("[OK] Frontend Docker demarre")
    else:
        print("[WARN] Frontend Docker non detecte, mais peut etre en cours de demarrage...")
    print()

    # 4. Afficher les informations
    print("[4/4] Informations des services:")
    print("=" * 60)
    print("  Services disponibles:")
    print("  - API: http://localhost:8001")
    print("  - Frontend: http://localhost:3000")
    print("  - Redis: localhost:6379")
    print("  - HDFS NameNode: http://localhost:9870")
    print("=" * 60)
    print()

    # 5. Lancer l'API (seulement si le port est libre, sinon on suppose qu'elle tourne dans Docker)
    api_cmd = ["uv", "run", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]

    # Verifier si le port 8001 est deja utilise
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", 8001))
        sock.close()
        if result == 0:
            print("L'API est déjà en cours d'exécution sur le port 8001.")
            print("Environnement de developpement prêt !")
            print("Pour arrêter: make dev-stop")
            
            # Boucle infinie pour garder le script actif (comme un service)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print()
                print("[INFO] Arret demande")
                sys.exit(0)
    except Exception:
        pass

    print("[INFO] Demarrage de l'API locale...")
    print("Pour arreter: make dev-stop")
    print()

    try:
        print("Appuyez sur Ctrl+C pour arreter")
        print()
        run_command(api_cmd, check=False)
    except KeyboardInterrupt:
        print()
        print("[INFO] Arret demande")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("[INFO] Arret demande")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Erreur: {e}", file=sys.stderr)
        sys.exit(1)
