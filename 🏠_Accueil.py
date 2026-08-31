"""
Point d'entrée Streamlit — Aletheia (Page d'accueil).
Présentation complète du projet Berlue.
"""

import streamlit as st
from datetime import datetime
import requests
import subprocess
import os
import sys
import time
import socket
import platform

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Aletheia | Plateforme de Détection d'Hallucinations",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CONSTANTES
# ==============================================================================
API_URL = "http://localhost:8000"
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
        response = requests.get(API_HEALTH_URL, timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

def is_port_in_use(port=8000):
    """
    Vérifie si le port est déjà utilisé.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except socket.error:
            return True

def open_terminal_and_run_command():
    """
    Ouvre un terminal et exécute les commandes pour lancer l'API.
    """
    # Chemin vers le projet
    project_path = "/opt/wagon/src/berlue"
    
    # Déterminer le système d'exploitation
    system = platform.system()
    
    # Commandes à exécuter
    if system == "Windows":
        # Windows - utilise cmd
        cmd = [
            "start", "cmd", "/k",
            f"cd /d {project_path} && make run_api"
        ]
        # Alternative avec PowerShell
        # cmd = ["powershell", "-Command", f"Start-Process cmd -ArgumentList '/k cd {project_path} && make run_api'"]
        
    elif system == "Darwin":  # macOS
        # macOS - utilise Terminal.app
        cmd = [
            "osascript", 
            "-e", 
            f'tell application "Terminal" to do script "cd {project_path} && make run_api"'
        ]
        # Alternative avec iTerm2 si disponible
        # cmd = [
        #     "osascript",
        #     "-e",
        #     f'tell application "iTerm" to create window with default profile command "cd {project_path} && make run_api"'
        # ]
        
    else:  # Linux
        # Linux - essaie plusieurs terminaux
        terminals = [
            ["gnome-terminal", "--", "bash", "-c", f"cd {project_path} && make run_api; exec bash"],
            ["konsole", "-e", "bash", "-c", f"cd {project_path} && make run_api; exec bash"],
            ["xterm", "-e", "bash", "-c", f"cd {project_path} && make run_api; exec bash"],
            ["xfce4-terminal", "--command", f"bash -c 'cd {project_path} && make run_api; exec bash'"],
            ["terminator", "-x", "bash", "-c", f"cd {project_path} && make run_api; exec bash"]
        ]
        
        for terminal_cmd in terminals:
            try:
                subprocess.Popen(terminal_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, f"Terminal ouvert avec {terminal_cmd[0]}"
            except FileNotFoundError:
                continue
        
        return False, "Aucun terminal trouvé sur ce système Linux"
    
    try:
        # Exécuter la commande pour ouvrir le terminal
        if system == "Windows":
            subprocess.Popen(cmd, shell=True)
        elif system == "Darwin":
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(cmd)
        
        return True, f"Terminal ouvert. Lancement de l'API dans le dossier {project_path}"
    
    except Exception as e:
        return False, f"Erreur lors de l'ouverture du terminal : {str(e)}"

def open_terminal_with_detailed_commands():
    """
    Ouvre un terminal et exécute les commandes étape par étape.
    """
    system = platform.system()
    project_path = "/opt/wagon/src/berlue"
    
    # Script avec les commandes complètes
    commands = f"""
echo "🚀 Lancement de l'API Berlue..."
echo "📂 Répertoire : {project_path}"

# Se déplacer dans le répertoire du projet
cd {project_path}
echo "✅ Dans le répertoire : $(pwd)"

# Afficher le contenu pour vérifier
echo "📋 Contenu du répertoire :"
ls -la

# Lancer l'API avec make
echo "🚀 make run_api..."
make run_api
"""
    
    if system == "Windows":
        # Windows
        cmd = [
            "start", "cmd", "/k",
            f"cd /d {project_path} && echo Lancement de l'API Berlue... && make run_api"
        ]
        return subprocess.Popen(cmd, shell=True)
        
    elif system == "Darwin":  # macOS
        # macOS avec Terminal.app
        cmd = [
            "osascript",
            "-e",
            f'tell application "Terminal" to do script "cd {project_path} && echo \\"🚀 Lancement de l\\\'API Berlue...\\" && echo \\"📂 Répertoire : $(pwd)\\" && make run_api"'
        ]
        return subprocess.Popen(cmd, shell=True)
        
    else:  # Linux
        # Linux
        cmd = ["gnome-terminal", "--", "bash", "-c", f"cd {project_path} && echo '🚀 Lancement de l\\'API Berlue...' && echo '📂 Répertoire : $(pwd)' && make run_api; exec bash"]
        
        # Essayer différents terminaux
        terminals = [
            ["gnome-terminal", "--", "bash", "-c", f"cd {project_path} && echo '🚀 Lancement de l\\'API...' && make run_api; exec bash"],
            ["konsole", "-e", "bash", "-c", f"cd {project_path} && echo '🚀 Lancement de l\\'API...' && make run_api; exec bash"],
            ["xterm", "-e", "bash", "-c", f"cd {project_path} && echo '🚀 Lancement de l\\'API...' && make run_api; exec bash"]
        ]
        
        for terminal_cmd in terminals:
            try:
                return subprocess.Popen(terminal_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                continue
        
        return None

# ==============================================================================
# STYLES PERSONNALISÉS
# ==============================================================================
st.markdown("""
<style>
    /* ===== VARIABLES ===== */
    :root {
        --primary: #667eea;
        --primary-dark: #5a67d8;
        --secondary: #764ba2;
        --success: #48bb78;
        --warning: #ed8936;
        --danger: #fc8181;
        --bg-dark: #0a0a0f;
        --bg-card: #14141e;
        --bg-card-hover: #1a1a2e;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --border-color: #2d2d44;
    }

    /* ===== BASE ===== */
    .stApp {
        background: var(--bg-dark);
    }
    
    /* ===== HEADER HERO ===== */
    .hero-section {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 3.5rem 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 60%;
        height: 200%;
        background: rgba(255,255,255,0.05);
        transform: rotate(25deg);
        pointer-events: none;
    }
    
    .hero-section::after {
        content: '✦';
        position: absolute;
        bottom: 10px;
        right: 30px;
        font-size: 4rem;
        opacity: 0.1;
        color: white;
    }
    
    .hero-section h1 {
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        letter-spacing: -0.02em;
    }
    
    .hero-section .subtitle {
        font-size: 1.4rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 300;
        letter-spacing: 0.02em;
    }
    
    .hero-section .tagline {
        font-size: 1.05rem;
        color: rgba(255,255,255,0.75);
        margin-top: 0.3rem;
        font-weight: 300;
    }
    
    .hero-section .badge-container {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .hero-badge {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 0.3rem 1.2rem;
        border-radius: 20px;
        color: white;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* ===== API STATUS CARD ===== */
    .api-status-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        transition: all 0.3s ease;
    }
    
    .api-status-card.status-success {
        border-color: var(--success);
    }
    
    .api-status-card.status-warning {
        border-color: var(--warning);
    }
    
    .api-status-card.status-error {
        border-color: var(--danger);
    }
    
    .api-status-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .api-status-icon {
        font-size: 2rem;
    }
    
    .api-status-text {
        display: flex;
        flex-direction: column;
    }
    
    .api-status-title {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .api-status-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .api-status-right {
        display: flex;
        gap: 0.8rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .btn-launch-api {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.6rem 1.8rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-launch-api:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .btn-launch-api:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
    
    .btn-refresh {
        background: var(--bg-card);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-refresh:hover {
        border-color: var(--primary);
        color: var(--text-primary);
    }
    
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-dot.online {
        background: var(--success);
        box-shadow: 0 0 10px rgba(72, 187, 120, 0.5);
    }
    
    .status-dot.offline {
        background: var(--danger);
        box-shadow: 0 0 10px rgba(252, 129, 129, 0.5);
    }
    
    .status-dot.warning {
        background: var(--warning);
        box-shadow: 0 0 10px rgba(237, 137, 54, 0.5);
    }

    /* ===== STATS ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin-top: 0.2rem;
        font-weight: 400;
    }
    
    /* ===== SECTION TITLE ===== */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 2rem 0 1rem 0;
        letter-spacing: -0.02em;
    }
    
    .section-subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* ===== PROCESS STEPS ===== */
    .process-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .process-step {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .process-step:hover {
        border-color: var(--primary);
        transform: translateY(-4px);
    }
    
    .process-step .step-number {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        line-height: 32px;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .process-step .step-icon {
        font-size: 2.5rem;
        margin: 0.3rem 0;
    }
    
    .process-step .step-title {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 600;
    }
    
    .process-step .step-desc {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin-top: 0.3rem;
        line-height: 1.5;
    }
    
    /* ===== FEATURE CARDS ===== */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-6px);
        border-color: var(--primary);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card .icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-card h3 {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    
    .feature-card .description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
        flex-grow: 1;
    }
    
    .feature-card ul {
        color: var(--text-secondary);
        font-size: 0.9rem;
        padding-left: 1.2rem;
        margin: 0.5rem 0 1rem 0;
        list-style: none;
    }
    
    .feature-card ul li {
        padding: 0.25rem 0;
        position: relative;
        padding-left: 1.5rem;
    }
    
    .feature-card ul li::before {
        content: '▸';
        position: absolute;
        left: 0;
        color: var(--primary);
        font-weight: bold;
    }
    
    .feature-card .btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        margin-top: auto;
        text-decoration: none;
        display: inline-block;
        width: fit-content;
    }
    
    .feature-card .btn-primary:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .feature-card .btn-primary:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        transform: none;
    }
    
    /* ===== ABOUT PROJECT ===== */
    .about-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .about-item {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .about-item:hover {
        border-color: var(--primary);
    }
    
    .about-item .label {
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .about-item .value {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    
    .about-item .badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 0.1rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        margin-top: 3rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid var(--border-color);
        text-align: center;
    }
    
    .footer .disclaimer {
        color: var(--text-secondary);
        font-size: 0.85rem;
        opacity: 0.7;
        font-style: italic;
    }
    
    .footer .copyright {
        color: var(--text-secondary);
        font-size: 0.8rem;
        opacity: 0.5;
        margin-top: 0.5rem;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .stats-grid, .process-grid, .about-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .feature-grid {
            grid-template-columns: 1fr;
        }
        .hero-section h1 {
            font-size: 2.5rem;
        }
        .api-status-card {
            flex-direction: column;
            align-items: stretch;
            text-align: center;
        }
        .api-status-left {
            flex-direction: column;
        }
        .api-status-right {
            justify-content: center;
            flex-wrap: wrap;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INITIALISATION DE L'ÉTAT DE SESSION
# ==============================================================================
if 'api_launching' not in st.session_state:
    st.session_state.api_launching = False

if 'api_launch_result' not in st.session_state:
    st.session_state.api_launch_result = None

# ==============================================================================
# CONTENU DE LA PAGE D'ACCUEIL
# ==============================================================================

# --- HERO SECTION ---
st.markdown("""
<div class="hero-section">
    <h1>🏛️ Aletheia</h1>
    <div class="subtitle">Le Moteur de Vérité pour les LLMs</div>
    <div class="tagline">Détection d'hallucinations · Fact-checking automatisé</div>
    <div class="badge-container">
        <span class="hero-badge">🔍 Berlue v1.0</span>
        <span class="hero-badge">🧠 FEVER + SelfCheckGPT</span>
        <span class="hero-badge">🤖 Llama · Mistral</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# VÉRIFICATION DE L'API BERLUE
# ==============================================================================

# Vérifier l'état de l'API
api_online = check_api_health()

# Déterminer le statut
if api_online:
    status_icon = "🟢"
    status_title = "API Berlue connectée"
    status_desc = "L'API est opérationnelle. Vous pouvez utiliser toutes les fonctionnalités."
    status_class = "status-success"
    status_dot = "online"
elif is_port_in_use(8000):
    status_icon = "🟡"
    status_title = "Port 8000 occupé"
    status_desc = "Le port 8000 est utilisé mais l'API ne répond pas. Vérifiez si un autre processus l'utilise."
    status_class = "status-warning"
    status_dot = "warning"
else:
    status_icon = "🔴"
    status_title = "API Berlue non détectée"
    status_desc = "L'API n'est pas en cours d'exécution. Lancez-la pour utiliser les fonctionnalités."
    status_class = "status-error"
    status_dot = "offline"

# Afficher la carte de statut
st.markdown(f"""
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
""", unsafe_allow_html=True)

if api_online:
    # API en ligne - bouton pour vérifier/rafraîchir
    st.markdown("""
        <button class="btn-refresh" onclick="location.reload()">🔄 Rafraîchir</button>
    """, unsafe_allow_html=True)
else:
    # API hors ligne - bouton pour lancer
    if st.button("🚀 Lancer l'API Berlue", key="launch_api_btn", use_container_width=False):
        # Ouvrir le terminal avec les commandes
        success, message = open_terminal_and_run_command()
        
        if success:
            st.success(f"✅ {message}")
            st.info("⏳ Attendez quelques secondes que l'API démarre, puis cliquez sur 'Rafraîchir'")
        else:
            st.error(f"❌ {message}")
            st.info("💡 Vous pouvez aussi lancer manuellement l'API avec :\n```bash\ncd /opt/wagon/src/berlue && make run_api\n```")
    
    # Bouton de rafraîchissement
    st.markdown("""
        <button class="btn-refresh" onclick="location.reload()">🔄 Rafraîchir</button>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# Si l'API n'est pas disponible, désactiver les liens vers les autres pages
feature_disabled = not api_online

# --- STATISTIQUES ---
st.markdown("""
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
""", unsafe_allow_html=True)

st.divider()

# --- DESCRIPTION ---
st.markdown("""
<p style="color: #a0aec0; font-size: 1.1rem; text-align: center; max-width: 800px; margin: 0 auto;">
    <strong>Aletheia</strong> est votre tableau de bord interactif pour auditer, tester et évaluer 
    les grands modèles de langage (LLMs). Grâce au moteur de fact-checking <strong>Berlue</strong> 
    en arrière-plan, cette plateforme vous permet de mesurer la fiabilité des réponses générées.
</p>
""", unsafe_allow_html=True)

st.divider()

# --- PROCESSUS BERLUE ---
st.markdown('<div class="section-title">⚡ Le Processus Berlue</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Vérification d\'hallucinations en 4 étapes</div>', unsafe_allow_html=True)

st.markdown("""
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
""", unsafe_allow_html=True)

st.divider()

# --- FEATURES ---
st.markdown('<div class="section-title">🚀 Explorez Aletheia</div>', unsafe_allow_html=True)

# Désactiver les liens si l'API n'est pas disponible
if feature_disabled:
    st.warning("⚠️ L'API Berlue n'est pas disponible. Lancez l'API ci-dessus pour accéder aux fonctionnalités de prédiction et d'évaluation.")

st.markdown(f"""
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
        <a href="/1_🔎_Prediction" target="_self" class="btn-primary {'btn-disabled' if feature_disabled else ''}" {'style="pointer-events: none; opacity: 0.5;"' if feature_disabled else ''}>
            {'🔒 ' if feature_disabled else '🔍 '}Accéder à l'Explorateur
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
        <a href="/2_📊_Evaluation" target="_self" class="btn-primary {'btn-disabled' if feature_disabled else ''}" {'style="pointer-events: none; opacity: 0.5;"' if feature_disabled else ''}>
            {'🔒 ' if feature_disabled else '📈 '}Accéder au Benchmark
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- À PROPOS DU PROJET ---
st.markdown('<div class="section-title">📖 À propos du projet</div>', unsafe_allow_html=True)

st.markdown("""
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
""", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<div class="footer">
    <div class="disclaimer">
        ⚠️ Les résultats sont indicatifs et ne remplacent pas une vérification humaine.
    </div>
    <div class="copyright">
        🚀 Propulsé par FastAPI &amp; Streamlit | Projet Berlue © 2026
    </div>
</div>
""", unsafe_allow_html=True)