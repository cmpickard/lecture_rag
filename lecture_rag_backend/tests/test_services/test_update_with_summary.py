from tests.conftest import make_db_mock

UUID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"


class TestUpdateWithSummary:
    def test_executes_update(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_with_summary")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("On Plato's Forms", UUID)
        cursor.execute.assert_called_once()

    def test_sql_is_an_update(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_with_summary")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("Title", UUID)
        sql = cursor.execute.call_args[0][0]
        assert "UPDATE" in sql.upper()

    def test_passes_summary_and_uuid(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_with_summary")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("On Plato's Forms", UUID)
        params = cursor.execute.call_args[0][1]
        assert params[0] == "On Plato's Forms"
        assert params[1] == UUID

    def test_commits_transaction(self, mocker):
        _, _, conn = make_db_mock(mocker, "src.services.update_with_summary")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("Title", UUID)
        conn.commit.assert_called_once()

    def test_closes_connection(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.update_with_summary")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("Title", UUID)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.update_with_summary")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("Title", UUID)
        conn.close.assert_called_once()

    def test_does_not_raise_on_error(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.update_with_summary")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.update_with_summary import update_with_summary
        update_with_summary("Title", UUID)  # must not propagate
