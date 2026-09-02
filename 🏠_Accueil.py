"""
Point d'entrée Streamlit — Aletheia (Page d'accueil).
Présentation complète du projet Berlue.
"""

import requests
import streamlit as st
from pathlib import Path

from utils.api_client import API_URL, ENV_NAME

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Aletheia | Plateforme de Détection d'Hallucinations",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# CONSTANTES
# ==============================================================================
API_HEALTH_URL = f"{API_URL}/"

# ==============================================================================
# CHARGEMENT DU CSS EXTERNE
# ==============================================================================

def load_css():
    """Charge le fichier CSS depuis assets/style.css"""
    css_paths = [
        Path("assets/style.css"),
        Path("style.css"),
        Path("../assets/style.css"),
    ]
    
    for path in css_paths:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            return True
    
    return False

# ==============================================================================
# FONCTIONS DE VÉRIFICATION DE L'API
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
# CHARGEMENT DE L'IMAGE DE FOND
# ==============================================================================

def get_image_base64(image_path):
    """Convertit une image en base64 pour l'utiliser en CSS."""
    try:
        import base64
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, IOError):
        return None

def get_background_image_style():
    """Récupère le style CSS pour l'image de fond."""
    image_paths = [
        Path("Berlue.png"),
        Path("assets/Berlue.png"),
        Path("images/Berlue.png"),
        Path("../Berlue.png"),
    ]
    
    for path in image_paths:
        if path.exists():
            bg_image_base64 = get_image_base64(path)
            if bg_image_base64:
                return f"""
                html, body, .stApp, .stApp > div, .stApp > header, .stApp > .main {{
                    background-image: url("data:image/png;base64,{bg_image_base64}") !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-attachment: fixed !important;
                    background-repeat: no-repeat !important;
                }}
                """
    return ""

# ==============================================================================
# CHARGEMENT DES STYLES
# ==============================================================================

load_css()

bg_style = get_background_image_style()
if bg_style:
    st.markdown(f"<style>{bg_style}</style>", unsafe_allow_html=True)

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
<div class="hero-section">
    <h1>🏛️ Aletheia</h1>
    <div class="subtitle">Le Moteur de Vérité pour les LLMs</div>
    <div class="tagline">Détection d'hallucinations · Fact-checking automatisé</div>
    <div class="hero-badge-container">
        <span class="hero-badge">🔍 Berlue v1.0</span>
        <span class="hero-badge">🧠 FEVER + SelfCheckGPT</span>
        <span class="hero-badge">🤖 Llama · Mistral</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# VÉRIFICATION DE L'API BERLUE
# ==============================================================================

api_online = check_api_health()

if api_online:
    status_icon = "🟢"
    status_title = "API Berlue connectée"
    status_desc = f"L'API répond sur {API_URL} (environnement {ENV_NAME})."
    status_class = "status-success"
    status_dot = "online"
else:
    status_icon = "🔴"
    status_title = "API Berlue injoignable"
    status_desc = f"Aucune réponse de {API_URL} (environnement {ENV_NAME})."
    status_class = "status-error"
    status_dot = "offline"

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
        <button class="btn-refresh" onclick="location.reload()">🔄 Rafraîchir</button>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

feature_disabled = not api_online

# --- STATISTIQUES ---
st.markdown(
    """
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">4</div>
        <div class="stat-label">Membres de l'équipe</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">2</div>
        <div class="stat-label">Modes d'analyse</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">v1.0</div>
        <div class="stat-label">Version</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">∞</div>
        <div class="stat-label">Questions possibles</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ==============================================================================
# DESCRIPTION - VERSION AMÉLIORÉE
# ==============================================================================

st.markdown(
    """
<div style="
    background: rgba(20, 20, 30, 0.40);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin: 1.5rem auto;
    max-width: 900px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.30);
    transition: all 0.3s ease;
">
    <div style="
        font-size: 1.2rem;
        color: #f0f4ff;
        line-height: 1.9;
        text-shadow: 0 2px 30px rgba(0, 0, 0, 0.95);
    ">
        <span style="
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
            filter: drop-shadow(0 2px 20px rgba(102, 126, 234, 0.30));
        ">Aletheia</span>
        <span style="color: #ffffff; text-shadow: 0 2px 25px rgba(0, 0, 0, 0.95);">
            est votre tableau de bord interactif pour auditer, tester et évaluer 
            les grands modèles de langage (LLMs).
        </span>
    </div>
    <div style="
        margin-top: 1rem;
        font-size: 1.1rem;
        color: #e8ecff;
        line-height: 1.8;
        text-shadow: 0 2px 25px rgba(0, 0, 0, 0.95);
        opacity: 0.90;
    ">
        Grâce au moteur de fact-checking 
        <span style="
            color: #a8b5f0;
            font-weight: 600;
            text-shadow: 0 2px 25px rgba(168, 181, 240, 0.30);
        ">Berlue</span> 
        en arrière-plan, cette plateforme vous permet de mesurer la fiabilité des réponses générées.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# --- PROCESSUS BERLUE ---
st.markdown(
    '<div class="section-title">⚡ Le Processus Berlue</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="section-subtitle">Vérification d\'hallucinations en 4 étapes</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="process-grid">
    <div class="process-step">
        <div class="step-number">1</div>
        <span class="step-icon">❓</span>
        <div class="step-title">Question</div>
        <div class="step-desc">L'utilisateur pose une question à un LLM local</div>
    </div>
    <div class="process-step">
        <div class="step-number">2</div>
        <span class="step-icon">✂️</span>
        <div class="step-title">Découpage</div>
        <div class="step-desc">Berlue découpe la réponse en affirmations</div>
    </div>
    <div class="process-step">
        <div class="step-number">3</div>
        <span class="step-icon">🔍</span>
        <div class="step-title">Vérification</div>
        <div class="step-desc">RAG inversé + auto-cohérence (SelfCheckGPT)</div>
    </div>
    <div class="process-step">
        <div class="step-number">4</div>
        <span class="step-icon">🎯</span>
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

# ==============================================================================
# ALERTE API INDISPONIBLE - VERSION AMÉLIORÉE
# ==============================================================================

if feature_disabled:
    st.markdown(
        """
<div style="
    background: linear-gradient(135deg, rgba(255, 70, 70, 0.10), rgba(255, 150, 50, 0.06));
    border: 1px solid rgba(255, 70, 70, 0.18);
    border-radius: 16px;
    padding: 1.2rem 1.8rem;
    margin: 0.5rem 0 1.5rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 4px 30px rgba(255, 70, 70, 0.06);
    transition: all 0.3s ease;
">
    <div style="font-size: 2.2rem; flex-shrink: 0;">⚠️</div>
    <div style="flex: 1;">
        <div style="color: #ff6b6b; font-weight: 600; font-size: 1.05rem; text-shadow: 0 2px 20px rgba(0,0,0,0.9);">
            API Berlue indisponible
        </div>
        <div style="color: #f0f4ff; font-size: 0.95rem; opacity: 0.85; text-shadow: 0 2px 15px rgba(0,0,0,0.9);">
            Le serveur API n'est pas accessible. Lancez l'API avec 
            <code style="
                background: rgba(255,255,255,0.08); 
                padding: 0.15rem 0.7rem; 
                border-radius: 6px; 
                color: #a8b5f0;
                font-size: 0.9rem;
                font-weight: 500;
                text-shadow: 0 2px 10px rgba(0,0,0,0.8);
            ">uv run api.py</code> 
            pour débloquer les fonctionnalités.
        </div>
    </div>
    <div style="flex-shrink: 0;">
        <button onclick="location.reload()" style="
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            text-shadow: 0 2px 10px rgba(0,0,0,0.6);
        "
        onmouseover="this.style.background='rgba(255,255,255,0.12)'; this.style.borderColor='rgba(255,255,255,0.20)'"
        onmouseout="this.style.background='rgba(255,255,255,0.06)'; this.style.borderColor='rgba(255,255,255,0.10)'">
            🔄 Rafraîchir
        </button>
    </div>
</div>
""",
        unsafe_allow_html=True,
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
        <a href="/Prediction" target="_self" class="btn-primary {"btn-disabled" if feature_disabled else ""}" {'style="pointer-events: none; opacity: 0.40;"' if feature_disabled else ""}>
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
        <a href="/Evaluation" target="_self" class="btn-primary {"btn-disabled" if feature_disabled else ""}" {'style="pointer-events: none; opacity: 0.40;"' if feature_disabled else ""}>
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
    '<div class="section-title">📖 À propos du projet</div>', unsafe_allow_html=True
)

st.markdown(
    """
<div class="about-grid">
    <div class="about-item">
        <div class="label">Moteur de vérification</div>
        <div class="value">Berlue <span class="badge">v1.0</span></div>
    </div>
    <div class="about-item">
        <div class="label">Méthode de détection</div>
        <div class="value">FEVER + SelfCheckGPT <span class="badge">Hybride</span></div>
    </div>
    <div class="about-item">
        <div class="label">Datasets d'évaluation</div>
        <div class="value">HaluEval · TruthfulQA</div>
    </div>
    <div class="about-item">
        <div class="label">Modèles supportés</div>
        <div class="value">Llama · Mistral <span class="badge">+ en cours</span></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- FOOTER ---
st.markdown(
    """
<div class="footer">
    <div class="disclaimer">
        ⚠️ Les résultats sont indicatifs et ne remplacent pas une vérification humaine.
    </div>
    <div class="copyright">
        🚀 Propulsé par FastAPI &amp; Streamlit | Projet Berlue © 2026
    </div>
</div>
""",
    unsafe_allow_html=True,
)