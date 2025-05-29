"""
WSGI entry point for web server integration.
This file serves as the entry point for hosting platforms like Passenger.
"""
import os
import sys
import json
import logging
from urllib.parse import parse_qs

from file_handler import get_file_path
from scraper.CoinTelegraphScraper import scrape_cointelegraph_and_save
from scraper.YahooScraper import scrape_and_save_yahoo_trending_table

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import local modules
from data_manager import process_next_item, read_json_file
from social_poster import post_to_x
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
DATA_FILE = os.getenv('DATA_FILE', 'news_data.json')
AUTH_CODE = os.getenv('AUTH_CODE', 'default_auth_code')  # NEVER use this default in production!


def application(environ, start_response):
    """
    WSGI application entry point

    Args:
        environ: WSGI environment dictionary
        start_response: WSGI start_response function

    Returns:
        List containing response body bytes
    """
    try:
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']

        # Parse query parameters
        if 'QUERY_STRING' in environ and environ['QUERY_STRING']:
            query_params = parse_qs(environ['QUERY_STRING'])
            auth_code = query_params.get('auth_code', [''])[0]
        else:
            auth_code = ''

        # Check authentication for protected routes
        if path not in ['/', '/status'] and auth_code != AUTH_CODE:
            start_response('401 Unauthorized', [('Content-Type', 'application/json')])
            return [json.dumps({
                'status': 'error',
                'message': 'Invalid or missing authentication code'
            }).encode()]

        # Route handling
        if path == '/':
            # Root endpoint - status check
            start_response('200 OK', [('Content-Type', 'text/plain')])
            message = 'News Scraper API is running\n'
            version = f'Python {sys.version.split()[0]}\n'
            return [(message + version).encode()]

        elif path == '/status':
            # Status endpoint
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({
                'status': 'online',
                'message': 'News Scraper API is running',
                'python_version': sys.version.split()[0]
            }).encode()]

        elif path == '/scrape' and method == 'GET':
            # Trigger scraping
            file_path = get_file_path()
            news = scrape_cointelegraph_and_save(file_path)
            scrape_and_save_yahoo_trending_table(file_path)

            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({
                'status': 'success',
                'message': 'Scraping completed successfully',
                'count': len(news)
            }).encode()]

        elif path == '/articles' and method == 'GET':
            # Get all articles
            articles = read_json_file(DATA_FILE)

            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps(articles).encode()]

        elif path == '/process' and method == 'GET':
            # Process next article
            result = process_next_item(DATA_FILE, post_to_x)

            if result is None:
                start_response('404 Not Found', [('Content-Type', 'application/json')])
                return [json.dumps({
                    'status': 'error',
                    'message': 'No articles available to process'
                }).encode()]

            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({
                'status': 'success',
                'message': 'Article processed successfully',
                'article': result
            }).encode()]

        else:
            # Route not found
            start_response('404 Not Found', [('Content-Type', 'application/json')])
            return [json.dumps({
                'status': 'error',
                'message': f"Route '{path}' not found"
            }).encode()]

    except Exception as e:
        # Log the error
        logger.error(f"Error handling request: {str(e)}")

        # Return error response
        start_response('500 Internal Server Error', [('Content-Type', 'application/json')])
        return [json.dumps({
            'status': 'error',
            'message': f"Internal server error: {str(e)}"
        }).encode()]


if __name__ == "__main__":
    # For local development, run a simple server
    from wsgiref.simple_server import make_server

    print("Starting development server on port 8080...")
    httpd = make_server('', 8080, application)
    print("Server running at http://localhost:8080")
    httpd.serve_forever()