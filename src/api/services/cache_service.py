"""Service de cache Redis pour les agrégations."""

import json
import logging
from typing import Any

import redis
from redis.exceptions import ConnectionError, RedisError

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service pour gérer le cache Redis."""

    def __init__(self) -> None:
        """Initialise la connexion Redis."""
        settings = get_settings()
        self.redis_client: redis.Redis[str] | None = None
        self.enabled = True

        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
            )
            # Test de connexion
            self.redis_client.ping()
            logger.info(f"Connexion Redis établie: {settings.redis_host}:{settings.redis_port}")
        except (ConnectionError, RedisError) as e:
            logger.warning(f"Redis non disponible: {e}. Le cache est désactivé.")
            self.enabled = False
            self.redis_client = None

    def get(self, key: str) -> Any | None:
        """
        Récupère une valeur depuis le cache.

        Args:
            key: Clé du cache

        Returns:
            Valeur désérialisée ou None si non trouvée
        """
        if not self.enabled or self.redis_client is None:
            return None

        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Erreur lors de la récupération du cache {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Stocke une valeur dans le cache.

        Args:
            key: Clé du cache
            value: Valeur à stocker (sera sérialisée en JSON)
            ttl: Time to live en secondes (défaut: 1 heure)

        Returns:
            True si succès, False sinon
        """
        if not self.enabled or self.redis_client is None:
            return False

        try:
            serialized = json.dumps(value, default=str)  # default=str pour gérer les dates
            self.redis_client.setex(key, ttl, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"Erreur lors du stockage dans le cache {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Supprime une clé du cache.

        Args:
            key: Clé à supprimer

        Returns:
            True si succès, False sinon
        """
        if not self.enabled or self.redis_client is None:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Erreur lors de la suppression du cache {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Supprime toutes les clés correspondant à un pattern.

        Args:
            pattern: Pattern Redis (ex: "usecase1:*")

        Returns:
            Nombre de clés supprimées
        """
        if not self.enabled or self.redis_client is None:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Erreur lors du nettoyage du cache {pattern}: {e}")
            return 0


# Instance singleton
_cache_service: CacheService | None = None


def get_cache_service() -> CacheService:
    """Retourne l'instance singleton du service de cache."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

