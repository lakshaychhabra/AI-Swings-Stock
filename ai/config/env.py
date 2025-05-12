import os
from dotenv import load_dotenv

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
ZERODHA_TOKEN = os.getenv("ZERODHA_TOKEN")
