"""
Point d'entrée Streamlit — Aletheia.

Déclare la navigation horizontale et délègue le contenu aux vues de `views/`.
Le dossier `pages/` n'est pas utilisé : sa convention impose un menu latéral et
un ordre dicté par les noms de fichiers.
"""

import streamlit as st

st.set_page_config(
    page_title="Aletheia | Plateforme de Détection d'Hallucinations",
    page_icon="🏛️",
    layout="wide",
    # « auto » et non « collapsed » : la navigation est passée en haut, mais la
    # page Prédiction garde ses réglages dans la barre latérale, qui doit donc
    # s'ouvrir d'elle-même là où elle sert.
    initial_sidebar_state="auto",
)

# Le menu vit dans <header>, auquel la vue Accueil impose un fond sombre en
# `!important`. Ces règles le reprennent avec une spécificité supérieure — un
# attribut en plus sur le même élément — sans quoi les libellés, sombres en
# thème clair, disparaissent sur ce fond.
st.markdown(
    """
<style>
    /* Marge haute par défaut de Streamlit : elle laisse un vide sous le menu,
       qui n'a plus lieu d'être depuis que la navigation occupe le header. */
    /* Les deux barres étant hors flux, le contenu passerait dessous sans ces
       dégagements — en haut pour le menu, en bas pour le pied de page. */
    .block-container { padding-top: 5rem; padding-bottom: 5rem; }
    section[data-testid="stSidebar"] > div {
        padding-top: 3.5rem;
        padding-bottom: 4.5rem;
    }

    /* Le conteneur est une rangée flex dont la barre latérale est le premier
       élément : le header, placé après, se retrouvait décalé de sa largeur.
       `fixed` le sort de cette rangée — le faire passer en tête avec un
       flex-wrap renvoyait le contenu sous la colonne dès qu'elle s'ouvrait. */
    /* Aucune couleur imposée : Streamlit habille son bandeau selon le thème, et
       y place des icônes — le menu de réglages, la flèche de la colonne —
       claires en sombre. Les forcer sur un fond clair les rendait invisibles.
       Ne reste ici que le positionnement. */
    header[data-testid="stHeader"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        z-index: 999999 !important;
    }
    /* La rangée de liens est le .rc-overflow du header : stTopNavLinkContainer
       n'enveloppe qu'un lien, le centrer ne déplacerait donc rien. Les classes
       st-emotion-cache-* changent d'un build à l'autre et ne sont pas des
       points d'accroche. */
    header[data-testid="stHeader"] .rc-overflow {
        width: 100%;
        justify-content: center;
    }
    [data-testid="stTopNavLink"] { font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# L'ordre de cette liste est celui du menu.
PAGES = [
    st.Page("views/accueil.py", title="Accueil", icon="🏠", default=True),
    st.Page("views/equipe.py", title="Équipe", icon="👥", url_path="equipe"),
    st.Page(
        "views/prediction.py", title="Prédiction", icon="🔎", url_path="prediction"
    ),
    st.Page("views/comment.py", title="Comment ?", icon="🏗️", url_path="comment"),
    st.Page("views/analyse.py", title="Analyse", icon="📊", url_path="analyse"),
]

st.navigation(PAGES, position="top").run()

# Rendu après la page : le pied de page suit son contenu, quelle qu'elle soit.
st.markdown(
    """
<style>
    /* Barre fixée en bas, pendant du menu : même fond, même bordure, toute la
       largeur de la fenêtre. `fixed` la sort du flux, donc sa place dans le
       document n'a pas d'importance et la colonne ne la décale pas. */
    .pied-de-page {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100vw;
        padding: 0.5rem 1rem;
        /* Teinte neutre plutôt qu'une couleur fixe : elle s'assombrit sur fond
           clair et s'éclaircit sur fond sombre, sans jamais masquer le texte. */
        background: rgba(128, 128, 128, 0.12);
        backdrop-filter: blur(6px);
        border-top: 1px solid rgba(128, 128, 128, 0.25);
        text-align: center;
        color: inherit;
        z-index: 999998;
    }
    .pied-de-page .avertissement {
        font-size: 0.82rem;
        font-style: italic;
        opacity: 0.85;
    }
    .pied-de-page .separateur {
        opacity: 0.4;
        margin: 0 0.5rem;
    }
    .pied-de-page .mentions {
        font-size: 0.76rem;
        opacity: 0.6;
    }
</style>
<div class="pied-de-page">
    <span class="avertissement">⚠️ Les résultats sont indicatifs et ne remplacent pas une vérification humaine.</span><span class="separateur">-</span><span class="mentions">🚀 Propulsé par FastAPI &amp; Streamlit | Projet Berlue © 2026</span>
</div>
""",
    unsafe_allow_html=True,
)
