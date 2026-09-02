"""
Page de prédiction — Aletheia.
Avec présentation du processus Berlue.
"""

import html

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

    /* Liste des verdicts : un <details> natif par affirmation. La ligne entière
       est cliquable et le détail s'ouvre dessous, sans réexécution du script —
       un st.expander imposerait son propre cadre et interdirait le fond coloré. */
    .verdict {
        border-radius: 8px;
        margin-bottom: 0.45rem;
        overflow: hidden;
    }
    .verdict > summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.7rem 1rem;
        color: #111111;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .verdict > summary::-webkit-details-marker { display: none; }
    .verdict > summary::marker { content: ""; }
    .verdict > summary:hover { filter: brightness(0.96); }
    .verdict .loupe { flex: 0 0 auto; font-size: 0.95rem; }
    .verdict .libelle { flex: 1 1 auto; }
    .verdict .score {
        flex: 0 0 auto;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        opacity: 0.7;
    }
    .verdict .detail {
        padding: 0 1rem 0.85rem 2.5rem;
        color: #111111;
        font-size: 0.88rem;
        line-height: 1.55;
    }
    .verdict .detail b { font-weight: 700; }
    .verdict-vrai { background: #b7e4b0; }
    .verdict-hallucination { background: #f3aaa8; }
    .verdict-incertain { background: #f2e3a3; }

    .ligne-analyse {
        /* `inherit` et non --text-primary, qui vaut blanc : ce bloc de style a
           été écrit pour un fond sombre, alors que l'app suit le thème clair de
           Streamlit. Hériter suit le thème quel qu'il soit. */
        color: inherit;
        font-size: 0.95rem;
        margin: 0.2rem 0 0.9rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def construire_verdict(claim: dict) -> str:
    """Une affirmation, en <details> repliable.

    L'élément est natif : la ligne s'ouvre sans réexécuter le script, là où un
    st.expander imposerait son propre cadre et un aller-retour serveur par clic.
    """
    statut = claim.get("status", "unknown").lower()
    if statut == "green":
        classe, etiquette = "verdict-vrai", "Vrai"
    elif statut == "red":
        classe, etiquette = "verdict-hallucination", "Hallucination"
    else:
        classe, etiquette = "verdict-incertain", "Incertain"

    score = claim.get("fusion_score")
    # Libellé explicite plutôt qu'un nombre nu entre crochets : rien n'y disait
    # qu'il s'agissait d'une confiance, ni sur quelle échelle.
    score_affiche = (
        f"confiance&nbsp;: {score * 100:.0f}&nbsp;%"
        if isinstance(score, int | float)
        else "confiance&nbsp;: —"
    )

    texte = html.escape(str(claim.get("claim_text", "N/A")))
    source = html.escape(str(claim.get("evidence_source", "N/A")))
    preuve = html.escape(str(claim.get("evidence_text", "N/A")))

    # Sur une seule ligne : indenté, le bloc deviendrait du code pour Markdown,
    # que st.markdown interprète avant de rendre le HTML.
    return (
        f'<details class="verdict {classe}">'
        f'<summary><span class="loupe">🔍</span>'
        f'<span class="libelle">{texte}</span>'
        f'<span class="score">{score_affiche}</span></summary>'
        f'<div class="detail"><b>Verdict :</b> {etiquette}<br>'
        f"<b>Source :</b> {source}<br>"
        f"<b>Preuve :</b> {preuve}</div>"
        f"</details>"
    )


def afficher_debug(result: dict) -> None:
    """Restitue le champ `debug` de la réponse, ou explique son absence.

    Le serveur ne le joint qu'à un calcul réel : demander le détail sur une
    question déjà en cache ne renvoie rien, et c'est le cas qu'un lecteur doit
    pouvoir distinguer d'une panne.
    """
    detail = result.get("debug")

    # Deux formes coexistent selon la version du backend : une trace texte, dont
    # les lignes sont séparées par des sauts, et une structure détaillée. La
    # première est ce que sert l'API aujourd'hui.
    if isinstance(detail, str):
        if detail.strip():
            st.code(detail, language="text")
            return
        # Une trace vide vaut une absence de détail : elle rejoint le message
        # qui en explique la cause plutôt qu'un bloc muet.
        detail = None

    if not detail:
        if (result.get("origin") or {}).get("cached"):
            st.info(
                "Réponse servie depuis le cache : le serveur en retire le "
                "détail, qui décrirait une exécution antérieure. Relance avec "
                "« Ignorer le cache » pour l'obtenir."
            )
        else:
            st.warning(
                "Le backend n'a pas renvoyé de détail. Il ne connaît "
                "probablement pas encore le champ `debug`."
            )
        return

    if detail.get("panne"):
        st.error(f"⛔ Étage en panne : {detail['panne']}")

    modeles = detail.get("models") or {}
    if modeles:
        st.markdown("**Modèles**")
        st.dataframe(
            [{"étage": role, "modèle": nom} for role, nom in modeles.items()],
            hide_index=True,
            use_container_width=True,
        )

    for index, claim in enumerate(detail.get("claims") or [], 1):
        st.markdown(f"**Affirmation #{index}** — {claim.get('claim_text', 'N/A')}")

        evidences = claim.get("evidences") or []
        if evidences:
            st.caption("Extraits FEVER remontés, par distance croissante")
            st.dataframe(evidences, hide_index=True, use_container_width=True)
        else:
            st.caption("Aucun extrait remonté par le RAG.")

        st.dataframe(
            [
                {"étage": "RAG — verdict", "valeur": claim.get("rag_verdict")},
                {"étage": "RAG — confiance", "valeur": claim.get("rag_confidence")},
                {
                    "étage": "RAG — extrait retenu",
                    "valeur": claim.get("rag_used_evidence_index"),
                },
                {
                    "étage": "SelfCheck — divergence",
                    "valeur": claim.get("selfcheck_divergence"),
                },
                {"étage": "Fusion — verdict", "valeur": claim.get("fusion_verdict")},
                {
                    "étage": "Fusion — confiance",
                    "valeur": claim.get("fusion_confidence"),
                },
                {
                    "étage": "Fusion — fondement",
                    "valeur": claim.get("fusion_fondement"),
                },
            ],
            hide_index=True,
            use_container_width=True,
        )

        if claim.get("rag_reasoning"):
            st.markdown(f"*Raisonnement RAG :* {claim['rag_reasoning']}")
        if claim.get("fusion_explanation"):
            st.markdown(f"*Explication de la fusion :* {claim['fusion_explanation']}")
        if claim.get("rag_generation"):
            st.caption(f"Génération RAG : {claim['rag_generation']}")
        st.divider()

    echantillons = detail.get("samples") or []
    if echantillons:
        st.markdown(f"**Échantillons SelfCheck** ({len(echantillons)})")
        for numero, echantillon in enumerate(echantillons, 1):
            st.markdown(f"{numero}. {echantillon}")


# ==============================================================================
# INTERFACE
# ==============================================================================

# --- EN-TÊTE ---
st.subheader("Posez votre question au LLM.")

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
        value=0.0,
        step=0.05,
        help="0 = factuel · 1 = créatif",
    )

    ignore_cache = st.toggle(
        "🔄 Ignorer le cache",
        value=False,
        help=(
            "Recalcule la réponse même si la question est déjà en cache, et "
            "remplace l'entrée existante. À utiliser après un changement de "
            "prompt ou de seuils, que la clé de cache ne voit pas."
        ),
    )
    if ignore_cache:
        st.warning("⏱️ Recalcul complet — plusieurs minutes.")

    debug = st.toggle(
        "🐞 Détail d'exécution",
        value=False,
        help=(
            "Rapatrie ce qui n'existe sinon que dans les logs du serveur : "
            "extraits FEVER remontés et leur distance, verdict et raisonnement "
            "du modèle RAG, divergence SelfCheck, fusion."
        ),
    )
    if debug and not ignore_cache:
        st.info(
            "ℹ️ Le détail ne décrit qu'un calcul réel : le serveur le retire "
            "d'une réponse servie depuis le cache. Active « Ignorer le cache » "
            "pour l'obtenir sur une question déjà connue."
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

# Saisie et bouton côte à côte
col_question, col_action = st.columns([5, 1], vertical_alignment="bottom")
with col_question:
    question_input = st.text_input(
        "Votre question",
        value=st.session_state.get("question", ""),
        placeholder="Ex: Pourquoi le ciel est-il bleu ?",
        label_visibility="collapsed",
    )
with col_action:
    lancer = st.button(
        "🚀 Générer & Vérifier",
        type="primary",
        use_container_width=True,
        disabled=not available_llms,
    )

if lancer:
    if not question_input.strip():
        st.warning("⚠️ Veuillez entrer une question.")
    else:
        with st.spinner(f"🔄 {selected_llm} en cours d'analyse..."):
            try:
                result = check_hallucinations(
                    question_input,
                    selected_llm,
                    selected_temp,
                    ignore_cache=ignore_cache,
                    debug=debug,
                )

                if result:
                    # Métadonnées
                    # L'origine est affichée : sans elle, rien ne distingue un
                    # recalcul d'une réponse resservie, et la bascule ci-contre
                    # serait invérifiable. Absente des backends qui ne la
                    # renvoient pas encore, d'où le repli silencieux.
                    origine = result.get("origin") or {}
                    provenance = ""
                    if "cached" in origine:
                        provenance = (
                            " · 💾 servi depuis le cache"
                            if origine["cached"]
                            else " · ⚙️ recalculé"
                        )
                    st.caption(
                        f"📊 {result.get('llm_used', {}).get('name', 'N/A')} · "
                        f"🌡️ {result.get('llm_used', {}).get('temperature', 'N/A')}"
                        f"{provenance}"
                    )

                    st.subheader("🤖 Réponse du Modèle")
                    with st.container(border=True):
                        st.markdown(
                            result.get("full_llm_answer", "Aucune réponse générée.")
                        )

                    st.subheader("🛡️ Vérification des Affirmations")

                    claims = result.get("claims", [])

                    if not claims:
                        st.info("ℹ️ Aucune affirmation vérifiable trouvée.")
                    else:
                        # Tout ce qui n'est ni green ni red est incertain, comme
                        # dans la liste plus bas : compter un statut nommé à la
                        # place laisserait une valeur inattendue hors des trois
                        # totaux, qui ne feraient alors plus la somme.
                        statuses = [c.get("status", "unknown").lower() for c in claims]
                        verified = statuses.count("green")
                        hallucinated = statuses.count("red")
                        uncertain = len(statuses) - verified - hallucinated

                        st.markdown(
                            f'<div class="ligne-analyse"><b>Analyse :</b> '
                            f"[{verified} vrai / {hallucinated} hallucination / "
                            f"{uncertain} incertain]</div>",
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            "".join(construire_verdict(claim) for claim in claims),
                            unsafe_allow_html=True,
                        )

                    if debug:
                        st.divider()
                        with st.expander("🔍 Voir le détail d'exécution"):
                            afficher_debug(result)
                else:
                    st.error("❌ L'analyse a échoué.")

            except Exception as e:  # noqa: BLE001 -- filet de sécurité UI, couvre aussi les erreurs de rendu
                st.error(f"❌ Erreur: {e!s}")
