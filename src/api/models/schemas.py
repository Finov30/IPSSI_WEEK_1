"""Schémas Pydantic pour les requêtes et réponses API."""

from typing import Any

from pydantic import BaseModel, Field


class UseCase1Response(BaseModel):
    """Réponse pour Use Case 1: Évolution des créations."""

    annee: int | None = Field(None, description="Année de création")
    secteur: str | None = Field(None, description="Code secteur d'activité")
    region: str | None = Field(None, description="Nom de la région")
    nombre_creations: int = Field(..., description="Nombre de créations d'entreprises")


class UseCase2Response(BaseModel):
    """Réponse pour Use Case 2: Répartition par sexe dirigeants."""

    sexe: str = Field(..., description="Sexe du dirigeant (M/F)")
    secteur: str | None = Field(None, description="Code secteur d'activité")
    region: str | None = Field(None, description="Nom de la région")
    nombre_entreprises: int = Field(..., description="Nombre d'entreprises")


class UseCase3Response(BaseModel):
    """Réponse pour Use Case 3: Répartition des effectifs."""

    effectifs: str = Field(..., description="Tranche d'effectifs")
    secteur: str | None = Field(None, description="Code secteur d'activité")
    region: str | None = Field(None, description="Nom de la région")
    nombre_entreprises: int = Field(..., description="Nombre d'entreprises")


class UseCase4Response(BaseModel):
    """Réponse pour Use Case 4: Dominance sectorielle."""

    region: str = Field(..., description="Nom de la région")
    secteur_dominant: str = Field(..., description="Code secteur dominant")
    nombre_entreprises: int = Field(..., description="Nombre d'entreprises dans ce secteur")


class UseCase5Response(BaseModel):
    """Réponse pour Use Case 5: Types juridiques."""

    categorie_juridique: int = Field(..., description="Code catégorie juridique")
    secteur: str | None = Field(None, description="Code secteur d'activité")
    region: str | None = Field(None, description="Nom de la région")
    nombre_entreprises: int = Field(..., description="Nombre d'entreprises")


class ErrorResponse(BaseModel):
    """Réponse d'erreur."""

    error: str = Field(..., description="Message d'erreur")
    detail: str | None = Field(None, description="Détails de l'erreur")


class HealthResponse(BaseModel):
    """Réponse de santé."""

    status: str = Field(..., description="Statut du service")
    data_loaded: bool = Field(..., description="Indique si les données sont chargées")
    cache_enabled: bool = Field(..., description="Indique si le cache est activé")

