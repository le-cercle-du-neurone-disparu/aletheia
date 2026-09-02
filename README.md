# Aletheia

Interface Streamlit du détecteur d'hallucinations LLM. Le backend est le
projet [Berlue](../berlue). Squelette de base — à implémenter.

## Setup

```bash
make local_setup   # crée .venv, installe les dépendances, génère .env (questions, Entrée = défaut)
make run_app       # lance l'app Streamlit en local
```

Le backend `berlue` doit tourner à part — voir la section suivante.

## Mettre en route le backend

Aletheia n'embarque aucun modèle : toutes ses pages appellent l'API du projet
[Berlue](../berlue). Sans backend joignable, l'app démarre mais le voyant de la
page d'accueil reste rouge.

### Backend local

Dans le dépôt `berlue`, au choix :

```bash
make run_api_local      # FastAPI directement, rechargement à chaud
make docker_run_local   # le même service en conteneur, port 8000
```

Berlue s'appuie sur un serveur Ollama pour l'inférence ; `make ollama_setup`
puis `make ollama_check` l'installent et vérifient qu'il tourne. Le README de
`berlue` fait foi sur les prérequis.

L'API écoute alors sur `http://localhost:8000`, qui est la valeur par défaut
d'Aletheia : rien à configurer côté front.

### Backend sur Cloud Run

Toujours dans `berlue` :

```bash
make gcp_setup     # provisionne l'infra (rejouable, ne déploie aucun service)
make gcp_deploy    # build, push et déploie les services (CLOUDRUN_ENV=test par défaut)
make cloudrun_url  # affiche l'URL du service déployé
```

`make cloudrun_url` est la commande qui donne la valeur à mettre dans
`BERLUE_API_URL` — c'est pourquoi aucune URL n'est écrite en dur dans ce dépôt :
elle dépend du projet GCP et de l'environnement (`test`, `staging`, `prod`).

Le service doit accepter les appels non authentifiés
(`--allow-unauthenticated`), sinon Streamlit reçoit un 403.

Vérifier qu'il répond avant de brancher le front :

```bash
curl "$(cd ../berlue && make -s cloudrun_url | tail -1)/llms"
```

### Brancher le front dessus

| Cible | Où mettre l'URL |
| --- | --- |
| app locale → backend local | rien à faire, c'est le défaut |
| app locale → backend Cloud Run | `BERLUE_API_GCP_URL` dans `.env`, puis `make run_app_gcp` |
| app Streamlit Cloud → backend Cloud Run | secrets de l'app, cf. `.streamlit/secrets.toml.example` |

## Environnements

L'app résout l'URL du backend dans cet ordre : secrets Streamlit, puis
`BERLUE_API_URL` de l'environnement (`.env`), puis `http://localhost:8000`.
Le voyant de la page d'accueil affiche l'environnement actif.

| Environnement | App | Backend | Source de l'URL |
| --- | --- | --- | --- |
| `local` | poste de dev, `make run_app` | `berlue` sur la même machine | `.env` |
| `cloud` | Streamlit Community Cloud | Cloud Run | secrets Streamlit |

Les requêtes HTTP partent du processus Streamlit, pas du navigateur du visiteur.
Sur Streamlit Cloud, `localhost` désigne donc le conteneur qui héberge l'app :
l'environnement `cloud` exige une URL publique.

### Déployer sur Streamlit Community Cloud

Prérequis côté backend : le service Cloud Run doit accepter les appels non
authentifiés (`--allow-unauthenticated`), sans quoi Streamlit reçoit un 403.

1. Pousser la branche à déployer sur GitHub — Streamlit Cloud lit le dépôt, pas
   le poste local.
2. Sur [share.streamlit.io](https://share.streamlit.io), *Create app* → *Deploy
   from GitHub*, puis renseigner :
   - Repository : `le-cercle-du-neurone-disparu/aletheia`
   - Branch : `main`
   - Main file path : `🏠_Accueil.py`
3. *Advanced settings* → Python 3.14, la version du projet
   (`PYTHON_VERSION` dans `make/local.mk`, et celle de la CI).
4. *Advanced settings* → *Secrets* : coller le contenu de
   `.streamlit/secrets.toml.example`, en remplaçant le gabarit par l'URL que
   donne `make cloudrun_url` dans `berlue`. Ne jamais committer
   `.streamlit/secrets.toml` (déjà dans `.gitignore`).
5. Déployer, puis vérifier sur la page d'accueil que le voyant annonce
   l'environnement `cloud` et l'URL Cloud Run — s'il affiche `local`, le secret
   n'a pas été pris en compte.

Le dépôt étant sous une organisation GitHub, il faut que le compte Streamlit ait
accès à l'organisation. Cette autorisation se donne au premier déploiement, et
se vérifie sur
`https://github.com/settings/connections/applications` (côté compte) ou
`https://github.com/organizations/le-cercle-du-neurone-disparu/settings/oauth_application_policy`
(côté organisation) — il n'y a pas d'endpoint d'API pour la lire. En pratique,
un déploiement qui atteint l'étape `Cloning repository...` dans ses logs prouve
que l'accès est en place.

`requirements.txt` ne doit jamais contenir `aletheia` : un paquet homonyme sans
rapport existe sur PyPI, et `pip freeze` après un `pip install -e .` l'y réinjecte.

### Tester le backend GCP depuis le poste local

```bash
make run_app_gcp   # utilise BERLUE_API_GCP_URL (cf. .env.example)
```

## Structure

```
🏠_Accueil.py           # point d'entrée Streamlit
pages/                  # pages Prédiction, Évaluation, ...
utils/
├── config.py           # résolution de l'URL du backend selon l'environnement
└── api_client.py       # appels /llms, /predict, /evaluate
scripts/
└── setup_env.sh        # génère .env interactivement (appelé par make local_setup)
.streamlit/
└── secrets.toml.example  # gabarit des secrets de l'environnement cloud
Makefile                # local_setup, run_app, run_app_gcp, lint
```

## Contrat API

Le contrat (routes, schémas des payloads) vit dans le repo du backend `berlue` :
`berlue/berlue/api/fast.py` et `berlue/berlue/api/schemas.py`.

## TODO

- [ ] Construire l'UI dans `streamlit_app.py` (ou passer en multipage via un
      dossier `pages/` si besoin).
- [ ] Brancher les appels aux endpoints `/predict` et `/evaluate` dans
      `utils/api_client.py` au fur et à mesure des besoins de l'UI.
