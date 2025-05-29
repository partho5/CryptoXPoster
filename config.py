# config.py

import os

from dotenv import load_dotenv

load_dotenv()

is_premium_user = False  # or False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000
