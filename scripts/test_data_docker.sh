#!/bin/bash
# Script de test pour vérifier que toutes les données remontent correctement
# À exécuter dans le container API

# Ne pas arrêter sur les erreurs dans les blocs Python (on gère les erreurs manuellement)
set +e

echo "=================================================================================="
echo "  TEST COMPLET - VÉRIFICATION DES DONNÉES"
echo "=================================================================================="

# Test 1: Vérifier HDFS
echo ""
echo "TEST 1: Vérification HDFS"
echo "=================================================================================="
uv run python -c "
from src.config.settings import get_settings
import requests

settings = get_settings()
webhdfs_url = f'http://{settings.hdfs_host}:9870'
processed_path = f'{settings.hdfs_path}/processed'
list_url = f'{webhdfs_url}/webhdfs/v1{processed_path}?op=LISTSTATUS'

print(f'  Vérification: {processed_path}')
try:
    response = requests.get(list_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        files = data.get('FileStatuses', {}).get('FileStatus', [])
        parquet_files = [f for f in files if f.get('pathSuffix', '').endswith('.parquet')]
        print(f'  ✓ {len(parquet_files)} fichiers Parquet trouvés')
        if parquet_files:
            print(f'    Exemple: {parquet_files[0].get(\"pathSuffix\")}')
    else:
        print(f'  ✗ Erreur WebHDFS: {response.status_code}')
except Exception as e:
    print(f'  ✗ Erreur: {e}')
"

# Test 2: Test Spark direct
echo ""
echo "TEST 2: Test Spark direct"
echo "=================================================================================="
uv run python -c "
from src.processing.spark_aggregations import (
    get_spark_session,
    load_processed_data_spark,
    aggregate_usecase1_creations_spark,
)

print('  Création de la session Spark...')
spark = get_spark_session()
print(f'  ✓ Session Spark créée: {spark.sparkContext.appName}')

print('  Chargement des données...')
df = None
try:
    df = load_processed_data_spark(use_test_data=True)
    print('  ✓ Données de test chargées')
except Exception as e:
    error_msg = str(e)
    # Détecter si c'est une erreur de chemin non trouvé (normal pour test_100k)
    is_path_not_found = (
        'PATH_NOT_FOUND' in error_msg or 
        'does not exist' in error_msg or 
        'File does not exist' in error_msg or
        'FileNotFoundException' in error_msg
    )
    
    if is_path_not_found:
        print('  ⚠ Données de test non disponibles (normal, utilisation des données de production)')
    else:
        print(f'  ⚠ Erreur données de test: {error_msg[:150]}')
    
    # Basculer vers les données de production
    try:
        print('  Chargement des données de production...')
        df = load_processed_data_spark(use_test_data=False)
        print('  ✓ Données de production chargées')
    except Exception as e2:
        print(f'  ✗ Erreur chargement données production: {str(e2)[:200]}')
        import sys
        sys.exit(1)

if df is not None:
    print('  Test agrégation Use Case 1...')
    try:
        result = aggregate_usecase1_creations_spark(df)
        print(f'  ✓ Résultat: {len(result)} groupes')
        if result:
            print(f'    Exemple: {result[0]}')
    except Exception as e:
        print(f'  ✗ Erreur agrégation: {str(e)[:200]}')
        import sys
        sys.exit(1)
else:
    print('  ✗ Impossible de charger les données')
    import sys
    sys.exit(1)
"

# Test 3: Test DataService
echo ""
echo "TEST 3: Test DataService API"
echo "=================================================================================="
uv run python -c "
from src.api.services.data_service import get_data_service

data_service = get_data_service()
print('  ✓ DataService initialisé')

print('  Test Use Case 1...')
result1 = data_service.get_usecase1_creations()
print(f'  ✓ Use Case 1: {len(result1)} résultats')
if result1:
    print(f'    Exemple: {result1[0]}')

print('  Test Use Case 2...')
result2 = data_service.get_usecase2_sexe_dirigeants()
print(f'  ✓ Use Case 2: {len(result2)} résultats')

print('  Test Use Case 3...')
result3 = data_service.get_usecase3_effectifs()
print(f'  ✓ Use Case 3: {len(result3)} résultats')

print('  Test Use Case 4...')
result4 = data_service.get_usecase4_dominance_sectorielle()
print(f'  ✓ Use Case 4: {len(result4)} résultats')

print('  Test Use Case 5...')
result5 = data_service.get_usecase5_types_juridiques()
print(f'  ✓ Use Case 5: {len(result5)} résultats')
"

echo ""
echo "=================================================================================="
echo "  TESTS TERMINÉS"
echo "=================================================================================="

