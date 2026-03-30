from flask import Blueprint, request, jsonify

from src.config import BASIC_MODEL, DIALOGUE_MODEL, BASIC_PROMPT_PATH, DIALOGUE_PROMPT_PATH
from src.extensions import client
from src.services.build_prompt import build_prompt
from src.services.context_retrieval import retrieve_most_similar
from src.services.conversations_retrieval import retrieve_all_conversations
from src.services.generate_summary import generate_summary
from src.services.history_retrieval import retrieve_history
from src.services.update_history import update_history
from src.services.update_with_summary import update_with_summary

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/", methods=["GET"])
def display_homepage():
    return "This is the backend! Go to the frontend port to see the stuff."


@chat_bp.route("/api/conversations", methods=["GET"])
def get_conversations():
    conversation_ids = request.args.getlist("ids")
    conversations = retrieve_all_conversations(conversation_ids)
    return jsonify(conversations)


@chat_bp.route("/", methods=["POST"])
def contact_llm():
    data = request.get_json()
    query = data["content"]
    conversation_id = data["conversation_id"]
    dialogue_mode = data["dialogue_mode"]

    context = retrieve_most_similar(query)

    result = retrieve_history(conversation_id, query)

    if isinstance(result, str):  # first-time query — result is the new UUID
        history = ""
        conversation_id = result
    else:
        history = result
        update_history("user", query, conversation_id)

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
