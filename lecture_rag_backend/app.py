from dotenv import load_dotenv
load_dotenv()  # must run before src.extensions is imported, so the API key is in the environment

from flask import Flask
from flask_cors import CORS

from src.routes.chat import chat_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(chat_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=3000)
