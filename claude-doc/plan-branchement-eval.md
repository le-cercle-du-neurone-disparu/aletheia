# Plan — brancher l'éval Berlue dans le frontend Aletheia

Branche de travail : `feat-branchement-eval` (aletheia, depuis `main`).
Côté `berlue`, aucune modification prévue à ce stade — l'API lecture seule
est déjà en place sur `feat-berlu-sur-gcp` (à merger sur `main`) et couvre
tout ce dont ce plan a besoin.

**Statut : implémenté et testé** (`utils/api_client.py` + `pages/2_📊_Evaluation.py`,
vérifié via l'API `berlue` réelle + `streamlit.testing.AppTest`, sans
navigateur). Ce document reflète l'état actuel du code, pas seulement
l'intention de départ.

## 1. Constat : la page Evaluation appelle une API qui n'existe plus

`pages/2_📊_Evaluation.py` + `utils/api_client.py::run_evaluation()`
appellent `POST /evaluate` (payload `dataset_name`/`sample_size`/
`llm_to_test`, réponse `{status, metrics: {baseline, berlue}}`) pour
calculer une éval **à la volée** depuis un bouton "🚀 Lancer le Benchmark".

Cette route n'existe plus dans `berlue/api/fast.py`. L'API actuelle
(`berlue/api/fast_eval.py`, documentée dans `berlue/docs/evaluation/api.md`)
n'expose que 4 routes **en lecture seule sur le cache** — aucune ne
déclenche de calcul :

| Route | Usage |
|---|---|
| `GET /evaluated-models` | liste les scopes déjà évalués (filtrable dataset/model_id/ratio/versions, `mode=dataset\|generated`) |
| `GET /model-evaluation` | matrice Berlue d'un scope précis → 404 si pas en cache |
| `GET /baseline-evaluation` | matrice baseline mode 1, recalculée à la volée (rapide, pas de LLM) |
| `GET /baseline-evaluation-generated` | matrice baseline mode 2, lecture cache seule |

Remplir le cache se fait via `make evaluate_model(_generated)_all` en
local, ou le service Cloud Run d'éval (`docs/gcp/cloudrun.md`) — jamais
depuis ces routes ni depuis le frontend.

`GET /llms` (liste des LLM installables, utilisée par `get_available_llms()`
sur la page Prédiction) est indépendante de ce changement et reste valide
telle quelle.

`schemas.py` garde encore `EvaluateInput`/`EvaluateOutput`/`Metrics` (les
schémas de l'ancienne route `/evaluate`) — plus utilisés par aucune route :
code mort côté `berlue`, à signaler mais hors scope de ce plan (touche
`berlue`, pas `aletheia`).

## 2. Ce qui reste réutilisable tel quel

Toute la couche calcul/affichage de `2_📊_Evaluation.py` ne dépend que
de la *forme* d'une matrice de confusion (`ground_truth_true/false` ×
`predicted_true/undecided/false`), identique dans l'ancien et le nouveau
format (`ConfusionMatrix` côté `berlue/api/schemas.py`) :

- `calculate_metrics(matrix)` — accuracy/precision/recall/f1
- `plot_confusion_heatmap(matrix, title, color_scale)`
- `aggregate_metrics(metrics_list)` — moyenne pour le mode combiné
- toute la logique d'affichage (cards, heatmaps, graphes comparatifs,
  mode combiné avec tabs par dataset)

Le mode combiné actuel (boucle sur `["HaluEval", "TruthfulQA"]`, un appel
API par dataset, agrégation côté client) colle exactement à la contrainte
`docs/evaluation/storage.md` : **un scope = un seul dataset**, jamais de
matrice combinée côté backend. Donc cette boucle-et-agrège reste la bonne
approche, juste avec un nouvel appel API par itération.

Seule la couche **récupération des données** (haut du fichier : sidebar +
bouton + `run_evaluation()`) doit changer.

## 3. Décision d'architecture : browse-only (tranché, pas de bouton "Lancer")

Le calcul n'est plus synchrone-sur-clic : un run complet prend de la
seconde (mock) à des dizaines de minutes (mode généré, vrais LLM — cf.
notre run mode 1 du jour : ~17 min pour 1000 exemples). Le seul point
d'entrée pour déclencher un calcul est soit `make evaluate_model...` en
local, soit `POST /invoke` sur le service Cloud Run d'éval
(`berlue/api/eval_service.py`) — un service à part, non exposé publiquement
de la même façon que `fast.py`, protégé par jeton d'identité GCP
(`gcloud auth print-identity-token --impersonate-service-account=...`),
pensé pour un opérateur via CLI/Makefile, pas pour un bouton grand public
dans Streamlit.

**Décision (validée) : Aletheia ne doit jamais pouvoir déclencher un
benchmark.** Ce n'était pas juste une limite technique de l'ancienne route
`/evaluate` : c'est une erreur de conception à corriger, pas une fonction
à reproduire autrement. La page Evaluation devient un navigateur de
résultats déjà calculés, en deux temps — **recherche puis sélection** :

1. **Filtres à facettes** : `mode` (dataset/généré) + `dataset`, `model_id`,
   `ratio`, `pipeline_version`, `generation_version`, `eval_version` — pas
   de texte libre : chaque `selectbox` n'propose que les valeurs qui
   existent réellement dans le store pour le mode courant (impossible de
   filtrer sur un scope qui n'a jamais été calculé). Ces valeurs viennent
   d'un unique `GET /evaluated-models?mode=...` **sans autre filtre**,
   mis en cache côté client 60s (`st.cache_data`, bouton "🔄 Actualiser"
   pour forcer un refresh) — un seul appel réseau alimente à la fois les
   options de filtre et l'univers de résultats. Le filtrage lui-même est
   ensuite purement client-side (aucun round-trip par changement de
   filtre) : pas de bouton "Rechercher", tout est réactif dès qu'une
   sélection change.
2. **Résultats** : compteur "`X résultat(s) sur Y au total`" (Y = tout le
   mode, X = après filtres) + table récapitulative des scopes filtrés
   (dataset, model_id, ratio, versions, `n_examples`/`dataset_test_size`,
   `computed_at`) — chaque entrée est déjà un `EvaluationResult` complet,
   **matrice Berlue incluse** : pas besoin de rappeler `/model-evaluation`
   à ce stade, le fetch initial a déjà tout ramené.
3. **Sélection** : l'utilisateur choisit une ligne (ou plusieurs, pour le
   mode combiné multi-dataset) parmi les résultats — ça fixe le scope
   exact à afficher.
4. **Baseline correspondante** : une fois le scope sélectionné, un appel
   séparé — `GET /baseline-evaluation` (mode dataset, calcul à la volée
   mais rapide, quasi toujours disponible) ou `GET /baseline-evaluation-generated`
   (mode généré, lecture cache seule). Cette dernière peut ne rien
   retourner (404) si la baseline n'a pas été calculée pour ce scope
   précis — traiter ce cas explicitement ("baseline pas encore calculée
   pour ce scope", pas une erreur) plutôt que planter, conformément à
   "la baseline correspondante si elle existe".
5. **Affichage** : reconstruire localement `{"baseline": ..., "berlue": ...}`
   (baseline absente → sauter les blocs qui la comparent, afficher Berlue
   seul) pour réutiliser tel quel `calculate_metrics`/
   `plot_confusion_heatmap`. Afficher aussi `n_examples` vs
   `dataset_test_size` pour signaler un run partiel.
6. Mode combiné (plusieurs datasets sélectionnés à l'étape 3) : agrégation
   client-side inchangée (`aggregate_metrics`).

Alternative écartée définitivement : un bouton qui déclenche un run via
le service Cloud Run puis re-poll le cache. Pas seulement à cause de
l'auth GCP à gérer côté Streamlit ou du calcul non borné en temps depuis
l'UI — Aletheia ne doit pas exposer de déclencheur de calcul, point final.
Lancer un benchmark reste un geste d'opérateur via `make evaluate_model...`
ou le service Cloud Run, jamais un bouton dans le frontend.

## 4. Plan d'implémentation

### 4.1 `utils/api_client.py` — réalisé

`run_evaluation()` remplacée par trois fonctions de lecture seule :

```python
@st.cache_data(ttl=60)
def list_evaluated_models(mode="dataset", **filters) -> list[dict] | None:
    """GET /evaluated-models — filters : valeur None = joker."""

def get_baseline_evaluation(dataset, ratio) -> dict | None:
    """GET /baseline-evaluation (mode dataset, calcul à la volée mais rapide)."""

def get_baseline_evaluation_generated(dataset, ratio, model_id,
                                       generation_version, eval_version) -> dict | None:
    """GET /baseline-evaluation-generated — lecture cache seule ; None (pas
    d'erreur affichée) sur 404, cas normal — cf. fetch_baseline() ci-dessous."""
```

Pas de wrapper pour `/model-evaluation` : inutile dans le flux implémenté,
le fetch initial (`list_evaluated_models`) ramène déjà la matrice Berlue
de chaque scope.

**Piège rencontré et corrigé** : `/baseline-evaluation` renvoie la
`ConfusionMatrix` nue, `/baseline-evaluation-generated` un
`EvaluationResult` complet (champ `.matrix`) — formats différents malgré
des noms de route proches (cf. `berlue/api/schemas.py`). La fonction
`fetch_baseline(mode, scope)` de la page gère cette différence.

### 4.2 `pages/2_📊_Evaluation.py` — réalisé

- Sidebar : radio `mode` (dataset/généré) + une `selectbox` par filtre
  (`dataset`, `model_id`, `ratio`, `pipeline_version`,
  `generation_version` si mode généré, `eval_version`), peuplées à partir
  de `list_evaluated_models(mode)` (un seul appel, pas d'autre filtre) —
  jamais de valeur qui ne correspond à aucun résultat. Bouton
  "🔄 Actualiser" pour vider le cache (`list_evaluated_models.clear()`)
  plutôt que d'attendre le TTL de 60s. Pas de bouton "Rechercher" : le
  filtrage est réactif, recalculé à chaque changement de sélection.
- Zone principale : compteur `X résultat(s) sur Y au total`, puis tableau
  des scopes filtrés (`st.dataframe`) + `st.multiselect` sur un libellé
  récapitulatif par scope (une sélection = affichage simple, plusieurs =
  mode combiné avec `st.tabs`).
- Sur sélection : la matrice Berlue vient directement de l'entrée
  sélectionnée ; `fetch_baseline()` appelle la route baseline adaptée au
  mode, avec repli explicite (`st.caption` "pas de baseline calculée")
  si absente plutôt qu'une erreur.
- `calculate_metrics`/`plot_confusion_heatmap` conservées, appelées
  depuis `render_scope()` (nouvelle fonction qui tolère une baseline
  `None`). `aggregate_metrics` n'est finalement pas utilisée : le mode
  combiné compare les scopes côte à côte (tabs + bar chart accuracy) sans
  moyenne globale — plus honnête quand les scopes combinés ne partagent
  pas le même dataset/modèle.
- Retiré entièrement : bouton "Lancer le Benchmark", spinner, `st.balloons()`.

**Bug latent trouvé et corrigé (préexistant, pas introduit ici)** :
l'ancien code faisait `key = name.lower()` sur `"F1-Score"` → clé
`"f1-score"` inexistante dans `calculate_metrics()` (qui utilise `"f1"`) —
`KeyError` jamais déclenché avant car la page entière était déjà cassée
(`/evaluate` en 404). Corrigé avec un mapping explicite nom affiché → clé.

### 4.3 Tests — réalisé

Pas de navigateur disponible dans l'environnement de dev (extension
Chrome non connectée) — validation faite autrement :

- Les 3 routes testées au `curl` contre l'API `berlue` réelle et de vrais
  scopes en cache local (200 attendu + 404 attendu sur baseline générée
  absente).
- `api_client.py` exercé directement (script Python, `st.error` mocké)
  contre l'API réelle.
- `streamlit.testing.v1.AppTest` : chargement initial, recherche mode
  dataset (sélection simple + combinée), mode généré, et le chemin
  "baseline absente" (scope orphelin inséré directement en SQLite local
  pour le test, supprimé juste après — aucune donnée de test restante).

## 5. Points ouverts

- ~~Confirmer le comportement souhaité pour la sélection de
  pipeline_version/generation_version/eval_version quand plusieurs
  coexistent~~ — réglé par les filtres à facettes (§3/§4.2) : toutes les
  valeurs existantes sont proposées explicitement, aucun défaut implicite
  à choisir.
- `EvaluateInput`/`EvaluateOutput`/`Metrics` dans `berlue/api/schemas.py`
  sont morts depuis le retrait de `/evaluate` — à nettoyer côté `berlue`
  dans une tâche séparée.
- Mode 2 (généré) volontairement délayé après ce refacto frontend (cf.
  discussion du jour) — le plan ci-dessus couvre déjà `mode=generated`
  côté lecture pour ne pas avoir à refaire la page une deuxième fois
  quand le run mode 2 sera relancé.
