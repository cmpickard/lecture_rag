import json
import pytest
from tests.conftest import make_db_mock

EXISTING_UUID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"
NEW_UUID = "a1b2c3d4-0000-0000-0000-000000000001"

HISTORY = [{"role": "user", "content": "Hi"}]


class TestRetrieveOrCreateHistory:
    # -----------------------------------------------------------------------
    # Retrieving an existing conversation
    # -----------------------------------------------------------------------
    def test_returns_history_for_existing_uuid(self, mocker):
        make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(HISTORY,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        result = retrieve_or_create_history(EXISTING_UUID, "Any query")
        assert result == HISTORY

    def test_returns_none_when_uuid_not_found(self, mocker):
        make_db_mock(mocker, "src.services.retrieve_or_create_history", fetchone=None)
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        result = retrieve_or_create_history(EXISTING_UUID, "Any query")
        assert result is None

    def test_does_not_commit_when_retrieving(self, mocker):
        _, _, conn = make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(HISTORY,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history(EXISTING_UUID, "Any query")
        conn.commit.assert_not_called()

    # -----------------------------------------------------------------------
    # Creating a new conversation (uuid == '')
    # -----------------------------------------------------------------------
    def test_returns_new_uuid_for_empty_conversation_id(self, mocker):
        make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(NEW_UUID,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        result = retrieve_or_create_history("", "First message")
        assert result == NEW_UUID

    def test_inserts_initial_user_message_when_creating(self, mocker):
        _, cursor, _ = make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(NEW_UUID,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history("", "First message")
        sql_call = cursor.execute.call_args[0][0]
        assert "INSERT" in sql_call.upper()

    def test_initial_message_contains_user_query(self, mocker):
        _, cursor, _ = make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(NEW_UUID,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history("", "What is consciousness?")
        params = cursor.execute.call_args[0][1]
        history_json = params[0]
        history = json.loads(history_json)
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "What is consciousness?"

    def test_commits_when_creating_new_conversation(self, mocker):
        _, _, conn = make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(NEW_UUID,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history("", "First message")
        conn.commit.assert_called_once()

    # -----------------------------------------------------------------------
    # Common: connection cleanup
    # -----------------------------------------------------------------------
    def test_closes_connection(self, mocker):
        _, cursor, conn = make_db_mock(
            mocker, "src.services.retrieve_or_create_history",
            fetchone=(HISTORY,)
        )
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history(EXISTING_UUID, "Q")
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.retrieve_or_create_history")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.retrieve_or_create_history import retrieve_or_create_history
        retrieve_or_create_history(EXISTING_UUID, "Q")
        conn.close.assert_called_once()
