from commands import (
    logger,
)
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB

    from routes import v1

    app.register_blueprint(v1)


if __name__ == "__main__":
    logger.info("Starting Flask application")
    app = create_app()
    app.run(debug=True)
    # app.run(host="localhost", port=8000, debug=True)
