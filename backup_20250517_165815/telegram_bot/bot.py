#!/usr/bin/env python3
"""
Telegram Bot for monitoring Solana tokens and verifying notable followers.

This bot allows:
1. Query information about tokens on Solana
2. Receive automatic notifications about new tokens
3. Customize the notable followers threshold
"""

import os
import logging
import sys
from pathlib import Path

# Add root directory to path to import modules from the main project
sys.path.append(str(Path(__file__).parent.parent))

# Import python-telegram-bot modules
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Import handlers
from telegram_bot.handlers.user_commands import start, help_command, status, auto_register_user
from telegram_bot.handlers.token_commands import token_info, recent_tokens, set_filter
from telegram_bot.handlers.admin_commands import admin_stats, admin_refresh, admin_broadcast

# Import services
from telegram_bot.services.notification_service import notification_service
from telegram_bot.utils.config import ADMIN_IDS

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telegram_bot/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Admin check decorator
def admin_only(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("Sorry, this command is only available for administrators.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def main():
    """Start the bot."""
    # Get bot token from environment variable or .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Load environment variables from .env if it exists
        
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            # Use hardcoded token from config.py
            from telegram_bot.utils.config import TELEGRAM_BOT_TOKEN
            TOKEN = TELEGRAM_BOT_TOKEN
            logger.info("Using bot token from config.py")
    except ImportError:
        logger.warning("python-dotenv is not installed. Using environment variables directly.")
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            # Use hardcoded token from config.py
            from telegram_bot.utils.config import TELEGRAM_BOT_TOKEN
            TOKEN = TELEGRAM_BOT_TOKEN
            logger.info("Using bot token from config.py")
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add basic command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    
    # Add token command handlers
    application.add_handler(CommandHandler("token", token_info))
    application.add_handler(CommandHandler("recent", recent_tokens))
    
    # Add filtering command handler
    application.add_handler(CommandHandler("setfilter", set_filter))
    
    # Add admin command handlers (restricted to admins)
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CommandHandler("refresh", admin_refresh))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))
    
    # Start notification service
    notification_service.start_monitoring()
    logger.info("Notification service started")
    
    # Start the bot (polling)
    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    # Stop notification service when finished
    notification_service.stop_monitoring()

if __name__ == "__main__":
    main() 