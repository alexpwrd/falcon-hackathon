import os
import requests
import json
import base64
import logging
import subprocess
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI71_API_KEY = os.getenv("AI71_API_KEY")

if not AI71_API_KEY:
    raise ValueError("AI71_API_KEY not found in .env file")

# Falcon API setup
FALCON_API_URL = "https://api.ai71.ai/v1/chat/completions"
FALCON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AI71_API_KEY}"
}

def encode_image(image_path):
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_image_description(image_path):
    logger.info("Generating image description")
    base64_image = encode_image(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
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
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    description = response.json()['choices'][0]['message']['content']
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

def take_photo():
    image_path = "/sdcard/Pictures/falcon_vision_photo.jpg"
    subprocess.run(["termux-camera-photo", image_path])
    return image_path

def speak_text(text):
    subprocess.run(["termux-tts-speak", text])

def process_image(image_path):
    logger.info("Processing image")
    image_description = generate_image_description(image_path)
    instructions = generate_instructions(image_description)
    logger.info("Image processing completed")
    return {"description": image_description, "instructions": instructions}

def main():
    print("Welcome to Falcon Vision!")
    while True:
        user_input = input("Press Enter to take a photo and process it, or type 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break
        
        image_path = take_photo()
        result = process_image(image_path)
        
        print("\nImage Description:")
        print(result["description"])
        speak_text(result["description"])
        
        print("\nInstructions:")
        print(result["instructions"])
        speak_text(result["instructions"])
        
        print("\n")

if __name__ == "__main__":
    main()