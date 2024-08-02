# no flask


from commands import (
    speak_text,
    take_photo,
    process_image,
    #
    logger,
)
import time, os

def main():
    welcome_message = "VisionAId walk assistant is ready to help you."
    speak_text(welcome_message)

    while True:
        try:
            user_input = "not exit"
            if user_input == "exit":
                break

            # get current folder
            dir_path = os.path.dirname(os.path.realpath(__file__))
            filepath = os.path.join(dir_path, 'testimage/')
            # check if folder exists
            _path = os.path.abspath(filepath)
            check = os.path.isdir(_path)
            if not check:
                os.makedirs(_path)

            _path = take_photo(filepath=filepath)
            # check if file exists
            image_path = os.path.abspath(_path)
            check = os.path.isfile(image_path)
            while not check:
                logger.info(f"Waiting for image to be taken...")
                time.sleep(0.02)
                check = os.path.isfile(image_path)
            logger.info(f"File exists: {check}")
            _json = process_image(image_path=_path)
            speak_text(_json["instructions"])

        except EOFError:  # Ctrl+D graceful exit
            break

if __name__ == "__main__":
    main()