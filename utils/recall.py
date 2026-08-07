"""
Fonctions liées à l'API Recall : envoi du bot, récupération et suppression de l'audio.
"""

def send_bot(lien_reunion):
    """
    Envoie un bot Recall sur le lien donné. Retourne le bot_id.
    """
    pass


def get_audio(bot_id):
    """
    Télécharge l'audio depuis Recall, retourne le nom du fichier sauvegardé.
    """
    pass


def delete_recording(recording_id):
    """
    Supprime l'enregistrement chez Recall via DELETE /api/v1/recording/{id}/
    recording_id vient du webhook bot.done, champ data.recording.id (distinct du bot_id).
    """
    pass
def get_audio(bot_id):
    url = f"https://eu-central-1.recall.ai/api/v1/bot/{bot_id}/"
    headers = {"Authorization": f"Token {RECALL_API_KEY}"}

    r = requests.get(url, headers=headers)
    bot_data = r.json()

    audio_url = bot_data["recordings"][0]["media_shortcuts"]["audio_mixed"]["data"]["download_url"]
    audio_response = requests.get(audio_url)

    filename = f"reunion_{bot_id}.mp3"
    with open(filename, "wb") as f:
        f.write(audio_response.content)

    return filename

def delete_recording(recording_id):
    url = f"https://eu-central-1.recall.ai/api/v1/recording/{recording_id}/"
    headers = {"Authorization": f"Token {RECALL_API_KEY}"}

    requests.delete(url, headers=headers)