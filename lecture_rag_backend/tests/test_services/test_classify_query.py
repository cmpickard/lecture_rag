import pytest
from unittest.mock import patch
from tests.conftest import make_openai_response


def _patch_client(text):
    return patch(
        "src.services.classify_query.client",
        **{"responses.create.return_value": make_openai_response(text)},
    )


def test_returns_true_for_yes():
    with _patch_client("YES"):
        from src.services.classify_query import classify_query
        assert classify_query("Explain the ontological argument.") is True


def test_returns_false_for_no():
    with _patch_client("NO"):
        from src.services.classify_query import classify_query
        assert classify_query("Can you clarify that last point?") is False


def test_case_insensitive_yes():
    with _patch_client("yes"):
        from src.services.classify_query import classify_query
        assert classify_query("What is Plato famous for?") is True


def test_case_insensitive_mixed():
    with _patch_client("Yes"):
        from src.services.classify_query import classify_query
        assert classify_query("What is Plato famous for?") is True


def test_returns_false_for_unexpected_response():
    with _patch_client("MAYBE"):
        from src.services.classify_query import classify_query
        assert classify_query("Some query") is False


def test_returns_false_for_empty_response():
    with _patch_client(""):
        from src.services.classify_query import classify_query
        assert classify_query("Some query") is False


def test_strips_whitespace_from_response():
    with _patch_client("  YES  \n"):
        from src.services.classify_query import classify_query
        assert classify_query("Explain Socrates.") is True


def test_calls_llm_with_low_token_limit(mocker):
    mock_client = mocker.patch("src.services.classify_query.client")
    mock_client.responses.create.return_value = make_openai_response("NO")
    from src.services.classify_query import classify_query
    classify_query("A query")
    call_kwargs = mock_client.responses.create.call_args
    assert call_kwargs.kwargs.get("max_output_tokens", 0) <= 32
