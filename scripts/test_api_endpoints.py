"""Script Python pour tester les routes API."""

import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://localhost:8000"


def test_endpoint(name: str, url: str, description: str = "") -> None:
    """Test un endpoint API."""
    print(f"\n{'='*80}")
    print(f"{name}")
    if description:
        print(f"Description: {description}")
    print(f"URL: {url}")
    print(f"{'='*80}")

    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            print(f"✓ Réponse: {len(data)} éléments")
            if len(data) > 0:
                print(f"\nPremier élément:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
                if len(data) > 1:
                    print(f"\n... ({len(data)-1} autres éléments)")
        else:
            print(f"✓ Réponse:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

    except httpx.ConnectError:
        print(f"✗ Erreur: Impossible de se connecter à l'API")
        print(f"  Assurez-vous que l'API est lancée (make run-api)")
    except httpx.HTTPStatusError as e:
        print(f"✗ Erreur HTTP {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print(f"✗ Erreur: {e}")


def main() -> None:
    """Fonction principale."""
    print("=" * 80)
    print("  TEST DES ROUTES API")
    print("=" * 80)

    # Vérifier que l'API est accessible
    print("\n1. Vérification de l'API...")
    try:
        response = httpx.get(f"{API_URL}/health", timeout=5.0)
        response.raise_for_status()
        health = response.json()
        print("✓ API accessible")
        print(f"  Status: {health.get('status', 'unknown')}")
        print(f"  Données chargées: {health.get('data_loaded', False)}")
        print(f"  Cache activé: {health.get('cache_enabled', False)}")
    except Exception as e:
        print(f"✗ API non accessible: {e}")
        print("  Assurez-vous que l'API est lancée: make run-api")
        sys.exit(1)

    # Tester chaque use case
    test_endpoint(
        "Use Case 1: Évolution des créations",
        f"{API_URL}/api/v1/usecase1/creations?year=2020",
        "Créations d'entreprises en 2020",
    )

    test_endpoint(
        "Use Case 1: Toutes les créations (sans filtre)",
        f"{API_URL}/api/v1/usecase1/creations",
        "Toutes les créations d'entreprises",
    )

    test_endpoint(
        "Use Case 2: Répartition par sexe dirigeants",
        f"{API_URL}/api/v1/usecase2/sexe-dirigeants?secteur=10",
        "Dirigeants par sexe dans le secteur 10 (Industrie alimentaire)",
    )

    test_endpoint(
        "Use Case 3: Répartition des effectifs",
        f"{API_URL}/api/v1/usecase3/effectifs",
        "Répartition des effectifs par secteur et région",
    )

    test_endpoint(
        "Use Case 4: Dominance sectorielle",
        f"{API_URL}/api/v1/usecase4/dominance-sectorielle",
        "Secteur dominant par région",
    )

    test_endpoint(
        "Use Case 5: Types juridiques",
        f"{API_URL}/api/v1/usecase5/types-juridiques",
        "Types juridiques par secteur et région",
    )

    print("\n" + "=" * 80)
    print("  TESTS TERMINÉS")
    print("=" * 80)
    print("\nPour voir la documentation interactive:")
    print(f"  Ouvrir {API_URL}/docs dans un navigateur")


if __name__ == "__main__":
    main()

