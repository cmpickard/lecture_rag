"""
Route integration tests for src/routes/chat.py.

All external dependencies (DB services, OpenAI) are mocked so these tests
run without a live database or API key.
"""
import json
import pytest

EXISTING_UUID = "d32ee5a6-4594-4c3d-aaec-717205c04cf4"
NEW_UUID = "aaaaaaaa-0000-0000-0000-000000000001"
DUMMY_EMBEDDING = [0.1] * 1536
HISTORY = [{"role": "user", "content": "What is virtue?"}]
# History whose total content exceeds HISTORY_CHAR_LIMIT (8000 chars)
LONG_HISTORY = [{"role": "user", "content": "x" * 4001}, {"role": "assistant", "content": "x" * 4001}]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def post_query(client, content="What is virtue?", conversation_id="", dialogue_mode=False):
    return client.post(
        "/",
        data=json.dumps({
            "content": content,
            "conversation_id": conversation_id,
            "dialogue_mode": dialogue_mode,
        }),
        content_type="application/json",
    )


def patch_all_services(mocker, *, cache_hit=None, cacheable=False,
                       history=None, is_new_conversation=False):
    """
    Patch every service imported by chat.py and return the mock objects
    in a dict for assertion in individual tests.
    """
    new_or_existing = NEW_UUID if is_new_conversation else (history if history is not None else HISTORY)

    mocks = {
        "retrieve_or_create_history": mocker.patch(
            "src.routes.chat.retrieve_or_create_history",
            return_value=NEW_UUID if is_new_conversation else (history if history is not None else HISTORY),
        ),
        "get_embedding": mocker.patch(
            "src.routes.chat.get_embedding",
            return_value=DUMMY_EMBEDDING,
        ),
        "cache_lookup": mocker.patch(
            "src.routes.chat.cache_lookup",
            return_value=cache_hit,
        ),
        "classify_query": mocker.patch(
            "src.routes.chat.classify_query",
            return_value=cacheable,
        ),
        "retrieve_most_similar": mocker.patch(
            "src.routes.chat.retrieve_most_similar",
            return_value=["Some lecture context."],
        ),
        "update_history": mocker.patch("src.routes.chat.update_history"),
        "update_with_summary": mocker.patch("src.routes.chat.update_with_summary"),
        "generate_summary": mocker.patch(
            "src.routes.chat.generate_summary",
            return_value="A generated title",
        ),
        "cache_write": mocker.patch("src.routes.chat.cache_write"),
        "compact_history": mocker.patch(
            "src.routes.chat.compact_history",
            return_value="Compacted summary of prior conversation.",
        ),
        "replace_history": mocker.patch("src.routes.chat.replace_history"),
        "client": mocker.patch("src.routes.chat.client"),
    }
    mocks["client"].responses.create.return_value = \
        type("R", (), {"output_text": "The LLM answered."})()
    return mocks


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------
class TestHomepage:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_returns_text_body(self, client):
        response = client.get("/")
        assert b"backend" in response.data.lower()


# ---------------------------------------------------------------------------
# GET /api/conversations
# ---------------------------------------------------------------------------
class TestGetConversations:
    def test_returns_200(self, mocker, client):
        mocker.patch(
            "src.routes.chat.retrieve_all_conversations",
            return_value={EXISTING_UUID: {"history": HISTORY, "summary": "Title"}},
        )
        response = client.get(f"/api/conversations?ids={EXISTING_UUID}")
        assert response.status_code == 200

    def test_returns_json_map(self, mocker, client):
        mocker.patch(
            "src.routes.chat.retrieve_all_conversations",
            return_value={EXISTING_UUID: {"history": HISTORY, "summary": "Title"}},
        )
        response = client.get(f"/api/conversations?ids={EXISTING_UUID}")
        data = response.get_json()
        assert EXISTING_UUID in data
        assert data[EXISTING_UUID]["history"] == HISTORY

    def test_passes_all_ids_to_service(self, mocker, client):
        mock_retrieve = mocker.patch(
            "src.routes.chat.retrieve_all_conversations",
            return_value={},
        )
        client.get(f"/api/conversations?ids={EXISTING_UUID}&ids={NEW_UUID}")
        call_args = mock_retrieve.call_args[0][0]
        assert EXISTING_UUID in call_args
        assert NEW_UUID in call_args

    def test_empty_ids_returns_empty_dict(self, mocker, client):
        mocker.patch("src.routes.chat.retrieve_all_conversations", return_value={})
        response = client.get("/api/conversations")
        assert response.status_code == 200
        assert response.get_json() == {}


# ---------------------------------------------------------------------------
# DELETE /api/delete/<resource_id>
# ---------------------------------------------------------------------------
class TestDeleteConversation:
    def test_returns_204(self, mocker, client):
        mocker.patch("src.routes.chat.conversation_deletion")
        response = client.delete(f"/api/delete/{EXISTING_UUID}")
        assert response.status_code == 204

    def test_calls_deletion_service_with_id(self, mocker, client):
        mock_delete = mocker.patch("src.routes.chat.conversation_deletion")
        client.delete(f"/api/delete/{EXISTING_UUID}")
        mock_delete.assert_called_once_with(EXISTING_UUID)

    def test_response_body_is_empty(self, mocker, client):
        mocker.patch("src.routes.chat.conversation_deletion")
        response = client.delete(f"/api/delete/{EXISTING_UUID}")
        assert response.data == b""


# ---------------------------------------------------------------------------
# POST / — cache hit path
# ---------------------------------------------------------------------------
class TestPostQueryCacheHit:
    def test_returns_200(self, mocker, client):
        patch_all_services(mocker, cache_hit="Cached answer.")
        response = post_query(client)
        assert response.status_code == 200

    def test_returns_cached_content(self, mocker, client):
        patch_all_services(mocker, cache_hit="Cached answer.")
        data = post_query(client).get_json()
        assert data["content"] == "Cached answer."

    def test_returns_assistant_role(self, mocker, client):
        patch_all_services(mocker, cache_hit="Cached answer.")
        data = post_query(client).get_json()
        assert data["role"] == "assistant"

    def test_does_not_call_llm_on_cache_hit(self, mocker, client):
        mocks = patch_all_services(mocker, cache_hit="Cached answer.")
        post_query(client)
        mocks["client"].responses.create.assert_not_called()

    def test_does_not_call_classify_query_on_hit(self, mocker, client):
        mocks = patch_all_services(mocker, cache_hit="Cached answer.")
        post_query(client)
        mocks["classify_query"].assert_not_called()

    def test_updates_assistant_history_on_hit(self, mocker, client):
        # Use is_new_conversation so retrieve_or_create_history returns a UUID
        # string (new convo path) — update_history is called exactly once with
        # that UUID.
        mocks = patch_all_services(mocker, cache_hit="Cached answer.", is_new_conversation=True)
        post_query(client)
        mocks["update_history"].assert_called_once_with(
            "assistant", "Cached answer.", NEW_UUID
        )

    def test_generates_summary_on_first_turn_hit(self, mocker, client):
        """When history == '' (new conversation), a summary should be generated."""
        mocks = patch_all_services(mocker, cache_hit="Cached answer.", is_new_conversation=True)
        post_query(client)
        mocks["generate_summary"].assert_called_once()

    def test_no_summary_on_subsequent_turn_hit(self, mocker, client):
        mocks = patch_all_services(mocker, cache_hit="Cached answer.")
        post_query(client)
        mocks["generate_summary"].assert_not_called()


# ---------------------------------------------------------------------------
# POST / — cache miss, normal RAG path
# ---------------------------------------------------------------------------
class TestPostQueryCacheMiss:
    def test_returns_200(self, mocker, client):
        patch_all_services(mocker)
        response = post_query(client)
        assert response.status_code == 200

    def test_returns_llm_response_content(self, mocker, client):
        patch_all_services(mocker)
        data = post_query(client).get_json()
        assert data["content"] == "The LLM answered."

    def test_returns_conversation_id(self, mocker, client):
        patch_all_services(mocker)
        data = post_query(client).get_json()
        assert "conversation_id" in data

    def test_calls_get_embedding(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client, content="What is virtue?")
        mocks["get_embedding"].assert_called_once_with("What is virtue?")

    def test_calls_retrieve_most_similar(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client)
        mocks["retrieve_most_similar"].assert_called_once_with(DUMMY_EMBEDDING)

    def test_calls_llm(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client)
        mocks["client"].responses.create.assert_called_once()

    def test_uses_basic_model_for_instruction_mode(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client, dialogue_mode=False)
        call_kwargs = mocks["client"].responses.create.call_args.kwargs
        from src.config import BASIC_MODEL
        assert call_kwargs["model"] == BASIC_MODEL

    def test_uses_dialogue_model_for_dialogue_mode(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client, dialogue_mode=True)
        call_kwargs = mocks["client"].responses.create.call_args.kwargs
        from src.config import DIALOGUE_MODEL
        assert call_kwargs["model"] == DIALOGUE_MODEL

    def test_writes_cache_when_cacheable(self, mocker, client):
        mocks = patch_all_services(mocker, cacheable=True)
        post_query(client)
        mocks["cache_write"].assert_called_once()

    def test_does_not_write_cache_when_not_cacheable(self, mocker, client):
        mocks = patch_all_services(mocker, cacheable=False)
        post_query(client)
        mocks["cache_write"].assert_not_called()

    def test_updates_assistant_history(self, mocker, client):
        # Use is_new_conversation so retrieve_or_create_history returns a UUID
        # string (new convo path) — update_history is called exactly once with
        # that UUID.
        mocks = patch_all_services(mocker, is_new_conversation=True)
        post_query(client)
        mocks["update_history"].assert_called_once_with(
            "assistant", "The LLM answered.", NEW_UUID
        )

    def test_generates_summary_on_first_turn(self, mocker, client):
        mocks = patch_all_services(mocker, is_new_conversation=True)
        post_query(client)
        mocks["generate_summary"].assert_called_once()

    def test_no_summary_on_subsequent_turn(self, mocker, client):
        mocks = patch_all_services(mocker)
        post_query(client)
        mocks["generate_summary"].assert_not_called()

    def test_summary_is_null_on_subsequent_turn(self, mocker, client):
        patch_all_services(mocker)
        data = post_query(client).get_json()
        assert data["summary"] is None

    def test_summary_returned_on_first_turn(self, mocker, client):
        patch_all_services(mocker, is_new_conversation=True)
        data = post_query(client).get_json()
        assert data["summary"] == "A generated title"

    def test_new_conversation_id_returned_on_first_turn(self, mocker, client):
        patch_all_services(mocker, is_new_conversation=True)
        data = post_query(client).get_json()
        assert data["conversation_id"] == NEW_UUID


# ---------------------------------------------------------------------------
# POST / — history compaction
# ---------------------------------------------------------------------------
class TestHistoryCompaction:
    def test_compaction_triggered_when_history_too_long(self, mocker, client):
        mocks = patch_all_services(mocker, history=LONG_HISTORY)
        post_query(client)
        mocks["compact_history"].assert_called_once_with(LONG_HISTORY)

    def test_compaction_not_triggered_when_history_short(self, mocker, client):
        mocks = patch_all_services(mocker, history=HISTORY)
        post_query(client)
        mocks["compact_history"].assert_not_called()

    def test_replace_history_called_when_compaction_triggered(self, mocker, client):
        mocks = patch_all_services(mocker, history=LONG_HISTORY)
        post_query(client, conversation_id=EXISTING_UUID)
        mocks["replace_history"].assert_called_once_with(
            "Compacted summary of prior conversation.", EXISTING_UUID
        )

    def test_replace_history_not_called_when_no_compaction(self, mocker, client):
        mocks = patch_all_services(mocker, history=HISTORY)
        post_query(client)
        mocks["replace_history"].assert_not_called()

    def test_compaction_not_triggered_for_new_conversation(self, mocker, client):
        mocks = patch_all_services(mocker, is_new_conversation=True)
        post_query(client)
        mocks["compact_history"].assert_not_called()

    def test_returns_200_after_compaction(self, mocker, client):
        patch_all_services(mocker, history=LONG_HISTORY)
        response = post_query(client, conversation_id=EXISTING_UUID)
        assert response.status_code == 200
