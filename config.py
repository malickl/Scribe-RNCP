from dotenv import load_dotenv
from groq import Groq
import assemblyai as aai
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
RECALL_API_KEY = os.getenv("RECALL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

client_groq = Groq(api_key=GROQ_API_KEY)

aai.settings.api_key = ASSEMBLYAI_API_KEY
aai.settings.base_url = "https://api.eu.assemblyai.com"
transcriber = aai.Transcriber()

with open("prompt_system.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()