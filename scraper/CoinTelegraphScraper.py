"""
Web scraper module for collecting news from Cointelegraph.
"""
import logging
import os
import re
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
import unicodedata
from bs4 import BeautifulSoup

from file_handler import prepend_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsScraperError(Exception):
    """Base exception for scraper errors"""
    pass


class RequestError(NewsScraperError):
    """Exception raised for request errors"""
    pass


class ParsingError(NewsScraperError):
    """Exception raised for parsing errors"""
    pass


class CointelegraphScraper:
    """Scraper for Cointelegraph news website"""

    def __init__(self, base_url: str = 'https://cointelegraph.com/', max_articles: int = 5):
        """
        Initialize the scraper with configuration

        Args:
            base_url: The base URL of the website to scrape
            max_articles: Maximum number of articles to scrape
        """
        self.base_url = base_url
        self.max_articles = max_articles
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        }

    import unicodedata

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Remove non-ASCII characters from text

        Args:
            text: Input text to clean

        Returns:
            Cleaned text
        """
        return re.sub(r'[^\x00-\x7F]+', '', text)

    def _make_request(self) -> str:
        """
        Make HTTP request to the target website

        Returns:
            HTML content of the page

        Raises:
            RequestError: If request fails
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve content from {self.base_url}: {str(e)}")
            raise RequestError(f"Failed to retrieve content: {str(e)}") from e

    def _parse_article(self, article) -> Optional[Dict[str, Any]]:
        """
        Parse a single article element

        Args:
            article: BeautifulSoup element representing an article

        Returns:
            Dictionary containing article data or None if parsing fails
        """
        try:
            title_tag = article.find('span', {'data-testid': 'post-card-title'})
            summary_tag = article.find('p', {'data-testid': 'post-card-preview-text'})
            link_tag = article.find('a', {'data-testid': 'post-cad__link'})

            # More specific image finding
            img_tag = article.select_one('img.lazy-image__img')
            img_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else None

            # Only proceed if we found a title
            if not title_tag:
                return None

            title = title_tag.get_text(strip=True)
            title = self.clean_text(title)
            summary = summary_tag.get_text(strip=True) if summary_tag else ''
            summary = self.clean_text(summary)
            href = link_tag['href'] if link_tag and link_tag.has_attr('href') else ''
            link = f"{self.base_url.rstrip('/')}{href}" if href.startswith('/') else href

            return {
                "title": title,
                "summary": summary[:180] + "..." if len(summary) > 180 else summary,
                "link": link,
                "image_url": img_url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Failed to parse article: {str(e)}")
            return None

    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape articles from the website

        Returns:
            List of article data dictionaries

        Raises:
            ParsingError: If parsing fails
        """
        try:
            html_content = self._make_request()
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all article list items using the data-testid attribute
            articles = soup.find_all('li', {'data-testid': 'posts-listing__item'})

            if not articles:
                logger.warning("No articles found. The website structure may have changed.")

            results = []

            for article in articles[:self.max_articles]:
                article_data = self._parse_article(article)
                if article_data:
                    results.append(article_data)

            return results
        except RequestError:
            # Re-raise if it's already a RequestError
            raise
        except Exception as e:
            logger.error(f"Failed to parse content: {str(e)}")
            raise ParsingError(f"Failed to parse content: {str(e)}") from e


def save_news_to_json(news_items: List[Dict[str, Any]], file_path: str) -> None:
    """
    Prepend news items to an existing JSON file

    Args:
        news_items: List of new news data to prepend
        file_path: Path to the JSON file

    Raises:
        IOError: If file cannot be read or written
    """
    prepend_data(file_path, news_items)

    # try:
    #     # Get absolute path to the parent of the current script directory
    #     base_dir = os.path.dirname(os.path.abspath(__file__))
    #     parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
    #     full_file_path = os.path.join(parent_dir, file_path)
    #
    #     # Load existing data if file exists
    #     existing_news = []
    #     if os.path.exists(full_file_path):
    #         try:
    #             with open(full_file_path, 'r', encoding='utf-8') as f:
    #                 existing_news = json.load(f)
    #                 # Ensure it's a list
    #                 if not isinstance(existing_news, list):
    #                     existing_news = []
    #             logger.info(f"Loaded {len(existing_news)} existing news items from {full_file_path}")
    #         except (json.JSONDecodeError, IOError) as e:
    #             logger.warning(
    #                 f"Could not load existing data from {full_file_path}: {str(e)}. Starting with empty list.")
    #             existing_news = []
    #     else:
    #         logger.info(f"File {full_file_path} does not exist. Creating new file.")
    #
    #     # Prepend new news items to existing ones (new items first)
    #     combined_news = news_items + existing_news
    #
    #     # Write combined data back to file
    #     with open(full_file_path, 'w', encoding='utf-8') as f:
    #         json.dump(combined_news, f, indent=2, ensure_ascii=False)
    #
    #     logger.info(f"Successfully prepended {len(news_items)} new news items to {len(existing_news)} existing items")
    #     logger.info(f"Total news items in file: {len(combined_news)}")
    #
    # except IOError as e:
    #     logger.error(f"Failed to save news to {full_file_path}: {str(e)}")
    #     raise IOError(f"Failed to save news: {str(e)}") from e


def scrape_cointelegraph_and_save(output_file: str = 'news_data.json') -> List[Dict[str, Any]]:
    """
    Scrape articles and save them to a file

    Args:
        output_file: Path to save the JSON file

    Returns:
        List of scraped articles
    """
    scraper = CointelegraphScraper()
    try:
        news = scraper.scrape()
        #print(news)
        save_news_to_json(news, output_file)
        return news
    except NewsScraperError as e:
        logger.error(f"Scraping failed: {str(e)}")
        return []

#
# if __name__ == "__main__":
#     try:
#         results = scrape_cointelegraph_and_save()
#         print(f"Scraped {len(results)} articles")
#     except Exception as e:
#         logger.critical(f"Unhandled exception: {str(e)}")
#         raise