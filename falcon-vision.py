import os
import requests
import json
import base64
import logging
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import imghdr
from flask import Flask, render_template, jsonify, request, send_from_directory
import threading
from flask_socketio import SocketIO
import time

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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app)

continuous_process_running = False

def take_photo(camera_id=0, filename='visionAId.jpg', filepath='~/storage/dcim/', resolution='800x600'):
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

def check_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    logger.info(f"Image size: {size_mb:.2f} MB")
    return size_mb

def check_image_format(file_path):
    try:
        image_type = imghdr.what(file_path)
        logger.info(f"Image format: {image_type}")
        return image_type
    except Exception as e:
        logger.error(f"Error checking image format: {e}")
        return None

def resize_and_encode_image(image_path, target_size="512x512"):
    resized_filename = f"resized_{os.path.basename(image_path)}"
    resized_path = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
    try:
        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Resize image using ImageMagick's magick convert command
        subprocess.run(['magick', 'convert', image_path, '-resize', target_size+'^', '-gravity', 'center', '-extent', target_size, resized_path], check=True)
        logger.info(f"Image resized and saved to {resized_path}")
        
        # Read and encode the resized image
        with open(resized_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        logger.info(f"Image encoded successfully. Encoded length: {len(encoded_image)}")
        return encoded_image, resized_filename
    except subprocess.CalledProcessError as e:
        logger.error(f"Error resizing image: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None, None

def generate_image_description(image_path):
    logger.info("OpenAI: Generating image description")
    
    base64_image, resized_filename = resize_and_encode_image(image_path)
    if not base64_image:
        logger.error("Failed to resize and encode image")
        return "I'm sorry, I couldn't process the image at this time.", None
    
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
    
    logger.info(f"Sending request to OpenAI API. Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        response = requests.post(OPENAI_API_URL, headers=OPENAI_HEADERS, json=payload)
        response.raise_for_status()
        description = response.json()['choices'][0]['message']['content']
        logger.info(f"OpenAI: Generated description: {description[:100]}...")
        return description, resized_filename
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI: Error in API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"OpenAI: Response status code: {e.response.status_code}")
            logger.error(f"OpenAI: Response content: {e.response.content}")
        return "I'm sorry, I couldn't generate a description at this time.", None

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

def speak_text(text):
    try:
        subprocess.run(['termux-tts-speak', text], check=True)
        logger.info(f"Text spoken successfully: {text[:50]}...")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error speaking text: {e}")
        return False

def process_image():
    image_path = take_photo()  # Use front camera (camera_id=1)
    if image_path and os.path.exists(image_path):
        file_size_mb = check_file_size(image_path)
        image_format = check_image_format(image_path)
        
        logger.info(f"Original image size: {file_size_mb:.2f} MB")
        logger.info(f"Original image format: {image_format}")
        
        image_description, resized_filename = generate_image_description(image_path)
        if resized_filename is None:
            return {"error": "Failed to resize and encode image"}
        
        resized_path = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
        
        # Check size of resized image
        resized_size_mb = check_file_size(resized_path)
        logger.info(f"Resized image size: {resized_size_mb:.2f} MB")
        
        instructions = generate_instructions(image_description)
        logger.info(f"Full image description: {image_description}")
        logger.info(f"Full instructions: {instructions}")
        
        # Speak the Falcon instructions and get the result
        instructions_spoken = speak_text(instructions)
        
        return {
            "description": image_description, 
            "instructions": instructions,
            "resized_image_url": f"/uploads/{resized_filename}?t={datetime.now().timestamp()}",
            "instructions_spoken": instructions_spoken
        }
    else:
        logger.error("Failed to take photo or photo file not found")
        return {"error": "Failed to take photo or photo file not found"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image_route():
    result = process_image()
    return jsonify(result)

@app.route('/continuous_process', methods=['POST'])
def continuous_process():
    global continuous_process_running
    continuous_process_running = True

    def run_continuous_process():
        while continuous_process_running:
            result = process_image()
            if result.get("error"):
                socketio.emit('continuous_result', result)
                break
            socketio.emit('continuous_result', result)
            time.sleep(5)  # Sleep for 5 seconds before capturing the next image

    threading.Thread(target=run_continuous_process).start()
    return jsonify({"status": "Continuous process started"})

@app.route('/stop_continuous_process', methods=['POST'])
def stop_continuous_process():
    global continuous_process_running
    continuous_process_running = False
    return jsonify({"status": "Continuous process stopped"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)