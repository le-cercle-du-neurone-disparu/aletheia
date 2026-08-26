# 1. Chargement du .env
-include .env

# 2. Export des variables pour qu'elles soient dispo dans le terminal
export

include make/*.mk

.DEFAULT_GOAL := help

help: ## Affiche ce menu d'aide
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<commande>\033[0m\n\nCommandes disponibles :\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ==============================================================================
# ▶️ RUN (local uniquement pour le moment)
# ==============================================================================

run_app: ## Lance l'app Streamlit en local
	-@streamlit run 🏠_Accueil.py
