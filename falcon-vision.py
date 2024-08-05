from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
import base64
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI71_API_KEY = os.getenv("AI71_API_KEY")

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
FALCON_API_URL = "https://api.ai71.ai/v1/chat/completions"

OPENAI_HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
FALCON_HEADERS = {"Authorization": f"Bearer {AI71_API_KEY}", "Content-Type": "application/json"}

def take_photo():
    filename = f'visionAId_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    filepath = '/data/data/com.termux/files/home/storage/dcim/'
    full_path = os.path.join(filepath, filename)
    cmd = f"termux-camera-photo -c 0 {full_path}"
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"Photo saved to {full_path}")
        return full_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error taking photo: {e}")
        return None

def resize_and_encode_image(image_path):
    resized_filename = f"resized_{os.path.basename(image_path)}"
    resized_path = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    try:
        subprocess.run(['magick', image_path, '-resize', '512x512^', '-gravity', 'center', '-extent', '512x512', resized_path], check=True)
        with open(resized_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8'), resized_filename
    except Exception as e:
        logger.error(f"Error resizing/encoding image: {e}")
        return None, None

def generate_image_description(base64_image):
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image concisely for a blind person. Focus on the main elements and their layout."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 300
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=OPENAI_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't generate a description at this time."

def generate_instructions(image_description):
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
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        logger.error(f"Falcon API error: {e}")
        return "Sorry, I couldn't generate instructions at this time."

def speak_text(text):
    try:
        subprocess.run(['termux-tts-speak', text], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error speaking text: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    image_path = take_photo()
    if not image_path:
        return jsonify({"error": "Failed to take photo"})
    
    base64_image, resized_filename = resize_and_encode_image(image_path)
    if not base64_image:
        return jsonify({"error": "Failed to process image"})
    
    description = generate_image_description(base64_image)
    instructions = generate_instructions(description)
    speak_text(instructions)
    
    return jsonify({
        "description": description,
        "instructions": instructions,
        "resized_image_url": f"/uploads/{resized_filename}?t={datetime.now().timestamp()}"
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)