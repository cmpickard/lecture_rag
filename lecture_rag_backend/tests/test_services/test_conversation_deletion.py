from tests.conftest import make_db_mock

TEST_UUID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"


class TestConversationDeletion:
    def test_executes_delete_with_uuid(self, mocker):
        _, cursor, _ = make_db_mock(mocker, "src.services.conversation_deletion")
        from src.services.conversation_deletion import conversation_deletion
        conversation_deletion(TEST_UUID)
        cursor.execute.assert_called_once()
        params = cursor.execute.call_args[0][1]
        assert params[0] == TEST_UUID

    def test_commits_transaction(self, mocker):
        _, _, conn = make_db_mock(mocker, "src.services.conversation_deletion")
        from src.services.conversation_deletion import conversation_deletion
        conversation_deletion(TEST_UUID)
        conn.commit.assert_called_once()

    def test_returns_none(self, mocker):
        make_db_mock(mocker, "src.services.conversation_deletion")
        from src.services.conversation_deletion import conversation_deletion
        result = conversation_deletion(TEST_UUID)
        assert result is None

    def test_closes_connection_after_success(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.conversation_deletion")
        from src.services.conversation_deletion import conversation_deletion
        conversation_deletion(TEST_UUID)
        cursor.close.assert_called_once()
        conn.close.assert_called_once()

    def test_closes_connection_on_db_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.conversation_deletion")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.conversation_deletion import conversation_deletion
        conversation_deletion(TEST_UUID)  # should not raise
        conn.close.assert_called_once()

    def test_does_not_commit_on_error(self, mocker):
        _, cursor, conn = make_db_mock(mocker, "src.services.conversation_deletion")
        cursor.execute.side_effect = Exception("DB error")
        from src.services.conversation_deletion import conversation_deletion
        conversation_deletion(TEST_UUID)
        conn.commit.assert_not_called()
