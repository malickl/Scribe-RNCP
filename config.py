"""
Centralise les clients API, la connexion à la base, et le chargement des variables d'environnement.
Chaque route importe ce dont elle a besoin depuis ici plutôt que de recréer ses propres clients.
"""

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
RECALL_API_KEY = os.getenv("RECALL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Exemple d'initialisation à compléter :
# from groq import Groq
# client_groq = Groq(api_key=GROQ_API_KEY)

# import assemblyai as aai
# aai.settings.api_key = ASSEMBLYAI_API_KEY
# aai.settings.base_url = "https://api.eu.assemblyai.com"
# transcriber = aai.Transcriber()

with open("prompt_system.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
