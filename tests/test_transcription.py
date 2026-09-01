from unittest.mock import MagicMock
from utils.transcription import transcribe, format_transcription


def test_format_transcription():
    segments = [
        {"speaker": "A", "text": "Bonjour"},
        {"speaker": "B", "text": "Salut"},
    ]

    assert format_transcription(segments) == "Speaker A : Bonjour\nSpeaker B : Salut\n"


def test_format_transcription_vide():
    assert format_transcription([]) == ""


def test_transcribe():
    utterance = MagicMock(speaker="A", text="Bonjour")
    transcriber = MagicMock()
    transcriber.transcribe.return_value.utterances = [utterance]

    segments = transcribe("fichier.mp3", transcriber)

    assert segments == [{"speaker": "A", "text": "Bonjour"}]


def test_transcribe_aucune_parole_detectee():
    """Sur un audio sans parole détectée, AssemblyAI renvoie
    utterances=None plutôt qu'une liste vide — ne doit pas planter."""
    transcriber = MagicMock()
    transcriber.transcribe.return_value.utterances = None

    segments = transcribe("silence.wav", transcriber)

    assert segments == []
