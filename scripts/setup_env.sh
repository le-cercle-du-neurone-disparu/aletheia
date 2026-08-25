#!/usr/bin/env bash
# scripts/setup_env.sh
#
# Crée .env de façon interactive (Entrée pour accepter la valeur par défaut).
# Ne touche jamais à un .env déjà existant.
#
# Usage : ./scripts/setup_env.sh   (appelé automatiquement par `make local_setup`)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env existe déjà — on n'y touche pas."
    exit 0
fi

echo "🔧 Configuration de .env (Entrée pour accepter la valeur par défaut) :"

ask() {
    local var_name="$1" default="$2" prompt="$3" value
    if [ -n "$default" ]; then
        read -rp "  $prompt [$default]: " value
        value="${value:-$default}"
    else
        read -rp "  $prompt: " value
    fi
    printf -v "$var_name" '%s' "$value"
}

ask BERLUE_API_URL "http://localhost:8000" "BERLUE_API_URL (URL de l'API berlue)"

{
    echo "BERLUE_API_URL=$BERLUE_API_URL"
} > "$ENV_FILE"

echo "✅ .env créé."
