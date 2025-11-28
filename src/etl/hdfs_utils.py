"""Utilitaires pour interagir avec HDFS via WebHDFS (API REST HTTP)."""

import logging
import time
from pathlib import Path

import requests

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def _get_webhdfs_base_url() -> str:
    """Retourne l'URL de base WebHDFS."""
    settings = get_settings()
    return f"http://{settings.hdfs_host}:9870/webhdfs/v1"


def copy_csv_to_hdfs(csv_path: str | Path, hdfs_destination: str | None = None, max_retries: int = 3) -> bool:
    """
    Copie un fichier CSV vers HDFS via WebHDFS avec retry en cas d'erreur.

    Args:
        csv_path: Chemin local du fichier CSV
        hdfs_destination: Chemin de destination dans HDFS. Si None, utilise le nom du fichier.
        max_retries: Nombre de tentatives en cas d'erreur

    Returns:
        True si la copie a réussi, False sinon
    """
    settings = get_settings()
    csv_path = Path(csv_path)

    if not csv_path.exists():
        logger.error(f"Fichier CSV introuvable: {csv_path}")
        return False

    if hdfs_destination is None:
        hdfs_destination = f"{settings.hdfs_path}/raw/{csv_path.name}"

    logger.info(f"Copie du CSV vers HDFS via WebHDFS: {csv_path} -> {hdfs_destination}")

    base_url = _get_webhdfs_base_url()

    for attempt in range(max_retries):
        try:
            # Créer le répertoire parent dans HDFS
            parent_dir = "/".join(hdfs_destination.split("/")[:-1])
            if parent_dir:
                mkdir_url = f"{base_url}{parent_dir}?op=MKDIRS&user.name=root"
                requests.put(mkdir_url, timeout=30)

            # Etape 1: Obtenir l'URL de redirection vers le DataNode
            create_url = f"{base_url}{hdfs_destination}?op=CREATE&overwrite=true&user.name=root"
            response = requests.put(create_url, allow_redirects=False, timeout=30)

            if response.status_code == 307:
                # Etape 2: Envoyer le fichier en streaming au DataNode (évite OOM)
                datanode_url = response.headers["Location"]
                file_size = csv_path.stat().st_size
                logger.info(f"Upload en cours... ({file_size / 1024 / 1024:.1f} MB)")

                with open(csv_path, "rb") as f:
                    write_response = requests.put(
                        datanode_url,
                        data=f,  # Streaming - pas de chargement complet en mémoire
                        headers={
                            "Content-Type": "application/octet-stream",
                            "Content-Length": str(file_size),
                        },
                        timeout=600,  # 10 minutes pour les très gros fichiers
                    )

                if write_response.status_code == 201:
                    logger.info(f"✓ CSV copié avec succès vers HDFS: {hdfs_destination}")
                    return True
                else:
                    raise RuntimeError(f"Erreur écriture: {write_response.status_code}")
            else:
                raise RuntimeError(f"Erreur création: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.warning(f"Tentative {attempt + 1}/{max_retries}: HDFS pas encore prêt, retry dans {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Erreur lors de la copie vers HDFS: {e}")
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la copie vers HDFS: {e}", exc_info=True)
            return False

    return False


def check_hdfs_connection(max_retries: int = 3, retry_delay: int = 2) -> bool:
    """
    Vérifie si la connexion à HDFS est disponible via WebHDFS.

    Args:
        max_retries: Nombre de tentatives
        retry_delay: Délai entre les tentatives (secondes)

    Returns:
        True si HDFS est accessible, False sinon
    """
    base_url = _get_webhdfs_base_url()
    settings = get_settings()

    for attempt in range(max_retries):
        try:
            # Tester la connexion en listant la racine via WebHDFS
            url = f"{base_url}/?op=LISTSTATUS&user.name=root"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                logger.info(f"✓ Connexion HDFS OK (WebHDFS): {settings.hdfs_host}:9870")
                return True
            else:
                raise RuntimeError(f"Status: {response.status_code}")

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                logger.debug(f"Tentative {attempt + 1}/{max_retries}: HDFS pas encore prêt, retry dans {retry_delay}s...")
                time.sleep(retry_delay)
                continue
            logger.warning("✗ Connexion HDFS échouée (WebHDFS non accessible)")
            return False
        except Exception as e:
            logger.warning(f"✗ Connexion HDFS échouée: {e}")
            return False

    return False


def wait_for_datanode(max_retries: int = 30, retry_delay: int = 2) -> bool:
    """
    Attend que le DataNode soit enregistré auprès du NameNode.

    Args:
        max_retries: Nombre de tentatives (30 x 2s = 60s max)
        retry_delay: Délai entre les tentatives (secondes)

    Returns:
        True si au moins un DataNode est disponible, False sinon
    """
    settings = get_settings()
    # API JMX du NameNode pour vérifier les DataNodes
    jmx_url = f"http://{settings.hdfs_host}:9870/jmx?qry=Hadoop:service=NameNode,name=FSNamesystemState"

    logger.info("Attente de l'enregistrement du DataNode...")

    for attempt in range(max_retries):
        try:
            response = requests.get(jmx_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                beans = data.get("beans", [])
                if beans:
                    num_live_datanodes = beans[0].get("NumLiveDataNodes", 0)
                    
                    # Vérifier si on est en Safe Mode
                    # "FSState" peut être "SafeMode" ou "Operational" (ou absent dans certaines versions)
                    # Une autre façon est de vérifier le champ "Safemode" (string vide si pas en safe mode, sinon message)
                    # Mais on utilise ici une commande explicite si besoin
                    
                    if num_live_datanodes > 0:
                        logger.info(f"✓ DataNode prêt: {num_live_datanodes} DataNode(s) actif(s)")
                        return True
                    else:
                        logger.debug(f"Tentative {attempt + 1}/{max_retries}: 0 DataNode actif, retry dans {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
        except requests.exceptions.ConnectionError:
            logger.debug(f"Tentative {attempt + 1}/{max_retries}: NameNode pas encore prêt, retry dans {retry_delay}s...")
            time.sleep(retry_delay)
            continue
        except Exception as e:
            logger.debug(f"Erreur vérification DataNode: {e}")
            time.sleep(retry_delay)
            continue

    logger.warning("✗ Aucun DataNode disponible après le délai d'attente")
    return False


def wait_for_safemode_exit(max_retries: int = 30, retry_delay: int = 2) -> bool:
    """
    Attend que le NameNode sorte du Safe Mode.
    """
    settings = get_settings()
    jmx_url = f"http://{settings.hdfs_host}:9870/jmx?qry=Hadoop:service=NameNode,name=NameNodeInfo"
    
    logger.info("Vérification du Safe Mode HDFS...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(jmx_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                beans = data.get("beans", [])
                if beans:
                    safemode = beans[0].get("Safemode", "")
                    if not safemode:
                        logger.info("✓ HDFS n'est plus en Safe Mode")
                        return True
                    else:
                        logger.info(f"Tentative {attempt + 1}/{max_retries}: HDFS en Safe Mode ({safemode}), attente...")
                        time.sleep(retry_delay)
                        continue
        except Exception as e:
            logger.debug(f"Erreur vérification Safe Mode: {e}")
            time.sleep(retry_delay)
            continue
            
    logger.warning("✗ HDFS est toujours en Safe Mode après le délai d'attente")
    return False

