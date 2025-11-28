"""Test simple pour vérifier que Spark peut lire depuis HDFS."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("TEST SPARK - LECTURE DEPUIS HDFS")
print("="*80)

# Test 1: Session Spark
print("\n[1] Création de la session Spark...")
from src.processing.spark_aggregations import get_spark_session

spark = get_spark_session()
print(f"✓ Session Spark créée")
print(f"  App Name: {spark.sparkContext.appName}")
print(f"  Default FS: {spark.sparkContext.getConf().get('spark.hadoop.fs.defaultFS', 'N/A')}")

# Test 2: Lecture directe depuis HDFS (données de production)
print("\n[2] Lecture des données depuis HDFS (données de production)...")
from src.processing.spark_aggregations import load_processed_data_spark

try:
    df = load_processed_data_spark(use_test_data=False)
    print("✓ DataFrame Spark créé (lazy)")
    
    # Test 3: Compter les lignes (déclenche l'action)
    print("\n[3] Comptage des lignes (déclenche la lecture depuis HDFS)...")
    count = df.count()
    print(f"✓ Nombre de lignes lues depuis HDFS: {count:,}")
    
    # Test 4: Afficher le schéma
    print("\n[4] Schéma du DataFrame:")
    df.printSchema()
    
    # Test 5: Afficher quelques lignes
    print("\n[5] Aperçu des données (5 premières lignes):")
    df.show(5, truncate=False)
    
    print("\n" + "="*80)
    print("✅ SPARK FONCTIONNE CORRECTEMENT AVEC HDFS")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

