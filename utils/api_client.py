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
    "get_baseline_evaluation",
    "get_baseline_evaluation_generated",
    "list_evaluated_models",
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


def check_hallucinations(
    question: str, llm_name: str, temperature: float, ignore_cache: bool = False
):
    """Envoie la question au backend pour prédiction et fact-checking.

    `ignore_cache` force le recalcul côté serveur et remplace l'entrée en
    cache. Un backend qui ne connaît pas encore le champ l'ignore sans erreur.
    """
    payload = {
        "question": question,
        "llm": {"name": llm_name, "temperature": temperature},
        "ignore_cache": ignore_cache,
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


@st.cache_data(
    ttl=60
)  # Met en cache brièvement — assez court pour voir arriver un nouveau run
def list_evaluated_models(mode: str = "dataset", **filters) -> list[dict] | None:
    """GET /evaluated-models — scopes déjà évalués et stockés (mode
    'dataset' ou 'generated'), filtrable par model_id/ratio/pipeline_version/
    generation_version/eval_version (`filters`, valeur `None` = joker, pas
    de filtre `dataset` côté API — à appliquer côté appelant si besoin).
    Chaque entrée est un `EvaluationResult` complet, matrice Berlue incluse
    — ne déclenche jamais de calcul."""
    params = {"mode": mode, **{k: v for k, v in filters.items() if v is not None}}
    try:
        response = requests.get(
            f"{API_URL}/evaluated-models", params=params, timeout=15
        )
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
            f"{API_URL}/baseline-evaluation",
            params={"dataset": dataset, "ratio": ratio},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors du calcul de la baseline : {e}")
        return None


def get_baseline_evaluation_generated(
    dataset: str,
    ratio: float,
    model_id: str,
    generation_version: str,
    eval_version: str,
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
