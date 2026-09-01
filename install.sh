#!/usr/bin/env bash
# Installe Scribe en local : environnement virtuel, dépendances, .env, base
# de données. Idempotent : peut être relancé sans casser une install déjà en
# place (venv réutilisé si présent, .env non écrasé s'il existe déjà).
set -e

cd "$(dirname "$0")"

echo "==> Environnement virtuel Python"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "==> Installation des dépendances"
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "==> Configuration (.env)"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "    .env créé à partir de .env.example — à remplir avec tes clés API"
else
    echo "    .env existe déjà, non modifié"
fi

if [ ! -f "credentials.json" ]; then
    echo "    ATTENTION : credentials.json (OAuth Google) absent."
    echo "    À télécharger depuis Google Cloud Console et à placer à la racine du projet."
fi

echo "==> Base de données"
if [ -f ".env" ] && grep -q "^DATABASE_PUBLIC_URL=.\+" .env; then
    python3 db/init_db.py
else
    echo "    DATABASE_PUBLIC_URL non renseignée dans .env — étape sautée."
    echo "    Relance ce script (ou 'python3 db/init_db.py') une fois .env complété."
fi

echo ""
echo "Installation terminée."
echo "Prochaines étapes si ce n'est pas déjà fait :"
echo "  1. Compléter .env avec tes clés API (Groq, AssemblyAI, Recall.ai, DATABASE_PUBLIC_URL)"
echo "  2. Ajouter credentials.json (OAuth Google) à la racine"
echo "  3. python3 db/init_db.py (si pas déjà fait ci-dessus)"
echo "  4. python3 app.py"
