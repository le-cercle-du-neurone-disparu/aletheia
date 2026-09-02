"""
Client HTTP minimal vers l'API Berlue (voir `berlue/berlue/api/fast.py` dans
le repo `berlue` pour le détail des routes/schémas).
"""

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


@st.cache_data(ttl=300)  # Met en cache pendant 5 minutes pour ne pas spammer l'API
def get_available_llms() -> list[str]:
    """GET /llms — liste des modèles LLM disponibles."""
    # 60 s et non 10 : la route interroge le serveur Ollama, dont l'instance
    # Cloud Run peut être froide. Mesuré à 23 s sur un démarrage à froid — la
    # borne de 10 s faisait passer un backend sain pour une panne de réseau.
    response = requests.get(f"{API_URL}/llms", timeout=60)
    response.raise_for_status()
    return response.json()["available_llms"]


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
