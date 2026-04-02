from flask import Blueprint, request, jsonify

from src.config import BASIC_MODEL, DIALOGUE_MODEL, BASIC_PROMPT_PATH, DIALOGUE_PROMPT_PATH, HISTORY_CHAR_LIMIT
from src.extensions import client
from src.services.build_prompt import build_prompt
from src.services.context_retrieval import retrieve_most_similar, get_embedding
from src.services.conversations_retrieval import retrieve_all_conversations
from src.services.generate_summary import generate_summary
from src.services.retrieve_or_create_history import retrieve_or_create_history
from src.services.update_history import update_history
from src.services.update_with_summary import update_with_summary
from src.services.conversation_deletion import conversation_deletion
from src.services.cache_lookup import cache_lookup
from src.services.classify_query import classify_query
from src.services.cache_write import cache_write
from src.services.compact_history import compact_history
from src.services.replace_history import replace_history


def history_is_too_long(history: list) -> bool:
    return sum(len(m["content"]) for m in history) > HISTORY_CHAR_LIMIT

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/", methods=["GET"])
def display_homepage():
    return "This is the backend! Go to the frontend port to see the stuff."


@chat_bp.route("/api/conversations", methods=["GET"])
def get_conversations():
    conversation_ids = request.args.getlist("ids")
    conversations = retrieve_all_conversations(conversation_ids)
    return jsonify(conversations)

@chat_bp.route("/api/delete/<resource_id>", methods=["DELETE"])
def delete_conversation(resource_id):
    conversation_deletion(resource_id)

    return '', 204

@chat_bp.route("/", methods=["POST"])
def contact_llm():
    data = request.get_json()
    query = data["content"]
    conversation_id = data["conversation_id"]
    dialogue_mode = data["dialogue_mode"]

    found_history = retrieve_or_create_history(conversation_id, query)

    if isinstance(found_history, str):
        history = ""
        conversation_id = found_history
    else:
        history = found_history
        if history_is_too_long(history):
            compacted = compact_history(history)
            replace_history(compacted, conversation_id)
            history = [{"role": "system", "content": f"Previous conversation summary: {compacted}"}]
        update_history("user", query, conversation_id)

    query_embedding = get_embedding(query)
    cacheable = False
    cache_hit = cache_lookup(query_embedding, dialogue_mode)

    if cache_hit:
        print("\n\033[92m[CACHE HIT]\033[0m Returning cached response.\n")
        update_history("assistant", cache_hit, conversation_id)
        summary = None
        if history == "":
            conversation = f"user: {query} \n assistant: {cache_hit}"
            summary = generate_summary(conversation)
            update_with_summary(summary, conversation_id)
        return jsonify({"role": "assistant", "content": cache_hit,
                    "conversation_id": conversation_id, "summary": summary})
    else:
        cacheable = classify_query(query)
        if cacheable:
            print("\n\033[93m[CACHE MISS — CACHEABLE]\033[0m Response will be cached.\n")
        else:
            print("\n\033[94m[CACHE MISS — NOT CACHEABLE]\033[0m Response will not be cached.\n")

    
    context = retrieve_most_similar(query_embedding)

    if (dialogue_mode == False):
        with open(BASIC_PROMPT_PATH, "r") as f:
            instructions = f.read().format(context=context, history=history)
    elif (dialogue_mode == True):
        with open(DIALOGUE_PROMPT_PATH, "r") as f:
            instructions = f.read().format(context=context, history=history)
    else:
        print("DIALOG_MODE IS NOT A BOOLEAN")

    prompt = build_prompt(instructions, query)

    response = client.responses.create(
        model=BASIC_MODEL if dialogue_mode == False else DIALOGUE_MODEL,
        input=prompt,
        max_output_tokens=1024,
    )

    output = response.output_text

    if cacheable:
        cache_write(query_embedding, query, output, dialogue_mode)

    update_history("assistant", output, conversation_id)

    summary = None
    if history == "":
        conversation = f"user: {query} \n assistant: {output}"
        summary = generate_summary(conversation)
        update_with_summary(summary, conversation_id)

    return jsonify({
        "role": "assistant",
        "content": output,
        "conversation_id": conversation_id,
        "summary": summary,
    })
