# utils.py

import re

def clean_response(text):
    # Remove code blocks, markdown, and excess whitespace
    text = re.sub(r"```(?:\w+)?\n(.*?)```", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    return text.strip()