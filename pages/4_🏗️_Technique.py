"""
Page de présentation technique — Aletheia.

Le schéma d'architecture reprend celui du pitch Berlue (`berlue-pitch`,
slide 07), transposé dans la palette sombre d'Aletheia.
"""

import streamlit as st

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Technique | Aletheia", page_icon="🏗️", layout="wide")

# ==============================================================================
# STYLE
# ==============================================================================
st.markdown(
    """
<style>
    :root {
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --warning: #ed8936;
        --border-color: #2d2d44;
        --bg-card: #14141e;
    }
    .schema-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
    }
    /* Le schéma est décrit en `currentColor` : la couleur du conteneur fixe
       donc celle des traits, des flèches et des libellés d'un seul geste. */
    .schema-card svg {
        color: var(--text-primary);
        width: 100%;
        height: auto;
    }
    .schema-legende {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-top: 1rem;
    }
    .schema-legende a { text-decoration: none; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# INTERFACE
# ==============================================================================
st.title("🏗️ Présentation technique")
st.markdown(
    "Les composants de la démo et la façon dont ils s'enchaînent, "
    "d'une question posée jusqu'au verdict rendu."
)
st.divider()

st.subheader("Composants de la démo — schéma d'architecture")

st.markdown(
    """
<div class="schema-card">
    <svg viewBox="0 0 930 560" role="img" aria-label="Architecture de la démo : l'utilisateur échange question et résultat avec l'interface web ; à l'intérieur du système Berlue, l'interface passe la question au LLM (Ollama ou transformers), qui la transmet à l'extracteur d'affirmations puis, en parallèle, au module SelfCheckGPT ; l'extracteur interroge le module RAG et son index vectoriel construit sur le corpus FEVER ; RAG et SelfCheckGPT envoient chacun leur verdict à la fusion de score, qui renvoie le résultat à l'interface web. Aucun composant externe au système hormis le corpus FEVER indexé par RAG.">
              <defs>
                <marker id="archArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                  <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
                </marker>
              </defs>

              <!-- Utilisateur (acteur) -->
              <g>
                <circle cx="140" cy="22" r="9" fill="none" stroke="currentColor"/>
                <line x1="140" y1="31" x2="140" y2="55" stroke="currentColor"/>
                <line x1="124" y1="40" x2="156" y2="40" stroke="currentColor"/>
                <line x1="140" y1="55" x2="126" y2="76" stroke="currentColor"/>
                <line x1="140" y1="55" x2="154" y2="76" stroke="currentColor"/>
                <text x="140" y="92" font-size="12" text-anchor="middle">Utilisateur</text>
              </g>
              <line x1="140" y1="100" x2="140" y2="176" stroke="currentColor" marker-end="url(#archArrow)" marker-start="url(#archArrow)"/>

              <!-- Système Berlue -->
              <rect x="20" y="130" width="880" height="410" rx="0" fill="none" stroke="currentColor"/>
              <text x="460" y="158" font-size="18" text-anchor="middle" font-weight="700">Berlue</text>

              <!-- Interface Web -->
              <rect x="50" y="176" width="170" height="54" rx="0" fill="none" stroke="currentColor"/>
              <text x="135" y="207" font-size="12.5" text-anchor="middle" font-weight="700">Interface Web</text>

              <!-- LLM -->
              <rect x="280" y="176" width="170" height="54" rx="0" fill="none" stroke="currentColor"/>
              <text x="365" y="200" font-size="12.5" text-anchor="middle" font-weight="700">LLM</text>
              <text x="365" y="217" font-size="10" text-anchor="middle" fill="var(--text-secondary)">ollama ou transformers</text>

              <!-- Extracteur d'affirmations -->
              <rect x="510" y="176" width="210" height="54" rx="0" fill="none" stroke="currentColor"/>
              <text x="615" y="200" font-size="12.5" text-anchor="middle" font-weight="700">Extracteur</text>
              <text x="615" y="216" font-size="12.5" text-anchor="middle" font-weight="700">d'affirmations</text>

              <!-- SelfCheckGPT -->
              <rect x="280" y="276" width="190" height="54" rx="0" fill="none" stroke="currentColor"/>
              <text x="375" y="300" font-size="12.5" text-anchor="middle" font-weight="700">SelfCheckGPT</text>
              <text x="375" y="317" font-size="10" text-anchor="middle" fill="var(--text-secondary)">module selfcheckgpt</text>

              <!-- RAG -->
              <rect x="740" y="176" width="140" height="180" rx="0" fill="none" stroke="currentColor"/>
              <text x="810" y="200" font-size="12.5" text-anchor="middle" font-weight="700">RAG</text>
              <text x="810" y="217" font-size="12.5" text-anchor="middle" font-weight="700">Index vectoriel</text>
              <text x="810" y="237" font-size="10" text-anchor="middle" fill="var(--text-secondary)">FAISS/Chroma lib</text>
              <ellipse cx="810" cy="270" rx="42" ry="9" fill="none" stroke="var(--warning)"/>
              <path d="M768,270 v50 a42,9 0 0 0 84,0 v-50" fill="none" stroke="var(--warning)"/>
              <text x="810" y="300" font-size="11" text-anchor="middle" font-weight="700" fill="var(--warning)">FEVER</text>

              <!-- Fusion Score -->
              <rect x="380" y="440" width="200" height="54" rx="0" fill="none" stroke="currentColor"/>
              <text x="480" y="472" font-size="12.5" text-anchor="middle" font-weight="700">Fusion Score</text>

              <!-- Interface -> LLM -->
              <line x1="220" y1="203" x2="280" y2="203" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- LLM -> Extracteur -->
              <line x1="450" y1="203" x2="510" y2="203" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- Extracteur -> RAG -->
              <polyline points="615,230 615,250 740,250" fill="none" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- LLM -> SelfCheckGPT -->
              <line x1="365" y1="230" x2="365" y2="276" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- SelfCheckGPT -> Fusion -->
              <polyline points="375,330 375,410 430,410 430,440" fill="none" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- RAG -> Fusion -->
              <polyline points="810,356 810,410 530,410 530,440" fill="none" stroke="currentColor" marker-end="url(#archArrow)"/>
              <!-- Fusion -> Interface (retour) -->
              <polyline points="480,494 480,515 60,515 60,230" fill="none" stroke="currentColor" marker-end="url(#archArrow)"/>
            </svg>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="schema-legende">
  <p><a href="https://huggingface.co/datasets/fever/fever" target="_blank"
        rel="noopener" style="color: var(--warning);">FEVER</a> :
     ~145k affirmations Wikipédia étiquetées soutenue / réfutée / pas assez
     d'info, chacune avec sa preuve — le corpus qu'on indexe pour le RAG
     inversé.</p>
  <p><a href="https://github.com/potsawee/selfcheckgpt" target="_blank"
        rel="noopener" style="color: #667eea;">SelfCheckGPT</a> :
     implémentation de référence du module de détection d'hallucination sans
     boîte noire, utilisé en parallèle du RAG inversé.</p>
</div>
""",
    unsafe_allow_html=True,
)
