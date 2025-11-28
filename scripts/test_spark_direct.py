#!/usr/bin/env python3
"""Test direct pour vérifier que Spark lit bien depuis HDFS."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*80)
print("TEST: Spark lit depuis HDFS")
print("="*80)

try:
    from src.processing.spark_aggregations import get_spark_session, load_processed_data_spark
    
    # 1. Créer la session
    print("\n[1] Création session Spark...")
    spark = get_spark_session()
    default_fs = spark.sparkContext.getConf().get('spark.hadoop.fs.defaultFS')
    print(f"✓ Session créée")
    print(f"  Default FS: {default_fs}")
    
    # 2. Lire directement depuis HDFS (production, pas test_100k)
    print("\n[2] Lecture depuis HDFS (données de production)...")
    print("    Chemin: hdfs://sirene-hdfs-namenode:8020/sirene_data/processed")
    
    df = load_processed_data_spark(use_test_data=False)
    print("✓ DataFrame créé (lazy)")
    
    # 3. Compter (déclenche la lecture)
    print("\n[3] Comptage (déclenche la lecture depuis HDFS)...")
    count = df.count()
    print(f"✓ {count:,} lignes lues depuis HDFS")
    
    # 4. Test agrégation
    print("\n[4] Test agrégation simple...")
    from src.processing.spark_aggregations import aggregate_usecase1_creations_spark
    
    result = aggregate_usecase1_creations_spark(df)
    print(f"✓ Agrégation réussie: {len(result)} groupes")
    if result:
        print(f"   Exemple: {result[0]}")
    
    print("\n" + "="*80)
    print("✅ SPARK FONCTIONNE - Il lit bien depuis HDFS")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

