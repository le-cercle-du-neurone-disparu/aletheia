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

CYCLE = 15.0  # durée d'un tour complet, en secondes

# Deux ambiances, deux palettes. Côté Aletheia : marbre et or, lettres romaines.
OR = "#A8842A"
OR_PALE = "#D9C27A"
IVOIRE = "#FBF6EA"
ENCRE_OR = "#4A3B12"
SERIF = '"Palatino Linotype", Palatino, Georgia, serif'

# Côté Berlue : encre froide, chasse fixe, angles vifs.
BLEU = "#345AB2"
CYAN = "#00808A"
VERT = "#2A9F56"
ORANGE = "#F86F32"
FOND_TECH = "#EFF4FB"
MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, monospace'

# Cinq échantillons régénérés à températures croissantes : du froid au chaud.
TEMPERATURES = ["#2F6FBF", "#5B86C9", "#9A82AE", "#D3796F", "#E8533F"]


# ==============================================================================
# COMPOSANTS
# ==============================================================================


def _lignes(cx, cy, lignes):
    """Empile des lignes de texte, centrées sur (cx, cy)."""
    interligne = 6
    total = sum(taille + interligne for taille, _, _ in lignes) - interligne
    y = cy - total / 2
    sortie = []
    for taille, texte, attributs in lignes:
        y += taille
        sortie.append(
            f'<text x="{cx}" y="{y:.1f}" font-size="{taille}" text-anchor="middle"'
            f" {attributs}>{texte}</text>"
        )
        y += interligne
    return "".join(sortie)


def _composant_aletheia(x, y, w, h, titre, sous_titre=""):
    """Bloc classique : fond ivoire, double filet d'or, titre en romain."""
    lignes = [(14.5, titre, f'font-family="{SERIF}" font-weight="700" fill="{ENCRE_OR}"')]
    if sous_titre:
        lignes.append(
            (12.5, sous_titre, f'font-family="{SERIF}" font-style="italic" fill="{OR}"')
        )
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{IVOIRE}" stroke="{OR}"/>
    <rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" fill="none"
          stroke="{OR_PALE}"/>
    {_lignes(x + w / 2, y + h / 2, lignes)}
  </g>"""


def _composant_berlue(x, y, w, h, titre, ligne2="", sous_titre=""):
    """Bloc technique : angles vifs, repères d'angle, sous-titre en chasse fixe."""
    lignes = [(14, titre, 'font-weight="700"')]
    if ligne2:
        lignes.append((14, ligne2, 'font-weight="700"'))
    if sous_titre:
        lignes.append((12, sous_titre, f'font-family="{MONO}" fill="{CYAN}"'))
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="{BLEU}"/>
    <path d="M{x},{y + 12} L{x},{y} L{x + 12},{y}" fill="none" stroke="{BLEU}" stroke-width="2.6"/>
    <path d="M{x + w},{y + h - 12} L{x + w},{y + h} L{x + w - 12},{y + h}" fill="none"
          stroke="{BLEU}" stroke-width="2.6"/>
    {_lignes(x + w / 2, y + h / 2, lignes)}
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


def _bloc(chemin, libelle, couleur, debut, fin, largeur=None, police=11.5, ronde=4):
    """Un bloc étiqueté qui parcourt `chemin` entre `debut` et `fin`."""
    largeur = largeur if largeur is not None else 0.62 * police * len(libelle) + 20
    t0, t1, a, b = _minutage(debut, fin, 0.010)
    return f"""
  <g opacity="0">
    <rect x="{-largeur / 2:.1f}" y="-13" width="{largeur:.1f}" height="26" rx="{ronde}"
          fill="{couleur}"/>
    <text x="0" y="{police * 0.36:.1f}" font-size="{police}" fill="#fff"
          text-anchor="middle" font-weight="600">{libelle}</text>
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
        _bloc("pUser", "?", OR, 0.3, 1.6, largeur=30, police=15, ronde=15),
        _halo(170, 240, 170, 62, OR, 1.5, 2.0),
        # L'interface la transmet au LLM de Berlue.
        _bloc("pItfLlm", "question", OR, 1.8, 3.0),
        _halo(435, 240, 180, 62, CYAN, 2.9, 3.7),
        # Le LLM produit sa réponse — et cinq régénérations, à températures
        # croissantes, qui partent en parallèle vers SelfCheckGPT.
        _bloc("pLlmExt", "réponse", CYAN, 3.7, 5.0),
        *[
            _bloc("pLlmScg", "réponse", couleur, 3.7 + 0.35 * i, 4.6 + 0.35 * i, police=10.5)
            for i, couleur in enumerate(TEMPERATURES)
        ],
        _halo(705, 240, 200, 62, CYAN, 4.9, 5.6),
        _halo(435, 390, 205, 62, BLEU, 5.5, 7.4),
        # L'extracteur découpe la réponse en affirmations, envoyées au RAG.
        *[
            _bloc("pExtRag", "claim", BLEU, 5.4 + 0.34 * i, 6.6 + 0.34 * i, police=11)
            for i in range(3)
        ],
        _halo(975, 240, 175, 210, ORANGE, 6.8, 7.6),
        # Les deux vérifications rendent leur verdict à la fusion.
        _bloc("pScgFus", "éval. + analyse", VERT, 7.6, 9.0, police=11),
        _bloc("pRagFus", "éval. + analyse", VERT, 7.6, 9.0, police=11),
        _halo(660, 520, 220, 62, VERT, 8.9, 9.8),
        # La fusion fabrique le score et le renvoie — lentement, c'est le
        # résultat, on doit avoir le temps de le lire.
        _bloc("pFusItf", "score + catégorie + analyse", ORANGE, 9.8, 12.6, police=11.5),
        _halo(170, 240, 170, 62, OR, 12.5, 13.1),
        _bloc("pUserRetour", "analyse", OR, 12.8, 14.2),
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
  svg { display: block; width: 100%; max-width: 1100px; height: auto;
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
<svg viewBox="0 -60 1200 740" role="img" aria-label="Architecture de la démo. À gauche, l'utilisateur échange avec Aletheia, l'application web. À droite, Berlue, le moteur de vérification : l'interface d'Aletheia passe la question au LLM, qui produit une réponse envoyée à l'extracteur d'affirmations et, en parallèle, cinq réponses régénérées à températures croissantes envoyées à SelfCheckGPT. L'extracteur découpe la réponse en affirmations et interroge le RAG et son index vectoriel FAISS, construit sur le corpus FEVER. SelfCheckGPT et RAG envoient chacun leur évaluation à la fusion de score, qui fabrique le score, sa catégorisation et son analyse, et les renvoie à l'interface puis à l'utilisateur.">
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

  <!-- Vignettes : chacune annonce son monde. Aletheia dans une niche d'or,
       Berlue dans un cadre technique. Les fichiers sont servis par Streamlit
       (enableStaticServing), pas encodés dans la page : le navigateur les met
       en cache une fois. Chemin relatif comme ailleurs — l'iframe de
       components.html hérite de l'URL de base de la page qui la porte. -->
  <g>
    <image href="app/static/aletheia-portrait.webp" x="190" y="-50" width="130" height="190"
           preserveAspectRatio="xMidYMid slice"/>
    <rect x="190" y="-50" width="130" height="190" fill="none" stroke="{OR}" stroke-width="2"/>
    <rect x="194" y="-46" width="122" height="182" fill="none" stroke="{OR_PALE}"/>
  </g>
  <g>
    <image href="app/static/berlue-hero.webp" x="640" y="-24" width="300" height="164"
           preserveAspectRatio="xMidYMid slice"/>
    <rect x="640" y="-24" width="300" height="164" fill="none" stroke="{BLEU}" stroke-width="1.5"/>
    <path d="M640,-10 L640,-24 L654,-24" fill="none" stroke="{BLEU}" stroke-width="2.6"/>
    <path d="M940,126 L940,140 L926,140" fill="none" stroke="{BLEU}" stroke-width="2.6"/>
  </g>

  <!-- Utilisateur (acteur), à gauche et à hauteur de l'interface : il s'adresse
       à Aletheia de plain-pied, sans que la flèche traverse son fronton. -->
  <g>
    <circle cx="58" cy="234" r="10" fill="none" stroke="currentColor"/>
    <line x1="58" y1="244" x2="58" y2="268" stroke="currentColor"/>
    <line x1="41" y1="253" x2="75" y2="253" stroke="currentColor"/>
    <line x1="58" y1="268" x2="43" y2="289" stroke="currentColor"/>
    <line x1="58" y1="268" x2="73" y2="289" stroke="currentColor"/>
    <text x="58" y="309" font-size="13.5" text-anchor="middle">Utilisateur</text>
  </g>

  <!-- Aletheia : l'application. Marbre, or et lettres romaines. -->
  <rect x="150" y="150" width="210" height="460" fill="{IVOIRE}" stroke="{OR}"/>
  <rect x="156" y="156" width="198" height="448" fill="none" stroke="{OR_PALE}"/>
  <text x="255" y="184" font-size="21" text-anchor="middle" font-family="{SERIF}"
        font-weight="700" fill="{OR}" letter-spacing="1.5">Aletheia</text>
  <text x="255" y="203" font-size="12.5" text-anchor="middle" font-family="{SERIF}"
        font-style="italic" fill="{OR}" opacity="0.8">ἀλήθεια — le dévoilement</text>
  <rect x="167" y="212" width="176" height="11" fill="url(#grecque)"/>
  {_composant_aletheia(170, 240, 170, 62, "Interface Web", "Streamlit")}
  <!-- Frise du bas en deux pans : le retour du score remonte par l'intervalle. -->
  <rect x="167" y="584" width="66" height="11" fill="url(#grecque)"/>
  <rect x="277" y="584" width="66" height="11" fill="url(#grecque)"/>

  <!-- Berlue : le moteur de vérification. Grille, filets et chasse fixe. -->
  <rect x="405" y="150" width="770" height="460" fill="{FOND_TECH}" stroke="{BLEU}"/>
  <rect x="405" y="150" width="770" height="460" fill="url(#grilleTech)" stroke="none"/>
  <text x="790" y="184" font-size="21" text-anchor="middle" font-weight="700"
        fill="{BLEU}" letter-spacing="0.5">Berlue</text>
  <text x="790" y="203" font-size="12" text-anchor="middle" font-family="{MONO}"
        fill="{BLEU}" opacity="0.75">moteur de vérification</text>

  {_composant_berlue(435, 240, 180, 62, "LLM", "", "ollama · transformers")}
  {_composant_berlue(705, 240, 200, 62, "Extracteur", "d'affirmations")}
  {_composant_berlue(435, 390, 205, 62, "SelfCheckGPT", "", "module selfcheckgpt")}
  {_composant_berlue(660, 520, 220, 62, "Fusion Score")}

  <!-- RAG et son corpus -->
  <g>
    <rect x="975" y="240" width="175" height="210" fill="#fff" stroke="{BLEU}"/>
    <path d="M975,252 L975,240 L987,240" fill="none" stroke="{BLEU}" stroke-width="2.6"/>
    <path d="M1150,438 L1150,450 L1138,450" fill="none" stroke="{BLEU}" stroke-width="2.6"/>
    <text x="1062" y="268" font-size="14" text-anchor="middle" font-weight="700">RAG</text>
    <text x="1062" y="286" font-size="14" text-anchor="middle" font-weight="700">Index vectoriel</text>
    <text x="1062" y="304" font-size="12" text-anchor="middle" font-family="{MONO}"
          fill="{CYAN}">FAISS</text>
    <ellipse cx="1062" cy="345" rx="46" ry="10" fill="none" stroke="{ORANGE}"/>
    <path d="M1016,345 v55 a46,10 0 0 0 92,0 v-55" fill="none" stroke="{ORANGE}"/>
    <text x="1062" y="380" font-size="13" text-anchor="middle" font-weight="700"
          fill="{ORANGE}">FEVER</text>
  </g>

  <!-- Liaisons. Ce sont aussi les trajectoires des blocs animés, d'où les
       identifiants et le choix de <path> plutôt que <line>/<polyline> :
       <mpath> ne sait suivre qu'un <path>. -->
  <path id="pUser" class="liaison" d="M88,271 L146,271"
        marker-end="url(#archArrow)" marker-start="url(#archArrow)"/>
  <path id="pUserRetour" d="M146,271 L88,271" fill="none" stroke="none"/>
  <path id="pItfLlm" class="liaison" d="M340,271 L431,271" marker-end="url(#archArrow)"/>
  <path id="pLlmExt" class="liaison" d="M615,271 L701,271" marker-end="url(#archArrow)"/>
  <path id="pLlmScg" class="liaison" d="M525,302 L525,386" marker-end="url(#archArrow)"/>
  <path id="pExtRag" class="liaison" d="M805,302 L805,325 L971,325"
        marker-end="url(#archArrow)"/>
  <path id="pScgFus" class="liaison" d="M537,452 L537,490 L700,490 L700,516"
        marker-end="url(#archArrow)"/>
  <path id="pRagFus" class="liaison" d="M1062,450 L1062,490 L840,490 L840,516"
        marker-end="url(#archArrow)"/>
  <path id="pFusItf" class="liaison" d="M770,582 L770,650 L255,650 L255,306"
        marker-end="url(#archArrow)"/>
  <text x="578" y="350" font-size="12.5" font-family="{MONO}" fill="{BLEU}">5 régénérations</text>
  <text x="578" y="368" font-size="12.5" font-family="{MONO}" fill="{BLEU}"
        opacity="0.8">températures croissantes</text>

  {MOUVEMENTS}
</svg>
"""
)

SCHEMA_HAUTEUR = 720

# ==============================================================================
# INTERFACE
# ==============================================================================
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
