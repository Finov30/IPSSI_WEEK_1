"""Routes API pour Use Case 2: Répartition par sexe des dirigeants."""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.models.schemas import ErrorResponse, UseCase2Response
from src.api.services.data_service import get_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usecase2", tags=["Use Case 2"])


@router.get(
    "/sexe-dirigeants",
    response_model=list[UseCase2Response],
    summary="Répartition par sexe des dirigeants",
    description="Retourne la répartition par sexe des dirigeants selon les secteurs d'activité",
)
async def get_sexe_dirigeants(
    sexe: str | None = Query(None, description="Filtre par sexe (M/F)"),
    secteur: str | None = Query(None, description="Filtre par secteur (code 2 chiffres)"),
    region: str | None = Query(None, description="Filtre par région"),
) -> list[UseCase2Response]:
    """
    Use Case 2: Répartition par sexe des dirigeants selon les secteurs d'activité.

    Args:
        sexe: Sexe du dirigeant (M ou F, optionnel)
        secteur: Code secteur d'activité (2 chiffres, optionnel)
        region: Nom de la région (optionnel)

    Returns:
        Liste des répartitions par sexe des dirigeants
    """
    try:
        data_service = get_data_service()
        results = data_service.get_usecase2_sexe_dirigeants(sexe=sexe, secteur=secteur, region=region)

        return [UseCase2Response(**item) for item in results]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

