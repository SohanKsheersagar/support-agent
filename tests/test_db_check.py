from unittest.mock import MagicMock, patch

import psycopg
import pytest

from app.db.check import check_database


def test_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="Set DATABASE_URL"):
        check_database()


def test_connection_is_closed_after_read_only_check(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    with patch("app.db.check.psycopg.connect") as connect:
        connection = MagicMock()
        connect.return_value.__enter__.return_value = connection
        check_database()
        connect.assert_called_once_with("postgresql://example/test", connect_timeout=5)
        connection.execute.assert_called_once_with("SELECT 1")
        connect.return_value.__exit__.assert_called_once()


def test_database_failure_is_not_reported_as_success(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    with patch("app.db.check.psycopg.connect", side_effect=psycopg.OperationalError):
        with pytest.raises(psycopg.OperationalError):
            check_database()
