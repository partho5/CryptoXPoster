# response_generator.py
from config import OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
from .openai_client import get_chat_completion
from .utils import clean_response

def generate_response(prompt, system_message="You are a helpful assistant."):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]
    try:
        raw_response, usage = get_chat_completion(
            messages=messages,
            model=OPENAI_MODEL,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        return clean_response(raw_response)
    except RuntimeError as e:
        # Optionally log the error here
        return f"[Error] {str(e)}"