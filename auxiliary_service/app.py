"""Application entrypoint for the auxiliary maintenance service."""

import os
from flask import Flask
from dotenv import load_dotenv
from routes import auxiliary_bp

load_dotenv()

def create_app():
    """Create and configure the Flask application instance."""
    application = Flask(__name__)
    application.register_blueprint(auxiliary_bp)
    return application


if __name__ == "__main__":
    app_instance = create_app()
    debug_mode = os.getenv("AUX_DEBUG", "0") == "1"
    app_instance.run(port=5001, debug=debug_mode)
