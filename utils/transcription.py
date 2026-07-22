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
    texte = ""
    for segment in segments:
        speaker = segment["speaker"]
        contenu = segment["text"]
        texte += f"Speaker {speaker} : {contenu}\n"
    return texte