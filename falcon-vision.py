import os
import requests
import json
import base64
import logging
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FALCON_API_KEY = os.getenv("FALCON_API_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Falcon API setup
AI71_API_KEY = os.getenv("AI71_API_KEY")
if not AI71_API_KEY:
    raise ValueError("AI71_API_KEY not found in .env file")

FALCON_API_URL = "https://api.ai71.ai/v1/chat/completions"
FALCON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AI71_API_KEY}"
}

app = Flask(__name__)

def encode_image(image_path):
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_image_description(image_path):
    logger.info("Generating image description")
    base64_image = encode_image(image_path)
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that describes images in detail for blind people. Focus on important elements, spatial relationships, and potential hazards or obstacles."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in detail for a blind person. What are the main elements and their layout?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )
    description = response.choices[0].message.content
    logger.info(f"Generated description: {description[:100]}...")  # Log first 100 characters
    return description

def generate_instructions(image_description):
    logger.info("Generating instructions based on image description")
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are an AI assistant helping a blind person navigate based on an image description. Provide clear, concise instructions for safe movement."},
            {"role": "user", "content": f"Based on this image description, what should a blind person do next? Image description: {image_description}"}
        ]
    }
    
    try:
        response = requests.post(FALCON_API_URL, headers=FALCON_HEADERS, json=payload)
        response.raise_for_status()
        instructions = response.json()['choices'][0]['message']['content']
        logger.info(f"Generated instructions: {instructions[:100]}...")  # Log first 100 characters
        return instructions
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.content}")
        return "I'm sorry, I couldn't generate instructions at this time."

@app.route('/')
def index():
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    logger.info("Processing image request received")
    image_path = "testimage/test.png"
    image_description = generate_image_description(image_path)
    instructions = generate_instructions(image_description)
    logger.info("Image processing completed")
    return jsonify({"description": image_description, "instructions": instructions})

if __name__ == "__main__":
    logger.info("Starting Flask application")
    app.run(debug=True)