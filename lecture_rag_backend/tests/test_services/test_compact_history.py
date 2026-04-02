from tests.conftest import make_openai_response


class TestCompactHistory:
    def test_returns_llm_output(self, mocker):
        mocker.patch(
            "src.services.compact_history.client",
            **{"responses.create.return_value": make_openai_response("Student asked about virtue and received an explanation.")},
        )
        from src.services.compact_history import compact_history
        history = [
            {"role": "user", "content": "What is virtue?"},
            {"role": "assistant", "content": "Virtue is excellence of character."},
        ]
        result = compact_history(history)
        assert result == "Student asked about virtue and received an explanation."

    def test_includes_history_content_in_prompt(self, mocker):
        mock_client = mocker.patch("src.services.compact_history.client")
        mock_client.responses.create.return_value = make_openai_response("Summary")
        from src.services.compact_history import compact_history
        history = [{"role": "user", "content": "Tell me about Kant."}]
        compact_history(history)
        prompt_arg = mock_client.responses.create.call_args.kwargs.get("input", "")
        assert "Kant" in prompt_arg

    def test_all_messages_included_in_prompt(self, mocker):
        mock_client = mocker.patch("src.services.compact_history.client")
        mock_client.responses.create.return_value = make_openai_response("Summary")
        from src.services.compact_history import compact_history
        history = [
            {"role": "user", "content": "What is the categorical imperative?"},
            {"role": "assistant", "content": "It is Kant's supreme principle of morality."},
            {"role": "user", "content": "Can you give an example?"},
        ]
        compact_history(history)
        prompt_arg = mock_client.responses.create.call_args.kwargs.get("input", "")
        assert "categorical imperative" in prompt_arg
        assert "morality" in prompt_arg
        assert "example" in prompt_arg

    def test_calls_responses_create_once(self, mocker):
        mock_client = mocker.patch("src.services.compact_history.client")
        mock_client.responses.create.return_value = make_openai_response("Summary")
        from src.services.compact_history import compact_history
        compact_history([{"role": "user", "content": "Hi"}])
        mock_client.responses.create.assert_called_once()
