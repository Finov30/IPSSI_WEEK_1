"""Application FastAPI principale."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import usecase1, usecase2, usecase3, usecase4, usecase5
from src.api.services.cache_service import get_cache_service
from src.api.services.data_service import get_data_service
from src.config.logging import setup_logging
from src.config.settings import get_settings

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="Sirene DataViz API",
    description="API pour la visualisation interactive des données Sirene",
    version="0.1.0",
)

# Configuration CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(usecase1.router)
app.include_router(usecase2.router)
app.include_router(usecase3.router)
app.include_router(usecase4.router)
app.include_router(usecase5.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Événement au démarrage de l'application."""
    logger.info("Démarrage de l'API Sirene DataViz")
    logger.info(f"Environment: {settings.environment}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Événement à l'arrêt de l'application."""
    logger.info("Arrêt de l'API Sirene DataViz")


@app.get("/")
async def root() -> dict[str, str]:
    """Endpoint racine."""
    return {
        "message": "Sirene DataViz API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str | bool]:
    """Endpoint de santé."""
    cache_service = get_cache_service()
    data_service = get_data_service()

    # Vérifier si les données sont chargées
    try:
        df = data_service._get_dataframe()
        data_loaded = not df.empty
    except Exception:
        data_loaded = False

    return {
        "status": "healthy",
        "data_loaded": data_loaded,
        "cache_enabled": cache_service.enabled,
    }

