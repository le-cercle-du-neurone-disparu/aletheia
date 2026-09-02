"""
Page de présentation technique — Aletheia.

Le schéma d'architecture est celui du pitch Berlue (`berlue-pitch`, slide 07),
repris avec ses couleurs d'origine.
"""

import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Technique | Aletheia", page_icon="🏗️", layout="wide")

# ==============================================================================
# SCHÉMA
# ==============================================================================
# Rendu via components.html et non st.markdown : ce dernier interprète son
# contenu comme du Markdown avant tout, et un SVG y devient un bloc de code.
# L'iframe a son propre document, d'où les couleurs écrites en dur.
#
# La carte reste claire quel que soit le thème de l'app : le schéma est dessiné
# en encre sombre, et l'inverser demanderait de reprendre chaque teinte.
SCHEMA = """
<style>
  body { margin: 0; background: hsl(222 32% 96%); border-radius: 12px;
         padding: 1.25rem 0; font-family: "Source Sans Pro", sans-serif; }
  svg { display: block; width: 100%; max-width: 930px; height: auto;
        margin: 0 auto; color: hsl(222 25% 16%); }
  /* Sans cette règle les libellés retombent sur `fill: black` : `color` ne se
     propage pas au remplissage d'un <text>, seulement aux traits en
     `stroke="currentColor"`. Le :not([fill]) épargne ceux qui portent déjà
     leur teinte, qu'une règle CSS supplanterait sinon. */
  svg text:not([fill]) { fill: currentColor; }
</style>
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
          <text x="365" y="217" font-size="12" text-anchor="middle" fill="#009DA8">ollama ou transformers</text>

          <!-- Extracteur d'affirmations -->
          <rect x="510" y="176" width="210" height="54" rx="0" fill="none" stroke="currentColor"/>
          <text x="615" y="200" font-size="12.5" text-anchor="middle" font-weight="700">Extracteur</text>
          <text x="615" y="216" font-size="12.5" text-anchor="middle" font-weight="700">d'affirmations</text>

          <!-- SelfCheckGPT -->
          <rect x="280" y="276" width="190" height="54" rx="0" fill="none" stroke="currentColor"/>
          <text x="375" y="300" font-size="12.5" text-anchor="middle" font-weight="700">SelfCheckGPT</text>
          <text x="375" y="317" font-size="12" text-anchor="middle" fill="#009DA8">module selfcheckgpt</text>

          <!-- RAG -->
          <rect x="740" y="176" width="140" height="180" rx="0" fill="none" stroke="currentColor"/>
          <text x="810" y="200" font-size="12.5" text-anchor="middle" font-weight="700">RAG</text>
          <text x="810" y="217" font-size="12.5" text-anchor="middle" font-weight="700">Index vectoriel</text>
          <text x="810" y="237" font-size="12" text-anchor="middle" fill="#009DA8">FAISS/Chroma lib</text>
          <ellipse cx="810" cy="270" rx="42" ry="9" fill="none" stroke="#F86F32"/>
          <path d="M768,270 v50 a42,9 0 0 0 84,0 v-50" fill="none" stroke="#F86F32"/>
          <text x="810" y="300" font-size="11" text-anchor="middle" font-weight="700" fill="#F86F32">FEVER</text>

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
"""

SCHEMA_HAUTEUR = 620

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

components.html(SCHEMA, height=SCHEMA_HAUTEUR, scrolling=False)

st.markdown(
    """
<div style="font-size: 0.9rem; line-height: 1.6;">
<p><a href="https://huggingface.co/datasets/fever/fever" target="_blank"
      rel="noopener" style="color: #F86F32; font-weight: 700; text-decoration: none;">FEVER</a>
   : ~145k affirmations Wikipédia étiquetées soutenue / réfutée / pas assez
   d'info, chacune avec sa preuve — le corpus qu'on indexe pour le RAG inversé.</p>
<p><a href="https://github.com/potsawee/selfcheckgpt" target="_blank"
      rel="noopener" style="color: #345AB2; font-weight: 700; text-decoration: none;">SelfCheckGPT</a>
   : implémentation de référence du module de détection d'hallucination sans
   boîte noire, utilisé en parallèle du RAG inversé.</p>
</div>
""",
    unsafe_allow_html=True,
)
