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

    import datetime
    import json as json_lib  # Assuming json is already imported as json_lib

    # Ensure current UTC timestamp in ISO 8601 format
    timestamp = datetime.datetime.utcnow().isoformat()

    # Format prompt
    prompt = f"""
You are a financial news assistant. Given the following market data:

{json_lib.dumps(data, indent=2)}

Generate a JSON object representing a single financial news post suitable for X (formerly Twitter). Use a professional yet engaging tone appropriate for financial newsfeeds.

- Make the summary more insightful and detailed, not just reporting numbers. Add context or market interpretation when possible.
- Use clear line breaks between paragraphs (use \\n\\n).
- If the provided URL is for live tracking (e.g., real-time quotes), explicitly mention that in the summary.
- Add a line break before and after the link to make the post visually clean.

Structure the JSON output exactly as:
{{
  "title": "[Brief headline including symbol or name, and price movement]",
  "summary": "[Natural language multi-paragraph summary with insights, line breaks, and spacing before/after link]",
  "link": "[empty string]",
  "image_url": null,
  "timestamp": "{timestamp}"
}}

Only return the JSON. Do not explain or comment.
This content will be posted to X using premium formatting features.
""".strip()

    # Call OpenAI API wrapper
    response = generate_response(prompt)

    # Return JSON string
    return response
