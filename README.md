# Falcon Vision Aid

This project is a vision aid application that uses AI to describe images and provide navigation instructions for visually impaired users. It's designed to run on Android devices using Termux, but can also be set up in a local environment.

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
   pkg install python git imagemagick termux-api
   ```

4. Install pip and upgrade it:
   ```
   pkg install python-pip
   pip install --upgrade pip
   ```

5. Clone this repository:
   ```
   git clone https://github.com/alexpwrd/falcon-hackathon.git
   cd falcon-hackathon
   ```

6. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

7. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "AI71_API_KEY=your_ai71_api_key_here" >> .env
   ```

8. Grant camera permissions to Termux:
   ```
   termux-setup-storage
   ```
   Then allow storage access when prompted.

9. Install Termux:API app from F-Droid:
   - Visit https://f-droid.org/en/packages/com.termux.api/ on your Android device
   - Download and install the Termux:API app

10. Grant necessary permissions to Termux:API:
    - Go to your Android Settings > Apps > Termux:API
    - Grant camera and microphone permissions

## Setup in Local Environment

1. Ensure you have Python 3.7+ installed on your system.

2. Clone this repository:
   ```
   git clone https://github.com/alexpwrd/falcon-hackathon.git
   cd falcon-hackathon
   ```

3. Create a virtual environment:
   ```
   python -m venv falcon_env
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     falcon_env\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source falcon_env/bin/activate
     ```

5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

6. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "AI71_API_KEY=your_ai71_api_key_here" >> .env
   ```

## Usage

1. Run the Flask application:
   ```
   python falcon-vision.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5001
   ```

3. Click the "Capture New Image" button to process an image and receive a description and navigation instructions.

## Files

- `falcon-vision.py`: Main application file
- `templates/index.html`: Web interface
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (API keys)

## Note

This application requires an active internet connection to communicate with the OpenAI and AI71 APIs. When running in a local environment, you may need to modify the image capture functionality to use your system's camera instead of the Termux-specific commands.

For more information about the project, visit the [original repository](https://github.com/alexpwrd/falcon-hackathon).