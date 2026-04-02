import json
from tests.conftest import make_db_mock


class TestReplaceHistory:
    CONV_ID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"

    def test_executes_update(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.replace_history")
        from src.services.replace_history import replace_history
        replace_history("Student asked about Forms.", self.CONV_ID)
        cursor.execute.assert_called_once()

    def test_history_is_single_system_message(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.replace_history")
        from src.services.replace_history import replace_history
        replace_history("Student asked about Forms.", self.CONV_ID)
        written_history = json.loads(cursor.execute.call_args[0][1][0])
        assert len(written_history) == 1
        assert written_history[0]["role"] == "system"

    def test_history_contains_summary_text(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.replace_history")
        from src.services.replace_history import replace_history
        replace_history("Student asked about Forms.", self.CONV_ID)
        written_history = json.loads(cursor.execute.call_args[0][1][0])
        assert "Student asked about Forms." in written_history[0]["content"]

    def test_passes_correct_uuid(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.replace_history")
        from src.services.replace_history import replace_history
        replace_history("Summary text.", self.CONV_ID)
        assert cursor.execute.call_args[0][1][1] == self.CONV_ID

    def test_commits_transaction(self, mocker):
        _, _, conn = make_db_mock(mocker, "src.services.replace_history")
        from src.services.replace_history import replace_history
        replace_history("Summary text.", self.CONV_ID)
        conn.commit.assert_called_once()
