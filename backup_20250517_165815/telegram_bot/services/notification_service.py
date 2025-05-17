"""
Notification service for the Telegram bot.
"""

import logging
import os
import sys
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import threading
import time
from telegram import Bot
from datetime import datetime
from typing import Dict, List, Optional

# Add root directory to path to import modules from the main project
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import functions from the monitoring system
from token_monitor_with_notable_check import get_approved_tokens

from ..utils.config import TELEGRAM_BOT_TOKEN, TRADING_BOTS, TELEGRAM_CHANNEL_ID

# Logging configuration
logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications to a Telegram channel."""
    
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self._last_processed_token = None
        self._monitor_thread = None
        self._running = False
        self._processed_tokens = set()
    
    def format_token_notification(self, token: Dict) -> str:
        """Format a token notification message."""
        try:
            response = (
                f"🆕 *New Token Approved!*\n\n"
            )
            
            # Add token image if available
            if token.get('image'):
                response += f"🖼 *Image:* {token['image']}\n\n"
            
            response += (
                f"📝 *Name:* {token.get('name', 'N/A')}\n"
                f"🔤 *Symbol:* {token.get('symbol', 'N/A')}\n"
                f"🔗 *Contract:* `{token['token_address']}`\n"
                f"👤 *Creator:* @{token.get('twitter_username', 'N/A')}\n"
                f"⭐ *Notable followers:* {token.get('notable_followers_count', 0)}\n"
            )
            
            # Add top notable followers if available
            if token.get('top_notables'):
                response += "\n*Top 5 Notable Followers:*\n"
                for notable in token['top_notables']:
                    followers = notable.get('followersCount', 0)
                    if followers >= 1_000_000:
                        followers_str = f"{followers/1_000_000:.1f}M"
                    elif followers >= 1_000:
                        followers_str = f"{followers/1_000:.1f}K"
                    else:
                        followers_str = str(followers)
                    
                    response += f"@{notable['username']} ({followers_str} followers)\n"
            
            response += (
                f"🕒 {token.get('timestamp', 'N/A')}\n"
            )
            
            return response
        except Exception as e:
            logger.error(f"Error formatting token notification: {str(e)}")
            return "Error formatting token notification"

    async def notify_new_token(self, token_data):
        """
        Notify about a new approved token en el canal de Telegram.
        """
        if not token_data:
            return
        token_address = token_data.get("token_address")
        if not token_address:
            return
        if token_address in self._processed_tokens:
            return
        self._processed_tokens.add(token_address)
        self._last_processed_token = token_address
        message = self.format_token_notification(token_data)
        keyboard = []
        row = []
        for name, url_template in TRADING_BOTS.items():
            button = InlineKeyboardButton(
                text=name.capitalize(),
                url=url_template.format(token_address=token_address)
            )
            row.append(button)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            logger.info(f"Notification sent to channel {TELEGRAM_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Error sending notification to channel: {str(e)}")

    def start_monitoring(self):
        """Start monitoring for new approved tokens."""
        if self._running:
            return
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_tokens)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Token monitoring started")

    def stop_monitoring(self):
        """Stop monitoring for new approved tokens."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Token monitoring stopped")

    def _monitor_tokens(self):
        """Monitor new approved tokens in a separate thread."""
        last_tokens = set()
        while self._running:
            try:
                tokens = get_approved_tokens()
                current_tokens = {token.get("token_address") for token in tokens if token.get("token_address")}
                new_tokens = current_tokens - last_tokens
                for token_address in new_tokens:
                    for token in tokens:
                        if token.get("token_address") == token_address:
                            asyncio.run(self.notify_new_token(token))
                            break
                last_tokens = current_tokens
                if len(self._processed_tokens) > 1000:
                    self._processed_tokens = set(list(self._processed_tokens)[-500:])
            except Exception as e:
                logger.error(f"Error monitoring tokens: {str(e)}")
            time.sleep(5)  # Check every 5 seconds

# Global instance of the notification service
notification_service = NotificationService() 