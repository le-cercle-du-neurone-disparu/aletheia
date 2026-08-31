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

@st.cache_data(ttl=300) # Met en cache pendant 5 minutes pour ne pas spammer l'API
def get_available_llms() -> list[str]:
    """GET /llms — liste des modèles LLM disponibles."""
    response = requests.get(f"{API_URL}/llms", timeout=10)
    response.raise_for_status()
    return response.json()["available_llms"]

def check_hallucinations(question: str, llm_name: str, temperature: float):
    """Envoie la question au backend pour prédiction et fact-checking."""
    payload = {
        "question": question,
        "llm": {
            "name": llm_name,
            "temperature": temperature
        }
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API : {e}")
        return None

def run_evaluation(dataset_name: str, sample_size: int, llm_name: str, temperature: float):
    """Appelle le endpoint /evaluate."""
    payload = {
        "dataset_name": dataset_name,
        "sample_size": sample_size,
        "llm_to_test": {
            "name": llm_name,
            "temperature": temperature
        }
    }
    try:
        response = requests.post(f"{API_URL}/evaluate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de l'appel à l'API : {e}")
        return None
