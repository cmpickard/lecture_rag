import pytest
from tests.conftest import make_db_mock

DUMMY_EMBEDDING = [0.1] * 1536


class TestCacheLookup:
    def test_returns_response_text_on_hit(self, mocker):
        make_db_mock(mocker, "src.services.cache_lookup", fetchone=("Cached answer.", 0.95))
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result == "Cached answer."

    def test_returns_none_on_miss_below_threshold(self, mocker):
        make_db_mock(mocker, "src.services.cache_lookup", fetchone=("Some answer.", 0.60))
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result is None

    def test_returns_none_when_cache_is_empty(self, mocker):
        make_db_mock(mocker, "src.services.cache_lookup", fetchone=None)
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result is None

    def test_hit_exactly_at_threshold_is_not_returned(self, mocker):
        """Threshold is 0.7; similarity == 0.7 should NOT be returned (strict >)."""
        make_db_mock(mocker, "src.services.cache_lookup", fetchone=("Answer.", 0.70))
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result is None

    def test_hit_just_above_threshold_is_returned(self, mocker):
        make_db_mock(mocker, "src.services.cache_lookup", fetchone=("Answer.", 0.701))
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result == "Answer."

    def test_passes_dialogue_mode_to_query(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.cache_lookup", fetchone=None)
        from src.services.cache_lookup import cache_lookup
        cache_lookup(DUMMY_EMBEDDING, True)
        call_args = cursor.execute.call_args[0]
        params = call_args[1]
        assert params[1] is True  # dialogue_mode passed as second param

    def test_closes_connection_on_success(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.cache_lookup", fetchone=None)
        from src.services.cache_lookup import cache_lookup
        cache_lookup(DUMMY_EMBEDDING, False)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_db_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.cache_lookup")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.cache_lookup import cache_lookup
        result = cache_lookup(DUMMY_EMBEDDING, False)
        assert result is None
        conn.close.assert_called_once()
