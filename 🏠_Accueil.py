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
    header[data-testid="stHeader"] {
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
