from flask import request, jsonify, Flask, send_from_directory
from flask_cors import CORS
from src.services.context_retrieval import retrieve_most_similar
from src.services.history_retrieval import retrieve_history
from src.services.build_prompt import build_prompt
from src.services.update_history import update_history
from src.services.conversations_retrieval import retrieve_all_conversations
from src.services.generate_summary import generate_summary
from src.services.update_with_summary import update_with_summary
from openai import OpenAI
from dotenv import load_dotenv
import os

MODEL = "gpt-5.4-nano"

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def display_homepage():
    return "This is the backend! Go to the frontend port to see the stuff."


@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    conversation_ids = request.args.getlist("ids")
    conversations = retrieve_all_conversations(conversation_ids)

    return jsonify(conversations) # { 'aln3450nff55gh': { history: [{role:..., content:...}, {role:..., content:...}], summary: "asdf" },
                                  #   'asdfn5243560ng': { history; [{role:..., content:...}, {role:..., content:...}], summary: "asdf" }
                                  # }


@app.route("/", methods=["POST"])
def contact_llm():
    # extract query from body -> 
    data = request.get_json() # {role: 'user', content: string, conversation_id: string}
    query = data['content']
    conversation_id = data['conversation_id']

    # get context for query
    context = retrieve_most_similar(query)
     
    # get conversation history
    result = retrieve_history(conversation_id, query) # list OR uuid
    
    if isinstance(result, str): # if this is a first-time query
        history = ''
        conversation_id = result
    else:
        history = result
        update_history('user', query, conversation_id)

    # get system instructions
    with open("./src/data/system_prompt.md", "r") as f:
        instructions = f.read().format(context=context, history=history)

    # call build_prompt(instructions, query)
    prompt = build_prompt(instructions, query)

    # contact AI
    response = client.responses.create(
                model=MODEL,
                input=prompt,
                max_tokens=1024
            )

    output = response.output_text
    update_history('assistant', output, conversation_id)

    if history == '':
        conversation = f"user: {query} \n assistant: {output}"
        summary = generate_summary(conversation, client, MODEL)
        update_with_summary(summary, conversation_id)

    return_body = { "role": "assistant",
                    "content": output,
                    "conversation_id": conversation_id,
                    "summary": summary if history == '' else None }
    
    print(return_body)
    return jsonify(return_body)

if __name__ == "__main__":
    app.run(debug=True, port=3000)  # runs on localhost:5000 by default