"""
Client HTTP minimal vers l'API Berlue (voir `berlue/berlue/api/fast.py` dans
le repo `berlue` pour le détail des routes/schémas).
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BERLUE_API_URL", "http://localhost:8000")


def get_llms() -> list[str]:
    """GET /llms — liste des modèles LLM disponibles."""
    response = requests.get(f"{API_URL}/llms", timeout=10)
    response.raise_for_status()
    return response.json()["available_llms"]
