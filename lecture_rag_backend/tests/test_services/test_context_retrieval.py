import pytest
from tests.conftest import make_db_mock, make_embedding_response


DUMMY_EMBEDDING = [0.1] * 1536


# ---------------------------------------------------------------------------
# get_embedding
# ---------------------------------------------------------------------------
class TestGetEmbedding:
    def test_returns_list_of_floats(self, mocker):
        mock_client = mocker.patch("src.services.context_retrieval.client")
        mock_client.embeddings.create.return_value = make_embedding_response(DUMMY_EMBEDDING)
        from src.services.context_retrieval import get_embedding
        result = get_embedding("Test query")
        assert result == DUMMY_EMBEDDING

    def test_calls_correct_model(self, mocker):
        mock_client = mocker.patch("src.services.context_retrieval.client")
        mock_client.embeddings.create.return_value = make_embedding_response(DUMMY_EMBEDDING)
        from src.services.context_retrieval import get_embedding
        get_embedding("Test query")
        call_kwargs = mock_client.embeddings.create.call_args
        assert call_kwargs.kwargs["model"] == "text-embedding-3-small"

    def test_passes_input_string(self, mocker):
        mock_client = mocker.patch("src.services.context_retrieval.client")
        mock_client.embeddings.create.return_value = make_embedding_response(DUMMY_EMBEDDING)
        from src.services.context_retrieval import get_embedding
        get_embedding("What is consciousness?")
        assert mock_client.embeddings.create.call_args.kwargs["input"] == "What is consciousness?"


# ---------------------------------------------------------------------------
# extract_contents
# ---------------------------------------------------------------------------
class TestExtractContents:
    def test_extracts_second_column(self):
        from src.services.context_retrieval import extract_contents
        rows = [("Lecture 1", "Content A", 0.9), ("Lecture 2", "Content B", 0.8)]
        assert extract_contents(rows) == ["Content A", "Content B"]

    def test_empty_results(self):
        from src.services.context_retrieval import extract_contents
        assert extract_contents([]) == []


# ---------------------------------------------------------------------------
# retrieve_most_similar
# ---------------------------------------------------------------------------
class TestRetrieveMostSimilar:
    def test_returns_list_of_content_strings(self, mocker):
        rows = [
            ("Lecture 1", "Plato's theory of Forms.", 0.85),
            ("Lecture 2", "The Allegory of the Cave.", 0.75),
        ]
        _, cursor, _ = make_db_mock(mocker, "src.services.context_retrieval", fetchall=rows)
        from src.services.context_retrieval import retrieve_most_similar
        result = retrieve_most_similar(DUMMY_EMBEDDING)
        assert result == ["Plato's theory of Forms.", "The Allegory of the Cave."]

    def test_returns_empty_list_when_no_matches(self, mocker):
        make_db_mock(mocker, "src.services.context_retrieval", fetchall=[])
        from src.services.context_retrieval import retrieve_most_similar
        result = retrieve_most_similar(DUMMY_EMBEDDING)
        assert result == []

    def test_closes_cursor_and_connection(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.context_retrieval", fetchall=[])
        from src.services.context_retrieval import retrieve_most_similar
        retrieve_most_similar(DUMMY_EMBEDDING)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_db_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.context_retrieval")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.context_retrieval import retrieve_most_similar
        result = retrieve_most_similar(DUMMY_EMBEDDING)
        assert result is None
        conn.close.assert_called_once()
