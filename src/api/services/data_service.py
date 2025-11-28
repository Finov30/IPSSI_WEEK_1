"""Service d'accès aux données agrégées."""

import logging
from typing import Any

import pandas as pd

from src.api.services.cache_service import get_cache_service
from src.processing.aggregations import (
    aggregate_usecase1_creations,
    aggregate_usecase2_sexe_dirigeants,
    aggregate_usecase3_effectifs,
    aggregate_usecase4_dominance_sectorielle,
    aggregate_usecase5_types_juridiques,
    load_processed_data,
)

logger = logging.getLogger(__name__)


class DataService:
    """Service pour accéder aux données agrégées."""

    def __init__(self) -> None:
        """Initialise le service."""
        self.cache = get_cache_service()
        self._df_cache: pd.DataFrame | None = None

    def _get_dataframe(self, use_test_data: bool = False) -> pd.DataFrame:
        """
        Charge le DataFrame en cache depuis HDFS UNIQUEMENT.

        Args:
            use_test_data: Si True, charge les données de test (test_100k) en priorité.

        Returns:
            DataFrame chargé depuis HDFS

        Raises:
            ConnectionError: Si HDFS n'est pas accessible
            FileNotFoundError: Si aucune donnée n'est trouvée dans HDFS
        """
        if self._df_cache is None:
            logger.info("Chargement des données traitées depuis HDFS...")
            try:
                # Essayer d'abord les données de test si disponibles
                try:
                    test_df = load_processed_data(use_test_data=True)
                    if not test_df.empty:
                        logger.info("Utilisation des données de test (test_100k) depuis HDFS")
                        self._df_cache = test_df
                        return self._df_cache
                except FileNotFoundError:
                    # Les données de test n'existent pas, continuer avec les données de production
                    logger.debug("Données de test non trouvées, utilisation des données de production")
                
                # Utiliser les données de production
                self._df_cache = load_processed_data(use_test_data=False)
                logger.info("Utilisation des données de production depuis HDFS")
            except (ConnectionError, FileNotFoundError) as e:
                logger.error(f"Impossible de charger les données depuis HDFS: {e}")
                raise
        return self._df_cache

    def get_usecase1_creations(
        self, year: int | None = None, secteur: str | None = None, region: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Use Case 1: Évolution des créations d'entreprises.
        
        Utilise PySpark pour traiter les données directement depuis HDFS
        sans charger tout en mémoire.

        Args:
            year: Filtre par année
            secteur: Filtre par secteur
            region: Filtre par région

        Returns:
            Liste de dictionnaires avec les données agrégées
        """
        # Générer la clé de cache
        cache_key = f"usecase1:year={year}:secteur={secteur}:region={region}"

        # Vérifier le cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Données récupérées du cache: {cache_key}")
            return cached

        # Utiliser Spark pour l'agrégation (ne charge pas tout en mémoire)
        try:
            from src.processing.spark_aggregations import (
                load_processed_data_spark,
                aggregate_usecase1_creations_spark,
            )
            
            # Essayer d'abord les données de test
            try:
                spark_df = load_processed_data_spark(use_test_data=True)
                logger.info("Utilisation des données de test avec Spark")
            except Exception:
                # Fallback sur les données de production
                spark_df = load_processed_data_spark(use_test_data=False)
                logger.info("Utilisation des données de production avec Spark")
            
            # Effectuer l'agrégation directement dans Spark
            result = aggregate_usecase1_creations_spark(
                spark_df, year=year, secteur=secteur, region=region
            )
            
            # Mettre en cache (1 heure)
            self.cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'agrégation Spark: {e}")
            # Fallback sur l'ancienne méthode si Spark échoue
            logger.warning("Fallback sur la méthode Pandas (peut être lent)")
            df = self._get_dataframe()
            if df.empty:
                return []
            result_df = aggregate_usecase1_creations(df, year=year, secteur=secteur, region=region)
            result = result_df.to_dict(orient="records")
            self.cache.set(cache_key, result, ttl=3600)
            return result

    def get_usecase2_sexe_dirigeants(
        self, sexe: str | None = None, secteur: str | None = None, region: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Use Case 2: Répartition par sexe des dirigeants.
        
        Utilise PySpark pour traiter les données directement depuis HDFS.

        Args:
            sexe: Filtre par sexe (M/F)
            secteur: Filtre par secteur
            region: Filtre par région

        Returns:
            Liste de dictionnaires avec les données agrégées
        """
        cache_key = f"usecase2:sexe={sexe}:secteur={secteur}:region={region}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from src.processing.spark_aggregations import (
                load_processed_data_spark,
                aggregate_usecase2_sexe_dirigeants_spark,
            )
            
            try:
                spark_df = load_processed_data_spark(use_test_data=True)
            except Exception:
                spark_df = load_processed_data_spark(use_test_data=False)
            
            result = aggregate_usecase2_sexe_dirigeants_spark(
                spark_df, sexe=sexe, secteur=secteur, region=region
            )
            self.cache.set(cache_key, result, ttl=3600)
            return result
        except Exception as e:
            logger.error(f"Erreur Spark usecase2: {e}")
            logger.warning("Fallback sur Pandas")
            df = self._get_dataframe()
            if df.empty:
                return []
            result_df = aggregate_usecase2_sexe_dirigeants(df, sexe=sexe, secteur=secteur, region=region)
            result = result_df.to_dict(orient="records")
            self.cache.set(cache_key, result, ttl=3600)
            return result

    def get_usecase3_effectifs(
        self, secteur: str | None = None, region: str | None = None, effectif: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Use Case 3: Répartition des effectifs.
        
        Utilise PySpark pour traiter les données directement depuis HDFS.

        Args:
            secteur: Filtre par secteur
            region: Filtre par région
            effectif: Filtre par tranche d'effectifs

        Returns:
            Liste de dictionnaires avec les données agrégées
        """
        cache_key = f"usecase3:secteur={secteur}:region={region}:effectif={effectif}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from src.processing.spark_aggregations import (
                load_processed_data_spark,
                aggregate_usecase3_effectifs_spark,
            )
            
            try:
                spark_df = load_processed_data_spark(use_test_data=True)
            except Exception:
                spark_df = load_processed_data_spark(use_test_data=False)
            
            result = aggregate_usecase3_effectifs_spark(
                spark_df, secteur=secteur, region=region, effectif=effectif
            )
            self.cache.set(cache_key, result, ttl=3600)
            return result
        except Exception as e:
            logger.error(f"Erreur Spark usecase3: {e}")
            logger.warning("Fallback sur Pandas")
            df = self._get_dataframe()
            if df.empty:
                return []
            result_df = aggregate_usecase3_effectifs(df, secteur=secteur, region=region, effectif=effectif)
            result = result_df.to_dict(orient="records")
            self.cache.set(cache_key, result, ttl=3600)
            return result

    def get_usecase4_dominance_sectorielle(self, year: int | None = None) -> list[dict[str, Any]]:
        """
        Use Case 4: Dominance sectorielle par région.
        
        Utilise PySpark pour traiter les données directement depuis HDFS.

        Args:
            year: Filtre par année

        Returns:
            Liste de dictionnaires avec les données agrégées
        """
        cache_key = f"usecase4:year={year}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from src.processing.spark_aggregations import (
                load_processed_data_spark,
                aggregate_usecase4_dominance_sectorielle_spark,
            )
            
            try:
                spark_df = load_processed_data_spark(use_test_data=True)
            except Exception:
                spark_df = load_processed_data_spark(use_test_data=False)
            
            result = aggregate_usecase4_dominance_sectorielle_spark(spark_df, year=year)
            self.cache.set(cache_key, result, ttl=3600)
            return result
        except Exception as e:
            logger.error(f"Erreur Spark usecase4: {e}")
            logger.warning("Fallback sur Pandas")
            df = self._get_dataframe()
            if df.empty:
                return []
            result_df = aggregate_usecase4_dominance_sectorielle(df, year=year)
            result = result_df.to_dict(orient="records")
            self.cache.set(cache_key, result, ttl=3600)
            return result

    def get_usecase5_types_juridiques(
        self,
        secteur: str | None = None,
        region: str | None = None,
        categorie_juridique: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Use Case 5: Types juridiques par secteur et région.
        
        Utilise PySpark pour traiter les données directement depuis HDFS.

        Args:
            secteur: Filtre par secteur
            region: Filtre par région
            categorie_juridique: Filtre par catégorie juridique

        Returns:
            Liste de dictionnaires avec les données agrégées
        """
        cache_key = f"usecase5:secteur={secteur}:region={region}:cat={categorie_juridique}"

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from src.processing.spark_aggregations import (
                load_processed_data_spark,
                aggregate_usecase5_types_juridiques_spark,
            )
            
            try:
                spark_df = load_processed_data_spark(use_test_data=True)
            except Exception:
                spark_df = load_processed_data_spark(use_test_data=False)
            
            result = aggregate_usecase5_types_juridiques_spark(
                spark_df, secteur=secteur, region=region, categorie_juridique=categorie_juridique
            )
            self.cache.set(cache_key, result, ttl=3600)
            return result
        except Exception as e:
            logger.error(f"Erreur Spark usecase5: {e}")
            logger.warning("Fallback sur Pandas")
            df = self._get_dataframe()
            if df.empty:
                return []
            result_df = aggregate_usecase5_types_juridiques(
                df, secteur=secteur, region=region, categorie_juridique=categorie_juridique
            )
            result = result_df.to_dict(orient="records")
            self.cache.set(cache_key, result, ttl=3600)
            return result


# Instance singleton
_data_service: DataService | None = None


def get_data_service() -> DataService:
    """Retourne l'instance singleton du service de données."""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service

