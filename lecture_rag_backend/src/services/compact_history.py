from src.config import COMPACT_MODEL
from src.extensions import client


def compact_history(history: list) -> str:
    history_text = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in history
    )
    prompt = f"""The following is a conversation history between a student and an AI teaching assistant for a philosophy course.
Summarize it concisely, preserving the key questions asked, answers given, and any conclusions reached.
The summary will replace the full history in future turns, so it must contain enough detail for the conversation to continue coherently.

Conversation:
{history_text}

Summary:"""
    response = client.responses.create(
        model=COMPACT_MODEL,
        input=prompt,
    )
    return response.output_text
