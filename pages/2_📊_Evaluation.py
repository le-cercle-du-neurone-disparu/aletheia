"""
Page d'évaluation par lot (Benchmark) — Aletheia.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from utils.api_client import get_available_llms, run_evaluation

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Évaluation | Aletheia", page_icon="📊", layout="wide")

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def plot_confusion_heatmap(matrix_data: dict, title: str, color_scale: str):
    """Transforme le dictionnaire de la matrice en Heatmap Plotly."""
    # 1. Conversion du dict imbriqué en DataFrame Pandas
    df = pd.DataFrame([
        matrix_data["ground_truth_true"],
        matrix_data["ground_truth_false"]
    ])

    # 2. Renommage des index et colonnes pour que ce soit beau à l'écran
    df.index = ["Vrai (Réalité)", "Faux (Réalité)"]
    df.columns = ["Prédit Vrai", "Prédit Indécis", "Prédit Faux"]

    # 3. Création de la Heatmap interactive avec Plotly
    fig = px.imshow(
        df,
        text_auto=True, # Affiche les chiffres dans les cases
        color_continuous_scale=color_scale,
        title=title,
        aspect="auto"
    )

    # 4. Nettoyage de l'affichage
    fig.update_layout(xaxis_title="Ce que le modèle a répondu", yaxis_title="La vérité", coloraxis_showscale=False)
    return fig

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
st.title("📊 Tableau de Bord d'Évaluation")
st.markdown("Lancez un benchmark complet sur un dataset pour comparer la **Baseline** (modèle brut) avec **Berlue** (modèle + fact-checking).")

# --- BARRE LATÉRALE ---
st.sidebar.header("⚙️ Paramètres du Benchmark")
dataset_choice = st.sidebar.selectbox("Dataset de test", ["HaluEval", "TruthfulQA"])
sample_size = st.sidebar.slider("Nombre d'échantillons", min_value=10, max_value=500, value=100, step=10)

st.sidebar.markdown("---")
available_llms = get_available_llms()
selected_llm = st.sidebar.selectbox("Modèle LLM à évaluer", options=available_llms)
selected_temp = st.sidebar.slider("Température", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# --- ZONE PRINCIPALE ---
if st.button("🚀 Lancer le Benchmark", type="primary"):
    with st.spinner(f"Évaluation de {sample_size} assertions sur {dataset_choice} avec {selected_llm}... Cela peut prendre un moment. ⏳"):

        result = run_evaluation(dataset_choice, sample_size, selected_llm, selected_temp)

        if result and result.get("status") == "success":
            st.success("Benchmark terminé avec succès !")

            metrics = result["metrics"]

            # --- AFFICHAGE DES HEATMAPS ---
            st.markdown("### 🗺️ Matrices de Confusion (2x3)")
            col1, col2 = st.columns(2)

            with col1:
                # Heatmap Baseline (en nuances de rouge/orange)
                fig_baseline = plot_confusion_heatmap(
                    metrics["baseline"],
                    title="Baseline (Sans Berlue)",
                    color_scale="Oranges"
                )
                st.plotly_chart(fig_baseline, use_container_width=True)

            with col2:
                # Heatmap Berlue (en nuances de bleu/vert)
                fig_berlue = plot_confusion_heatmap(
                    metrics["berlue"],
                    title="Berlue (Avec Fact-Checking)",
                    color_scale="Greens"
                )
                st.plotly_chart(fig_berlue, use_container_width=True)

            # --- ANALYSE RAPIDE ---
            st.info("💡 **Comment lire ces graphiques ?** La diagonale idéale (haut-gauche vers bas-droite) représente les bonnes prédictions. L'objectif de Berlue est de maximiser la case 'Prédit Faux' sur la ligne 'Faux (Réalité)' par rapport à la baseline.")
