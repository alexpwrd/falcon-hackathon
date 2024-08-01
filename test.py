import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
AI71_API_KEY = os.getenv("AI71_API_KEY")

if not AI71_API_KEY:
    raise ValueError("AI71_API_KEY not found in .env file")

# API endpoint
API_URL = "https://api.ai71.ai/v1/chat/completions"

# Headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AI71_API_KEY}"
}

# Test a simple chat completion
def simple_completion():
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! What can you tell me about the Falcon language model?"},
        ],
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        print(content)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Test streaming
def streaming_completion():
    payload = {
        "model": "tiiuae/falcon-180B-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about AI."},
        ],
        "stream": True,
    }

    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        print(content, end='', flush=True)

if __name__ == "__main__":
    print("Simple chat completion:")
    simple_completion()

    print("\nStreaming response:")
    streaming_completion()

    print("\nDone!")