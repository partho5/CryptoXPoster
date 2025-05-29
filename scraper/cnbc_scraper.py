import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import os

from ai.response_generator import generate_response
from file_handler import get_file_path, prepend_data
from utils.x_post import create_x_post_from


class CNBCQuoteScraper:
    BASE_URL = "https://www.cnbc.com"

    def __init__(self, symbol: str):
        # Example: symbol = "BTC.CM="
        self.symbol = symbol
        self.quote_url = f"{self.BASE_URL}/quotes/{self.symbol}"

    def _fetch_html(self, url):
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        res.raise_for_status()
        return BeautifulSoup(res.content, "html.parser")

    def _parse_quote_data(self, soup: BeautifulSoup):
        container = soup.find("div", class_="QuoteStrip-dataContainer")
        if not container:
            raise ValueError("Could not find quote container")

        time_tag = container.find("div", class_="QuoteStrip-lastTradeTime")
        price_tag = container.find("span", class_="QuoteStrip-lastPrice")
        change_container = container.find("span", class_="QuoteStrip-changeUp") or \
                           container.find("span", class_="QuoteStrip-changeDown")

        if not (time_tag and price_tag and change_container):
            raise ValueError("Some elements are missing in the quote data")

        change_parts = change_container.find_all("span")

        return {
            "symbol": self.symbol,
            "url": self.quote_url,
            "last_trade_time": time_tag.text.strip(),
            "price": price_tag.text.strip().replace(",", ""),
            "change": change_parts[0].text.strip() if len(change_parts) > 0 else None,
            "percent_change": change_parts[1].text.strip("()") if len(change_parts) > 1 else None
        }

    def scrape(self):
        soup = self._fetch_html(self.quote_url)
        return self._parse_quote_data(soup)

    def scrape_and_save(self, file_name="quote_data.json"):
        data = self.scrape()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))
        file_path = os.path.join(parent_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data


symbols = ['XDC', 'HBAR', 'BTC.BS=', 'BTC', 'BTC.CB=', 'BTC.GM=', 'BTC.BF=',
           'BCH', 'BCH.BS=', 'BNB', 'EOS', 'ETH', 'ETC', 'ETH.GM=',
           'ETH.BF=', 'LTC', 'LTC.BF=', 'LUNA', 'XRP', 'XRP.BS=', 'XTZ',
           'XLM', 'XLM.BF=', 'ZRX', 'ZRX.BF=', 'ZEC', 'NEXO', 'ADA',
           'LINK', 'MATIC', 'ATOM', 'SOL', 'DOT', 'SAND', 'AXS',
           'BUSD', 'USDC', 'USDT', 'UNI', 'DAI', 'SHIB']

top_10_active_cryptos = [
    "BTC",  # Bitcoin
    "ETH",  # Ethereum
    "BNB",  # BNB
    "SOL",  # Solana (Binance-Peg SOL)
    "LTC",  # Litecoin
    "UNI",  # Uniswap
    "DOT",  # Polkadot
    "ADA",  # Cardano
    "SHIB", # Shiba Inu (interpreted from Dogecoin-like pricing)
    "XRP"   # XRP
]

symbols = top_10_active_cryptos

import json

def cnbc_quotes_scrape_save(symbols):
    """
    Scrapes CNBC quotes for a list of symbols, converts the result to a news format,
    and prepends it to the data file.
    """
    for symbol in symbols:
        scraper = CNBCQuoteScraper(symbol + ".CM=")  # .CM= is required for CNBC quote URLs
        try:
            data = scraper.scrape()
            print(data)

            # Create a news-format JSON string using OpenAI
            json_string = create_x_post_from(data)

            # Convert JSON string to Python dict
            news_item = json.loads(json_string)

            # Wrap in list to match expected type
            news_format = [news_item]

            # Prepend to data file
            prepend_data(get_file_path(), news_format)

            # break  # stop after first successful scrape
        except Exception as e:
            print(f"Failed to scrape {symbol}: {e}")

cnbc_quotes_scrape_save(symbols)
