"""
Page de prédiction — Aletheia.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api_client import get_available_llms, check_hallucinations

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Prédiction | Aletheia", page_icon="🔎", layout="wide")

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
st.title("🔎 Aletheia - Détecteur d'Hallucinations LLM")
st.markdown("Posez une question, le modèle génère une réponse et **Aletheia vérifie la véracité** des affirmations.")

# --- BARRE LATÉRALE (Configuration) ---
st.sidebar.header("⚙️ Configuration du Modèle")

# 1. Chargement de la liste des modèles
available_llms = get_available_llms()

# 2. Sélecteurs utilisateur
selected_llm = st.sidebar.selectbox("Modèle LLM", options=available_llms)
selected_temp = st.sidebar.slider("Température", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

st.sidebar.markdown("---")
st.sidebar.info("La température contrôle la créativité du modèle. Une valeur proche de 0 donne des réponses plus factuelles, proche de 1 plus créatives (mais avec plus de risques d'hallucinations).")

# --- ZONE PRINCIPALE ---
question_input = st.text_area("Votre question :", placeholder="Ex: Pourquoi le ciel est-il bleu ?")

if st.button("Générer & Vérifier", type="primary"):
    if not question_input.strip():
        st.warning("Veuillez entrer une question.")
    else:
        with st.spinner(f"Interrogation de {selected_llm} et vérification des faits en cours... ⏳"):

            result = check_hallucinations(question_input, selected_llm, selected_temp)

            if result:
                st.success("Analyse terminée !")

                # Création de deux colonnes pour l'affichage
                col1, col2 = st.columns([1, 1.5])

                # Colonne 1 : La réponse brute du LLM
                with col1:
                    st.subheader("🤖 Réponse du Modèle")
                    st.info(result.get("full_llm_answer", "Aucune réponse générée."))

                    st.caption(f"**Modèle utilisé :** {result['llm_used']['name']} (Température: {result['llm_used']['temperature']})")

                # Colonne 2 : Le fact-checking
                with col2:
                    st.subheader("🛡️ Vérification des Affirmations (Claims)")
                    claims = result.get("claims", [])

                    if not claims:
                        st.write("Aucune affirmation vérifiable trouvée.")
                    else:
                        for idx, claim in enumerate(claims):
                            # Choix de la couleur/icône selon le statut
                            status = claim.get("status", "unknown").lower()
                            if status == "green":
                                icon_color = "✅"
                                border_color = "border-left: 5px solid #28a745;"
                            elif status == "red":
                                icon_color = "❌"
                                border_color = "border-left: 5px solid #dc3545;"
                            else:
                                icon_color = "⚠️"
                                border_color = "border-left: 5px solid #ffc107;"

                            # Affichage stylisé avec HTML/Markdown
                            st.markdown(f"""
                            <div style="{border_color} padding: 10px; background-color: #1e1e1e; border-radius: 5px; margin-bottom: 10px;">
                                <strong>{icon_color} Affirmation :</strong> {claim.get('claim_text')}
                            </div>
                            """, unsafe_allow_html=True)

                            # Détails dans un expander (accordéon) pour garder l'UI propre
                            with st.expander(f"Détails de l'analyse (Score: {claim.get('fusion_score', 0):.2f})"):
                                st.markdown(f"**Source de preuve :** `{claim.get('evidence_source')}`")
                                st.markdown(f"**Preuve :** {claim.get('evidence_text')}")
