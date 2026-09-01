import requests
import os

RECALL_API_KEY = os.getenv("RECALL_API_KEY")


def send_bot(lien_reunion):
    url = "https://eu-central-1.recall.ai/api/v1/bot/"
    headers = {
        "Authorization": f"Token {RECALL_API_KEY}",
        "content-type": "application/json"
    }
    payload = {
        "meeting_url": lien_reunion,
        "bot_name": "Bot Scribe",
        "recording_config": {"audio_mixed_mp3": {}}
    }

    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        raise RuntimeError(f"Recall a refusé l'envoi du bot ({response.status_code}) : {response.text}")

    return response.json()["id"]


def get_audio(bot_id):
    """Télécharge l'audio et renvoie aussi le recording_id, pour permettre
    à l'appelant d'effacer l'enregistrement chez Recall.ai une fois le
    fichier récupéré (voir delete_recording)."""
    url = f"https://eu-central-1.recall.ai/api/v1/bot/{bot_id}/"
    headers = {"Authorization": f"Token {RECALL_API_KEY}"}

    r = requests.get(url, headers=headers)
    if not r.ok:
        raise RuntimeError(f"Recall a refusé la lecture du bot {bot_id} ({r.status_code}) : {r.text}")
    bot_data = r.json()

    recordings = bot_data.get("recordings") or []
    if not recordings:
        raise RuntimeError(f"Aucun enregistrement disponible pour le bot {bot_id}")

    recording_id = recordings[0]["id"]
    audio_url = recordings[0]["media_shortcuts"]["audio_mixed"]["data"]["download_url"]
    audio_response = requests.get(audio_url)
    audio_response.raise_for_status()

    filename = f"reunion_{bot_id}.mp3"
    with open(filename, "wb") as f:
        f.write(audio_response.content)

    return filename, recording_id


def delete_recording(recording_id):
    url = f"https://eu-central-1.recall.ai/api/v1/recording/{recording_id}/"
    headers = {"Authorization": f"Token {RECALL_API_KEY}"}

    response = requests.delete(url, headers=headers)
    if not response.ok:
        raise RuntimeError(
            f"Recall a refusé la suppression de l'enregistrement {recording_id} "
            f"({response.status_code}) : {response.text}"
        )
