import json
from tests.conftest import make_db_mock

UUID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"


class TestUpdateHistory:
    def test_executes_update(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("user", "Hello", UUID)
        cursor.execute.assert_called_once()

    def test_sql_is_an_update(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("user", "Hello", UUID)
        sql = cursor.execute.call_args[0][0]
        assert "UPDATE" in sql.upper()

    def test_appends_correct_role_and_content(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("assistant", "Virtue is excellence.", UUID)
        params = cursor.execute.call_args[0][1]
        appended = json.loads(params[0])
        assert appended == [{"role": "assistant", "content": "Virtue is excellence."}]

    def test_passes_uuid_as_where_clause_param(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("user", "Q", UUID)
        params = cursor.execute.call_args[0][1]
        assert params[1] == UUID

    def test_commits_transaction(self, mocker):
        _, _, conn = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("user", "Q", UUID)
        conn.commit.assert_called_once()

    def test_closes_connection(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.update_history")
        from src.services.update_history import update_history
        update_history("user", "Q", UUID)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.update_history")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.update_history import update_history
        update_history("user", "Q", UUID)
        conn.close.assert_called_once()

    def test_does_not_commit_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.update_history")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.update_history import update_history
        update_history("user", "Q", UUID)
        conn.commit.assert_not_called()
