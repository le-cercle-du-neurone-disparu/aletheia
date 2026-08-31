"""
Page d'évaluation — Aletheia.
Avec présentation des datasets HaluEval et TruthfulQA.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from typing import List, Dict

from utils.api_client import get_available_llms, run_evaluation

# ==============================================================================
# CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Évaluation | Aletheia", page_icon="📊", layout="wide")

# ==============================================================================
# STYLES
# ==============================================================================
st.markdown("""
<style>
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --success: #48bb78;
        --warning: #ed8936;
        --danger: #fc8181;
        --bg-dark: #0a0a0f;
        --bg-card: #14141e;
        --text-primary: #ffffff;
        --text-secondary: #a0aec0;
        --border-color: #2d2d44;
    }

    .dataset-badge {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .dataset-badge.halueval { background: linear-gradient(135deg, #48bb78, #38a169); }
    .dataset-badge.truthfulqa { background: linear-gradient(135deg, #ed8936, #dd6b20); }
    .dataset-badge.combined { background: linear-gradient(135deg, #48bb78, #ed8936); }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    .metric-card .label {
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.2rem 0;
    }
    .metric-card .value.green { color: var(--success); }
    .metric-card .value.purple { color: var(--secondary); }
    .metric-card .baseline {
        color: var(--text-secondary);
        font-size: 0.75rem;
        opacity: 0.6;
    }
    .metric-card .delta {
        font-size: 0.75rem;
        font-weight: 600;
    }
    .metric-card .delta.positive { color: var(--success); }
    .metric-card .delta.negative { color: var(--danger); }
    
    .dataset-info {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .dataset-info .name {
        font-weight: 600;
        color: var(--text-primary);
    }
    .dataset-info .desc {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FONCTIONS
# ==============================================================================

def plot_confusion_heatmap(matrix_data: dict, title: str, color_scale: str) -> go.Figure:
    df = pd.DataFrame([
        matrix_data["ground_truth_true"],
        matrix_data["ground_truth_false"]
    ])
    
    df.index = ["✅ Vrai (Réalité)", "❌ Faux (Réalité)"]
    df.columns = ["✅ Prédit Vrai", "⚠️ Indécis", "❌ Prédit Faux"]
    
    fig = px.imshow(df, text_auto=True, color_continuous_scale=color_scale, title=title, aspect="auto")
    fig.update_layout(
        xaxis_title="Prédiction",
        yaxis_title="Vérité terrain",
        coloraxis_showscale=False,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    for i in range(len(df)):
        for j in range(len(df.columns)):
            val = df.iloc[i, j]
            fig.add_annotation(
                x=j, y=i, text=str(val),
                showarrow=False,
                font=dict(size=18, color="white" if val > 20 else "#2d3748", weight=700)
            )
    return fig

def calculate_metrics(matrix: dict) -> dict:
    tp = matrix["ground_truth_true"]["predicted_true"]
    tn = matrix["ground_truth_false"]["predicted_false"]
    fp = matrix["ground_truth_false"]["predicted_true"]
    fn = matrix["ground_truth_true"]["predicted_false"]
    
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}

def aggregate_metrics(metrics_list: List[Dict]) -> Dict:
    if not metrics_list:
        return {}
    agg = {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "count": 0}
    for m in metrics_list:
        for key in ["accuracy", "precision", "recall", "f1"]:
            agg[key] += m[key]
        agg["count"] += 1
    for key in ["accuracy", "precision", "recall", "f1"]:
        agg[key] /= agg["count"]
    return agg

def get_dataset_label(option: str) -> str:
    labels = {"HaluEval": "📚 HaluEval", "TruthfulQA": "📚 TruthfulQA", 
              "HaluEval+TruthfulQA": "📚 HaluEval + TruthfulQA"}
    return labels.get(option, option)

def get_dataset_badge(option: str) -> str:
    badges = {
        "HaluEval": '<span class="dataset-badge halueval">HaluEval</span>',
        "TruthfulQA": '<span class="dataset-badge truthfulqa">TruthfulQA</span>',
        "HaluEval+TruthfulQA": '<span class="dataset-badge combined">HaluEval + TruthfulQA</span>'
    }
    return badges.get(option, "")

def get_datasets_from_option(option: str) -> List[str]:
    if option == "HaluEval":
        return ["HaluEval"]
    elif option == "TruthfulQA":
        return ["TruthfulQA"]
    elif option == "HaluEval+TruthfulQA":
        return ["HaluEval", "TruthfulQA"]
    return []

# ==============================================================================
# INTERFACE
# ==============================================================================

# --- EN-TÊTE ---
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.2rem; font-weight: 700; color: #fff; letter-spacing: -0.02em;">
        📊 Tableau de Bord d'Évaluation
    </h1>
    <p style="color: #a0aec0; font-size: 1.05rem; margin-top: 0.3rem;">
        Lancez un benchmark pour comparer la <strong>Baseline</strong> (modèle brut) 
        avec <strong>Berlue</strong> (modèle + fact-checking)
    </p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    
    # Dataset
    st.markdown("#### 📚 Dataset")
    dataset_option = st.radio(
        "Choisissez le dataset à tester :",
        options=["HaluEval", "TruthfulQA", "HaluEval+TruthfulQA"],
        format_func=get_dataset_label,
        label_visibility="collapsed"
    )
    
    # Info datasets
    if dataset_option == "HaluEval":
        st.markdown("""
        <div class="dataset-info">
            <div class="name">📚 HaluEval</div>
            <div class="desc">~35k réponses QA/dialogue/résumé, appariées correcte vs hallucinée</div>
        </div>
        """, unsafe_allow_html=True)
    elif dataset_option == "TruthfulQA":
        st.markdown("""
        <div class="dataset-info">
            <div class="name">📚 TruthfulQA</div>
            <div class="desc">817 questions sur 38 catégories d'idées reçues</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="dataset-info">
            <div class="name">📚 Mode Combiné</div>
            <div class="desc">HaluEval + TruthfulQA — évaluation complète</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sample size
    st.markdown("#### 📊 Échantillonnage")
    sample_size = st.slider(
        "Nombre d'échantillons",
        min_value=10, max_value=500, value=100, step=10,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Model
    st.markdown("#### 🤖 Modèle LLM")
    try:
        available_llms = get_available_llms()
    except:
        available_llms = ["llama-2-7b", "mistral-7b", "llama3.1:8b"]
    
    selected_llm = st.selectbox("Modèle", options=available_llms, label_visibility="collapsed")
    
    st.markdown("#### 🌡️ Température")
    selected_temp = st.slider(
        "Température",
        min_value=0.0, max_value=1.0, value=0.7, step=0.05,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Summary
    datasets = get_datasets_from_option(dataset_option)
    st.markdown(f"""
    <div style="background: rgba(102,126,234,0.08); border: 1px solid rgba(102,126,234,0.2); border-radius: 10px; padding: 1rem; font-size: 0.85rem; color: #a0aec0; line-height: 1.8;">
        <div><strong style="color: #fff;">Dataset(s):</strong> {', '.join(datasets)}</div>
        <div><strong style="color: #fff;">Échantillons:</strong> {sample_size} / dataset</div>
        <div><strong style="color: #fff;">Total:</strong> {len(datasets) * sample_size}</div>
        <div><strong style="color: #fff;">Modèle:</strong> {selected_llm}</div>
        <div><strong style="color: #fff;">Température:</strong> {selected_temp:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN ---

# Badge
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
    <span style="color: #a0aec0;">Dataset :</span> {get_dataset_badge(dataset_option)}
</div>
""", unsafe_allow_html=True)

# Bouton
if st.button("🚀 Lancer le Benchmark", type="primary", use_container_width=True):
    datasets = get_datasets_from_option(dataset_option)
    
    with st.spinner(f"🔄 Évaluation sur {len(datasets)} dataset(s)..."):
        try:
            all_results = []
            all_baseline_metrics = []
            all_berlue_metrics = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, dataset in enumerate(datasets):
                status_text.text(f"📊 {dataset} ({idx+1}/{len(datasets)})")
                result = run_evaluation(dataset, sample_size, selected_llm, selected_temp)
                
                if result and result.get("status") == "success":
                    all_results.append({"dataset": dataset, "result": result})
                    baseline_metrics = calculate_metrics(result["metrics"]["baseline"])
                    berlue_metrics = calculate_metrics(result["metrics"]["berlue"])
                    all_baseline_metrics.append(baseline_metrics)
                    all_berlue_metrics.append(berlue_metrics)
                
                progress_bar.progress((idx + 1) / len(datasets))
            
            status_text.empty()
            progress_bar.empty()
            
            if not all_results:
                st.error("❌ L'évaluation a échoué.")
                st.stop()
            
            st.success(f"✅ Benchmark terminé sur {len(all_results)} dataset(s)")
            st.balloons()
            
            # --- AFFICHAGE ---
            
            if len(datasets) == 1:
                result_data = all_results[0]
                dataset = result_data["dataset"]
                result = result_data["result"]
                metrics = result["metrics"]
                
                baseline_metrics = calculate_metrics(metrics["baseline"])
                berlue_metrics = calculate_metrics(metrics["berlue"])
                
                st.markdown("### 📊 Métriques de Performance")
                
                col1, col2, col3, col4 = st.columns(4)
                metric_names = ["Accuracy", "Precision", "Recall", "F1-Score"]
                
                for col, name in zip([col1, col2, col3, col4], metric_names):
                    key = name.lower()
                    delta = berlue_metrics[key] - baseline_metrics[key]
                    delta_class = "positive" if delta >= 0 else "negative"
                    delta_sign = "▲" if delta >= 0 else "▼"
                    
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">{name}</div>
                            <div class="value green">{berlue_metrics[key]:.1%}</div>
                            <div class="baseline">Baseline: {baseline_metrics[key]:.1%}</div>
                            <div class="delta {delta_class}">{delta_sign} {abs(delta):.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = plot_confusion_heatmap(metrics["baseline"], f"Baseline — {dataset}", "Oranges")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = plot_confusion_heatmap(metrics["berlue"], f"Berlue — {dataset}", "Greens")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Graphique comparatif
                st.divider()
                st.markdown("### 📈 Comparaison Baseline vs Berlue")
                
                fig_compare = go.Figure()
                fig_compare.add_trace(go.Bar(
                    name="Baseline",
                    x=metric_names,
                    y=[baseline_metrics[m.lower()] for m in metric_names],
                    marker_color="#fc8181",
                    text=[f"{v:.1%}" for v in [baseline_metrics[m.lower()] for m in metric_names]],
                    textposition="outside"
                ))
                fig_compare.add_trace(go.Bar(
                    name="Berlue",
                    x=metric_names,
                    y=[berlue_metrics[m.lower()] for m in metric_names],
                    marker_color="#48bb78",
                    text=[f"{v:.1%}" for v in [berlue_metrics[m.lower()] for m in metric_names]],
                    textposition="outside"
                ))
                fig_compare.update_layout(
                    title=f"Performance sur {dataset}",
                    xaxis_title="Métrique",
                    yaxis_title="Score",
                    yaxis_tickformat=".0%",
                    height=400,
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_compare, use_container_width=True)
                
            else:
                # Mode combiné
                agg_baseline = aggregate_metrics(all_baseline_metrics)
                agg_berlue = aggregate_metrics(all_berlue_metrics)
                
                st.markdown("### 🎯 Performance Globale (Moyenne)")
                
                col1, col2, col3, col4 = st.columns(4)
                metric_names = ["Accuracy", "Precision", "Recall", "F1-Score"]
                
                for col, name in zip([col1, col2, col3, col4], metric_names):
                    key = name.lower()
                    delta = agg_berlue[key] - agg_baseline[key]
                    delta_class = "positive" if delta >= 0 else "negative"
                    delta_sign = "▲" if delta >= 0 else "▼"
                    
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">{name} (moyen)</div>
                            <div class="value purple">{agg_berlue[key]:.1%}</div>
                            <div class="baseline">Baseline: {agg_baseline[key]:.1%}</div>
                            <div class="delta {delta_class}">{delta_sign} {abs(delta):.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.divider()
                
                # Graphique global
                st.markdown("### 📈 Performance Moyenne sur les 2 Datasets")
                
                fig_global = go.Figure()
                baseline_values = [agg_baseline[m.lower()] for m in metric_names]
                berlue_values = [agg_berlue[m.lower()] for m in metric_names]
                
                fig_global.add_trace(go.Bar(
                    name="Baseline",
                    x=metric_names,
                    y=baseline_values,
                    marker_color="#fc8181",
                    text=[f"{v:.1%}" for v in baseline_values],
                    textposition="outside"
                ))
                fig_global.add_trace(go.Bar(
                    name="Berlue",
                    x=metric_names,
                    y=berlue_values,
                    marker_color="#9F7AEA",
                    text=[f"{v:.1%}" for v in berlue_values],
                    textposition="outside"
                ))
                fig_global.update_layout(
                    title="Performance moyenne HaluEval + TruthfulQA",
                    xaxis_title="Métrique",
                    yaxis_title="Score",
                    yaxis_tickformat=".0%",
                    height=400,
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_global, use_container_width=True)
                
                st.divider()
                
                # Résultats par dataset
                st.markdown("### 📊 Résultats par Dataset")
                tabs = st.tabs([f"📊 {r['dataset']}" for r in all_results])
                
                for idx, tab in enumerate(tabs):
                    with tab:
                        result_data = all_results[idx]
                        dataset = result_data["dataset"]
                        result = result_data["result"]
                        metrics = result["metrics"]
                        
                        baseline_metrics = calculate_metrics(metrics["baseline"])
                        berlue_metrics = calculate_metrics(metrics["berlue"])
                        
                        c1, c2, c3, c4 = st.columns(4)
                        for col, name in zip([c1, c2, c3, c4], metric_names):
                            key = name.lower()
                            with col:
                                st.markdown(f"""
                                <div class="metric-card" style="padding: 0.6rem;">
                                    <div class="label" style="font-size: 0.65rem;">{name}</div>
                                    <div class="value green" style="font-size: 1.3rem;">{berlue_metrics[key]:.1%}</div>
                                    <div class="baseline" style="font-size: 0.65rem;">Baseline: {baseline_metrics[key]:.1%}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            fig = plot_confusion_heatmap(metrics["baseline"], f"Baseline — {dataset}", "Oranges")
                            st.plotly_chart(fig, use_container_width=True)
                        with c2:
                            fig = plot_confusion_heatmap(metrics["berlue"], f"Berlue — {dataset}", "Greens")
                            st.plotly_chart(fig, use_container_width=True)
                
                # Comparaison
                st.divider()
                st.markdown("### 📊 Comparaison HaluEval vs TruthfulQA")
                
                comparison_data = []
                for result_data in all_results:
                    dataset = result_data["dataset"]
                    result = result_data["result"]
                    baseline_metrics = calculate_metrics(result["metrics"]["baseline"])
                    berlue_metrics = calculate_metrics(result["metrics"]["berlue"])
                    comparison_data.append({
                        "Dataset": dataset,
                        "Baseline": baseline_metrics["accuracy"],
                        "Berlue": berlue_metrics["accuracy"],
                        "Gain": berlue_metrics["accuracy"] - baseline_metrics["accuracy"]
                    })
                
                df_compare = pd.DataFrame(comparison_data)
                
                fig_compare = go.Figure()
                fig_compare.add_trace(go.Bar(
                    name="Baseline",
                    x=df_compare["Dataset"],
                    y=df_compare["Baseline"],
                    marker_color="#fc8181",
                    text=[f"{v:.1%}" for v in df_compare["Baseline"]],
                    textposition="outside"
                ))
                fig_compare.add_trace(go.Bar(
                    name="Berlue",
                    x=df_compare["Dataset"],
                    y=df_compare["Berlue"],
                    marker_color="#48bb78",
                    text=[f"{v:.1%}" for v in df_compare["Berlue"]],
                    textposition="outside"
                ))
                fig_compare.update_layout(
                    title="Comparaison des performances par dataset",
                    xaxis_title="Dataset",
                    yaxis_title="Accuracy",
                    yaxis_tickformat=".0%",
                    height=400,
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_compare, use_container_width=True)
            
            # Footer
            st.divider()
            st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
            st.caption("💡 Les résultats sont basés sur les échantillons testés")
            
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")