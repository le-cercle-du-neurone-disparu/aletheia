# 1. Chargement du .env
-include .env

# 2. Export des variables pour qu'elles soient dispo dans le terminal
export

.DEFAULT_GOAL := help

help: ## Affiche ce menu d'aide
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<commande>\033[0m\n\nCommandes disponibles :\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ==============================================================================
# 🧰 SETUP
# ==============================================================================

PYTHON_VERSION=3.14.6

VENV_NAME=aletheia-env

local_setup: ## Crée le venv, installe les dépendances, génère .env si besoin
	@echo "🐍 Installing Python $(PYTHON_VERSION)..."
	pyenv install -s $(PYTHON_VERSION)
	@echo "📦 Creating virtual environment $(VENV_NAME)..."
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME) || true
	@echo "🔗 Linking virtual environment to current folder..."
	pyenv local $(VENV_NAME)
	@echo "🛠️ Upgrading pip..."
	pip install --upgrade pip
	@echo "📚 Installing project and dependencies in editable mode..."
	pip install -e .
	@bash scripts/setup_env.sh

# ==============================================================================
# ▶️ RUN (local uniquement pour le moment)
# ==============================================================================

run_app: ## Lance l'app Streamlit en local
	@.venv/bin/streamlit run streamlit_app.py
