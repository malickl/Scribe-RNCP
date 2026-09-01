# Scribe

Assistant de réunion intelligent. Scribe capte l'audio d'une réunion — en
visioconférence via un bot silencieux, ou en présentiel via un dictaphone
navigateur — le transcrit avec attribution des tours de parole, puis génère
automatiquement un compte-rendu structuré : thème, catégorie, humeur,
résumé et liste d'actions.

## Fonctionnalités

- **Connexion Google** (OAuth) : authentification et lecture de l'agenda.
- **Visio** : envoi d'un bot ([Recall.ai](https://recall.ai)) sur une
  réunion Google Meet, réunion par réunion, avec confirmation explicite.
- **Dictaphone** : enregistrement direct depuis le navigateur, pour les
  réunions en présentiel.
- **Transcription** multilingue avec diarisation
  ([AssemblyAI](https://www.assemblyai.com)) — détection automatique de la
  langue, attribution des propos par locuteur.
- **Analyse** par LLM ([Groq](https://groq.com)) : thème, catégorie,
  humeur, résumé, actions à cocher au fur et à mesure.
- **Tableau de bord** : historique filtrable (type, catégorie, période,
  dates), statistiques, renommage des éléments.
- **RGPD** : écran de consentement bloquant, droit à l'effacement,
  suppression de l'audio brut (local et chez Recall.ai) après traitement.
  Détails dans `/conditions` une fois l'app lancée.

## Architecture

Application Flask monolithique, rendu server-side (Jinja2), sans front
séparé. Les diagrammes C4, le modèle de données et les choix techniques
détaillés sont dans le document "Spécifications & architecture" fourni
séparément (hors dépôt).

```
routes/
  auth.py        OAuth Google, profil, suppression de compte
  captation.py   liste des réunions, envoi du bot, dictaphone, webhook Recall
  dashboard.py   tableau de bord, filtres, actions
  pipeline.py    transcription -> analyse -> écriture en base (commun aux deux modes)
utils/
  database.py    accès PostgreSQL (pool de connexions)
  recall.py      API Recall.ai (bot, audio, suppression)
  transcription.py  API AssemblyAI
  analysis.py    API Groq
templates/       pages Jinja2
tests/           tests unitaires (mockés) + tests de latence réelle (opt-in)
```

## Installation

### Rapide

```bash
./install.sh
```

Le script crée l'environnement virtuel, installe les dépendances, prépare
`.env` à partir de `.env.example`, et initialise les tables si
`DATABASE_PUBLIC_URL` est déjà renseignée. Il reste deux étapes manuelles,
propres à chaque environnement et non automatisables :

1. Compléter `.env` avec tes clés API (voir ci-dessous).
2. Récupérer `credentials.json` (identifiants OAuth Google) depuis
   [Google Cloud Console](https://console.cloud.google.com) et le placer
   à la racine du projet.

### Manuelle

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis remplir .env
# ajouter credentials.json à la racine
python3 db/init_db.py
python3 app.py
```

### Variables d'environnement (`.env`)

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Clé API Groq (analyse LLM) |
| `ASSEMBLYAI_API_KEY` | Clé API AssemblyAI (transcription) |
| `RECALL_API_KEY` | Clé API Recall.ai (bot de réunion) |
| `DATABASE_PUBLIC_URL` | URL de connexion PostgreSQL |
| `SECRET_KEY` | Clé de session Flask (production uniquement) |
| `GOOGLE_CREDENTIALS_JSON` | Alternative à `credentials.json` en production (contenu JSON en une ligne) |

## Tests et qualité

```bash
pytest tests/           # suite par défaut : tout est mocké, aucun appel API réel
pytest tests/ -m latency  # tests de latence réelle (appelle Groq, AssemblyAI, Recall — coût réel négligeable)
flake8 .                 # lint (PEP 8)
```

Une CI GitHub Actions (`.github/workflows/ci.yml`) exécute le lint et la
suite de tests par défaut sur chaque push et pull request vers `main`.

## Déploiement

Hébergé sur [Railway](https://railway.app), avec redéploiement automatique
à chaque fusion sur `main`. La base PostgreSQL est hébergée sur le même
service. `Procfile` : `gunicorn app:app --workers 1` (un seul worker :
`flow_store` dans `routes/auth.py` est un dict en mémoire process, non
partagé entre workers).
