"""Routes API pour Use Case 1: Évolution des créations d'entreprises."""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.models.filters import UseCase1Filters
from src.api.models.schemas import ErrorResponse, UseCase1Response
from src.api.services.data_service import get_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usecase1", tags=["Use Case 1"])


@router.get(
    "/creations",
    response_model=list[UseCase1Response],
    summary="Évolution des créations d'entreprises",
    description="Retourne l'évolution des créations d'entreprises par année, secteur et région",
)
async def get_creations(
    year: int | None = Query(None, description="Filtre par année"),
    secteur: str | None = Query(None, description="Filtre par secteur (code 2 chiffres)"),
    region: str | None = Query(None, description="Filtre par région"),
) -> list[UseCase1Response]:
    """
    Use Case 1: Évolution des créations d'entreprises par année et secteur d'activité.

    Args:
        year: Année de création (optionnel)
        secteur: Code secteur d'activité (2 chiffres, optionnel)
        region: Nom de la région (optionnel)

    Returns:
        Liste des créations d'entreprises agrégées
    """
    try:
        data_service = get_data_service()
        results = data_service.get_usecase1_creations(year=year, secteur=secteur, region=region)

        return [UseCase1Response(**item) for item in results]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des créations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

