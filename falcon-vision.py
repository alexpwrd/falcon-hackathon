import os
import requests
import json
import base64
import logging
import subprocess
import tempfile
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI71_API_KEY = os.getenv("AI71_API_KEY")

if not AI71_API_KEY or not OPENAI_API_KEY:
    raise ValueError("API keys not found in .env file")

# API setups
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
FALCON_API_URL = "https://api.ai71.ai/v1/chat/completions"

OPENAI_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

FALCON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AI71_API_KEY}"
}

app = Flask(__name__)

def take_photo():
    logger.info("Taking photo with front camera")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Use termux-camera-photo to take a picture with the front camera
        subprocess.run(["termux-camera-photo", "-c", "1", temp_filename], check=True)
        logger.info(f"Photo saved to {temp_filename}")
        return temp_filename
    except subprocess.CalledProcessError as e:
        logger.error(f"Error taking photo: {e}")
        return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_image_description(image_path):
    logger.info("OpenAI: Generating image description")
    base64_image = encode_image(image_path)
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image concisely for a blind person. Focus on the main elements and their layout."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 200
    }
    
    response = requests.post(OPENAI_API_URL, headers=OPENAI_HEADERS, json=payload)
    response.raise_for_status()
    description = response.json()['choices'][0]['message']['content']
    logger.info(f"OpenAI: Generated description: {description[:100]}...")
    return description

def generate_instructions(image_description):
    logger.info("Falcon: Generating instructions based on image description")
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are an AI assistant helping a blind person navigate. Provide very brief, clear instructions for safe movement based on the image description."},
            {"role": "user", "content": f"Based on this image description, what should a blind person do next? Keep it brief. Image description: {image_description}"}
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(FALCON_API_URL, headers=FALCON_HEADERS, json=payload)
        response.raise_for_status()
        instructions = response.json()['choices'][0]['message']['content']
        logger.info(f"Falcon: Generated instructions: {instructions[:100]}...")
        return instructions
    except requests.exceptions.RequestException as e:
        logger.error(f"Falcon: Error in API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Falcon: Response content: {e.response.content}")
        return "I'm sorry, I couldn't generate instructions at this time."

def process_image():
    image_path = take_photo()
    if image_path:
        image_description = generate_image_description(image_path)
        instructions = generate_instructions(image_description)
        os.unlink(image_path)  # Delete the temporary file
        return {"description": image_description, "instructions": instructions}
    else:
        return {"error": "Failed to take photo"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image_route():
    result = process_image()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)