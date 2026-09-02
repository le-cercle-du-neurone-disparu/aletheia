"""
Client HTTP minimal vers l'API Berlue (voir `berlue/berlue/api/fast.py` dans
le repo `berlue` pour le détail des routes/schémas).
"""

import re

import requests
import streamlit as st

from utils.config import API_URL, ENV_NAME

__all__ = [
    "API_URL",
    "ENV_NAME",
    "check_hallucinations",
    "get_available_llms",
    "run_evaluation",
]

# Un modèle sans taille lisible dans son tag est trié en dernier : le premier
# de la liste est celui que `st.selectbox` présélectionne, et on ne veut y
# mettre que des modèles dont on sait qu'ils sont petits.
_UNKNOWN_SIZE = float("inf")


# La taille est un nombre suivi de « b », isolé dans le tag : `8b`, `0.5b`,
# `8b-instruct-q4_0`. La borne de fin évite de lire une taille dans un suffixe
# de quantification comme `q4_0`.
_SIZE_PATTERN = re.compile(r"(?:^|[-_])(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?b(?:$|[-_])")


def _model_size(model_name: str) -> float:
    """
    Nombre de milliards de paramètres lu dans le tag Ollama d'un modèle.

    `llama3.2:3b` vaut 3, `phi3:14b` vaut 14, `qwen2.5:0.5b` vaut 0.5. Un
    modèle à experts noté `8x7b` est compté au produit, soit 56.
    """
    _, separator, tag = model_name.rpartition(":")
    if not separator:
        return _UNKNOWN_SIZE
    match = _SIZE_PATTERN.search(tag.lower())
    if not match:
        return _UNKNOWN_SIZE
    experts, size = match.group(1), match.group(2)
    return float(experts) * float(size) if size else float(experts)


@st.cache_data(ttl=300)  # Met en cache pendant 5 minutes pour ne pas spammer l'API
def get_available_llms() -> list[str]:
    """GET /llms — liste des modèles LLM disponibles."""
    # 60 s et non 10 : la route interroge le serveur Ollama, dont l'instance
    # Cloud Run peut être froide. Mesuré à 23 s sur un démarrage à froid — la
    # borne de 10 s faisait passer un backend sain pour une panne de réseau.
    response = requests.get(f"{API_URL}/llms", timeout=60)
    response.raise_for_status()
    # Du plus petit au plus grand : le premier élément est présélectionné par
    # les `st.selectbox` des pages, et doit être le modèle le moins coûteux à
    # interroger, pas le gros modèle que Berlue utilise pour son pipeline interne.
    return sorted(response.json()["available_llms"], key=lambda m: (_model_size(m), m))


def check_hallucinations(question: str, llm_name: str, temperature: float):
    """Envoie la question au backend pour prédiction et fact-checking."""
    payload = {
        "question": question,
        "llm": {"name": llm_name, "temperature": temperature},
    }
    try:
        # 600 s et non 60 : le pipeline enchaîne génération, extraction, K
        # échantillons, l'inférence NLI et un appel RAG par affirmation. Mesuré à
        # 6 min 23 sur Cloud Run avec phi3:14b à l'extraction et au RAG — la borne
        # d'une minute coupait une requête qui aboutissait pourtant côté serveur.
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=600)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API : {e}")
        return None


def run_evaluation(
    dataset_name: str, sample_size: int, llm_name: str, temperature: float
):
    """Appelle le endpoint /evaluate."""
    payload = {
        "dataset_name": dataset_name,
        "sample_size": sample_size,
        "llm_to_test": {"name": llm_name, "temperature": temperature},
    }
    try:
        response = requests.post(f"{API_URL}/evaluate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API : {e}")
        return None
