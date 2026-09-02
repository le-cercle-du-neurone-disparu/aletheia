"""
Résolution de la configuration selon l'environnement d'exécution.

Deux environnements sont prévus :

- `local` : l'app et le backend Berlue tournent sur la même machine. L'URL est
  lue dans `.env` (voir `.env.example`).
- `cloud` : l'app tourne sur Streamlit Community Cloud, le backend sur Cloud
  Run. L'URL est lue dans les secrets Streamlit — panneau « Secrets » de l'app
  en ligne, ou `.streamlit/secrets.toml` pour rejouer cette configuration en
  local (voir `.streamlit/secrets.toml.example`).

Les appels HTTP partent du processus Streamlit, pas du navigateur du visiteur :
sur Streamlit Cloud, `localhost` désigne le conteneur qui héberge l'app. Une URL
publique est donc obligatoire dans cet environnement.
"""

import os
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv()

DEFAULT_API_URL = "http://localhost:8000"

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _from_secrets(key: str) -> str | None:
    """
    Lit un secret Streamlit.

    Streamlit lève `StreamlitSecretNotFoundError` quand aucun fichier
    `secrets.toml` n'existe — cas normal en environnement `local`, où la
    configuration vient de `.env`.
    """
    try:
        return st.secrets.get(key)
    except StreamlitSecretNotFoundError:
        return None


# Les secrets priment sur `.env` : sur Streamlit Cloud, ils sont la seule source
# de vérité, et un `.env` traînant dans le dépôt ne doit pas pouvoir la court-circuiter.
API_URL = (
    _from_secrets("BERLUE_API_URL") or os.getenv("BERLUE_API_URL") or DEFAULT_API_URL
).rstrip("/")

IS_LOCAL_API = urlparse(API_URL).hostname in LOCAL_HOSTS

ENV_NAME = "local" if IS_LOCAL_API else "cloud"
