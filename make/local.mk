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
