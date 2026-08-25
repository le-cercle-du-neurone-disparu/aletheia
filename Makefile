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

local_setup: ## Crée le venv, installe les dépendances, génère .env si besoin
	@echo "📦 Création du venv (.venv)..."
	@python3 -m venv .venv
	@echo "🛠️ Installation des dépendances..."
	@.venv/bin/pip install --upgrade pip -q
	@.venv/bin/pip install -r requirements.txt -q
	@bash scripts/setup_env.sh
	@echo "✅ Setup terminé. Active le venv : source .venv/bin/activate"

# ==============================================================================
# ▶️ RUN (local uniquement pour le moment)
# ==============================================================================

run_app: ## Lance l'app Streamlit en local
	@.venv/bin/streamlit run streamlit_app.py
