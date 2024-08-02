import os
import requests
import json
import base64
import logging
from dotenv import load_dotenv
from openai import OpenAI
import os
from datetime import datetime
import subprocess
import time
import warnings
from flask import Flask, render_template, request, jsonify, Blueprint

# ---- #

from openai import OpenAI
import logging
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FALCON_API_KEY = os.getenv("FALCON_API_KEY")
AI71_API_KEY = os.getenv("AI71_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

FALCON_API_URL = "https://api.ai71.ai/v1/chat/completions"
FALCON_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AI71_API_KEY}",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
