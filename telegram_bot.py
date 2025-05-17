#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram bot to handle token monitoring commands.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from monitor_token_activity import TokenMonitor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("TelegramBot")

# Initialize token monitor
monitor = TokenMonitor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to the Token Monitor Bot!\n\n"
        "I'll notify you about token activity and provide information about notable followers.\n\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "🤖 <b>Available Commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/monitor - Start monitoring token activity\n"
        "/stop - Stop monitoring\n"
        "/status - Check monitoring status",
        parse_mode='HTML'
    )

async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start monitoring token activity."""
    await update.message.reply_text("🚀 Starting token monitoring...")
    await monitor.start_monitoring()

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop monitoring token activity."""
    # TODO: Implement stop monitoring
    await update.message.reply_text("🛑 Token monitoring stopped.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check monitoring status."""
    # TODO: Implement status check
    await update.message.reply_text("📊 Monitoring is active.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("monitor", monitor_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 