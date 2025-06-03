# News Scraper and Social Media Poster

A modular Python application that scrapes news articles from Cointelegraph, saves them to a JSON file, and posts them to social media platforms via a secure REST API.

## Features

- **Web Scraping**: Collects the latest news articles from Cointelegraph
- **REST API**: Secure API endpoints with authentication
- **Social Media Integration**: Posts scraped articles to Twitter/X
- **Modular Design**: Follows the Single Responsibility Principle
- **Error Handling**: Comprehensive exception handling throughout

## Project Structure

```
news-scraper/
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment variables template
├── api_server.py         # FastAPI server implementation
├── data_manager.py       # JSON file operations
├── main.py               # Command line interface
├── passenger_wsgi.py     # WSGI entry point for web hosting
├── requirements.txt      # Python dependencies
├── scraper.py            # Web scraping implementation
├── social_poster.py      # Social media posting functionality
└── news_data.json        # Scraped data storage (generated)
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news-scraper.git
   cd news-scraper
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration settings
   ```

## Usage

### Command Line Interface

The application provides a simple command line interface via `main.py`:

```bash
# Scrape news articles
python main.py scrape

# Process and post the next article
python main.py process

# Check status of the data file
python main.py status

# Start the API server
python main.py serve
```

### API Endpoints

When running the API server, the following endpoints are available:

- `GET /` - Status check
- `GET /status` - Detailed status information
- `GET /scrape?auth_code=YOUR_AUTH_CODE` - Trigger scraping operation
- `GET /articles?auth_code=YOUR_AUTH_CODE` - Get all scraped articles
- `GET /process?auth_code=YOUR_AUTH_CODE` - Process and post the next article

All secured endpoints require the `auth_code` query parameter matching the value set in your `.env` file.

### Web Hosting with Passenger

For web hosting environments using Passenger, the application includes a WSGI entry point in `passenger_wsgi.py`. This file handles HTTP requests and routes them to the appropriate handler functions.

## Configuration

Configure the application by setting environment variables in your `.env` file:

- `AUTH_CODE` - Authentication code for API access
- `HOST` - Host for the API server (default: 127.0.0.1)
- `PORT` - Port for the API server (default: 8000)
- `DATA_FILE` - Path to the JSON data file (default: news_data.json)
- `TW_*` - Twitter API credentials

## Error Handling

The application implements comprehensive error handling throughout the codebase:

- Custom exception classes for specific error types
- Try-except blocks to handle potential exceptions
- Logging of errors with appropriate severity levels
- Graceful error responses from API endpoints

## Security Considerations

- API endpoints are protected with an authentication code
- Sensitive credentials are stored in environment variables
- Input validation is performed to prevent security issues
- CORS middleware is configured to control access


>Rate Limit docs:
https://docs.x.com/x-api/fundamentals/rate-limits

## License

This project is licensed under the MIT License - see the LICENSE file for details.