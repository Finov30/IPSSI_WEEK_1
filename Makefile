.PHONY: help install setup env-file run-etl run-api run-frontend test lint format clean docker-up docker-down dev dev-stop

help: ## Affiche l'aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

env-file: ## Crée le fichier .env depuis .env.example si il n'existe pas
	@uv run python scripts/create_env.py || python scripts/create_env.py

install: env-file ## Installe les dépendances avec UV
	uv sync

setup: install ## Setup complet du projet
	@echo "✓ Installation des dépendances"
	@echo "✓ Fichier .env configuré"
	@echo "✓ Configuration terminée"

run-etl: env-file ## Lance le pipeline ETL
	uv run python scripts/run_etl.py

test-etl-100k: env-file ## Teste l'ETL avec le fichier 100k.csv
	uv run python scripts/test_etl_100k.py

verify-etl: env-file ## Vérifie les résultats de l'ETL
	uv run python scripts/verify_etl_results.py

test-api: env-file ## Teste les routes API (nécessite que l'API soit lancée)
	uv run python scripts/test_api_endpoints.py

run-api: env-file ## Lance l'API FastAPI
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Lance le frontend React
	cd src/frontend && npm start

test: env-file ## Lance les tests
	uv run pytest tests/ -v --cov=src --cov-report=html

test-unit: env-file ## Lance uniquement les tests unitaires
	uv run pytest tests/unit/ -v

test-integration: env-file ## Lance uniquement les tests d'intégration
	uv run pytest tests/integration/ -v

lint: ## Vérifie le code avec ruff et black
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format: ## Formate le code avec black et ruff
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Nettoie les fichiers temporaires
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

docker-up: ## Lance les containers Docker
	docker-compose up -d

docker-down: ## Arrête les containers Docker
	docker-compose down

docker-build: ## Construit les images Docker
	docker-compose build

docker-logs: ## Affiche les logs Docker
	docker-compose logs -f

dev: env-file ## Lance toutes les ressources pour le développement (Docker + API + Frontend)
	@uv run python scripts/dev.py

dev-stop: ## Arrête toutes les ressources de développement
	@echo "Arrêt de l'environnement de développement..."
	@docker-compose stop redis hdfs-namenode hdfs-datanode spark-master spark-worker
	@echo "[OK] Services Docker arrêtés"
	@echo "Arrêt de l'API et du Frontend..."
	@-pkill -f "uvicorn src.api.main:app" 2>/dev/null || true
	@-pkill -f "npm start" 2>/dev/null || true
	@-taskkill //F //IM node.exe 2>/dev/null || true
	@echo "[OK] Toutes les ressources arrêtées"

