"""
Page de présentation de l'équipe — Aletheia.
"""

import json

import streamlit as st

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="L'Équipe | Aletheia", page_icon="👥", layout="wide")


# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================
@st.cache_data
def load_team_data(filepath: str = "team.json") -> list[dict]:
    """Charge les données de l'équipe depuis le fichier JSON."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"❌ Le fichier {filepath} est introuvable.")
        return []
    except json.JSONDecodeError:
        st.error(f"❌ Le fichier {filepath} est mal formaté (Erreur JSON).")
        return []


# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
st.title("👥 L'Équipe derrière Berlue")
st.markdown(
    "Découvrez les esprits passionnés qui ont construit le moteur de fact-checking **Berlue** et l'interface **Aletheia**."
)
st.divider()

# Chargement des données
team_members = load_team_data("team.json")

if team_members:
    # Affichage dynamique sous forme de grille (2 personnes par ligne)
    # range(0, len, 2) permet de faire des pas de 2
    for i in range(0, len(team_members), 2):
        cols = st.columns(2)  # Crée 2 colonnes pour la ligne actuelle

        for j in range(2):
            # Vérifie si on ne dépasse pas la taille de la liste (ex: nombre impair de membres)
            if i + j < len(team_members):
                member = team_members[i + j]

                with cols[j], st.container(border=True):
                    img_col, text_col = st.columns([1, 2])

                    with img_col:
                        # Affiche l'image (marche avec des URL ou des chemins locaux)
                        if member.get("photo_url"):
                            st.image(member["photo_url"], use_container_width=True)

                    with text_col:
                        st.subheader(member.get("name", "Anonyme"))
                        # Affiche le rôle en gris (caption) s'il existe
                        if member.get("role"):
                            st.caption(f"💼 {member['role']}")

                        st.write(member.get("description", ""))

                        # Affiche le bouton GitHub uniquement si l'URL est remplie
                        github_link = member.get("github_url", "").strip()
                        if github_link:
                            st.link_button("🐙 Voir le GitHub", url=github_link)
else:
    st.info("Les membres de l'équipe n'ont pas encore été configurés.")
