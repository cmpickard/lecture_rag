def generate_summary(history, client, model):
  prompt = f"""
    Generate a short summary (12 words or fewer) of this exchange, suitable
    for use as the title of this conversation -- such that the topic can be
    quickly taken in at a glance:
    {history}
  """
  response = client.responses.create(
    model=model,
    input=prompt
  )

  summary = response.output_text

  return summary