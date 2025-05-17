"""
Configuration for the Telegram bot.
"""

import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env if it exists
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
DATABASE_PATH = str(Path(__file__).parent.parent / "data" / "bot_data.db")
DEFAULT_NOTABLE_FOLLOWERS = int(os.getenv("DEFAULT_NOTABLE_FOLLOWERS", "5"))
WEBHOOK_URL = "https://webhook.site/00c4fb6a-04cb-460e-a4d2-4ca2055f1dd6"

# Convert admin IDs string to a list of integers
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(",") if admin_id.strip().isdigit()]

# Add your own Telegram ID as admin if not already set
if not ADMIN_IDS:
    # Default admin ID - replace with your own if needed
    ADMIN_IDS = [123456789]

# API URLs
HELIUS_API_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
PROTOKOLS_API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"

# File paths
COOKIES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "protokols_cookies.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bot.log")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "approved_tokens.json")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = DATABASE_PATH

# Monitoring system configuration
MONITOR_HOST = "localhost"
MONITOR_PORT = 5000

# Default notable followers threshold
DEFAULT_NOTABLE_FOLLOWERS_THRESHOLD = DEFAULT_NOTABLE_FOLLOWERS

# Trading bot URLs
TRADING_BOTS = {
    "geckoterminal": "https://www.geckoterminal.com/solana/tokens/{token_address}",
    "dextools": "https://www.dextools.io/app/solana/pair-explorer/{token_address}",
    "birdeye": "https://birdeye.so/token/{token_address}?chain=solana",
    "raydium": "https://raydium.io/swap/?inputCurrency=sol&outputCurrency={token_address}"
}

# Cache configuration
CACHE_EXPIRATION = 3600  # 1 hour in seconds

TELEGRAM_CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID", "0")) 