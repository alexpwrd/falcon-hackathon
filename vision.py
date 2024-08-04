import os
import requests
import json
import base64
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

def take_photo(camera_id=1, filename='visionAId.jpg', filepath='~/storage/dcim/'):
    _path = os.path.join(filepath, filename)
    _path = os.path.expanduser(_path)  # Expand the ~ in the filepath
    logger.info(f"Taking photo with camera ID {camera_id}")
    logger.info(f"Saving photo to {_path}")
    cmd = f"termux-camera-photo -c {camera_id} {_path}"
    try:
        subprocess.call(cmd, shell=True)
        logger.info(f"Photo saved to {_path}")
        return _path
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
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image concisely for a blind person. Focus on the main elements and their layout."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=OPENAI_HEADERS, json=payload)
        response.raise_for_status()
        description = response.json()['choices'][0]['message']['content']
        logger.info(f"OpenAI: Generated description: {description[:100]}...")
        return description
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI: Error in API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"OpenAI: Response content: {e.response.content}")
        return "I'm sorry, I couldn't generate a description at this time."

def generate_instructions(image_description):
    logger.info("Falcon: Generating instructions based on image description")
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are an AI assistant helping a blind person navigate. Provide very brief, clear instructions for safe movement based on the image description."},
            {"role": "user", "content": f"Based on this image description, what should a blind person do next? Keep it brief. Image description: {image_description}"}
        ],
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
    image_path = take_photo()  # Use front camera (camera_id=1)
    if image_path and os.path.exists(image_path):
        image_description = generate_image_description(image_path)
        instructions = generate_instructions(image_description)
        logger.info(f"Full image description: {image_description}")
        logger.info(f"Full instructions: {instructions}")
        return {"description": image_description, "instructions": instructions}
    else:
        logger.error("Failed to take photo or photo file not found")
        return {"error": "Failed to take photo or photo file not found"}

if __name__ == "__main__":
    logger.info("Starting image processing")
    result = process_image()
    if "error" in result:
        logger.error(result["error"])
    else:
        logger.info("Image processing completed successfully")
        logger.info(f"Description: {result['description']}")
        logger.info(f"Instructions: {result['instructions']}")