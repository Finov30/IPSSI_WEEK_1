"""Tests unitaires pour les utilitaires."""

import pytest

from src.utils.ape_utils import get_secteur_from_ape, normalize_ape_code
from src.utils.date_utils import extract_year, parse_date
from src.utils.region_utils import normalize_region_name


class TestDateUtils:
    """Tests pour les utilitaires de dates."""

    def test_parse_date_iso(self):
        """Test parsing date ISO."""
        date_str = "2024-03-22T15:40:57"
        result = parse_date(date_str)
        assert result is not None
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 22

    def test_parse_date_simple(self):
        """Test parsing date simple."""
        date_str = "2024-03-22"
        result = parse_date(date_str)
        assert result is not None
        assert result.year == 2024

    def test_parse_date_none(self):
        """Test parsing date None."""
        assert parse_date(None) is None
        assert parse_date("NaN") is None
        assert parse_date("null") is None

    def test_extract_year(self):
        """Test extraction année."""
        assert extract_year("2024-03-22") == 2024
        assert extract_year("2024-03-22T15:40:57") == 2024
        assert extract_year(None) is None


class TestApeUtils:
    """Tests pour les utilitaires APE."""

    def test_normalize_ape_code(self):
        """Test normalisation code APE."""
        assert normalize_ape_code("32.12Z") == "32.12Z"
        assert normalize_ape_code("3212Z") == "32.12Z"
        assert normalize_ape_code(None) is None
        assert normalize_ape_code("NaN") is None

    def test_get_secteur_from_ape(self):
        """Test extraction secteur."""
        assert get_secteur_from_ape("32.12Z") == "32"
        assert get_secteur_from_ape("10.11A") == "10"
        assert get_secteur_from_ape(None) is None


class TestRegionUtils:
    """Tests pour les utilitaires régions."""

    def test_normalize_region_name(self):
        """Test normalisation nom région."""
        assert normalize_region_name("Île-de-France") == "Île-de-France"
        assert normalize_region_name("  Auvergne-Rhône-Alpes  ") == "Auvergne-Rhône-Alpes"
        assert normalize_region_name(None) is None
        assert normalize_region_name("NaN") is None

