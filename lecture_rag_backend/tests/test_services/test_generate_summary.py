from tests.conftest import make_openai_response


class TestGenerateSummary:
    def test_returns_llm_output(self, mocker):
        mocker.patch(
            "src.services.generate_summary.client",
            **{"responses.create.return_value": make_openai_response("Plato and the theory of Forms")},
        )
        from src.services.generate_summary import generate_summary
        result = generate_summary("user: What are Forms?\nassistant: Forms are perfect ideals.")
        assert result == "Plato and the theory of Forms"

    def test_passes_history_in_prompt(self, mocker):
        mock_client = mocker.patch("src.services.generate_summary.client")
        mock_client.responses.create.return_value = make_openai_response("Title")
        from src.services.generate_summary import generate_summary
        history = "user: Tell me about Kant.\nassistant: Kant developed the categorical imperative."
        generate_summary(history)
        prompt_arg = mock_client.responses.create.call_args.kwargs.get(
            "input", mock_client.responses.create.call_args[1].get("input", "")
        )
        assert "Kant" in prompt_arg

    def test_calls_responses_create(self, mocker):
        mock_client = mocker.patch("src.services.generate_summary.client")
        mock_client.responses.create.return_value = make_openai_response("Title")
        from src.services.generate_summary import generate_summary
        generate_summary("user: Hi\nassistant: Hello")
        mock_client.responses.create.assert_called_once()
