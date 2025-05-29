# openai_client.py

from openai import OpenAI
from config import OPENAI_API_KEY

# Create client instance
client = OpenAI(api_key=OPENAI_API_KEY)

def get_chat_completion(messages, model, temperature, max_tokens):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip(), response.usage
    except Exception as e:
        # Handle specific OpenAI exceptions
        error_type = type(e).__name__
        if "AuthenticationError" in error_type:
            raise RuntimeError("Invalid API key")
        elif "RateLimitError" in error_type:
            raise RuntimeError("Rate limit exceeded")
        elif "APIError" in error_type:
            raise RuntimeError(f"OpenAI API Error: {e}")
        else:
            raise RuntimeError(f"Unexpected error: {e}")