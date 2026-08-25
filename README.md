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

## Structure

```
streamlit_app.py       # page principale, vide
utils/
└── api_client.py      # get_llms() — GET /llms
scripts/
└── setup_env.sh       # génère .env interactivement (appelé par make local_setup)
Makefile                # local_setup, run_app
```

## Contrat API

Le contrat (routes, schémas des payloads) vit dans le repo du backend `berlue` :
`berlue/berlue/api/fast.py` et `berlue/berlue/api/schemas.py`.

## TODO

- [ ] Construire l'UI dans `streamlit_app.py` (ou passer en multipage via un
      dossier `pages/` si besoin).
- [ ] Brancher les appels aux endpoints `/predict` et `/evaluate` dans
      `utils/api_client.py` au fur et à mesure des besoins de l'UI.
