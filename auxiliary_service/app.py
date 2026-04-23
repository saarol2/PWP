from flask import Flask
from routes import auxiliary_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auxiliary_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5001, debug=True)
