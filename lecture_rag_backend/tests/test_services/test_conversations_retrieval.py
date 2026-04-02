import pytest
from tests.conftest import make_db_mock

UUID_1 = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"
UUID_2 = "d33ded99-da56-43e4-9725-de1cc07a362f"

HISTORY = [{"role": "user", "content": "What is a Form?"}, {"role": "assistant", "content": "A Form is..."}]


class TestRetrieveConversation:
    def test_returns_history_and_summary_when_found(self, mocker):
        make_db_mock(
            mocker, "src.services.conversations_retrieval",
            fetchone=(HISTORY, "On Plato's Forms")
        )
        from src.services.conversations_retrieval import retrieve_conversation
        result = retrieve_conversation(UUID_1)
        assert result["history"] == HISTORY
        assert result["summary"] == "On Plato's Forms"

    def test_returns_empty_history_when_not_found(self, mocker):
        make_db_mock(mocker, "src.services.conversations_retrieval", fetchone=None)
        from src.services.conversations_retrieval import retrieve_conversation
        result = retrieve_conversation(UUID_1)
        assert result["history"] == []

    def test_returns_empty_summary_when_not_found(self, mocker):
        make_db_mock(mocker, "src.services.conversations_retrieval", fetchone=None)
        from src.services.conversations_retrieval import retrieve_conversation
        result = retrieve_conversation(UUID_1)
        assert result["summary"] == ""

    def test_passes_uuid_to_query(self, mocker):
        _, cursor, _ = make_db_mock(
            mocker, "src.services.conversations_retrieval",
            fetchone=(HISTORY, None)
        )
        from src.services.conversations_retrieval import retrieve_conversation
        retrieve_conversation(UUID_1)
        params = cursor.execute.call_args[0][1]
        assert params[0] == UUID_1

    def test_closes_connection(self, mocker):
        _, cursor, conn = make_db_mock(
            mocker, "src.services.conversations_retrieval",
            fetchone=(HISTORY, None)
        )
        from src.services.conversations_retrieval import retrieve_conversation
        retrieve_conversation(UUID_1)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.conversations_retrieval")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.conversations_retrieval import retrieve_conversation
        retrieve_conversation(UUID_1)
        conn.close.assert_called_once()

    def test_returns_empty_defaults_on_db_error(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.conversations_retrieval")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.conversations_retrieval import retrieve_conversation
        result = retrieve_conversation(UUID_1)
        assert result["history"] == []
        assert result["summary"] == ""


class TestRetrieveAllConversations:
    def test_returns_dict_keyed_by_uuid(self, mocker):
        mocker.patch(
            "src.services.conversations_retrieval.retrieve_conversation",
            side_effect=lambda uuid: {"history": [], "summary": uuid}
        )
        from src.services.conversations_retrieval import retrieve_all_conversations
        result = retrieve_all_conversations([UUID_1, UUID_2])
        assert set(result.keys()) == {UUID_1, UUID_2}

    def test_calls_retrieve_conversation_for_each_uuid(self, mocker):
        mock_retrieve = mocker.patch(
            "src.services.conversations_retrieval.retrieve_conversation",
            return_value={"history": [], "summary": None}
        )
        from src.services.conversations_retrieval import retrieve_all_conversations
        retrieve_all_conversations([UUID_1, UUID_2])
        assert mock_retrieve.call_count == 2

    def test_returns_empty_dict_for_empty_input(self, mocker):
        mocker.patch("src.services.conversations_retrieval.retrieve_conversation")
        from src.services.conversations_retrieval import retrieve_all_conversations
        result = retrieve_all_conversations([])
        assert result == {}
