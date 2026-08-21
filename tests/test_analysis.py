from unittest.mock import MagicMock
from utils.analysis import analyze


def test_analyze():
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = (
        '{"theme": "Suivi projet", "categorie": "Interne", "humeur": "positif", '
        '"resume": "Résumé de la réunion.", "actions": ["Faire X"]}'
    )

    report = analyze("texte de la transcription", client, "prompt système")

    assert report["theme"] == "Suivi projet"
    assert report["actions"] == ["Faire X"]

    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}
    assert kwargs["messages"][1]["content"] == "texte de la transcription"
