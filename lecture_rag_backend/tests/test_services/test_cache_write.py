from tests.conftest import make_db_mock

DUMMY_EMBEDDING = [0.1] * 1536


class TestCacheWrite:
    def test_executes_insert(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.cache_write")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "What is virtue?", "Virtue is excellence.", False)
        cursor.execute.assert_called_once()

    def test_commits_transaction(self, mocker):
        _, _, conn = make_db_mock(mocker, "src.services.cache_write")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "Q", "A", False)
        conn.commit.assert_called_once()

    def test_passes_all_four_values_to_query(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.cache_write")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "What is virtue?", "Virtue is excellence.", True)
        params = cursor.execute.call_args[0][1]
        assert params[0] == DUMMY_EMBEDDING
        assert params[1] == "What is virtue?"
        assert params[2] == "Virtue is excellence."
        assert params[3] is True

    def test_closes_connection_after_success(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.cache_write")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "Q", "A", False)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_db_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.cache_write")
        cursor.execute.side_effect = Exception("Insert failed")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "Q", "A", False)  # should not raise
        conn.close.assert_called_once()

    def test_does_not_commit_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.cache_write")
        cursor.execute.side_effect = Exception("Insert failed")
        from src.services.cache_write import cache_write
        cache_write(DUMMY_EMBEDDING, "Q", "A", False)
        conn.commit.assert_not_called()
