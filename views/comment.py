"""
Page de présentation technique — Aletheia.

Le schéma reprend celui du pitch Berlue (slide 07), corrigé sur un point :
l'interface web appartient à Aletheia, pas à Berlue. Aletheia est
l'application qui pose les questions ; Berlue est le moteur de vérification
qu'elle interroge. Ce sont deux composants distincts, et le dessin le montre —
ivoire, or et grecque du côté d'Aletheia, grille et filets techniques du côté
de Berlue.

Le schéma est animé : un cycle rejoue le trajet d'une question, de
l'utilisateur jusqu'au score qui lui revient.
"""

import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# CONFIGURATION
# ==============================================================================

CYCLE = 13.0  # durée d'un tour complet, en secondes

# Deux ambiances, deux palettes. Côté Aletheia : marbre et or, lettres romaines.
OR = "#A8842A"
OR_PALE = "#D9C27A"
IVOIRE = "#FBF6EA"
SERIF = '"Palatino Linotype", Palatino, Georgia, serif'

# Côté Berlue : encre froide, chasse fixe, angles vifs.
BLEU = "#345AB2"
CYAN = "#009DA8"
VERT = "#2A9F56"
ORANGE = "#F86F32"
FOND_TECH = "#EFF4FB"
MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'

# Cinq échantillons régénérés à températures croissantes : du froid au chaud.
TEMPERATURES = ["#2F6FBF", "#5B86C9", "#9A82AE", "#D3796F", "#E8533F"]


# ==============================================================================
# COMPOSANTS
# ==============================================================================


def _composant_aletheia(x, y, w, h, titre, sous_titre=""):
    """Bloc classique : fond ivoire, double filet d'or, titre en romain."""
    st_html = (
        f'<text x="{x + w / 2}" y="{y + h - 15}" font-size="11.5" text-anchor="middle"'
        f' font-family="{SERIF}" font-style="italic" fill="{OR}">{sous_titre}</text>'
        if sous_titre
        else ""
    )
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{IVOIRE}" stroke="{OR}"/>
    <rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" fill="none"
          stroke="{OR_PALE}"/>
    <text x="{x + w / 2}" y="{y + (h / 2 if not sous_titre else h / 2 - 6)}"
          font-size="13" text-anchor="middle" font-family="{SERIF}"
          font-weight="700" fill="#4A3B12">{titre}</text>
    {st_html}
  </g>"""


def _composant_berlue(x, y, w, h, titre, ligne2="", sous_titre=""):
    """Bloc technique : angles vifs, repères d'angle, sous-titre en chasse fixe."""
    corps = f'<text x="{x + w / 2}" y="{y + 24}" font-size="12.5" text-anchor="middle" font-weight="700">{titre}</text>'
    if ligne2:
        corps += f'<text x="{x + w / 2}" y="{y + 40}" font-size="12.5" text-anchor="middle" font-weight="700">{ligne2}</text>'
    if sous_titre:
        corps += (
            f'<text x="{x + w / 2}" y="{y + (56 if ligne2 else 41)}" font-size="10"'
            f' text-anchor="middle" font-family="{MONO}" fill="{CYAN}">{sous_titre}</text>'
        )
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{BLEU}"/>
    <path d="M{x},{y + 11} L{x},{y} L{x + 11},{y}" fill="none" stroke="{BLEU}" stroke-width="2.4"/>
    <path d="M{x + w},{y + h - 11} L{x + w},{y + h} L{x + w - 11},{y + h}" fill="none"
          stroke="{BLEU}" stroke-width="2.4"/>
    {corps}
  </g>"""


# ==============================================================================
# BRIQUES D'ANIMATION
# ==============================================================================
# Chaque animation dure un cycle entier et se répète indéfiniment ; c'est le
# jeu de `keyTimes` qui place le mouvement réel dans la fenêtre voulue. Faire
# autrement — une durée courte et un `begin` décalé — ne reboucle pas : SMIL
# ne sait pas rejouer un ensemble d'animations décalées les unes des autres.


def _minutage(debut, fin, fondu):
    """keyTimes d'apparition/disparition encadrant le trajet, en fraction de cycle."""
    t0, t1 = debut / CYCLE, fin / CYCLE
    return t0, t1, min(t0 + fondu, t1), max(t1 - fondu, t0)


def _bloc(chemin, libelle, couleur, debut, fin, largeur=None, police=9.5, ronde=4):
    """Un bloc étiqueté qui parcourt `chemin` entre `debut` et `fin`."""
    largeur = largeur if largeur is not None else max(26, 6.2 * len(libelle) + 16)
    t0, t1, a, b = _minutage(debut, fin, 0.012)
    return f"""
  <g opacity="0">
    <rect x="{-largeur / 2:.1f}" y="-10" width="{largeur:.1f}" height="20" rx="{ronde}"
          fill="{couleur}"/>
    <text x="0" y="4" font-size="{police}" fill="#fff" text-anchor="middle"
          font-weight="600">{libelle}</text>
    <animateMotion dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear"
                   keyPoints="0;0;1;1" keyTimes="0;{t0:.4f};{t1:.4f};1" rotate="0">
      <mpath href="#{chemin}"/>
    </animateMotion>
    <animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite"
             values="0;0;1;1;0;0" keyTimes="0;{t0:.4f};{a:.4f};{b:.4f};{t1:.4f};1"/>
  </g>"""


def _pastille(chemin, couleur, debut, fin, cote=15):
    """Une pastille de couleur — un échantillon régénéré, sans étiquette."""
    t0, t1, a, b = _minutage(debut, fin, 0.010)
    return f"""
  <g opacity="0">
    <rect x="{-cote / 2:.1f}" y="{-cote / 2:.1f}" width="{cote}" height="{cote}" rx="3"
          fill="{couleur}"/>
    <animateMotion dur="{CYCLE}s" repeatCount="indefinite" calcMode="linear"
                   keyPoints="0;0;1;1" keyTimes="0;{t0:.4f};{t1:.4f};1" rotate="0">
      <mpath href="#{chemin}"/>
    </animateMotion>
    <animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite"
             values="0;0;1;1;0;0" keyTimes="0;{t0:.4f};{a:.4f};{b:.4f};{t1:.4f};1"/>
  </g>"""


def _halo(x, y, w, h, couleur, debut, fin):
    """Le composant s'allume pendant qu'il travaille."""
    t0, t1 = debut / CYCLE, fin / CYCLE
    m = (t0 + t1) / 2
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{couleur}" opacity="0">
    <animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite"
             values="0;0;0.18;0;0" keyTimes="0;{t0:.4f};{m:.4f};{t1:.4f};1"/>
  </rect>"""


# ==============================================================================
# SCÉNARIO
# ==============================================================================
# Le trajet d'une question, dans l'ordre. Les temps sont en secondes du cycle ;
# c'est ici, et nulle part ailleurs, qu'on règle le rythme de l'animation.

MOUVEMENTS = "".join(
    [
        # L'utilisateur pose sa question à l'interface d'Aletheia.
        _bloc("pUser", "?", OR, 0.3, 1.5, largeur=26, police=12, ronde=13),
        _halo(170, 236, 170, 58, OR, 1.4, 1.9),
        # L'interface la transmet au LLM de Berlue.
        _bloc("pItfLlm", "question", OR, 1.7, 2.8),
        _halo(430, 236, 170, 58, CYAN, 2.7, 3.4),
        # Le LLM produit sa réponse, et cinq régénérations à températures croissantes.
        _bloc("pLlmExt", "réponse", CYAN, 3.4, 4.6),
        *[
            _pastille("pLlmScg", couleur, 3.4 + 0.18 * i, 4.2 + 0.18 * i)
            for i, couleur in enumerate(TEMPERATURES)
        ],
        _halo(650, 236, 195, 58, CYAN, 4.5, 5.1),
        _halo(430, 346, 195, 58, BLEU, 5.2, 6.7),
        # L'extracteur découpe la réponse en affirmations, envoyées au RAG.
        *[
            _bloc(
                "pExtRag",
                "claim",
                BLEU,
                4.9 + 0.32 * i,
                5.9 + 0.32 * i,
                largeur=42,
                police=8.5,
            )
            for i in range(3)
        ],
        _halo(895, 236, 165, 195, ORANGE, 6.0, 6.7),
        # Les deux vérifications rendent leur verdict à la fusion.
        _bloc("pScgFus", "éval. + analyse", VERT, 6.8, 8.0, police=8.5),
        _bloc("pRagFus", "éval. + analyse", VERT, 6.8, 8.0, police=8.5),
        _halo(585, 468, 205, 58, VERT, 7.9, 8.7),
        # La fusion fabrique le score, qui remonte à l'utilisateur.
        _bloc("pFusItf", "score + catégorie + analyse", ORANGE, 8.8, 10.4, police=8.5),
        _halo(170, 236, 170, 58, OR, 10.3, 10.8),
        _bloc("pUserRetour", "résultat", OR, 10.6, 11.7),
    ]
)


# ==============================================================================
# SCHÉMA
# ==============================================================================
# Rendu via components.html et non st.markdown : ce dernier interprète son
# contenu comme du Markdown avant tout, et un SVG y devient un bloc de code.
# L'iframe a son propre document, d'où les couleurs écrites en dur.
#
# La carte reste claire quel que soit le thème de l'app : le schéma est dessiné
# en encre sombre, et l'inverser demanderait de reprendre chaque teinte.

STYLE = """
<style>
  body { margin: 0; background: hsl(222 32% 96%); border-radius: 12px;
         padding: 1.25rem 0; font-family: "Source Sans Pro", sans-serif; }
  svg { display: block; width: 100%; max-width: 1040px; height: auto;
        margin: 0 auto; color: hsl(222 25% 16%); }
  /* Sans cette règle les libellés retombent sur `fill: black` : `color` ne se
     propage pas au remplissage d'un <text>, seulement aux traits en
     `stroke="currentColor"`. Le :not([fill]) épargne ceux qui portent déjà
     leur teinte, qu'une règle CSS supplanterait sinon. */
  svg text:not([fill]) { fill: currentColor; }
  /* Les liaisons restent en retrait : ce sont les blocs qui circulent dessus
     que l'œil doit suivre. */
  .liaison { fill: none; stroke: currentColor; stroke-opacity: 0.5; }
  @media (prefers-reduced-motion: reduce) { svg * { animation: none !important; } }
</style>
"""

SCHEMA = (
    STYLE
    + f"""
<svg viewBox="0 0 1110 640" role="img" aria-label="Architecture de la démo. À gauche, l'utilisateur échange avec Aletheia, l'application web. À droite, Berlue, le moteur de vérification : l'interface d'Aletheia passe la question au LLM, qui produit une réponse envoyée à l'extracteur d'affirmations et, en parallèle, cinq régénérations à températures croissantes envoyées à SelfCheckGPT. L'extracteur découpe la réponse en affirmations et interroge le RAG et son index vectoriel construit sur le corpus FEVER. SelfCheckGPT et RAG envoient chacun leur évaluation à la fusion de score, qui fabrique le score, sa catégorisation et son analyse, et les renvoie à l'interface puis à l'utilisateur.">
  <defs>
    <marker id="archArrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor" fill-opacity="0.5"/>
    </marker>
    <!-- Grecque : le motif à la clé, répété en frise. -->
    <pattern id="grecque" width="22" height="11" patternUnits="userSpaceOnUse">
      <path d="M2,9 V2 H18 V7 H8 V5 H14" fill="none" stroke="{OR}"
            stroke-width="1.3" stroke-opacity="0.6"/>
    </pattern>
    <!-- Grille : le fond technique, discret. -->
    <pattern id="grilleTech" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1" fill="{BLEU}" fill-opacity="0.14"/>
    </pattern>
  </defs>

  <!-- Utilisateur (acteur), à gauche et à hauteur de l'interface : il s'adresse
       à Aletheia de plain-pied, sans que la flèche traverse son fronton. -->
  <g>
    <circle cx="58" cy="228" r="9" fill="none" stroke="currentColor"/>
    <line x1="58" y1="237" x2="58" y2="260" stroke="currentColor"/>
    <line x1="42" y1="246" x2="74" y2="246" stroke="currentColor"/>
    <line x1="58" y1="260" x2="44" y2="280" stroke="currentColor"/>
    <line x1="58" y1="260" x2="72" y2="280" stroke="currentColor"/>
    <text x="58" y="299" font-size="12" text-anchor="middle">Utilisateur</text>
  </g>

  <!-- Aletheia : l'application. Marbre, or et lettres romaines. -->
  <rect x="150" y="150" width="210" height="400" fill="{IVOIRE}" stroke="{OR}"/>
  <rect x="156" y="156" width="198" height="388" fill="none" stroke="{OR_PALE}"/>
  <text x="255" y="182" font-size="19" text-anchor="middle" font-family="{SERIF}"
        font-weight="700" fill="{OR}" letter-spacing="1.5">Aletheia</text>
  <text x="255" y="199" font-size="11.5" text-anchor="middle" font-family="{SERIF}"
        font-style="italic" fill="{OR}" opacity="0.75">ἀλήθεια — le dévoilement</text>
  <rect x="167" y="208" width="176" height="11" fill="url(#grecque)"/>
  {_composant_aletheia(170, 236, 170, 58, "Interface Web", "Streamlit")}
  <!-- Frise du bas en deux pans : le retour du score remonte par l'intervalle. -->
  <rect x="167" y="524" width="66" height="11" fill="url(#grecque)"/>
  <rect x="277" y="524" width="66" height="11" fill="url(#grecque)"/>

  <!-- Berlue : le moteur de vérification. Grille, filets et chasse fixe. -->
  <rect x="405" y="150" width="675" height="400" fill="{FOND_TECH}" stroke="{BLEU}"/>
  <rect x="405" y="150" width="675" height="400" fill="url(#grilleTech)" stroke="none"/>
  <text x="742" y="182" font-size="19" text-anchor="middle" font-weight="700"
        fill="{BLEU}" letter-spacing="0.5">Berlue</text>
  <text x="742" y="199" font-size="10.5" text-anchor="middle" font-family="{MONO}"
        fill="{BLEU}" opacity="0.7">moteur de vérification</text>

  {_composant_berlue(430, 236, 170, 58, "LLM", "", "ollama · transformers")}
  {_composant_berlue(650, 236, 195, 58, "Extracteur", "d'affirmations")}
  {_composant_berlue(430, 346, 195, 58, "SelfCheckGPT", "", "module selfcheckgpt")}
  {_composant_berlue(585, 468, 205, 58, "Fusion Score")}

  <!-- RAG et son corpus -->
  <g>
    <rect x="895" y="236" width="165" height="195" fill="#fff" stroke="{BLEU}"/>
    <path d="M895,247 L895,236 L906,236" fill="none" stroke="{BLEU}" stroke-width="2.4"/>
    <path d="M1060,420 L1060,431 L1049,431" fill="none" stroke="{BLEU}" stroke-width="2.4"/>
    <text x="977" y="260" font-size="12.5" text-anchor="middle" font-weight="700">RAG</text>
    <text x="977" y="276" font-size="12.5" text-anchor="middle" font-weight="700">Index vectoriel</text>
    <text x="977" y="292" font-size="10" text-anchor="middle" font-family="{MONO}"
          fill="{CYAN}">FAISS · Chroma</text>
    <ellipse cx="977" cy="330" rx="44" ry="9" fill="none" stroke="{ORANGE}"/>
    <path d="M933,330 v52 a44,9 0 0 0 88,0 v-52" fill="none" stroke="{ORANGE}"/>
    <text x="977" y="362" font-size="11" text-anchor="middle" font-weight="700"
          fill="{ORANGE}">FEVER</text>
  </g>

  <!-- Liaisons. Ce sont aussi les trajectoires des blocs animés, d'où les
       identifiants et le choix de <path> plutôt que <line>/<polyline> :
       <mpath> ne sait suivre qu'un <path>. -->
  <path id="pUser" class="liaison" d="M88,265 L146,265"
        marker-end="url(#archArrow)" marker-start="url(#archArrow)"/>
  <path id="pUserRetour" d="M146,265 L88,265" fill="none" stroke="none"/>
  <path id="pItfLlm" class="liaison" d="M340,265 L426,265" marker-end="url(#archArrow)"/>
  <path id="pLlmExt" class="liaison" d="M600,265 L646,265" marker-end="url(#archArrow)"/>
  <path id="pLlmScg" class="liaison" d="M515,294 L515,342" marker-end="url(#archArrow)"/>
  <path id="pExtRag" class="liaison" d="M747,294 L747,314 L891,314"
        marker-end="url(#archArrow)"/>
  <path id="pScgFus" class="liaison" d="M527,404 L527,440 L635,440 L635,464"
        marker-end="url(#archArrow)"/>
  <path id="pRagFus" class="liaison" d="M977,431 L977,440 L737,440 L737,464"
        marker-end="url(#archArrow)"/>
  <path id="pFusItf" class="liaison" d="M687,526 L687,595 L255,595 L255,296"
        marker-end="url(#archArrow)"/>
  <text x="525" y="322" font-size="9.5" font-family="{MONO}" fill="{BLEU}">5 régénérations</text>

  {MOUVEMENTS}
</svg>
"""
)

SCHEMA_HAUTEUR = 700

# ==============================================================================
# INTERFACE
# ==============================================================================
st.subheader("Comment ça marche ?")

components.html(SCHEMA, height=SCHEMA_HAUTEUR, scrolling=False)

st.markdown(
    """
<div style="font-size: 0.9rem; line-height: 1.6;">
<p><strong>Aletheia</strong> est l'application : l'interface web, les pages de
   prédiction et d'analyse. <strong>Berlue</strong> est le moteur de
   vérification qu'elle interroge — il ne connaît pas l'interface.</p>
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
