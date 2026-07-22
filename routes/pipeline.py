"""
Lot 3 : Traitement
Ne capte rien. Reçoit un fichier audio déjà obtenu (peu importe son origine)
et le transforme : transcription, analyse, écriture en base.
C'est ici que vit l'abstraction "source audio commune" : run_pipeline().
"""

# from utils.transcription import transcribe, format_transcription
# from utils.analysis import analyze

def run_pipeline(filename, table, row_id):
    """
    Fonction commune aux deux modes de captation.
    reçoit : le nom du fichier audio, la table cible ('reunions' ou 'dictaphones'),
    l'identifiant de la ligne à mettre à jour.
    """
    # segments = transcribe(filename, transcriber)
    # texte = format_transcription(segments)
    # report = analyze(texte, client_groq, system_prompt)
    # ... écriture en base ...
    # ... suppression du fichier local ...
    pass
