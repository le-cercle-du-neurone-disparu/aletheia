"""
Page d'évaluation — Aletheia.
Recherche et consultation des résultats d'évaluation Berlue déjà calculés
(cache berlue.evaluation.result_store) — cette page ne déclenche jamais de
calcul, cf. berlue/docs/evaluation/api.md pour les routes utilisées.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import (
    get_baseline_evaluation,
    get_baseline_evaluation_generated,
    list_evaluated_models,
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# ==============================================================================
# STYLES
# ==============================================================================
st.markdown(
    """
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
        background: linear-gradient(135deg, #4a5568, #2d3748);
    }
    .dataset-badge.halueval { background: linear-gradient(135deg, #48bb78, #38a169); }
    .dataset-badge.truthfulqa { background: linear-gradient(135deg, #ed8936, #dd6b20); }

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

    .scope-info {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# FONCTIONS — calcul/affichage (indépendantes de la source des matrices)
# ==============================================================================


def plot_confusion_heatmap(
    matrix_data: dict, title: str, color_scale: str
) -> go.Figure:
    df = pd.DataFrame(
        [matrix_data["ground_truth_true"], matrix_data["ground_truth_false"]]
    )

    df.index = ["✅ Vrai (Réalité)", "❌ Faux (Réalité)"]
    df.columns = ["✅ Prédit Vrai", "⚠️ Indécis", "❌ Prédit Faux"]

    # text_auto=False : les valeurs sont dessinées via add_annotation ci-dessous
    # (contraste blanc/foncé selon la valeur) — text_auto=True superposerait un
    # second jeu de chiffres par-dessus, illisible (effet de flou/dédoublement).
    fig = px.imshow(
        df,
        text_auto=False,
        color_continuous_scale=color_scale,
        title=title,
        aspect="auto",
    )
    fig.update_layout(
        xaxis_title="Prédiction",
        yaxis_title="Vérité terrain",
        coloraxis_showscale=False,
        height=380,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    # Badge à fond fixe plutôt qu'un texte dont la couleur s'adapterait à la
    # case — reste lisible quelle que soit l'intensité de la couleur en
    # dessous, pas besoin de deviner un seuil de contraste.
    for i in range(len(df)):
        for j in range(len(df.columns)):
            fig.add_annotation(
                x=j,
                y=i,
                text=str(df.iloc[i, j]),
                showarrow=False,
                font={"size": 16, "color": "#1a202c", "weight": 700},
                bgcolor="rgba(255, 255, 255, 0.88)",
                bordercolor="rgba(0, 0, 0, 0.15)",
                borderwidth=1,
                borderpad=4,
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
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def get_dataset_badge(dataset: str) -> str:
    labels = {"halueval": "HaluEval", "truthfulqa": "TruthfulQA"}
    css_class = dataset if dataset in labels else ""
    return (
        f'<span class="dataset-badge {css_class}">{labels.get(dataset, dataset)}</span>'
    )


def scope_label(evaluation: dict) -> str:
    """Libellé lisible d'un résultat de recherche, pour le sélecteur d'affichage."""
    versions = f"pipeline={evaluation.get('pipeline_version') or '—'}"
    if evaluation.get("generation_version"):
        versions += f", generation={evaluation['generation_version']}"
    versions += f", eval={evaluation['eval_version']}"
    return (
        f"{evaluation['dataset']} · {evaluation['model_id']} · ratio={evaluation['ratio']} · "
        f"{versions} · n={evaluation['n_examples']}/{evaluation.get('dataset_test_size') or '?'}"
    )


def fetch_baseline(mode: str, scope: dict) -> dict | None:
    """Baseline correspondant à `scope`, ou `None` si elle n'existe pas
    (mode généré, cache seul — cf. `EvaluationResult`). `/baseline-evaluation`
    (mode dataset) renvoie la `ConfusionMatrix` nue, `/baseline-evaluation-generated`
    un `EvaluationResult` complet — formats différents, cf. berlue/api/schemas.py."""
    if mode == "generated":
        result = get_baseline_evaluation_generated(
            dataset=scope["dataset"],
            ratio=scope["ratio"],
            model_id=scope["model_id"],
            generation_version=scope["generation_version"],
            eval_version=scope["eval_version"],
        )
        return result["matrix"] if result else None
    return get_baseline_evaluation(dataset=scope["dataset"], ratio=scope["ratio"])


def render_scope(scope: dict, baseline_matrix: dict | None, key_prefix: str) -> None:
    """Affiche heatmaps + cards pour un scope (matrice Berlue + baseline si
    dispo) — heatmaps en premier, blocs d'info (fond sombre) en dessous."""
    berlue_matrix = scope["matrix"]
    berlue_metrics = calculate_metrics(berlue_matrix)
    baseline_metrics = calculate_metrics(baseline_matrix) if baseline_matrix else None

    if baseline_matrix is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                plot_confusion_heatmap(
                    baseline_matrix, f"Baseline — {scope['dataset']}", "Oranges"
                ),
                use_container_width=True,
                key=f"{key_prefix}-baseline",
            )
        with c2:
            st.plotly_chart(
                plot_confusion_heatmap(
                    berlue_matrix, f"Berlue — {scope['dataset']}", "Greens"
                ),
                use_container_width=True,
                key=f"{key_prefix}-berlue",
            )
    else:
        st.caption("⚠️ Pas de baseline calculée pour ce scope.")
        st.plotly_chart(
            plot_confusion_heatmap(
                berlue_matrix, f"Berlue — {scope['dataset']}", "Greens"
            ),
            use_container_width=True,
            key=f"{key_prefix}-berlue-only",
        )

    n_examples, test_size = scope["n_examples"], scope.get("dataset_test_size")
    coverage_note = (
        f" — run partiel ({n_examples}/{test_size})"
        if test_size and n_examples < test_size
        else ""
    )
    st.markdown(
        f"""
    <div class="scope-info">
        {get_dataset_badge(scope["dataset"])} &nbsp;
        <strong style="color:#fff;">{scope["model_id"]}</strong> · ratio={scope["ratio"]} ·
        {n_examples} exemple(s){coverage_note} · calculé le {scope["computed_at"]}
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    metric_keys = [
        ("Accuracy", "accuracy"),
        ("Precision", "precision"),
        ("Recall", "recall"),
        ("F1-Score", "f1"),
    ]
    for col, (name, key) in zip([col1, col2, col3, col4], metric_keys):
        baseline_html = ""
        if baseline_metrics is not None:
            delta = berlue_metrics[key] - baseline_metrics[key]
            delta_class = "positive" if delta >= 0 else "negative"
            delta_sign = "▲" if delta >= 0 else "▼"
            # Pas d'indentation ici : une ligne indentée ≥4 espaces dans le
            # markdown final serait rendue comme un bloc de code littéral
            # plutôt que comme le HTML brut attendu (unsafe_allow_html).
            baseline_html = (
                f'<div class="baseline">Baseline: {baseline_metrics[key]:.1%}</div>'
                f'<div class="delta {delta_class}">{delta_sign} {abs(delta):.1%}</div>'
            )
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="label">{name}</div>'
                f'<div class="value green">{berlue_metrics[key]:.1%}</div>'
                f"{baseline_html}"
                f"</div>",
                unsafe_allow_html=True,
            )


# ==============================================================================
# INTERFACE
# ==============================================================================

st.markdown(
    """
<style>
    .entete-analyse {
        display: flex;
        align-items: center;
        gap: 1.4rem;
        margin-bottom: 2rem;
    }
    .entete-analyse .figure {
        flex: 0 0 auto;
        height: 130px;
        width: auto;
    }
    /* Sous cette largeur la figure écraserait le titre : le texte prime. */
    @media (max-width: 640px) {
        .entete-analyse .figure { display: none; }
    }
    .entete-analyse h1 {
        /* `inherit` et non une couleur fixe : le titre était en blanc, donc
           invisible sur le thème clair de Streamlit. */
        color: inherit;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .entete-analyse p {
        color: #a0aec0;
        font-size: 1.05rem;
        margin: 0.3rem 0 0;
    }
</style>
<div class="entete-analyse">
    <img class="figure" src="app/static/aletheia-parle.webp" alt="Aletheia">
    <div>
        <h1>Tableau de Bord d'Évaluation</h1>
        <p>
            Recherchez un résultat d'évaluation déjà calculé pour comparer
            <strong>Baseline</strong> (modèle brut) et <strong>Berlue</strong> (modèle + fact-checking)
        </p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Un seul libellé pour « pas de filtre », partagé par le mode et les autres
# listes : deux formulations pour la même idée se lisaient comme deux notions.
LIBELLE_TOUS = "🗂️ Tous"

FILTER_JOKER = LIBELLE_TOUS

MODE_TOUS = "tous"
MODE_LIBELLES = {
    MODE_TOUS: LIBELLE_TOUS,
    "dataset": "📚 Dataset (réponse du jeu de données)",
    "generated": "🤖 Généré + juge",
}


def _scopes_du_mode(mode: str) -> list[dict]:
    """Évaluations disponibles, chacune marquée de son mode d'origine.

    En mode « tous », les deux familles se mélangent dans le tableau alors
    qu'elles ne se lisent pas au même endpoint : `_mode` accompagne chaque
    ligne pour que la baseline soit ensuite cherchée là où elle se trouve.
    """
    modes = ("dataset", "generated") if mode == MODE_TOUS else (mode,)
    return [
        {**scope, "_mode": m}
        for m in modes
        for scope in (list_evaluated_models(mode=m) or [])
    ]


def _filter_options(scopes: list[dict], field: str) -> list[str]:
    """Valeurs distinctes de `field` réellement présentes dans `scopes`,
    triées — alimente les selectbox de filtre (jamais de valeur qui ne
    correspond à aucun résultat)."""
    values = {str(r[field]) for r in scopes if r.get(field) is not None}
    return [FILTER_JOKER, *sorted(values)]


with st.sidebar:
    st.markdown("### 🔍 Filtres")

    mode = st.selectbox(
        "Mode",
        options=[MODE_TOUS, "dataset", "generated"],
        format_func=lambda m: MODE_LIBELLES[m],
    )

    all_scopes = _scopes_du_mode(mode)

    dataset_filter = st.selectbox(
        "Dataset", options=_filter_options(all_scopes, "dataset")
    )
    model_id_filter = st.selectbox(
        "Model ID", options=_filter_options(all_scopes, "model_id")
    )
    ratio_filter = st.selectbox(
        "Ratio train/test", options=_filter_options(all_scopes, "ratio")
    )
    pipeline_version_filter = st.selectbox(
        "Pipeline version", options=_filter_options(all_scopes, "pipeline_version")
    )
    generation_version_filter = FILTER_JOKER
    if mode in ("generated", MODE_TOUS):
        generation_version_filter = st.selectbox(
            "Generation version",
            options=_filter_options(all_scopes, "generation_version"),
        )
    eval_version_filter = st.selectbox(
        "Eval version", options=_filter_options(all_scopes, "eval_version")
    )

    if st.button("🔄 Actualiser", use_container_width=True):
        list_evaluated_models.clear()
        st.rerun()

# --- RÉSULTATS ---


def _matches(scope: dict) -> bool:
    checks = [
        (dataset_filter, scope["dataset"]),
        (model_id_filter, scope["model_id"]),
        (ratio_filter, scope["ratio"]),
        (pipeline_version_filter, scope.get("pipeline_version")),
        (eval_version_filter, scope["eval_version"]),
    ]
    # Seules les lignes générées portent une version de génération : appliquer
    # le filtre aux autres les écarterait toutes dès qu'il est renseigné.
    if scope.get("_mode") == "generated":
        checks.append((generation_version_filter, scope.get("generation_version")))
    return all(
        selected == FILTER_JOKER or str(actual) == selected
        for selected, actual in checks
    )


results = [r for r in all_scopes if _matches(r)]

st.markdown(f"### 🔎 {len(results)} résultat(s) sur {len(all_scopes)} au total")

if not all_scopes:
    st.warning("Aucune évaluation en cache pour ce mode.")
elif not results:
    st.warning("Aucun résultat pour ces filtres.")
else:
    st.caption(
        "Sélectionne une ou plusieurs lignes (case à cocher) pour afficher leur baseline."
    )
    selection_event = st.dataframe(
        pd.DataFrame(
            [
                {
                    **(
                        {"Mode": MODE_LIBELLES[r["_mode"]]} if mode == MODE_TOUS else {}
                    ),
                    "Dataset": r["dataset"],
                    "Model ID": r["model_id"],
                    "Ratio": r["ratio"],
                    "Pipeline": r.get("pipeline_version") or "—",
                    "Génération": r.get("generation_version") or "—",
                    "Éval": r["eval_version"],
                    "N": r["n_examples"],
                    "Split total": r.get("dataset_test_size") or "?",
                    "Calculé le": r["computed_at"],
                }
                for r in results
            ]
        ),
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )
    # Streamlit ne réinitialise pas la sélection quand `results` change de
    # taille (ex. filtre resserré) — un index sélectionné avant peut ne plus
    # exister dans la liste courante, d'où le garde-fou sur len(results).
    selected = [results[i] for i in selection_event.selection.rows if i < len(results)]

    if not selected:
        st.info("Sélectionne au moins un résultat ci-dessus pour l'afficher.")
    else:
        st.divider()
        entries = [(scope, fetch_baseline(scope["_mode"], scope)) for scope in selected]

        if len(entries) == 1:
            scope, baseline_matrix = entries[0]
            render_scope(scope, baseline_matrix, key_prefix="single")
        else:
            tabs = st.tabs([f"📊 {scope_label(scope)}" for scope, _ in entries])
            for tab, (scope, baseline_matrix) in zip(tabs, entries):
                with tab:
                    render_scope(
                        scope, baseline_matrix, key_prefix=scope["computed_at"]
                    )

            st.divider()
            st.markdown("### 📈 Comparaison Accuracy")
            comparison_labels = [
                f"{s['dataset']} · {s['model_id']}" for s, _ in entries
            ]
            berlue_acc = [
                calculate_metrics(s["matrix"])["accuracy"] for s, _ in entries
            ]
            baseline_acc = [
                calculate_metrics(b)["accuracy"] if b is not None else None
                for _, b in entries
            ]

            fig_compare = go.Figure()
            if any(v is not None for v in baseline_acc):
                fig_compare.add_trace(
                    go.Bar(
                        name="Baseline",
                        x=comparison_labels,
                        y=[v or 0 for v in baseline_acc],
                        marker_color="#fc8181",
                        text=[
                            f"{v:.1%}" if v is not None else "—" for v in baseline_acc
                        ],
                        textposition="outside",
                    )
                )
            fig_compare.add_trace(
                go.Bar(
                    name="Berlue",
                    x=comparison_labels,
                    y=berlue_acc,
                    marker_color="#48bb78",
                    text=[f"{v:.1%}" for v in berlue_acc],
                    textposition="outside",
                )
            )
            fig_compare.update_layout(
                xaxis_title="Scope",
                yaxis_title="Accuracy",
                yaxis_tickformat=".0%",
                height=400,
                barmode="group",
                legend={
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": 1.02,
                    "xanchor": "right",
                    "x": 1,
                },
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_compare, use_container_width=True)

    st.divider()
