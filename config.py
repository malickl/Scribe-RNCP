from dotenv import load_dotenv
from groq import Groq
import assemblyai as aai
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
RECALL_API_KEY = os.getenv("RECALL_API_KEY")
DATABASE_PUBLIC_URL = os.getenv("DATABASE_PUBLIC_URL")

# Construction différée : une clé absente ou invalide ne doit pas empêcher
# l'import de ce module (tests, CI) ni le démarrage de l'application —
# seule l'analyse elle-même échouera si la clé manque réellement à l'usage.
try:
    client_groq = Groq(api_key=GROQ_API_KEY)
except Exception:
    client_groq = None

aai.settings.api_key = ASSEMBLYAI_API_KEY
aai.settings.base_url = "https://api.eu.assemblyai.com"
try:
    transcriber = aai.Transcriber()
except Exception:
    transcriber = None

with open("prompt_system.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
