from src.config import CLASSIFY_MODEL, CLASSIFY_MODEL_PROMPT
from src.extensions import client
from src.services.build_prompt import build_prompt


def classify_query(query):
    with open(CLASSIFY_MODEL_PROMPT, "r") as f:
        instructions = f.read()

    prompt = build_prompt(instructions, query)

    response = client.responses.create(
        model=CLASSIFY_MODEL,
        input=prompt,
        max_output_tokens=16,
    )

    decision = response.output_text.strip().upper()
    return decision == "YES"
