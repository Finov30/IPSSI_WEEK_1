"""Utilitaires pour les régions."""

from typing import Optional


def normalize_region_name(region: Optional[str]) -> Optional[str]:
    """
    Normalise le nom d'une région.

    Args:
        region: Nom de la région

    Returns:
        Nom de région normalisé ou None
    """
    if not region or region == "NaN" or region == "null":
        return None

    # Nettoyer et normaliser
    normalized = str(region).strip()

    # Gérer les cas particuliers (accents, etc.)
    # Exemple: "Provence-Alpes-Côte d'Azur" -> "Provence-Alpes-Cote d'Azur"
    # (à adapter selon les besoins)

    return normalized if normalized else None


# Liste des régions françaises (métropole + DOM)
REGIONS_FRANCE = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche-Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand Est",
    "Hauts-de-France",
    "Île-de-France",
    "Normandie",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Pays de la Loire",
    "Provence-Alpes-Côte d'Azur",
    "Guadeloupe",
    "Guyane",
    "La Réunion",
    "Martinique",
    "Mayotte",
]


def is_valid_region(region: Optional[str]) -> bool:
    """
    Vérifie si une région est valide.

    Args:
        region: Nom de la région

    Returns:
        True si la région est valide, False sinon
    """
    normalized = normalize_region_name(region)
    if not normalized:
        return False

    return normalized in REGIONS_FRANCE

