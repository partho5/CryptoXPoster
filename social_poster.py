"""
Module for posting content to social media platforms.
"""
import os
import logging
from typing import Dict, Any, Optional

import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialPostError(Exception):
    """Base exception for social posting errors"""
    pass


class TwitterApiError(SocialPostError):
    """Exception raised for Twitter API errors"""
    pass


class InvalidContentError(SocialPostError):
    """Exception raised for invalid content errors"""
    pass


def format_news_for_twitter(article: Dict[str, Any]) -> str:
    """
    Format an article for posting on Twitter/X

    Args:
        article: Article data dictionary

    Returns:
        Formatted string for posting

    Raises:
        InvalidContentError: If article doesn't contain required fields
    """
    try:
        if not article.get('title'):
            raise InvalidContentError("Article must contain a title")

        # Create a short tweet with title and link
        title = article['title']
        link = article.get('link', '')

        # Ensure we don't exceed Twitter's character limit (280)
        max_title_length = 200 if link else 270
        if len(title) > max_title_length:
            title = title[:max_title_length - 3] + "..."

        tweet = f"{title}"
        if link:
            tweet += f"\n\n{link}"

        # Add hashtags based on content
        crypto_terms = ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'token', 'nft']
        matched = False

        for term in crypto_terms:
            if term.lower() in title.lower() and len(tweet) < 260:
                tweet += f" #{term.capitalize()}"
                matched = True

        if not matched and len(tweet) < 260:
            tweet += " #CryptoNews #cryptocurrencies"  # default hashtags

        return tweet
    except KeyError as e:
        logger.error(f"Missing required key in article: {str(e)}")
        raise InvalidContentError(f"Missing required key in article: {str(e)}") from e
    except Exception as e:
        logger.error(f"Failed to format article for Twitter: {str(e)}")
        raise InvalidContentError(f"Failed to format article: {str(e)}") from e


def post_to_x(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post an article to Twitter/X

    Args:
        article: Article data dictionary

    Returns:
        Dictionary containing post result status

    Raises:
        TwitterApiError: If posting to Twitter fails
    """
    try:
        consumer_key = os.environ.get("TW_CONSUMER_KEY")
        consumer_secret = os.environ.get("TW_CONSUMER_SECRET")
        access_token = os.environ.get("TW_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TW_ACCESS_TOKEN_SECRET")
        bearer_token = os.environ.get("TW_BEARER_TOKEN")

        # Check if required credentials are available
        if not all([consumer_key, consumer_secret, access_token, access_token_secret, bearer_token]):
            logger.warning("Twitter API credentials not found in environment variables")
            return {
                "status": "skipped",
                "message": "Twitter API credentials not configured",
                "article": article
            }

        # Format the article for Twitter
        tweet_text = format_news_for_twitter(article)

        # Initialize Twitter client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Post to Twitter
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data['id']

        logger.info(f"Successfully posted to Twitter. Tweet ID: {tweet_id}")

        return {
            "status": "success",
            "message": f"Posted to Twitter with ID: {tweet_id}",
            "tweet_id": tweet_id,
            "article": article
        }
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API error: {str(e)}")
        raise TwitterApiError(f"Twitter API error: {str(e)}") from e
    except InvalidContentError:
        # Re-raise if it's already an InvalidContentError
        raise
    except Exception as e:
        logger.error(f"Unexpected error posting to Twitter: {str(e)}")
        raise SocialPostError(f"Failed to post to Twitter: {str(e)}") from e


def test_twitter_connection() -> Dict[str, Any]:
    """
    Test the Twitter API connection

    Returns:
        Dictionary containing connection test results
    """
    try:
        consumer_key = os.environ.get("TW_CONSUMER_KEY")
        consumer_secret = os.environ.get("TW_CONSUMER_SECRET")
        access_token = os.environ.get("TW_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TW_ACCESS_TOKEN_SECRET")
        bearer_token = os.environ.get("TW_BEARER_TOKEN")

        # Check if required credentials are available
        if not all([consumer_key, consumer_secret, access_token, access_token_secret, bearer_token]):
            return {
                "status": "error",
                "message": "Twitter API credentials not found in environment variables"
            }

        # Initialize Twitter client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Get user information to verify credentials
        me = client.get_me()

        return {
            "status": "success",
            "message": f"Successfully connected to Twitter API as @{me.data.username}"
        }
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API connection test failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Twitter API connection test failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in Twitter connection test: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    # Run connection test
    result = test_twitter_connection()
    print(f"Twitter connection test: {result['status']} - {result['message']}")
