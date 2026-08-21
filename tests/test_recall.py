from unittest.mock import patch, MagicMock
import pytest
from utils.recall import send_bot


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
