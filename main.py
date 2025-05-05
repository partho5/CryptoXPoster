"""
Main entry point for the news scraper and poster application.
"""
import os
import argparse
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from scraper import scrape_and_save
from data_manager import process_next_item, read_json_file
from social_poster import post_to_x
from api_server import start_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
DATA_FILE = os.getenv('DATA_FILE', 'news_data.json')


def run_scraper() -> Dict[str, Any]:
    """
    Run the scraper and save results

    Returns:
        Dictionary with status and count
    """
    try:
        logger.info("Starting scraping operation")
        articles = scrape_and_save(DATA_FILE)

        return {
            "status": "success",
            "message": "Scraping completed successfully",
            "count": len(articles)
        }
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Scraping failed: {str(e)}"
        }


def process_article() -> Dict[str, Any]:
    """
    Process the next article

    Returns:
        Dictionary with status and article info
    """
    try:
        logger.info("Processing next article")
        result = process_next_item(DATA_FILE, post_to_x)

        if result is None:
            return {
                "status": "error",
                "message": "No articles available to process"
            }

        return {
            "status": "success",
            "message": "Article processed successfully",
            "article": result
        }
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }


def main():
    """Main function to parse arguments and run commands"""
    parser = argparse.ArgumentParser(description="News Scraper and Poster")
    parser.add_argument('command', choices=['scrape', 'process', 'serve', 'status'],
                        help='Command to execute')

    args = parser.parse_args()

    if args.command == 'scrape':
        result = run_scraper()
        print(f"{result['status'].upper()}: {result['message']}")
        if 'count' in result:
            print(f"Scraped {result['count']} articles")

    elif args.command == 'process':
        result = process_article()
        print(f"{result['status'].upper()}: {result['message']}")

    elif args.command == 'serve':
        print("Starting API server...")
        start_server()

    elif args.command == 'status':
        try:
            articles = read_json_file(DATA_FILE)
            print(f"Data file: {DATA_FILE}")
            print(f"Articles stored: {len(articles)}")
            print(f"Status: OK")
        except Exception as e:
            print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    main()