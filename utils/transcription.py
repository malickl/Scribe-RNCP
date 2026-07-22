"""
Fonctions liées à AssemblyAI : transcription et diarisation.
"""
import assemblyai as aai


def transcribe(filename, transcriber):
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="fr"
    )
    transcript = transcriber.transcribe(filename, config)

    segments = []
    for utterance in transcript.utterances:
        segments.append({
            "speaker": utterance.speaker,
            "text": utterance.text
        })
    return segments

def format_transcription(segments):
    """
    Transforme la liste de segments en texte "Speaker A : ... / Speaker B : ..."
    """
    pass
