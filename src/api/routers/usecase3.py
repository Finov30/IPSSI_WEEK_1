"""Routes API pour Use Case 3: Répartition des effectifs."""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.models.schemas import ErrorResponse, UseCase3Response
from src.api.services.data_service import get_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usecase3", tags=["Use Case 3"])


@router.get(
    "/effectifs",
    response_model=list[UseCase3Response],
    summary="Répartition des effectifs",
    description="Retourne la répartition des effectifs par secteurs et territoires",
)
async def get_effectifs(
    secteur: str | None = Query(None, description="Filtre par secteur (code 2 chiffres)"),
    region: str | None = Query(None, description="Filtre par région"),
    effectif: str | None = Query(None, description="Filtre par tranche d'effectifs"),
) -> list[UseCase3Response]:
    """
    Use Case 3: Répartition des effectifs par secteurs et territoires.

    Args:
        secteur: Code secteur d'activité (2 chiffres, optionnel)
        region: Nom de la région (optionnel)
        effectif: Tranche d'effectifs (optionnel)

    Returns:
        Liste des répartitions des effectifs
    """
    try:
        data_service = get_data_service()
        results = data_service.get_usecase3_effectifs(secteur=secteur, region=region, effectif=effectif)

        return [UseCase3Response(**item) for item in results]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

