"""Modèles de filtres pour les requêtes API."""

from typing import Annotated

from pydantic import BaseModel, Field


class UseCase1Filters(BaseModel):
    """Filtres pour Use Case 1."""

    year: Annotated[int | None, Field(None, description="Filtre par année")] = None
    secteur: Annotated[str | None, Field(None, description="Filtre par secteur (code 2 chiffres)")] = None
    region: Annotated[str | None, Field(None, description="Filtre par région")] = None


class UseCase2Filters(BaseModel):
    """Filtres pour Use Case 2."""

    sexe: Annotated[str | None, Field(None, description="Filtre par sexe (M/F)")] = None
    secteur: Annotated[str | None, Field(None, description="Filtre par secteur")] = None
    region: Annotated[str | None, Field(None, description="Filtre par région")] = None


class UseCase3Filters(BaseModel):
    """Filtres pour Use Case 3."""

    secteur: Annotated[str | None, Field(None, description="Filtre par secteur")] = None
    region: Annotated[str | None, Field(None, description="Filtre par région")] = None
    effectif: Annotated[str | None, Field(None, description="Filtre par tranche d'effectifs")] = None


class UseCase4Filters(BaseModel):
    """Filtres pour Use Case 4."""

    year: Annotated[int | None, Field(None, description="Filtre par année")] = None


class UseCase5Filters(BaseModel):
    """Filtres pour Use Case 5."""

    secteur: Annotated[str | None, Field(None, description="Filtre par secteur")] = None
    region: Annotated[str | None, Field(None, description="Filtre par région")] = None
    categorie_juridique: Annotated[int | None, Field(None, description="Filtre par catégorie juridique")] = None

