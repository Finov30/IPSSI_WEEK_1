"""Routes API pour Use Case 5: Types juridiques."""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.api.models.schemas import ErrorResponse, UseCase5Response
from src.api.services.data_service import get_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/usecase5", tags=["Use Case 5"])


@router.get(
    "/types-juridiques",
    response_model=list[UseCase5Response],
    summary="Types juridiques par secteur et région",
    description="Retourne l'analyse des types juridiques et catégories d'entreprise par secteur et région",
)
async def get_types_juridiques(
    secteur: str | None = Query(None, description="Filtre par secteur (code 2 chiffres)"),
    region: str | None = Query(None, description="Filtre par région"),
    categorie_juridique: int | None = Query(None, description="Filtre par catégorie juridique"),
) -> list[UseCase5Response]:
    """
    Use Case 5: Types juridiques et catégories par secteur et région.

    Args:
        secteur: Code secteur d'activité (2 chiffres, optionnel)
        region: Nom de la région (optionnel)
        categorie_juridique: Code catégorie juridique (optionnel)

    Returns:
        Liste des types juridiques par secteur et région
    """
    try:
        data_service = get_data_service()
        results = data_service.get_usecase5_types_juridiques(
            secteur=secteur, region=region, categorie_juridique=categorie_juridique
        )

        return [UseCase5Response(**item) for item in results]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

