# Aletheia

Interface Streamlit du détecteur d'hallucinations LLM. Le backend est le
projet [Berlue](../berlue). Squelette de base — à implémenter.

## Setup

```bash
make local_setup   # crée .venv, installe les dépendances, génère .env (questions, Entrée = défaut)
make run_app       # lance l'app Streamlit en local
```

Le backend `berlue` doit tourner à part (`make run_api` ou `make docker_run_local`
dans le repo `berlue`, voir son README).

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
3. *Advanced settings* → Python 3.13 (les versions épinglées dans
   `requirements.txt` n'ont pas de wheels au-delà).
4. *Advanced settings* → *Secrets* : coller le contenu de
   `.streamlit/secrets.toml.example`, avec l'URL du service Cloud Run. Ne jamais
   committer `.streamlit/secrets.toml` (déjà dans `.gitignore`).
5. Déployer, puis vérifier sur la page d'accueil que le voyant annonce
   l'environnement `cloud` et l'URL Cloud Run — s'il affiche `local`, le secret
   n'a pas été pris en compte.

Le dépôt étant sous une organisation GitHub, il faut que le compte Streamlit ait
accès à l'organisation (autorisation OAuth à accorder côté GitHub au premier
déploiement).

Vérifier aussi le timeout du service Cloud Run : le client attend jusqu'à 600 s
sur `/predict`, ce qui ne sert à rien si GCP coupe la requête avant.

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
