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
[Berlue](https://github.com/le-cercle-du-neurone-disparu/berlue). Sans backend
joignable, l'app démarre mais le voyant de la page d'accueil reste rouge.

La procédure — local natif, Docker local, puis Cloud Run — vit dans le dépôt
`berlue` et n'est pas reproduite ici :
**[Mise en service & API](https://github.com/le-cercle-du-neurone-disparu/berlue#mise-en-service--api)**.

Ce qu'Aletheia en attend :

| Backend visé | URL à utiliser |
| --- | --- |
| local | `http://localhost:8000`, le défaut — rien à configurer |
| Cloud Run | la sortie de `make cloudrun_url` dans `berlue` |

Aucune URL Cloud Run n'est versionnée dans ce dépôt : elle dépend du projet GCP
et de `CLOUDRUN_ENV` (`test`, `staging`, `prod`).

Où la poser, selon la combinaison visée :

| Front | Backend | Où mettre l'URL |
| --- | --- | --- |
| local | local | rien à faire |
| local | Cloud Run | `BERLUE_API_GCP_URL` dans `.env`, puis `make run_app_gcp` |
| Streamlit Cloud | Cloud Run | secrets de l'app, cf. `.streamlit/secrets.toml.example` |

## Environnements

L'app résout l'URL du backend dans cet ordre : secrets Streamlit, puis
`BERLUE_API_URL` de l'environnement (`.env`), puis `http://localhost:8000`.
Le voyant de la page d'accueil affiche l'environnement actif.

`.streamlit/secrets.toml` est ignoré par git non pas parce qu'il contiendrait
un secret, mais parce qu'il prime sur `.env` : versionné, il forcerait le
backend distant à tous ceux qui clonent le dépôt.

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
4. *Advanced settings* → *Secrets* : y déclarer `BERLUE_API_URL`, avec l'URL
   que donne `make cloudrun_url` dans `berlue` (gabarit :
   `.streamlit/secrets.toml.example`).

   Malgré son nom, ce panneau ne sert pas ici à cacher quoi que ce soit — une
   URL Cloud Run publique n'a rien de confidentiel. C'est simplement le seul
   endroit où injecter une configuration dans une app déployée, `.env` n'étant
   pas versionné.
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
