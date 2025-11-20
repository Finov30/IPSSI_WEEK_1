"""Utilitaires pour la manipulation des dates."""

from datetime import datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse une date depuis un string.

    Formats supportés:
    - ISO format: "2024-03-22T15:40:57"
    - Date simple: "2024-03-22"
    - Format Sirene: "2000-09-26"

    Args:
        date_str: String de date à parser

    Returns:
        Objet datetime ou None si parsing échoue
    """
    if not date_str or date_str == "NaN" or date_str == "null":
        return None

    try:
        # Essayer format ISO avec timestamp
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Essayer format date simple
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, AttributeError):
        return None


def extract_year(date_str: Optional[str]) -> Optional[int]:
    """
    Extrait l'année depuis une date string.

    Args:
        date_str: String de date

    Returns:
        Année (int) ou None
    """
    date_obj = parse_date(date_str)
    if date_obj:
        return date_obj.year
    return None

