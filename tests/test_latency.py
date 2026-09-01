import time
import wave
import struct
import pytest
import requests
from utils.analysis import analyze
from utils.transcription import transcribe
from config import client_groq, system_prompt, transcriber, RECALL_API_KEY

pytestmark = pytest.mark.latency

TRANSCRIPTION_ECHANTILLON = (
    "Speaker A : Bonjour à tous, on va faire un point rapide sur l'avancement du projet.\n"
    "Speaker B : Oui, le sprint 1 est terminé, il reste juste les tests à finaliser.\n"
    "Speaker A : Parfait, on se donne jusqu'à vendredi pour livrer ça.\n"
)


def _wav_silence(path, duree_secondes=2, frequence=16000):
    """Génère un WAV de silence, suffisant pour mesurer le round-trip de
    l'API de transcription sans dépendre d'un vrai enregistrement."""
    n_frames = duree_secondes * frequence
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(frequence)
        f.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))


def test_latency_groq():
    """Temps de réponse d'un appel d'analyse réel (résumé/thème/actions)."""
    debut = time.perf_counter()
    report = analyze(TRANSCRIPTION_ECHANTILLON, client_groq, system_prompt)
    duree = time.perf_counter() - debut

    print(f"\n[latence] Groq (analyze) : {duree:.2f} s")
    assert "resume" in report
    assert duree < 30, "Réponse anormalement lente pour un texte aussi court"


def test_latency_assemblyai(tmp_path):
    """Temps de réponse d'une transcription réelle (fichier court, silence)."""
    fichier = str(tmp_path / "silence.wav")
    _wav_silence(fichier)

    debut = time.perf_counter()
    segments = transcribe(fichier, transcriber)
    duree = time.perf_counter() - debut

    print(f"\n[latence] AssemblyAI (transcribe, silence 2s) : {duree:.2f} s")
    assert isinstance(segments, list)
    assert duree < 60, "Réponse anormalement lente pour un fichier de 2 secondes"


def test_latency_recall_api():
    """Temps de réponse de l'API Recall (liste des bots), sans en créer un :
    créer un vrai bot nécessite une réunion en direct, impossible à
    automatiser ici. Ce test mesure la latence réseau/auth de base de
    l'API, pas le temps de captation d'une réunion réelle."""
    headers = {"Authorization": f"Token {RECALL_API_KEY}"}

    debut = time.perf_counter()
    response = requests.get("https://eu-central-1.recall.ai/api/v1/bot/", headers=headers)
    duree = time.perf_counter() - debut

    print(f"\n[latence] Recall.ai (GET /bot/) : {duree:.2f} s")
    assert response.ok
    assert duree < 10, "Réponse anormalement lente pour un simple GET"
