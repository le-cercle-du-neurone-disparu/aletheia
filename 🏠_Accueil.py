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
    .block-container { padding-top: 5rem; }

    /* Le header étant hors flux, la colonne passerait dessous sans ce dégagement. */
    section[data-testid="stSidebar"] > div { padding-top: 3.5rem; }

    /* Le conteneur est une rangée flex dont la barre latérale est le premier
       élément : le header, placé après, se retrouvait décalé de sa largeur.
       `fixed` le sort de cette rangée — le faire passer en tête avec un
       flex-wrap renvoyait le contenu sous la colonne dès qu'elle s'ouvrait. */
    header[data-testid="stHeader"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        z-index: 999999 !important;
        background: #f0f2f6 !important;
        backdrop-filter: none !important;
        border-bottom: 1px solid #d6d9e0 !important;
    }
    /* La rangée de liens est le .rc-overflow du header : stTopNavLinkContainer
       n'enveloppe qu'un lien, le centrer ne déplacerait donc rien. Les classes
       st-emotion-cache-* changent d'un build à l'autre et ne sont pas des
       points d'accroche. */
    header[data-testid="stHeader"] .rc-overflow {
        width: 100%;
        justify-content: center;
    }
    [data-testid="stTopNavLink"],
    [data-testid="stTopNavLink"] * {
        color: #1a1a2e !important;
        font-weight: 600;
    }
    [data-testid="stTopNavLink"][aria-current="page"],
    [data-testid="stTopNavLink"][aria-current="page"] * {
        color: #667eea !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# L'ordre de cette liste est celui du menu.
PAGES = [
    st.Page("views/accueil.py", title="Accueil", icon="🏠", default=True),
    st.Page("views/comment.py", title="Comment ?", icon="🏗️", url_path="comment"),
    st.Page(
        "views/prediction.py", title="Prédiction", icon="🔎", url_path="prediction"
    ),
    st.Page("views/analyse.py", title="Analyse", icon="📊", url_path="analyse"),
    st.Page("views/equipe.py", title="Équipe", icon="👥", url_path="equipe"),
]

st.navigation(PAGES, position="top").run()

# Rendu après la page : le pied de page suit son contenu, quelle qu'elle soit.
st.markdown(
    """
<style>
    /* Même bandeau que le menu : fond et bordure repris du header pour que les
       deux barres se répondent. Il occupe sa colonne et non 100vw — décalé par
       la barre latérale, un bloc pleine fenêtre déborderait sur la droite. */
    .pied-de-page {
        margin: 3rem 0 0 0;
        width: 100%;
        padding: 0.9rem 1rem;
        background: #f0f2f6;
        border-top: 1px solid #d6d9e0;
        text-align: center;
        color: #1a1a2e;
    }
    .pied-de-page .avertissement {
        font-size: 0.85rem;
        font-style: italic;
        opacity: 0.85;
    }
    .pied-de-page .mentions {
        font-size: 0.8rem;
        opacity: 0.6;
        margin-top: 0.25rem;
    }
</style>
<div class="pied-de-page">
    <div class="avertissement">
        ⚠️ Les résultats sont indicatifs et ne remplacent pas une vérification humaine.
    </div>
    <div class="mentions">
        🚀 Propulsé par FastAPI &amp; Streamlit | Projet Berlue © 2026
    </div>
</div>
""",
    unsafe_allow_html=True,
)
