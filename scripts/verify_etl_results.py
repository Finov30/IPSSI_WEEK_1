"""Script pour vérifier rapidement les résultats de l'ETL."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import get_settings


def verify_results() -> None:
    """Vérifie les résultats de l'ETL."""
    settings = get_settings()

    # Vérifier les données de test
    test_dir = Path(settings.data_processed_path) / "test_100k"
    processed_dir = Path(settings.data_processed_path)

    print("=" * 80)
    print("VÉRIFICATION DES RÉSULTATS ETL")
    print("=" * 80)

    # Vérifier les fichiers de test
    if test_dir.exists():
        test_files = list(test_dir.glob("*.parquet"))
        if test_files:
            print(f"\n✓ Fichiers de test trouvés: {len(test_files)}")
            print(f"  Répertoire: {test_dir}")

            # Charger et analyser
            print("\nAnalyse des données de test...")
            df = pd.concat([pd.read_parquet(f) for f in test_files], ignore_index=True)

            print(f"  - Total lignes: {len(df):,}")
            print(f"  - Total colonnes: {len(df.columns)}")
            print(f"  - Taille mémoire: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

            # Vérifications
            checks = []

            # Vérifier entreprises radiées
            if "Etat_Administratif_Entreprise" in df.columns:
                radiees = (df["Etat_Administratif_Entreprise"] == "C").sum()
                if radiees == 0:
                    checks.append("✓ Aucune entreprise radiée")
                else:
                    checks.append(f"⚠ {radiees} entreprises radiées restantes")

            # Vérifier colonnes supprimées
            colonnes_a_supprimer = [
                "Enseigne_Etablissement",
                "Denomination_Usuelle_Etablissement",
                "Statut_Diffusion",
                "Employeur_Entreprise",
                "Prenom_Dirigeant",
                "Nom_Dirigeant",
            ]
            colonnes_presentes = [col for col in colonnes_a_supprimer if col in df.columns]
            if not colonnes_presentes:
                checks.append("✓ Colonnes inutiles supprimées")
            else:
                checks.append(f"⚠ Colonnes non supprimées: {colonnes_presentes}")

            # Vérifier effectifs
            if "Effectifs_Entreprise" in df.columns:
                nulls = df["Effectifs_Entreprise"].isna().sum()
                if nulls == 0:
                    checks.append("✓ Effectifs nulls gérés (remplacés par 'NN')")
                else:
                    checks.append(f"⚠ {nulls} effectifs nulls restants")

            # Afficher les vérifications
            print("\nVérifications:")
            for check in checks:
                print(f"  {check}")

            # Aperçu des données
            print("\nAperçu des données:")
            print(df.head().to_string())

        else:
            print(f"\n⚠ Aucun fichier Parquet trouvé dans {test_dir}")
    else:
        print(f"\n⚠ Répertoire de test introuvable: {test_dir}")

    # Vérifier les fichiers de production
    if processed_dir.exists():
        prod_files = [f for f in processed_dir.glob("*.parquet") if "test_100k" not in str(f)]
        if prod_files:
            print(f"\n✓ Fichiers de production trouvés: {len(prod_files)}")
            print(f"  Répertoire: {processed_dir}")
        else:
            print(f"\nℹ Aucun fichier de production trouvé dans {processed_dir}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    verify_results()

