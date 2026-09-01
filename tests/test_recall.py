from unittest.mock import patch, MagicMock
import pytest
from utils.recall import send_bot, get_audio, delete_recording


@patch("utils.recall.requests.post")
def test_send_bot(mock_post):
    mock_post.return_value = MagicMock(ok=True, json=lambda: {"id": "bot-123"})

    bot_id = send_bot("https://meet.google.com/abc-defg-hij")

    assert bot_id == "bot-123"


@patch("utils.recall.requests.post")
def test_send_bot_echec(mock_post):
    mock_post.return_value = MagicMock(ok=False, status_code=400, text="Lien invalide")

    with pytest.raises(RuntimeError):
        send_bot("lien-invalide")


@patch("utils.recall.requests.get")
def test_get_audio(mock_get, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    bot_response = MagicMock(ok=True, json=lambda: {
        "recordings": [{
            "id": "recording-456",
            "media_shortcuts": {"audio_mixed": {"data": {"download_url": "https://exemple.com/audio.mp3"}}}
        }]
    })
    audio_response = MagicMock(content=b"faux-audio")
    audio_response.raise_for_status = lambda: None
    mock_get.side_effect = [bot_response, audio_response]

    filename, recording_id = get_audio("bot-123")

    assert recording_id == "recording-456"
    assert filename == "reunion_bot-123.mp3"
    assert (tmp_path / filename).read_bytes() == b"faux-audio"


@patch("utils.recall.requests.delete")
def test_delete_recording_echec(mock_delete):
    mock_delete.return_value = MagicMock(ok=False, status_code=404, text="Introuvable")

    with pytest.raises(RuntimeError):
        delete_recording("recording-inconnu")
