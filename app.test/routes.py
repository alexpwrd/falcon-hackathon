from flask import render_template, Blueprint
from commands import (
    speak_text,
    take_photo,
    process_image,
    #
    logger,
)


v1 = Blueprint("main", __name__)


@v1.route("/")
def index():
    logger.info("Serving index page")
    return render_template("index.html")


@v1.route("/walk-assistant", methods=["GET"])
def walk_assistant():
    welcome_message = "VisionAId walk assistant is ready to help you."
    speak_text(welcome_message)

    while True:
        try:
            user_input = "not exit"
            if user_input == "exit":
                break

            _path = take_photo()
            _json = process_image(image_path=_path)
            speak_text(_json["instructions"])

        except EOFError:  # Ctrl+D graceful exit
            break
