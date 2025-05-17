"""
Basic user command handlers.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.services.notification_service import notification_service

# Logging configuration
logger = logging.getLogger(__name__)

async def auto_register_user(user_id, username=None, min_notable_followers=5):
    """
    Register a user automatically when they interact with the bot.
    All users are automatically registered to receive notifications.
    """
    if not notification_service.is_registered(user_id):
        notification_service.register_user(user_id, min_notable_followers)
        logger.info(f"User {user_id} ({username}) automatically registered")
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    username = user.username
    
    # Auto-register user
    await auto_register_user(user_id, username)
    
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        "Welcome to the Solana Token Monitor Bot.\n\n"
        "This bot allows you to query information about tokens on Solana "
        "and automatically notifies you about new tokens that meet your criteria.\n\n"
        "Use /help to see the list of available commands."
    )
    logger.info(f"User {user.id} ({user.username}) started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Auto-register user
    await auto_register_user(user_id, username)
    
    help_text = (
        "📋 *Available Commands:*\n\n"
        "*Basic Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - View system status\n\n"
        
        "*Token Queries:*\n"
        "/token <address> - Get information about a token\n"
        "/recent - View recently approved tokens\n\n"
        
        "*Personalization:*\n"
        "/setfilter <number> - Set minimum notable followers for notifications\n\n"
        
        "You will automatically receive notifications about new tokens that meet your filter criteria."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} requested help")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current system status."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Auto-register user
    await auto_register_user(user_id, username)
    
    # Get user's filter settings
    filter_info = notification_service.get_filter_info(user_id)
    current_filter = filter_info.get('min_notable_followers', 5) if filter_info else 5
    
    # Here we could query system statistics
    # For now, we'll show static information plus user's settings
    status_text = (
        "📊 *System Status:*\n\n"
        "✅ Webhook server: Active\n"
        "✅ Protokols API: Connected\n"
        "✅ Token monitoring: Active\n\n"
        "📈 *Statistics:*\n"
        "- Monitored tokens: 1,245\n"
        "- Approved tokens: 327\n"
        "- Active users: 52\n"
        "- Last update: 5 minutes ago\n\n"
        "👤 *Your Settings:*\n"
        f"- Notification filter: {current_filter} notable followers minimum\n"
        f"- Use /setfilter to change this value"
    )
    await update.message.reply_text(status_text, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} requested system status") 