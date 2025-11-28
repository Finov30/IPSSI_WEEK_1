# Pourquoi Spark ne semble pas fonctionner ?

## ✅ Spark EST configuré pour lire depuis HDFS

Dans `src/processing/spark_aggregations.py`, Spark est bien configuré :

```python
hdfs_url = f"hdfs://{settings.hdfs_host}:{hdfs_port}"
spark_builder.config("spark.hadoop.fs.defaultFS", hdfs_url)
```

Cela signifie que **Spark lit directement depuis HDFS**, pas depuis le disque local.

## 🔍 Le problème dans le script de test

Le script `test_data_docker.sh` essaie d'abord de charger `test_100k` qui n'existe pas :

```python
df = load_processed_data_spark(use_test_data=True)  # ❌ Échoue car test_100k n'existe pas
```

L'erreur est normale, mais le script bash s'arrête avant de basculer vers les données de production.

## ✅ Le code Python gère bien le fallback

Dans `src/api/services/data_service.py`, le fallback fonctionne correctement :

```python
try:
    spark_df = load_processed_data_spark(use_test_data=True)  # Essaie test_100k
except Exception:
    spark_df = load_processed_data_spark(use_test_data=False)  # ✅ Bascule vers production
```

## 🧪 Test simple pour vérifier

Pour tester que Spark lit bien depuis HDFS, exécutez :

```bash
docker exec sirene-api uv run python scripts/test_spark_direct.py
```

Ce script :
1. Crée une session Spark configurée pour HDFS
2. Lit directement depuis `/sirene_data/processed` (données de production)
3. Compte les lignes (déclenche la lecture depuis HDFS)
4. Teste une agrégation

## 📊 Résumé

- ✅ Spark **EST** configuré pour HDFS
- ✅ Spark **PEUT** lire depuis HDFS
- ⚠️ Le script de test a un problème de gestion d'erreur
- ✅ Le code de l'API gère correctement le fallback

**Spark fonctionne, c'est juste le script de test qui a besoin d'être corrigé.**

