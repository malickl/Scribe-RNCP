from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch, MagicMock
from utils.database import rename_item, get_all_reunion_keys


def _fake_get_cursor(cur):
    @contextmanager
    def get_cursor(commit=False):
        yield cur
    return get_cursor


@patch("utils.database.get_cursor")
def test_rename_item_reunions(mock_get_cursor):
    cur = MagicMock()
    mock_get_cursor.side_effect = _fake_get_cursor(cur)

    rename_item("user-1", "reunions", "reunion-1", "Nouveau titre")

    sql = cur.execute.call_args[0][0]
    assert "UPDATE reunions" in sql
    assert "id_reunion" in sql


@patch("utils.database.get_cursor")
def test_rename_item_dictaphones(mock_get_cursor):
    cur = MagicMock()
    mock_get_cursor.side_effect = _fake_get_cursor(cur)

    rename_item("user-1", "dictaphones", "dicta-1", "Nouveau titre")

    sql = cur.execute.call_args[0][0]
    assert "UPDATE dictaphones" in sql
    assert "id_dictaphone" in sql


@patch("utils.database.get_cursor")
def test_get_all_reunion_keys(mock_get_cursor):
    cur = MagicMock()
    cur.fetchall.return_value = [
        ("Réunion X", datetime(2026, 8, 20, 10, 0), "id-1"),
    ]
    mock_get_cursor.side_effect = _fake_get_cursor(cur)

    keys = get_all_reunion_keys()

    assert keys[("Réunion X", "2026-08-20T10:00:00")] == "id-1"
