# Falcon Vision Aid

This project is a vision aid application that uses AI to describe images and provide navigation instructions for visually impaired users. It's designed to run on Android devices using Termux.

## Setup on Android with Termux

1. Install Termux from F-Droid:
   - Visit https://f-droid.org/en/packages/com.termux/ on your Android device
   - Download and install the Termux app

2. Open Termux and update the package list:
   ```
   pkg update
   ```

3. Install required packages:
   ```
   pkg install python git opencv-python imagemagick
   ```

4. Clone this repository:
   ```
   git clone https://github.com/alexpwrd/falcon-hackathon.git
   cd falcon-hackathon
   ```

5. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "AI71_API_KEY=your_ai71_api_key_here" >> .env
   ```

7. Grant camera permissions to Termux:
   ```
   termux-setup-storage
   ```
   Then allow storage access when prompted.

## Usage

1. Run the Flask application:
   ```
   python falcon-vision.py
   ```

2. Open a web browser on your device and navigate to:
   ```
   http://localhost:5001
   ```

3. Click the "Simulate Capture Image" button to process an image and receive a description and navigation instructions.

## Files

- `falcon-vision.py`: Main application file
- `templates/index.html`: Web interface
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (API keys)

## Note

This application requires an active internet connection to communicate with the OpenAI and AI71 APIs.

For more information about the project, visit the [original repository](https://github.com/alexpwrd/falcon-hackathon).