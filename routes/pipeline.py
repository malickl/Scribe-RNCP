"""
Lot 3 : Traitement
Ne capte rien. Reçoit un fichier audio déjà obtenu (peu importe son origine)
et le transforme : transcription, analyse, écriture en base.
C'est ici que vit l'abstraction "source audio commune" : run_pipeline().
"""

from utils.transcription import transcribe, format_transcription
from utils.analysis import analyze
from utils.database import update_analysis
from config import transcriber, client_groq, system_prompt
import os


def run_pipeline(filename, table, row_id):
    segments = transcribe(filename, transcriber)
    text = format_transcription(segments)
    report = analyze(text, client_groq, system_prompt)

    update_analysis(table, row_id, report)

    os.remove(filename)