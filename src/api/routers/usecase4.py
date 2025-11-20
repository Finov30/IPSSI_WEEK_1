"""Routes API pour Use Case 4: Dominance sectorielle."""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.models.schemas import ErrorResponse, UseCase4Response
from src.api.services.data_service import get_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usecase4", tags=["Use Case 4"])


@router.get(
    "/dominance-sectorielle",
    response_model=list[UseCase4Response],
    summary="Dominance sectorielle par région",
    description="Retourne le secteur dominant par région",
)
async def get_dominance_sectorielle(
    year: int | None = Query(None, description="Filtre par année"),
) -> list[UseCase4Response]:
    """
    Use Case 4: Dominance sectorielle par région.

    Retourne le secteur d'activité dominant (celui avec le plus d'entreprises) pour chaque région.

    Args:
        year: Année de création (optionnel)

    Returns:
        Liste des secteurs dominants par région
    """
    try:
        data_service = get_data_service()
        results = data_service.get_usecase4_dominance_sectorielle(year=year)

        return [UseCase4Response(**item) for item in results]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

