# 1. Chargement du .env
-include .env

# 2. Export des variables pour qu'elles soient dispo dans le terminal
export

include make/*.mk

.DEFAULT_GOAL := help

help: ## Affiche ce menu d'aide
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<commande>\033[0m\n\nCommandes disponibles :\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ==============================================================================
# ▶️ RUN
# ==============================================================================

run_app: ## Lance l'app Streamlit en local (env `local` : backend sur localhost, cf. .env)
	-@streamlit run 🏠_Accueil.py

run_app_gcp: ## Lance l'app Streamlit en local mais branchée sur le backend Cloud Run (env `cloud`)
	@test -n "$(BERLUE_API_GCP_URL)" || { \
		echo "❌ BERLUE_API_GCP_URL n'est pas défini. Ajoute-le dans .env, ou : make run_app_gcp BERLUE_API_GCP_URL=https://..."; \
		exit 1; \
	}
	-@BERLUE_API_URL=$(BERLUE_API_GCP_URL) streamlit run 🏠_Accueil.py
