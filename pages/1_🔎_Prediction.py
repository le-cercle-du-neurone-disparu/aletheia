"""
Page de prédiction — Aletheia.
Avec présentation du processus Berlue.
"""

import requests
import streamlit as st

from utils.api_client import (
    API_URL,
    ENV_NAME,
    check_hallucinations,
    get_available_llms,
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Prédiction | Aletheia", page_icon="🔎", layout="wide")

# ==============================================================================
# STYLES
# ==============================================================================
st.markdown(
    """
<style>
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --success: #48bb78;
        --warning: #ed8936;
        --danger: #fc8181;
        --bg-dark: #0a0a0f;
        --bg-card: #14141e;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --border-color: #2d2d44;
    }

    .claim-card {
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 5px solid;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-left-width: 5px;
    }
    .claim-green { border-left-color: var(--success); }
    .claim-red { border-left-color: var(--danger); }
    .claim-yellow { border-left-color: var(--warning); }
    
    .claim-card .claim-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.3rem;
    }
    
    .claim-card .claim-text {
        color: var(--text-primary);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .badge-green { background: var(--success); }
    .badge-red { background: var(--danger); }
    .badge-yellow { background: var(--warning); color: #1a1a2e; }
    
    .answer-box {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--border-color);
        min-height: 120px;
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .process-mini {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .process-mini .step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.3rem 0;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    
    .process-mini .step .num {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        text-align: center;
        line-height: 22px;
        font-size: 0.7rem;
        font-weight: 700;
        flex-shrink: 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# INTERFACE
# ==============================================================================

# --- EN-TÊTE ---
st.title("🔎 Aletheia - Détecteur d'Hallucinations LLM")
st.markdown(
    "Posez une question, le modèle génère une réponse et **Aletheia vérifie la véracité** des affirmations."
)
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # Status backend
    try:
        available_llms = get_available_llms()
        if available_llms:
            st.success("✅ Backend opérationnel")
        else:
            st.warning("⚠️ Aucun modèle chargé côté serveur")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur de connexion : {e}")
        available_llms = []

    st.divider()

    # Sélecteurs
    # Aucune liste de repli : un modèle absent du serveur Ollama ne produit
    # qu'un 500 opaque sur /predict, alors qu'un sélecteur vide montre la panne.
    selected_llm = st.selectbox("🤖 Modèle LLM", options=available_llms)

    selected_temp = st.slider(
        "🌡️ Température",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05,
        help="0 = factuel · 1 = créatif",
    )

    # Indicateur
    if selected_temp < 0.3:
        st.info("🔵 Mode factuel — réponses stables")
    elif selected_temp < 0.7:
        st.info("🟡 Mode équilibré")
    else:
        st.warning("🔴 Mode créatif — risque d'hallucinations")

    st.divider()

    # Processus Berlue
    st.markdown(
        """
    <div class="process-mini">
        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
            ⚡ Processus Berlue
        </div>
        <div class="step"><span class="num">1</span> Découpage en affirmations</div>
        <div class="step"><span class="num">2</span> RAG inversé (FEVER)</div>
        <div class="step"><span class="num">3</span> Auto-cohérence (SelfCheckGPT)</div>
        <div class="step"><span class="num">4</span> Score de confiance</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.caption(f"🔗 API ({ENV_NAME}) : {API_URL}")

# --- ZONE PRINCIPALE ---

# Questions d'exemple
st.subheader("💡 Exemples de questions")
example_cols = st.columns(3)
with example_cols[0]:
    if st.button("🏛️ Capitale de la France", use_container_width=True):
        st.session_state["question"] = "Quelle est la capitale de la France ?"
with example_cols[1]:
    if st.button("⚽ Coupe du Monde 2022", use_container_width=True):
        st.session_state["question"] = "Qui a remporté la Coupe du Monde 2022 ?"
with example_cols[2]:
    if st.button("🔬 Relativité", use_container_width=True):
        st.session_state["question"] = "Explique la théorie de la relativité d'Einstein"

st.divider()

# Input
question_input = st.text_area(
    "📝 Votre question :",
    value=st.session_state.get("question", ""),
    placeholder="Ex: Pourquoi le ciel est-il bleu ?",
    height=80,
)

# Bouton
if st.button(
    "🚀 Générer & Vérifier",
    type="primary",
    use_container_width=True,
    disabled=not available_llms,
):
    if not question_input.strip():
        st.warning("⚠️ Veuillez entrer une question.")
    else:
        with st.spinner(f"🔄 {selected_llm} en cours d'analyse..."):
            try:
                result = check_hallucinations(
                    question_input, selected_llm, selected_temp
                )

                if result:
                    st.success("✅ Analyse terminée")
                    st.balloons()

                    # Métadonnées
                    st.caption(
                        f"📊 {result.get('llm_used', {}).get('name', 'N/A')} · "
                        f"🌡️ {result.get('llm_used', {}).get('temperature', 'N/A')}"
                    )

                    col1, col2 = st.columns([1, 1.5])

                    # Réponse
                    with col1:
                        st.subheader("🤖 Réponse du Modèle")
                        with st.container(border=True):
                            st.markdown(
                                result.get("full_llm_answer", "Aucune réponse générée.")
                            )

                    # Claims
                    with col2:
                        st.subheader("🛡️ Vérification des Affirmations")

                        claims = result.get("claims", [])

                        if not claims:
                            st.info("ℹ️ Aucune affirmation vérifiable trouvée.")
                        else:
                            # Stats
                            total = len(claims)
                            verified = sum(
                                1 for c in claims if c.get("status") == "green"
                            )
                            hallucinated = sum(
                                1 for c in claims if c.get("status") == "red"
                            )
                            uncertain = sum(
                                1 for c in claims if c.get("status") == "unknown"
                            )

                            col_ok, col_ko, col_unk = st.columns(3)
                            with col_ok:
                                st.metric(
                                    "✅ Vrai",
                                    verified,
                                    delta=f"{verified / total * 100:.0f}%",
                                )
                            with col_ko:
                                st.metric(
                                    "❌ Hallucination",
                                    hallucinated,
                                    delta=f"{hallucinated / total * 100:.0f}%",
                                )
                            with col_unk:
                                st.metric(
                                    "⚠️ Incertain",
                                    uncertain,
                                    delta=f"{uncertain / total * 100:.0f}%",
                                )

                            st.divider()

                            # Affichage
                            for idx, claim in enumerate(claims, 1):
                                status = claim.get("status", "unknown").lower()

                                if status == "green":
                                    color_class = "claim-green"
                                    badge = '<span class="status-badge badge-green">✅ Vrai</span>'
                                elif status == "red":
                                    color_class = "claim-red"
                                    badge = '<span class="status-badge badge-red">❌ Hallucination</span>'
                                else:
                                    color_class = "claim-yellow"
                                    badge = '<span class="status-badge badge-yellow">⚠️ Incertain</span>'

                                st.markdown(
                                    f"""
                                <div class="claim-card {color_class}">
                                    <div class="claim-header">
                                        <span style="font-weight: 600; color: var(--text-secondary); font-size: 0.85rem;">
                                            Affirmation #{idx}
                                        </span>
                                        {badge}
                                    </div>
                                    <div class="claim-text">{claim.get("claim_text", "N/A")}</div>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                                with st.expander(
                                    f"📋 Détails (Score: {claim.get('fusion_score', 0):.2f})"
                                ):
                                    st.markdown(
                                        f"**Source :** `{claim.get('evidence_source', 'N/A')}`"
                                    )
                                    st.markdown(
                                        f"**Preuve :** {claim.get('evidence_text', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Score de confiance :** {claim.get('fusion_score', 0):.2f}"
                                    )
                else:
                    st.error("❌ L'analyse a échoué.")

            except Exception as e:  # noqa: BLE001 -- filet de sécurité UI, couvre aussi les erreurs de rendu
                st.error(f"❌ Erreur: {e!s}")

# Footer
st.divider()
st.caption("🔍 Analyse par Berlue · Résultats indicatifs")
