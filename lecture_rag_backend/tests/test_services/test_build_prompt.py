from src.services.build_prompt import build_prompt


def test_returns_two_messages():
    result = build_prompt("System instructions.", "User question?")
    assert len(result) == 2


def test_first_message_is_system():
    result = build_prompt("System instructions.", "User question?")
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "System instructions."


def test_second_message_is_user():
    result = build_prompt("System instructions.", "User question?")
    assert result[1]["role"] == "user"
    assert result[1]["content"] == "User question?"


def test_preserves_content_exactly():
    instructions = "You are a TA.\n\nContext: {context}"
    query = "Explain the ontological argument."
    result = build_prompt(instructions, query)
    assert result[0]["content"] == instructions
    assert result[1]["content"] == query


def test_returns_list():
    result = build_prompt("i", "q")
    assert isinstance(result, list)


def test_each_item_is_dict():
    result = build_prompt("i", "q")
    for msg in result:
        assert isinstance(msg, dict)
        assert "role" in msg
        assert "content" in msg
