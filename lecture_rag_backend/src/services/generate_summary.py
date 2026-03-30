from src.config import BASIC_MODEL
from src.extensions import client


def generate_summary(history):
    prompt = f"""
    Generate a short summary (12 words or fewer) of this exchange, suitable
    for use as the title of this conversation -- such that the topic can be
    quickly taken in at a glance:
    {history}
  """
    response = client.responses.create(
        model=BASIC_MODEL,
        input=prompt,
    )
    return response.output_text
