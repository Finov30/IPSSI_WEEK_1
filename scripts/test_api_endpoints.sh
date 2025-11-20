#!/bin/bash
# Script de test rapide pour les routes API

API_URL="http://localhost:8000"

echo "=========================================="
echo "  TEST DES ROUTES API"
echo "=========================================="
echo ""

# Vérifier que l'API est accessible
echo "1. Vérification de l'API..."
HEALTH=$(curl -s "${API_URL}/health")
if [ $? -eq 0 ]; then
    echo "✓ API accessible"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "✗ API non accessible. Assurez-vous que l'API est lancée (make run-api)"
    exit 1
fi

echo ""
echo "2. Test Use Case 1: Évolution des créations"
echo "   GET ${API_URL}/api/v1/usecase1/creations?year=2020"
curl -s "${API_URL}/api/v1/usecase1/creations?year=2020" | python3 -m json.tool | head -20

echo ""
echo "3. Test Use Case 2: Répartition par sexe dirigeants"
echo "   GET ${API_URL}/api/v1/usecase2/sexe-dirigeants?secteur=10"
curl -s "${API_URL}/api/v1/usecase2/sexe-dirigeants?secteur=10" | python3 -m json.tool | head -20

echo ""
echo "4. Test Use Case 3: Répartition des effectifs"
echo "   GET ${API_URL}/api/v1/usecase3/effectifs"
curl -s "${API_URL}/api/v1/usecase3/effectifs" | python3 -m json.tool | head -20

echo ""
echo "5. Test Use Case 4: Dominance sectorielle"
echo "   GET ${API_URL}/api/v1/usecase4/dominance-sectorielle"
curl -s "${API_URL}/api/v1/usecase4/dominance-sectorielle" | python3 -m json.tool

echo ""
echo "6. Test Use Case 5: Types juridiques"
echo "   GET ${API_URL}/api/v1/usecase5/types-juridiques"
curl -s "${API_URL}/api/v1/usecase5/types-juridiques" | python3 -m json.tool | head -20

echo ""
echo "=========================================="
echo "  Tests terminés"
echo "=========================================="
echo ""
echo "Pour voir la documentation interactive:"
echo "  Ouvrir http://localhost:8000/docs dans un navigateur"

