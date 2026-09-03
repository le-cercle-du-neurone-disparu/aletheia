"""
Point d'entrée Streamlit — Aletheia (Page d'accueil).
Présentation complète du projet Berlue.
"""

from pathlib import Path

import requests
import streamlit as st

from utils.api_client import API_URL, ENV_NAME

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# ==============================================================================
# CONSTANTES
# ==============================================================================
API_HEALTH_URL = f"{API_URL}/"

# ==============================================================================
# FONCTIONS DE VÉRIFICATION ET DE LANCEMENT DE L'API
# ==============================================================================


def check_api_health():
    """
    Vérifie si l'API Berlue est accessible.
    Retourne True si l'API répond, False sinon.
    """
    try:
        response = requests.get(API_HEALTH_URL, timeout=10)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


# ==============================================================================
# STYLES PERSONNALISÉS AVEC IMAGE DE FOND
# ==============================================================================


# Fonction pour encoder l'image en base64
def get_image_base64(image_path):
    """Convertit une image en base64 pour l'utiliser en CSS."""
    try:
        import base64

        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.warning(f"⚠️ Image non trouvée : {image_path}")
        return None


# Récupérer l'image - essayons plusieurs chemins possibles
image_paths = [
    Path("Berlue.png"),
    Path("assets/Berlue.png"),
    Path("images/Berlue.png"),
    Path("../Berlue.png"),
]

bg_image_base64 = None
for path in image_paths:
    if path.exists():
        bg_image_base64 = get_image_base64(path)
        if bg_image_base64:
            break

# Construction du style avec arrière-plan
if bg_image_base64:
    background_style = f"""
    /* Forcer l'arrière-plan sur tous les éléments */
    html, body, .stApp, .stApp > div, .stApp > header, .stApp > .main {{
        background-image: url("data:image/png;base64,{bg_image_base64}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }}
    
    /* Overlay pour améliorer la lisibilité du contenu */
    .stApp::before {{
        content: '';
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        background: rgba(10, 10, 15, 0.85) !important;
        z-index: 0 !important;
        pointer-events: none !important;
    }}
    
    /* S'assurer que le contenu est au-dessus de l'overlay */
    .stApp > div {{
        position: relative !important;
        z-index: 1 !important;
    }}
    
    /* Forcer la transparence du header Streamlit */
    header {{
        background: rgba(10, 10, 15, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(45, 45, 68, 0.3) !important;
    }}
    
    /* Sidebar avec transparence */
    .css-1d391kg, .css-1lcbmhc, .st-emotion-cache-1d391kg, .st-emotion-cache-1lcbmhc {{
        background: rgba(10, 10, 15, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(45, 45, 68, 0.3) !important;
    }}
    """
else:
    background_style = ""

st.markdown(
    f"""
<style>
    /* ===== VARIABLES ===== */
    :root {{
        --primary: #667eea;
        --primary-dark: #5a67d8;
        --secondary: #764ba2;
        --success: #48bb78;
        --warning: #ed8936;
        --danger: #fc8181;
        --bg-dark: #0a0a0f;
        --bg-card: rgba(20, 20, 30, 0.92);
        --bg-card-hover: rgba(26, 26, 46, 0.95);
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --border-color: rgba(45, 45, 68, 0.8);
    }}

    /* ===== ARRIÈRE-PLAN ===== */
    {background_style}

    /* ===== BASE ===== */
    .stApp {{
        background: rgba(10, 10, 15, 0.9) !important;
    }}
    
    /* ===== CARTES AVEC FOND TRANSPARENT ===== */
    .hero-section {{
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.85) 0%, rgba(118, 75, 162, 0.85) 100%) !important;
        backdrop-filter: blur(10px) !important;
        padding: 3.5rem 2.5rem !important;
        border-radius: 20px !important;
        text-align: center !important;
        margin-bottom: 2.5rem !important;
        position: relative !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}
    
    .hero-section::before {{
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        right: -20% !important;
        width: 60% !important;
        height: 200% !important;
        background: rgba(255,255,255,0.05) !important;
        transform: rotate(25deg) !important;
        pointer-events: none !important;
    }}
    
    .hero-section::after {{
        content: '✦' !important;
        position: absolute !important;
        bottom: 10px !important;
        right: 30px !important;
        font-size: 3rem !important;
        opacity: 0.1 !important;
        color: white !important;
    }}
    
    .hero-section h1 {{
        font-size: 4rem !important;
        font-weight: 800 !important;
        color: white !important;
        margin: 0 !important;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        letter-spacing: -0.02em !important;
    }}
    
    .hero-section .subtitle {{
        font-size: 1.15rem !important;
        color: rgba(255,255,255,0.9) !important;
        margin-top: 0.5rem !important;
        font-weight: 300 !important;
        letter-spacing: 0.02em !important;
    }}
    
    .hero-section .tagline {{
        font-size: 0.95rem !important;
        color: rgba(255,255,255,0.75) !important;
        margin-top: 0.3rem !important;
        font-weight: 300 !important;
    }}
    
    .hero-section .badge-container {{
        display: flex !important;
        justify-content: center !important;
        gap: 0.8rem !important;
        margin-top: 1rem !important;
        flex-wrap: wrap !important;
    }}
    
    .hero-badge {{
        background: rgba(255,255,255,0.15) !important;
        backdrop-filter: blur(10px) !important;
        padding: 0.3rem 1.2rem !important;
        border-radius: 20px !important;
        color: white !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}

    /* ===== API STATUS CARD ===== */
    .api-status-card {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1.5rem 2rem !important;
        margin: 1.5rem 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        flex-wrap: wrap !important;
        gap: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .api-status-card.status-success {{
        border-color: var(--success) !important;
    }}
    
    .api-status-card.status-warning {{
        border-color: var(--warning) !important;
    }}
    
    .api-status-card.status-error {{
        border-color: var(--danger) !important;
    }}
    
    .api-status-left {{
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
    }}
    
    .api-status-icon {{
        font-size: 2rem !important;
    }}
    
    .api-status-text {{
        display: flex !important;
        flex-direction: column !important;
    }}
    
    .api-status-title {{
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }}
    
    .api-status-desc {{
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
    }}
    
    .api-status-right {{
        display: flex !important;
        gap: 0.8rem !important;
        align-items: center !important;
        flex-wrap: wrap !important;
    }}
    
    .btn-launch-api {{
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 1.8rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }}
    
    .btn-launch-api:hover {{
        transform: scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }}
    
    .btn-launch-api:disabled {{
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }}
    
    .btn-refresh {{
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color) !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }}
    
    .btn-refresh:hover {{
        border-color: var(--primary) !important;
        color: var(--text-primary) !important;
    }}
    
    .status-dot {{
        display: inline-block !important;
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        margin-right: 8px !important;
    }}
    
    .status-dot.online {{
        background: var(--success) !important;
        box-shadow: 0 0 10px rgba(72, 187, 120, 0.5) !important;
    }}
    
    .status-dot.offline {{
        background: var(--danger) !important;
        box-shadow: 0 0 10px rgba(252, 129, 129, 0.5) !important;
    }}
    
    .status-dot.warning {{
        background: var(--warning) !important;
        box-shadow: 0 0 10px rgba(237, 137, 54, 0.5) !important;
    }}

    /* ===== STATS ===== */
    
    
    
    
    
    /* ===== SECTION TITLE ===== */
    .section-title {{
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin: 2rem 0 1rem 0 !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
    }}
    
    .section-subtitle {{
        color: var(--text-secondary) !important;
        font-size: 1.05rem !important;
        margin-bottom: 1.5rem !important;
    }}
    
    /* ===== PROCESS STEPS ===== */
    .process-grid {{
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 1rem !important;
        margin: 1.5rem 0 !important;
    }}
    
    .process-step {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }}
    
    .process-step:hover {{
        border-color: var(--primary) !important;
        transform: translateY(-4px) !important;
    }}
    
    .process-step .step-number {{
        display: inline-block !important;
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        line-height: 32px !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .process-step .step-icon {{
        font-size: 2.5rem !important;
        margin: 0.3rem 0 !important;
    }}
    
    .process-step .step-title {{
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }}
    
    .process-step .step-desc {{
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        margin-top: 0.3rem !important;
        line-height: 1.5 !important;
    }}
    
    /* ===== FEATURE CARDS ===== */
    .feature-grid {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 1.5rem !important;
        margin: 1.5rem 0 !important;
    }}
    
    .feature-card {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        padding: 2rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    
    .feature-card::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 3px !important;
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
    }}
    
    .feature-card:hover {{
        transform: translateY(-6px) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2) !important;
    }}
    
    .feature-card:hover::before {{
        opacity: 1 !important;
    }}
    
    .feature-card .icon {{
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .feature-card h3 {{
        color: var(--text-primary) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin: 0.5rem 0 !important;
    }}
    
    .feature-card .description {{
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        flex-grow: 1 !important;
    }}
    
    .feature-card ul {{
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        padding-left: 1.2rem !important;
        margin: 0.5rem 0 1rem 0 !important;
        list-style: none !important;
    }}
    
    .feature-card ul li {{
        padding: 0.25rem 0 !important;
        position: relative !important;
        padding-left: 1.5rem !important;
    }}
    
    .feature-card ul li::before {{
        content: '▸' !important;
        position: absolute !important;
        left: 0 !important;
        color: var(--primary) !important;
        font-weight: bold !important;
    }}
    
    .feature-card .btn-primary {{
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
        margin-top: auto !important;
        text-decoration: none !important;
        display: inline-block !important;
        width: fit-content !important;
    }}
    
    .feature-card .btn-primary:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }}
    
    .feature-card .btn-primary:disabled {{
        opacity: 0.4 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }}
    
    /* ===== ABOUT PROJECT ===== */
    .about-grid {{
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 1rem !important;
        margin: 1rem 0 !important;
    }}
    
    .about-item {{
        background: var(--bg-card) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        padding: 1.2rem !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }}
    
    .about-item:hover {{
        border-color: var(--primary) !important;
    }}

    .about-item .detail {{
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
        line-height: 1.5 !important;
        margin-top: 0.6rem !important;
        text-align: left !important;
    }}
    
    .about-item .label {{
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    
    .about-item .value {{
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin-top: 0.2rem !important;
    }}
    
    .about-item .badge {{
        display: inline-block !important;
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        padding: 0.1rem 0.8rem !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }}
    
    /* ===== FOOTER ===== */
    .footer {{
        margin-top: 3rem !important;
        padding: 2rem 0 1rem 0 !important;
        border-top: 1px solid var(--border-color) !important;
        text-align: center !important;
    }}
    
    .footer .disclaimer {{
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
        opacity: 0.7 !important;
        font-style: italic !important;
    }}
    
    .footer .copyright {{
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        opacity: 0.5 !important;
        margin-top: 0.5rem !important;
    }}
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {{
        .process-grid, .about-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
        }}
        .feature-grid {{
            grid-template-columns: 1fr !important;
        }}
        .hero-section h1 {{
            font-size: 2.5rem !important;
        }}
        .api-status-card {{
            flex-direction: column !important;
            align-items: stretch !important;
            text-align: center !important;
        }}
        .api-status-left {{
            flex-direction: column !important;
        }}
        .api-status-right {{
            justify-content: center !important;
            flex-wrap: wrap !important;
        }}
    }}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# INITIALISATION DE L'ÉTAT DE SESSION
# ==============================================================================
if "api_launching" not in st.session_state:
    st.session_state.api_launching = False

if "api_launch_result" not in st.session_state:
    st.session_state.api_launch_result = None

# ==============================================================================
# CONTENU DE LA PAGE D'ACCUEIL
# ==============================================================================

# --- HERO SECTION ---
st.markdown(
    """
<style>
    /* Le cadre passe en trois parties : une figure, le texte, une figure. Les
       z-index gardent les images au-dessus du reflet décoratif du ::before. */
    .hero-section {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 2.5rem !important;
    }
    .hero-contenu { flex: 1 1 auto; position: relative; z-index: 1; }
    /* Streamlit accroche une ancre de lien à chaque titre : elle n'a pas de
       sens sur une page d'une seule section, et déborde du cadre. */
    .hero-section a[href^="#"] { display: none !important; }
    .hero-figure {
        flex: 0 0 auto;
        height: 300px;
        width: auto;
        border-radius: 14px;
        position: relative;
        z-index: 1;
    }
    /* Sous cette largeur les figures écraseraient le texte : le titre prime. */
    @media (max-width: 1100px) {
        .hero-figure { display: none; }
    }

    /* Seconde bande, sous le cadre du titre : même famille, en plus discret. */
    .intro-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.72) 0%, rgba(118, 75, 162, 0.72) 100%);
        backdrop-filter: blur(10px);
        padding: 1.6rem 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2.5rem;
        text-align: center;
    }
    .intro-section p {
        color: #ffffff;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0 auto;
        max-width: 900px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-section">
    <!-- Chemin relatif et non /app/static : un préfixe d'URL, tel qu'en pose un
         hébergement sous chemin, casserait la forme absolue. -->
    <img class="hero-figure" src="app/static/berlue-idle.webp" alt="Berlue">
    <div class="hero-contenu">
    <h1>🏛️ Aletheia</h1>
    <div class="subtitle">Le Moteur de Vérité pour les LLMs</div>
    <div class="tagline">Détection d'hallucinations · Fact-checking automatisé</div>
    <div class="badge-container">
        <span class="hero-badge">🧠 FEVER + SelfCheckGPT</span>
        <span class="hero-badge">🤖 Llama</span>
    </div>
    </div>
    <img class="hero-figure" src="app/static/aletheia.webp" alt="Aletheia">
</div>

<div class="intro-section">
    <p>
        <strong>Aletheia</strong> est votre tableau de bord interactif pour auditer, tester et
        évaluer les grands modèles de langage (LLMs). Grâce au moteur de fact-checking
        <strong>Berlue</strong> en arrière-plan, cette plateforme vous permet de mesurer la
        fiabilité des réponses générées.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# VÉRIFICATION DE L'API BERLUE
# ==============================================================================

# Vérifier l'état de l'API
api_online = check_api_health()

# Déterminer le statut
if api_online:
    status_icon = "🟢"
    status_title = "API Berlue connectée"
    status_desc = f"Environnement {ENV_NAME}."
    status_class = "status-success"
    status_dot = "online"
else:
    status_icon = "🔴"
    status_title = "API Berlue injoignable"
    status_desc = f"Aucune réponse du backend (environnement {ENV_NAME})."
    status_class = "status-error"
    status_dot = "offline"

# Afficher la carte de statut
# Tout en un seul appel : Streamlit referme le conteneur de chaque st.markdown,
# donc une carte ouverte dans l'un et fermée dans l'autre laisse son contenu
# retomber en dehors. Le rafraîchissement est un lien et non un bouton à
# `onclick` : le JavaScript en ligne est retiré à l'assainissement.
st.markdown(
    f"""
<div class="api-status-card {status_class}">
    <div class="api-status-left">
        <div class="api-status-icon">{status_icon}</div>
        <div class="api-status-text">
            <div class="api-status-title">
                <span class="status-dot {status_dot}"></span>
                {status_title}
            </div>
            <div class="api-status-desc">{status_desc}</div>
        </div>
    </div>
    <div class="api-status-right">
        <a class="btn-refresh" href="/" target="_self">🔄 Rafraîchir</a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Si l'API n'est pas disponible, désactiver les liens vers les autres pages
feature_disabled = not api_online

# --- PROCESSUS BERLUE ---
st.markdown(
    '<div class="section-title">⚡ Le Processus Berlue</div>', unsafe_allow_html=True
)

st.markdown(
    """
<div class="process-grid">
    <div class="process-step">
        <div class="step-number">1</div>
        <div class="step-icon">❓</div>
        <div class="step-title">Question</div>
        <div class="step-desc">L'utilisateur pose une question à un LLM local</div>
    </div>
    <div class="process-step">
        <div class="step-number">2</div>
        <div class="step-icon">✂️</div>
        <div class="step-title">Découpage</div>
        <div class="step-desc">Berlue découpe la réponse en affirmations</div>
    </div>
    <div class="process-step">
        <div class="step-number">3</div>
        <div class="step-icon">🔍</div>
        <div class="step-title">Vérification</div>
        <div class="step-desc">RAG inversé + auto-cohérence (SelfCheckGPT)</div>
    </div>
    <div class="process-step">
        <div class="step-number">4</div>
        <div class="step-icon">🎯</div>
        <div class="step-title">Résultat</div>
        <div class="step-desc">Surlignage vert/orange/rouge avec preuves</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# --- FEATURES ---
st.markdown(
    '<div class="section-title">🚀 Explorez Aletheia</div>', unsafe_allow_html=True
)

# Désactiver les liens si l'API n'est pas disponible
if feature_disabled:
    st.warning(
        "⚠️ L'API Berlue n'est pas disponible. Lancez l'API ci-dessus pour accéder aux fonctionnalités de prédiction et d'évaluation."
    )

st.markdown(
    f"""
<div class="feature-grid">
    <div class="feature-card">
        <div class="icon">🔎</div>
        <h3>Prédiction</h3>
        <div class="description">Test unitaire — Exploration en direct</div>
        <ul>
            <li>Posez une question au modèle de votre choix</li>
            <li>Obtenez la réponse brute et analysée</li>
            <li>Identifiez les hallucinations avec code couleur</li>
            <li>Vérifiez les sources utilisées pour chaque affirmation</li>
        </ul>
        <a href="/prediction" target="_self" class="btn-primary {"btn-disabled" if feature_disabled else ""}" {'style="pointer-events: none; opacity: 0.5;"' if feature_disabled else ""}>
            {"🔒 " if feature_disabled else "🔍 "}Accéder à l'Explorateur
        </a>
    </div>
    <div class="feature-card">
        <div class="icon">📊</div>
        <h3>Évaluation</h3>
        <div class="description">Benchmark — Preuve de pertinence</div>
        <ul>
            <li>Lancez des tests sur HaluEval &amp; TruthfulQA</li>
            <li>Comparez Baseline vs Berlue</li>
            <li>Visualisez les matrices de confusion (2×3)</li>
            <li>Analysez les performances globales</li>
        </ul>
        <a href="/analyse" target="_self" class="btn-primary {"btn-disabled" if feature_disabled else ""}" {'style="pointer-events: none; opacity: 0.5;"' if feature_disabled else ""}>
            {"🔒 " if feature_disabled else "📈 "}Accéder au Benchmark
        </a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# --- À PROPOS DU PROJET ---
st.markdown(
    """
<div class="about-grid">
    <div class="about-item">
        <div class="label">Moteur de vérification</div>
        <div class="value">Berlue <span class="badge">v1.0</span></div>
        <div class="detail">
            L'API qui découpe la réponse du modèle en affirmations vérifiables,
            confronte chacune aux sources, puis rend un verdict et un score de
            confiance.
        </div>
    </div>
    <div class="about-item">
        <div class="label">Méthode de détection</div>
        <div class="value">FEVER + SelfCheckGPT <span class="badge">Hybride</span></div>
        <div class="detail">
            Deux avis indépendants : le RAG cherche une preuve dans le corpus
            FEVER, SelfCheckGPT mesure si le modèle se contredit d'un
            échantillon à l'autre. La fusion tranche.
        </div>
    </div>
    <div class="about-item">
        <div class="label">Datasets d'évaluation</div>
        <div class="value">HaluEval · TruthfulQA</div>
        <div class="detail">
            Jeux de questions dont la réponse attendue est connue : ils servent
            à mesurer ce que Berlue détecte vraiment, plutôt qu'à le supposer.
        </div>
    </div>
    <div class="about-item">
        <div class="label">Modèles supportés</div>
        <div class="value">Tous les modèles Ollama</div>
        <div class="detail">
            Llama, Mistral, Qwen, Gemma, Phi… tout ce que sert le serveur
            Ollama configuré. La liste du sélecteur vient de lui, elle suit donc
            ce qui y est réellement installé.
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
