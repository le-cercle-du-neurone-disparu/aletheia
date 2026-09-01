"""
Client HTTP minimal vers l'API Berlue (voir `berlue/berlue/api/fast.py` dans
le repo `berlue` pour le détail des routes/schémas).
"""

import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BERLUE_API_URL", "http://localhost:8000")


@st.cache_data(ttl=300)  # Met en cache pendant 5 minutes pour ne pas spammer l'API
def get_available_llms() -> list[str]:
    """GET /llms — liste des modèles LLM disponibles."""
    response = requests.get(f"{API_URL}/llms", timeout=10)
    response.raise_for_status()
    return response.json()["available_llms"]


def check_hallucinations(question: str, llm_name: str, temperature: float):
    """Envoie la question au backend pour prédiction et fact-checking."""
    payload = {
        "question": question,
        "llm": {"name": llm_name, "temperature": temperature},
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API : {e}")
        return None


@st.cache_data(ttl=60)  # Met en cache brièvement — assez court pour voir arriver un nouveau run
def list_evaluated_models(mode: str = "dataset", **filters) -> list[dict] | None:
    """GET /evaluated-models — scopes déjà évalués et stockés (mode
    'dataset' ou 'generated'), filtrable par model_id/ratio/pipeline_version/
    generation_version/eval_version (`filters`, valeur `None` = joker, pas
    de filtre `dataset` côté API — à appliquer côté appelant si besoin).
    Chaque entrée est un `EvaluationResult` complet, matrice Berlue incluse
    — ne déclenche jamais de calcul."""
    params = {"mode": mode, **{k: v for k, v in filters.items() if v is not None}}
    try:
        response = requests.get(f"{API_URL}/evaluated-models", params=params, timeout=15)
        response.raise_for_status()
        return response.json()["evaluations"]
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la recherche d'évaluations : {e}")
        return None


def get_baseline_evaluation(dataset: str, ratio: float) -> dict | None:
    """GET /baseline-evaluation — baseline NLI mode dataset, recalculée à la
    volée à chaque appel (jamais stockée), indépendante du modèle évalué."""
    try:
        response = requests.get(
            f"{API_URL}/baseline-evaluation", params={"dataset": dataset, "ratio": ratio}, timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors du calcul de la baseline : {e}")
        return None


def get_baseline_evaluation_generated(
    dataset: str, ratio: float, model_id: str, generation_version: str, eval_version: str
) -> dict | None:
    """GET /baseline-evaluation-generated — baseline mode généré, lecture
    cache seule. Retourne `None` sans afficher d'erreur si ce scope précis
    n'a pas encore de baseline calculée (404, cas normal — cf. `EvaluationResult`)."""
    try:
        response = requests.get(
            f"{API_URL}/baseline-evaluation-generated",
            params={
                "dataset": dataset,
                "ratio": ratio,
                "model_id": model_id,
                "generation_version": generation_version,
                "eval_version": eval_version,
            },
            timeout=15,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la lecture de la baseline générée : {e}")
        return None
