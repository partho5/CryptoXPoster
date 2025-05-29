# x_post.py

from ai.response_generator import generate_response
from config import is_premium_user
import datetime
import json as json_lib


def max_post_length() -> int:
    """
    Returns the maximum allowed post length based on user's subscription status.

    Returns:
        int: Maximum number of characters allowed in a post.
    """
    return 25000 if is_premium_user else 280


def create_x_post_from(data: dict) -> str:
    """
    Formats financial market data into a structured JSON post for X (Twitter).
    Uses OpenAI API via the generate_response(prompt) function.
    """

    # Ensure current UTC timestamp in ISO 8601 format
    timestamp = datetime.datetime.utcnow().isoformat()

    # Format prompt
    prompt = f"""
You are a financial news assistant. Given the following market data:

{json_lib.dumps(data, indent=2)}

Generate a JSON object representing a single financial news post suitable for X (formerly Twitter). Use a professional yet engaging tone appropriate for financial newsfeeds.

Structure the JSON output as:
{{
  "title": "[Brief headline including symbol or name, and price movement]",
  "summary": "[Natural language summary of current trading price and change]",
  "link": "[Use the provided URL]",
  "image_url": null,
  "timestamp": "{timestamp}"
}}

Only return the JSON. No explanations. This content will be posted to X using premium features.
""".strip()

    # Call OpenAI API wrapper
    response = generate_response(prompt)

    # Return JSON string
    return response
