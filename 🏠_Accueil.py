"""
Point d'entrée Streamlit — Aletheia (Page d'accueil).
Backend : projet Berlue.
"""

import streamlit as st

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Cette configuration s'applique par défaut à toutes les pages de l'app
st.set_page_config(
    page_title="Aletheia | Accueil",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CONTENU DE LA PAGE D'ACCUEIL
# ==============================================================================
st.title("🏛️ Bienvenue sur Aletheia")
st.markdown("### L'interface d'exploration du moteur **Berlue** (Détection d'hallucinations LLM)")

st.markdown("---")

st.markdown("""
Aletheia est votre tableau de bord interactif pour auditer, tester et évaluer les grands modèles de langage (LLMs).
Grâce au moteur de fact-checking **Berlue** en arrière-plan, cette plateforme vous permet de mesurer la fiabilité des réponses générées.

👈 **Sélectionnez un outil dans le menu latéral pour commencer :**
""")

st.write("") # Espace
col1, col2 = st.columns(2)

with col1:
    st.info("""
    ### 🔎 1. Prédiction (Test Unitaire)
    **Idéal pour l'exploration.**
    * Posez une question au modèle de votre choix.
    * Obtenez la réponse brute.
    * Analysez chaque affirmation (claim) extraite par Berlue pour voir si elle est soutenue par des preuves (FEVER, SelfCheckGPT, etc.) ou si c'est une hallucination.
    """)

with col2:
    st.success("""
    ### 📊 2. Évaluation (Benchmark)
    **Idéal pour l'analytique.**
    * Lancez des tests massifs sur des datasets standards (TruthfulQA, FEVER...).
    * Comparez les performances globales du modèle (Baseline) face au modèle augmenté par Berlue.
    * Visualisez les matrices de confusion pour comprendre où le modèle se trompe.
    """)


st.markdown("---")
st.caption("🚀 Propulsé par FastAPI & Streamlit | Projet Berlue")
