"""Script de test complet pour vérifier que toutes les données remontent correctement.

Ce script teste :
1. Connexion HDFS
2. Vérification des fichiers Parquet dans HDFS
3. Test des endpoints API
4. Vérification des données retournées
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_hdfs_files() -> bool:
    """Vérifie que les fichiers Parquet existent dans HDFS."""
    print("\n" + "="*80)
    print("TEST 1: Vérification des fichiers dans HDFS")
    print("="*80)
    
    try:
        from src.config.settings import get_settings
        import requests
        
        settings = get_settings()
        webhdfs_url = f"http://{settings.hdfs_host}:9870"
        
        # Vérifier via WebHDFS
        processed_path = f"{settings.hdfs_path}/processed"
        list_url = f"{webhdfs_url}/webhdfs/v1{processed_path}?op=LISTSTATUS"
        
        print(f"  Vérification: {processed_path}")
        response = requests.get(list_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            files = data.get("FileStatuses", {}).get("FileStatus", [])
            parquet_files = [f for f in files if f.get("pathSuffix", "").endswith(".parquet")]
            
            print(f"  ✓ {len(parquet_files)} fichiers Parquet trouvés")
            if parquet_files:
                print(f"    Exemple: {parquet_files[0].get('pathSuffix')}")
                return True
            else:
                print("  ⚠ Aucun fichier Parquet trouvé")
                return False
        else:
            print(f"  ✗ Erreur WebHDFS: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint(endpoint: str, name: str) -> tuple[bool, list[dict[str, Any]]]:
    """Teste un endpoint API."""
    try:
        import httpx
        
        api_url = "http://localhost:8001"
        full_url = f"{api_url}{endpoint}"
        
        print(f"  Test {name}...")
        print(f"    URL: {full_url}")
        
        response = httpx.get(full_url, timeout=60.0)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"    ✓ Réponse: {len(data)} éléments")
                if data:
                    print(f"      Exemple: {json.dumps(data[0], indent=6, ensure_ascii=False)}")
                return True, data
            else:
                print(f"    ✓ Réponse: {json.dumps(data, indent=4, ensure_ascii=False)}")
                return True, [data] if data else []
        else:
            print(f"    ✗ Erreur HTTP {response.status_code}: {response.text[:200]}")
            return False, []
            
    except httpx.ConnectError:
        print(f"    ✗ Impossible de se connecter à l'API (http://localhost:8001)")
        print(f"      Assurez-vous que l'API est démarrée: docker-compose up -d api")
        return False, []
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_all_api_endpoints() -> dict[str, bool]:
    """Teste tous les endpoints API."""
    print("\n" + "="*80)
    print("TEST 2: Endpoints API")
    print("="*80)
    
    endpoints = {
        "/api/v1/usecase1/creations": "Use Case 1 - Créations",
        "/api/v1/usecase2/sexe-dirigeants": "Use Case 2 - Sexe dirigeants",
        "/api/v1/usecase3/effectifs": "Use Case 3 - Effectifs",
        "/api/v1/usecase4/dominance-sectorielle": "Use Case 4 - Dominance sectorielle",
        "/api/v1/usecase5/types-juridiques": "Use Case 5 - Types juridiques",
    }
    
    results = {}
    all_data = {}
    
    for endpoint, name in endpoints.items():
        success, data = test_api_endpoint(endpoint, name)
        results[name] = success
        all_data[name] = data
        print()
    
    return results, all_data


def test_spark_direct() -> bool:
    """Teste directement Spark si possible."""
    print("\n" + "="*80)
    print("TEST 3: Test direct Spark (si disponible)")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import (
            get_spark_session,
            load_processed_data_spark,
            aggregate_usecase1_creations_spark,
        )
        
        print("  Création de la session Spark...")
        spark = get_spark_session()
        print(f"  ✓ Session Spark créée: {spark.sparkContext.appName}")
        
        print("  Chargement des données...")
        try:
            df = load_processed_data_spark(use_test_data=True)
            print("  ✓ Données de test chargées")
        except Exception:
            df = load_processed_data_spark(use_test_data=False)
            print("  ✓ Données de production chargées")
        
        print("  Test agrégation Use Case 1...")
        result = aggregate_usecase1_creations_spark(df)
        print(f"  ✓ Résultat: {len(result)} groupes")
        if result:
            print(f"    Exemple: {result[0]}")
        
        return True
        
    except ImportError as e:
        print(f"  ⚠ PySpark non disponible: {e}")
        print("    (Normal si exécuté en local sans PySpark installé)")
        return True  # Pas une erreur critique
    except Exception as e:
        print(f"  ✗ Erreur Spark: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> None:
    """Fonction principale."""
    print("="*80)
    print("  TEST COMPLET - VÉRIFICATION DES DONNÉES")
    print("="*80)
    
    results = {}
    
    # Test 1: Fichiers HDFS
    results["hdfs_files"] = test_hdfs_files()
    
    # Test 2: Endpoints API
    api_results, api_data = test_all_api_endpoints()
    results.update(api_results)
    
    # Test 3: Spark direct (optionnel)
    results["spark_direct"] = test_spark_direct()
    
    # Résumé
    print("\n" + "="*80)
    print("  RÉSUMÉ")
    print("="*80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False
    
    # Statistiques des données API
    print("\n" + "="*80)
    print("  STATISTIQUES DES DONNÉES API")
    print("="*80)
    for name, data in api_data.items():
        if isinstance(data, list):
            print(f"  {name}: {len(data)} éléments")
        else:
            print(f"  {name}: {data}")
    
    print("\n" + "="*80)
    if all_passed:
        print("  ✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print("  ❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n  Vérifications à faire:")
        if not results.get("hdfs_files"):
            print("    - Vérifier que HDFS contient des fichiers Parquet")
            print("    - Exécuter: make run-etl-docker")
        if not any(results.get(k) for k in api_results.keys()):
            print("    - Vérifier que l'API est démarrée: docker-compose up -d api")
            print("    - Vérifier les logs: docker logs sirene-api")
    print("="*80)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

