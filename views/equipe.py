"""
Page de présentation de l'équipe — Aletheia.
"""

import json

import streamlit as st

# ==============================================================================
# CONFIGURATION
# ==============================================================================


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
st.markdown(
    """
<style>
    .fiche-equipe p, .fiche-equipe li { font-size: 0.82rem; line-height: 1.45; }
    .fiche-equipe h3 { font-size: 1.05rem; margin-bottom: 0.1rem; }
</style>
""",
    unsafe_allow_html=True,
)

st.subheader("Équipe Aletheia / Berlue")

# Chargement des données
team_members = load_team_data("team.json")

if team_members:
    # Une colonne par membre : tout le monde tient dans la page, sans défilement.
    # Trié ici et non dans team.json : l'ordre reste alphabétique quel que soit
    # l'ordre d'ajout des membres au fichier. Casse ignorée, sans quoi les
    # pseudonymes en majuscules passeraient tous devant.
    membres = sorted(team_members, key=lambda m: m.get("name", "").casefold())

    for col, member in zip(st.columns(len(membres)), membres, strict=True):
        with col, st.container(border=True):
            st.markdown('<div class="fiche-equipe">', unsafe_allow_html=True)

            if member.get("photo_url"):
                st.image(member["photo_url"], width="stretch")

            st.markdown(f"### {member.get('name', 'Anonyme')}")
            if member.get("role"):
                st.caption(f"💼 {member['role']}")

            st.write(member.get("description", ""))

            github_link = member.get("github_url", "").strip()
            if github_link:
                st.link_button("🐙 GitHub", url=github_link)

            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Les membres de l'équipe n'ont pas encore été configurés.")
