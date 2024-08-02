from extensions import (
    logger,
    openai_client,
    #
    FALCON_API_URL,
    FALCON_HEADERS,
    #
    base64,
    jsonify,
    requests,
    os,
    datetime,
    subprocess,
    time,
    #
)

####################################################################################################
# AI Image Processing
####################################################################################################

def encode_image(image_path):
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_image_description(image_path):
    logger.info("Generating image description")
    base64_image = encode_image(image_path)

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": '''
                You are a helpful assistant that describes images in detail for blind people.
                Focus on important elements, spatial relationships, and potential hazards or obstacles.
                ''',
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in detail for a blind person. What are the main elements and their layout?",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
    )
    description = response.choices[0].message.content
    logger.info(
        f"Generated description: {description[:100]}..."
    )  # Log first 100 characters
    return description


def generate_instructions(image_description):
    logger.info("Generating instructions based on image description")
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {
                "role": "system",
                "content": '''
                You are an AI assistant helping a blind person navigate based on an image description.
                Provide clear, concise instructions for safe movement.''',
            },
            {
                "role": "user",
                "content": f'''
                Based on this image description, what should a blind person do next?
                Image description: {image_description}''',
            },
        ],
    }

    try:
        response = requests.post(FALCON_API_URL, headers=FALCON_HEADERS, json=payload)
        response.raise_for_status()
        instructions = response.json()["choices"][0]["message"]["content"]
        logger.info(
            f"Generated instructions: {instructions[:100]}..."
        )  # Log first 100 characters
        return instructions
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in API request: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response content: {e.response.content}")
        return "I'm sorry, I couldn't generate instructions at this time."


def process_image(**kwargs):
    logger.info("Processing image request received")
    # image_path = "testimage/test.png"
    image_path = kwargs.get("image_path")
    image_description = generate_image_description(image_path)
    instructions = generate_instructions(image_description)
    logger.info("Image processing completed")
    return jsonify({"description": image_description, "instructions": instructions})


####################################################################################################
# Termux Commands
####################################################################################################


def take_photo(camera_id=0, filename='visionAId.jpg',filepath='~/storage/dcim/', **kwargs): # camera_id = 0 or 1 (0 back camera, 1 front camera)
    camera_id = kwargs.get("camera_id", 0)
    # filename = f"photo_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg"
    _path = os.path.join(filepath, filename)
    print(_path)
    cmd = f"termux-camera-photo -c {camera_id} {_path}"
    subprocess.call(cmd, shell=True)
    return _path

def get_location(): # slow and buggy
    cmd = "termux-location -p passive -r once"
    o = subprocess.check_output(cmd, shell=True)
    return o


def start_recording(location="~/storage/dcim/audio.mp3", duration=30):
    # cmd = f"termux-microphone-record -f {location} -l {duration}"
    cmd = f"termux-microphone-record -f {location}"
    subprocess.call(cmd, shell=True)

def stop_recording():
    cmd = "termux-microphone-record -q"
    subprocess.call(cmd, shell=True)


def speak_text(text):
    os.system("termux-tts-speak {}".format(text))