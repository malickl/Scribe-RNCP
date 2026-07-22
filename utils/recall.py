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
