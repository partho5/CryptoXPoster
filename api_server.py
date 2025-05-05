"""
REST API server for the news scraper.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from scraper import scrape_and_save
from data_manager import process_next_item, read_json_file, DataManagerError

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
AUTH_CODE = os.getenv('AUTH_CODE', 'default_auth_code')  # NEVER use this default in production!
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', '8000'))

app = FastAPI(
    title="News Scraper API",
    description="API for scraping and serving news articles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScrapingResponse(BaseModel):
    """Response model for scraping operations"""
    status: str
    message: str
    count: int
    timestamp: str


class ErrorResponse(BaseModel):
    """Response model for errors"""
    status: str
    message: str


def verify_auth_code(auth_code: str = Query(..., description="Authentication code required for API access")):
    """
    Dependency to verify the authentication code

    Args:
        auth_code: The authentication code provided in the request

    Returns:
        The authenticated auth_code if valid

    Raises:
        HTTPException: If the authentication code is invalid
    """
    if auth_code != AUTH_CODE:
        logger.warning(f"Unauthorized access attempt with auth code: {auth_code}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication code"
        )
    return auth_code


@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint that returns basic information"""
    return {"status": "online", "message": "News Scraper API is running"}


@app.get("/scrape", response_model=ScrapingResponse, dependencies=[Depends(verify_auth_code)])
async def trigger_scrape(auth_code: str = Query(...)):
    """
    Trigger a new scraping operation and save results

    Args:
        auth_code: Authentication code for verification

    Returns:
        ScrapingResponse with status and count of scraped articles
    """
    try:
        articles = scrape_and_save(DATA_FILE)

        return {
            "status": "success",
            "message": "Scraping completed successfully",
            "count": len(articles),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


@app.get("/articles", response_model=List[Dict[str, Any]], dependencies=[Depends(verify_auth_code)])
async def get_articles(auth_code: str = Query(...)):
    """
    Get all articles from the data file

    Args:
        auth_code: Authentication code for verification

    Returns:
        List of articles
    """
    try:
        articles = read_json_file(DATA_FILE)
        return articles
    except DataManagerError as e:
        logger.error(f"Failed to read articles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read articles: {str(e)}"
        )


@app.get("/process", response_model=Dict[str, Any], dependencies=[Depends(verify_auth_code)])
async def process_article(auth_code: str = Query(...)):
    """
    Process the next article and post it

    Args:
        auth_code: Authentication code for verification

    Returns:
        The processed article or an error message
    """
    from social_poster import post_to_x  # Import here to avoid circular imports

    try:
        processed_item = process_next_item(DATA_FILE, post_to_x)

        if processed_item is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No articles available to process"}
            )

        return {
            "status": "success",
            "message": "Article processed successfully",
            "article": processed_item
        }
    except Exception as e:
        logger.error(f"Failed to process article: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process article: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": f"Internal server error: {str(exc)}"}
    )


def start_server():
    """Start the API server"""
    try:
        uvicorn.run(
            "api_server:app",
            host=HOST,
            port=PORT,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    start_server()