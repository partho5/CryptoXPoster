import re
import time
import logging
from typing import List, Dict, Union, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import os
import json
from datetime import datetime

from file_handler import prepend_data, get_file_path

DATA_FILE = os.getenv('DATA_FILE', 'news_data.json')


class CryptoScrapeError(Exception):
    """Custom exception for scraping errors."""
    pass


class YahooFinanceCryptoScraper:
    BASE_URL = "https://finance.yahoo.com"
    CRYPTO_TRENDING_URL = f"{BASE_URL}/markets/crypto/trending/"

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.session = self._init_session(max_retries)
        self.logger = self._init_logger()

    def _init_session(self, max_retries: int) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        })
        return session

    def _init_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            ))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _fetch_html(self, url: str) -> BeautifulSoup:
        try:
            res = self.session.get(url, timeout=self.timeout)
            res.raise_for_status()
            return BeautifulSoup(res.content, "html.parser")
        except Exception as e:
            raise CryptoScrapeError(f"Request failed: {e}")

    def _clean(self, text: Optional[str]) -> str:
        return re.sub(r"\s+", " ", text.strip()) if text else ""

    def _parse_number(self, value: str) -> Union[float, str, None]:
        value = self._clean(value)

        if not value:
            return None

        if "%" in value:
            try:
                return float(value.replace("%", "").replace(",", "").replace("+", ""))
            except ValueError:
                return value

        suffixes = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}
        for suffix, mult in suffixes.items():
            if value.endswith(suffix):
                try:
                    return float(value[:-1].replace(",", "")) * mult
                except ValueError:
                    return value

        try:
            return float(value.replace(",", "").replace("+", "").replace("$", ""))
        except ValueError:
            return value

    def _extract_row(self, row) -> Dict[str, Union[str, float, None]]:
        tds = row.find_all("td")
        data = {
            "symbol": None,
            "name": None,
            "price": None,
            "change": None,
            "change_percent": None,
            "market_cap": None,
            "volume": None,
            "volume_currency_24hr": None,
            "total_volume_24hr": None,
            "circulating_supply": None,
            "week_52_change_percent": None,
        }

        if len(tds) < 12:
            return data

        try:
            symbol_tag = tds[0].find("span", class_="symbol")
            if symbol_tag:
                data["symbol"] = self._clean(symbol_tag.get_text())

            data["name"] = self._clean(tds[1].get_text())

            def get_field(cell, field):
                tag = cell.find("fin-streamer", {"data-field": field})
                return self._parse_number(tag.get_text()) if tag else None

            data["price"] = get_field(tds[3], "regularMarketPrice")
            data["change"] = get_field(tds[4], "regularMarketChange")
            data["change_percent"] = get_field(tds[5], "regularMarketChangePercent")
            data["market_cap"] = get_field(tds[6], "marketCap")
            data["volume"] = get_field(tds[7], "regularMarketVolume")
            data["volume_currency_24hr"] = self._parse_number(tds[8].get_text())
            data["total_volume_24hr"] = self._parse_number(tds[9].get_text())
            data["circulating_supply"] = self._parse_number(tds[10].get_text())

            change_52 = tds[11].find("fin-streamer", {"data-field": "fiftyTwoWeekChangePercent"})
            if change_52:
                data["week_52_change_percent"] = self._parse_number(change_52.get_text())

        except Exception as e:
            self.logger.warning(f"Row extraction failed: {e}")

        return data

    def _scrape(self) -> List[Dict[str, Union[str, float, None]]]:
        soup = self._fetch_html(self.CRYPTO_TRENDING_URL)
        table = soup.find("table")
        if not table:
            raise CryptoScrapeError("No table found on page")

        rows = table.find("tbody").find_all("tr")
        if not rows:
            raise CryptoScrapeError("No data rows found")

        return [self._extract_row(r) for r in rows if r.find("td")]

    @classmethod
    def get_data(cls) -> List[Dict[str, Union[str, float, None]]]:
        return cls()._scrape()



def transform_raw_data_to_news_post(crypto_data):
    """
    Transform raw cryptocurrency data to news post format.
    This is a placeholder function that converts crypto market data
    into a news-like format for consistency with existing data structure.
    """
    # Create a news-like title based on crypto data
    price_direction = "rises" if crypto_data.get('change', 0) > 0 else "falls"
    title = f"{crypto_data.get('name', 'Unknown Crypto')} {price_direction} to ${crypto_data.get('price', 0):.2f}"

    # Create a summary with key market information
    change_percent = crypto_data.get('change_percent', 0)
    market_cap = crypto_data.get('market_cap', 0)
    volume = crypto_data.get('volume', 0)

    summary = f"Trading at ${crypto_data.get('price', 0):.2f} with a {change_percent:+.2f}% change. Market cap: ${market_cap / 1e9:.1f}B, 24h volume: ${volume / 1e9:.1f}B"

    # Create a placeholder link (you might want to customize this)
    symbol = crypto_data.get('symbol', 'UNKNOWN')
    link = f"https://finance.yahoo.com/quote/{symbol}"

    return {
        "title": "Trending Now\n\n"+title,
        "summary": summary,
        "link": link,
        "image_url": None,
        "timestamp": datetime.now().isoformat()
    }


def load_existing_data():
    """Load existing JSON data from file, return empty list if file doesn't exist."""
    file_path = get_file_path()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Loaded {len(data)} existing entries from {file_path}")
            return data
    except FileNotFoundError:
        print(f"File {file_path} not found. Starting with empty list.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {file_path}: {e}")
        return []


def save_data(data):
    """
    Save data to JSON file in the parent directory of this script.
    """
    file_path = get_file_path()

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} total entries to {file_path}")


def scrape_and_save_yahoo_trending_table2():
    """Main function to get crypto data and prepend to existing file."""
    try:
        # Get crypto data
        print("Fetching crypto data from Yahoo Finance...")
        data = YahooFinanceCryptoScraper.get_data()

        if data:
            # Load existing data from file
            existing_data = load_existing_data()

            # Transform and prepend new data
            new_entries = []
            for entry in data:
                transformed_entry = transform_raw_data_to_news_post(entry)
                new_entries.append(transformed_entry)
                print(f"Added: {transformed_entry['title']}")

            # Prepend new entries to existing data (new entries first)
            combined_data = new_entries + existing_data

            # Save updated data back to file
            save_data(combined_data)
            print(f"Successfully prepended {len(new_entries)} new entries to existing {len(existing_data)} entries")
            print(f"Total entries in file: {len(combined_data)}")
        else:
            print("No data retrieved from YahooFinanceCryptoScraper")

    except Exception as e:
        print(f"Error in append_crypto_data_to_file: {e}")
        import traceback
        traceback.print_exc()



def scrape_and_save_yahoo_trending_table(file_path):
    """Main function to get crypto data and prepend to existing file."""
    try:
        # Get crypto data
        print("Fetching crypto data from Yahoo Finance...")
        data = YahooFinanceCryptoScraper.get_data()

        if data:
            # Transform new data
            new_entries = []
            for entry in data:
                transformed_entry = transform_raw_data_to_news_post(entry)
                new_entries.append(transformed_entry)
                print(f"Added: {transformed_entry['title']}")

            # Use the modular function to prepend data
            # Assuming your existing file path - adjust as needed
            prepend_data(file_path, new_entries, resolve_path=False)

            print(f"Successfully prepended {len(new_entries)} new entries")
        else:
            print("No data retrieved from YahooFinanceCryptoScraper")

    except Exception as e:
        print(f"Error in append_crypto_data_to_file: {e}")
        import traceback
        traceback.print_exc()


# prepend_crypto_data_to_file()
