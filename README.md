# Crypto News Scraper and Social Media Poster

A modular Python application that scrapes cryptocurrency news articles from multiple sources (Cointelegraph, Yahoo Finance, CNBC), saves them to a JSON file, and posts them to social media platforms via a secure REST API.

## Features

- **Multi-Source Web Scraping**: Collects news from Cointelegraph, Yahoo Finance, and CNBC
- **REST API**: Secure API endpoints with authentication
- **Social Media Integration**: Posts scraped articles to Twitter/X
- **Automated Scheduling**: Built-in scheduler for continuous operation
- **Modular Design**: Follows the Single Responsibility Principle
- **Error Handling**: Comprehensive exception handling throughout

## Project Structure

```
CryptoNewsPostToX/
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment variables template
├── api_server.py         # FastAPI server implementation (port 8000)
├── passenger_wsgi.py     # WSGI server implementation (port 8080) - MAIN SERVER
├── scheduler_in_local_pc.py  # Automated scheduler that starts the main server
├── main.py               # Command line interface
├── data_manager.py       # JSON file operations
├── scraper/              # Scraping modules
│   ├── CoinTelegraphScraper.py
│   ├── YahooScraper.py
│   └── cnbc_scraper.py
├── ai/                   # AI response generation
├── utils/                # Utility modules
├── requirements.txt      # Python dependencies
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

### Server

The application uses `passenger_wsgi.py` which runs on port 8080 and includes all scraping sources:

```bash
# Start the server directly
python passenger_wsgi.py

# Or use the automated scheduler (recommended for production)
python scheduler_in_local_pc.py
```

The scheduler automatically:
1. Starts the server on port 8080
2. Triggers initial scraping from all 3 sources (max 3 articles per source)
3. Continuously processes and posts articles every 3 hours
4. Maintains max 10 articles total in the data file

**✅ This is the working server that handles all functionality properly.**

### Command Line Interface

The application provides a simple command line interface via `main.py`:

```bash
# Scrape news articles
python main.py scrape

# Process and post the next article
python main.py process

# Check status of the data file
python main.py status
```

### API Endpoints

The server provides the following endpoints:

- `GET /` - Status check
- `GET /status` - Detailed status information
- `GET /scrape?auth_code=YOUR_AUTH_CODE` - Trigger scraping operation
- `GET /articles?auth_code=YOUR_AUTH_CODE` - Get all scraped articles
- `GET /process?auth_code=YOUR_AUTH_CODE` - Process and post the next article

**Scraping Details:**
- **3 Sources**: Cointelegraph, Yahoo Finance, CNBC
- **Max 3 articles per source** (9 total maximum per scrape)
- **Max 10 articles total** in `news_data.json` file
- **Automated scheduling** with 3-hour intervals

**Features:**
- WSGI production-ready server
- Built-in authentication
- Multi-source news aggregation

All secured endpoints require the `auth_code` query parameter matching the value set in your `.env` file.

### Authentication

The default authentication code is: `59bd0119d5fec5ffa3622e196ab5fd10`

Example usage:
```bash
curl "http://localhost:8080/scrape?auth_code=59bd0119d5fec5ffa3622e196ab5fd10"
```

## Troubleshooting

### Common Issues

1. **If you get import errors:**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're in the correct directory

2. **If scraping doesn't add new articles:**
   - Check the server logs for errors
   - Verify that the `news_data.json` file exists and is writable
   - The scraping is working if you see articles with recent timestamps
   - Note: File is limited to max 10 articles total

3. **PowerShell issues**: If you encounter PowerShell errors, try using Command Prompt instead
4. **Port conflicts**: Make sure port 8080 is not in use by other applications
5. **Authentication**: Use the correct auth code: `59bd0119d5fec5ffa3622e196ab5fd10`

## Configuration

Configure the application by setting environment variables in your `.env` file:

- `AUTH_CODE` - Authentication code for API access (default: 59bd0119d5fec5ffa3622e196ab5fd10)
- `HOST` - Host for the API server (default: 127.0.0.1)
- `PORT` - Port for the API server (default: 8080)
- `DATA_FILE` - Path to the JSON data file (default: news_data.json)
- `TW_*` - Twitter API credentials
- `OPENAI_API_KEY` - OpenAI API key for AI response generation

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