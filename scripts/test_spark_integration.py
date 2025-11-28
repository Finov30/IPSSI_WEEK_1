"""Script de test complet pour vérifier l'intégration Spark avec HDFS.

Ce script teste :
1. Connexion HDFS
2. Session Spark
3. Chargement des données depuis HDFS
4. Tous les use cases avec Spark
5. Vérification des résultats
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_hdfs_connection() -> bool:
    """Teste la connexion HDFS."""
    print("\n" + "="*80)
    print("TEST 1: Connexion HDFS")
    print("="*80)
    
    try:
        from src.config.settings import get_settings
        from src.etl.hdfs_utils import check_hdfs_connection
        
        settings = get_settings()
        print(f"  HDFS Host: {settings.hdfs_host}")
        print(f"  HDFS Port: {settings.hdfs_port}")
        print(f"  HDFS Path: {settings.hdfs_path}")
        
        if check_hdfs_connection():
            print("  ✓ Connexion HDFS: OK")
            return True
        else:
            print("  ✗ Connexion HDFS: ÉCHEC")
            return False
    except Exception as e:
        print(f"  ✗ Erreur connexion HDFS: {e}")
        return False


def test_spark_session() -> bool:
    """Teste la création de la session Spark."""
    print("\n" + "="*80)
    print("TEST 2: Session Spark")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import get_spark_session
        
        spark = get_spark_session()
        print(f"  ✓ Session Spark créée")
        print(f"    App Name: {spark.sparkContext.appName}")
        print(f"    Master: {spark.sparkContext.master}")
        print(f"    Default FS: {spark.sparkContext.getConf().get('spark.hadoop.fs.defaultFS', 'N/A')}")
        return True
    except Exception as e:
        print(f"  ✗ Erreur création session Spark: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_data_spark() -> tuple[bool, Any]:
    """Teste le chargement des données avec Spark."""
    print("\n" + "="*80)
    print("TEST 3: Chargement des données Spark depuis HDFS")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import load_processed_data_spark
        
        # Essayer d'abord les données de test
        try:
            print("  Tentative de chargement depuis test_100k...")
            df = load_processed_data_spark(use_test_data=True)
            print("  ✓ Données de test chargées (lazy)")
            return True, df
        except Exception as e:
            print(f"  Données de test non disponibles: {e}")
            print("  Tentative de chargement depuis données de production...")
            df = load_processed_data_spark(use_test_data=False)
            print("  ✓ Données de production chargées (lazy)")
            return True, df
    except Exception as e:
        print(f"  ✗ Erreur chargement données Spark: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_usecase1(spark_df: Any) -> bool:
    """Teste le Use Case 1 avec Spark."""
    print("\n" + "="*80)
    print("TEST 4: Use Case 1 - Évolution des créations")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import aggregate_usecase1_creations_spark
        
        print("  Test sans filtres...")
        result = aggregate_usecase1_creations_spark(spark_df)
        print(f"  ✓ Résultat: {len(result)} groupes")
        if result:
            print(f"    Exemple: {result[0]}")
        else:
            print("    ⚠ Aucun résultat")
            return False
        
        print("  Test avec filtre année=2020...")
        result_filtered = aggregate_usecase1_creations_spark(spark_df, year=2020)
        print(f"  ✓ Résultat filtré: {len(result_filtered)} groupes")
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur Use Case 1: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usecase2(spark_df: Any) -> bool:
    """Teste le Use Case 2 avec Spark."""
    print("\n" + "="*80)
    print("TEST 5: Use Case 2 - Répartition par sexe dirigeants")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import aggregate_usecase2_sexe_dirigeants_spark
        
        print("  Test sans filtres...")
        result = aggregate_usecase2_sexe_dirigeants_spark(spark_df)
        print(f"  ✓ Résultat: {len(result)} groupes")
        if result:
            print(f"    Exemple: {result[0]}")
        else:
            print("    ⚠ Aucun résultat")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur Use Case 2: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usecase3(spark_df: Any) -> bool:
    """Teste le Use Case 3 avec Spark."""
    print("\n" + "="*80)
    print("TEST 6: Use Case 3 - Répartition des effectifs")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import aggregate_usecase3_effectifs_spark
        
        print("  Test sans filtres...")
        result = aggregate_usecase3_effectifs_spark(spark_df)
        print(f"  ✓ Résultat: {len(result)} groupes")
        if result:
            print(f"    Exemple: {result[0]}")
        else:
            print("    ⚠ Aucun résultat")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur Use Case 3: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usecase4(spark_df: Any) -> bool:
    """Teste le Use Case 4 avec Spark."""
    print("\n" + "="*80)
    print("TEST 7: Use Case 4 - Dominance sectorielle")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import aggregate_usecase4_dominance_sectorielle_spark
        
        print("  Test sans filtres...")
        result = aggregate_usecase4_dominance_sectorielle_spark(spark_df)
        print(f"  ✓ Résultat: {len(result)} régions")
        if result:
            print(f"    Exemple: {result[0]}")
        else:
            print("    ⚠ Aucun résultat")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur Use Case 4: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_usecase5(spark_df: Any) -> bool:
    """Teste le Use Case 5 avec Spark."""
    print("\n" + "="*80)
    print("TEST 8: Use Case 5 - Types juridiques")
    print("="*80)
    
    try:
        from src.processing.spark_aggregations import aggregate_usecase5_types_juridiques_spark
        
        print("  Test sans filtres...")
        result = aggregate_usecase5_types_juridiques_spark(spark_df)
        print(f"  ✓ Résultat: {len(result)} groupes")
        if result:
            print(f"    Exemple: {result[0]}")
        else:
            print("    ⚠ Aucun résultat")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur Use Case 5: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_service() -> bool:
    """Teste le DataService de l'API."""
    print("\n" + "="*80)
    print("TEST 9: DataService API")
    print("="*80)
    
    try:
        from src.api.services.data_service import get_data_service
        
        data_service = get_data_service()
        print("  ✓ DataService initialisé")
        
        print("  Test Use Case 1 via API...")
        result1 = data_service.get_usecase1_creations()
        print(f"  ✓ Use Case 1: {len(result1)} résultats")
        if result1:
            print(f"    Exemple: {result1[0]}")
        
        print("  Test Use Case 2 via API...")
        result2 = data_service.get_usecase2_sexe_dirigeants()
        print(f"  ✓ Use Case 2: {len(result2)} résultats")
        
        print("  Test Use Case 3 via API...")
        result3 = data_service.get_usecase3_effectifs()
        print(f"  ✓ Use Case 3: {len(result3)} résultats")
        
        print("  Test Use Case 4 via API...")
        result4 = data_service.get_usecase4_dominance_sectorielle()
        print(f"  ✓ Use Case 4: {len(result4)} résultats")
        
        print("  Test Use Case 5 via API...")
        result5 = data_service.get_usecase5_types_juridiques()
        print(f"  ✓ Use Case 5: {len(result5)} résultats")
        
        return True
    except Exception as e:
        print(f"  ✗ Erreur DataService: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> None:
    """Fonction principale de test."""
    print("="*80)
    print("  TEST D'INTÉGRATION SPARK + HDFS")
    print("="*80)
    
    results = {}
    
    # Test 1: Connexion HDFS
    results["hdfs"] = test_hdfs_connection()
    
    # Test 2: Session Spark
    results["spark_session"] = test_spark_session()
    
    # Test 3: Chargement des données
    load_ok, spark_df = test_load_data_spark()
    results["load_data"] = load_ok
    
    if not load_ok or spark_df is None:
        print("\n" + "="*80)
        print("  ❌ ÉCHEC: Impossible de charger les données")
        print("="*80)
        print("\nRésumé des tests:")
        for test_name, result in results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
        sys.exit(1)
    
    # Tests des use cases
    results["usecase1"] = test_usecase1(spark_df)
    results["usecase2"] = test_usecase2(spark_df)
    results["usecase3"] = test_usecase3(spark_df)
    results["usecase4"] = test_usecase4(spark_df)
    results["usecase5"] = test_usecase5(spark_df)
    
    # Test API Service
    results["api_service"] = test_api_service()
    
    # Résumé final
    print("\n" + "="*80)
    print("  RÉSUMÉ DES TESTS")
    print("="*80)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("  ✅ TOUS LES TESTS SONT PASSÉS")
    else:
        print("  ❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*80)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

