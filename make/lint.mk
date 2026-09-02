# ==============================================================================
# 🧹 LINT
# ==============================================================================
# Python : ruff (dans requirements.txt, cf. pyproject.toml pour la config).
# Shell : shellcheck — outil externe, pas installable via pip.
#   Debian/Ubuntu/WSL : sudo apt-get install shellcheck
#   macOS             : brew install shellcheck

lint: ## Vérifie tout (Python + shell), ne modifie rien
	@command -v shellcheck >/dev/null 2>&1 || { \
		echo "❌ shellcheck n'est pas installé. Debian/Ubuntu/WSL : sudo apt-get install shellcheck — macOS : brew install shellcheck"; \
		exit 1; \
	}
	ruff check views/
	ruff format --check views/
	shellcheck -x scripts/*.sh

lint_format: ## Corrige et formate automatiquement le code Python (ruff)
	ruff check --fix views/
	ruff format views/
