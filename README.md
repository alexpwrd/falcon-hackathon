# Falcon AI Hackathon Project

This project demonstrates how to interact with the Falcon AI model using the AI71 API.

## Setup

### 1. Miniconda Installation

If you don't have Miniconda installed, follow these steps:

a. Download Miniconda for your operating system: https://docs.conda.io/en/latest/miniconda.html

b. Install Miniconda by following the instructions for your OS: https://conda.io/projects/conda/en/latest/user-guide/install/index.html

### 2. Create and Activate Conda Environment

Once Miniconda is installed, create and activate a new environment with Python 3.11:

```bash
conda create -n falcon python=3.11
conda activate falcon
```

### 3. Project Setup

1. Clone this repository:
   ```
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your AI71 API key:
   ```
   AI71_API_KEY=your_actual_api_key_here
   ```

## Usage

Ensure your conda environment is activated:

```bash
conda activate falcon
```

Then, run the main script to test the Falcon AI model:

```bash
python test.py
```

This script demonstrates two functionalities:
1. A simple chat completion
2. A streaming chat completion

## Files
