from src.services.context_retrieval import retrieve_most_similar
from src.services.history_retrieval import retrieve_history
from src.services.build_prompt import build_prompt
from openai import OpenAI
from dotenv import load_dotenv
import os

MODEL = "gpt-5.4-nano"

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

fake_request = {'role': 'user', 'content': 'What about the Theory of Natural Law?', 'conversation_id': '9f8cd020-14c0-4bda-b62f-84c17d168bd3'}

def contact_llm():
    # extract query from body -> 
    # data = request.get_json() # {role: 'user', content: string, conversation_id: string}
    data = fake_request

    # get context for query
    context = retrieve_most_similar(data['content'])
     
    # # get conversation history
    history = retrieve_history(data['conversation_id'])

    # # get system instructions

    with open("./src/data/system_prompt.md", "r") as f:
        instructions = f.read().format(context=context, history=history)

    # call build_prompt(instructions, query)
    prompt = build_prompt(instructions, data['content'])

    

    # contact AI
    response = client.responses.create(
                model=MODEL,
                input=prompt
            )
    print(response.output_text)
    # # return response as {role: 'assistant', content: response_text}
    # return response.output_text
    
contact_llm()

## THIS ALL SEEMS TO WORK!