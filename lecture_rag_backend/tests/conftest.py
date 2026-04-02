"""
Shared fixtures and environment setup for the test suite.

This file is loaded by pytest before any test collection begins,
so setting OPENAI_API_KEY here ensures src.extensions can import
the OpenAI client without raising an authentication error.
"""
import os
import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")


def make_db_mock(mocker, module_path, fetchone=None, fetchall=None):
    """
    Return a (mock_connect, mock_cursor, mock_conn) triple for any service
    that calls psycopg2.connect().

    Usage:
        mock_connect, cursor, conn = make_db_mock(mocker, 'src.services.my_service')
    """
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = fetchone
    mock_cursor.fetchall.return_value = fetchall if fetchall is not None else []

    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_connect = mocker.patch(f"{module_path}.psycopg2.connect", return_value=mock_conn)
    return mock_connect, mock_cursor, mock_conn


def make_openai_response(text: str):
    """Return a minimal mock that mimics client.responses.create() return value."""
    import unittest.mock as mock
    resp = mock.MagicMock()
    resp.output_text = text
    return resp


def make_embedding_response(embedding: list):
    """Return a minimal mock that mimics client.embeddings.create() return value."""
    import unittest.mock as mock
    item = mock.MagicMock()
    item.embedding = embedding
    resp = mock.MagicMock()
    resp.data = [item]
    return resp


@pytest.fixture()
def app():
    """Configured Flask test application."""
    from app import create_app
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()
