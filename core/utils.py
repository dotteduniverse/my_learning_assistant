import os
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in environment variables")
else:
    logger.info("GROQ_API_KEY loaded")

def load_json(filepath):
    logger.debug(f"Reading JSON from {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(filepath, data):
    logger.debug(f"Writing JSON to {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)