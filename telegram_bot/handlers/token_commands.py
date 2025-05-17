"""
Token command handlers para canal de Telegram.
"""

import logging
import sys
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Add root directory to path to import modules from the main project
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import servicios
from ..services.token_service import (
    get_token_info,
    get_recent_tokens
)
from ..utils.config import TRADING_BOTS

# Logging configuration
logger = logging.getLogger(__name__)

def format_notable_followers(notables):
    """Format the list of notable followers for display."""
    if not notables:
        return "No notable followers found"
    formatted = []
    for notable in notables:
        followers = notable.get('followersCount', 0)
        if followers >= 1_000_000:
            followers_str = f"{followers/1_000_000:.1f}M"
        elif followers >= 1_000:
            followers_str = f"{followers/1_000:.1f}K"
        else:
            followers_str = str(followers)
        formatted.append(f"@{notable['username']} ({followers_str} followers)")
    return "\n".join(formatted)

async def token_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed information about a specific token."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide the token address. Example:\n"
            "/token 8wnN6EuyqsNvXD5pbF9MErcL2QB1eZ4pTmb4wwMGVXwj"
        )
        return
    token_address = context.args[0]
    wait_message = await update.message.reply_text(
        "⏳ Fetching token information...",
    )
    try:
        token_info = get_token_info(token_address)
        if not token_info:
            await wait_message.delete()
            await update.message.reply_text(
                "❌ Could not find information for the specified token. "
                "Please verify that the address is correct."
            )
            return
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
        response = f"🪙 *Token Information:*\n\n"
        if token_info.get('image'):
            response += f"🖼 *Image:* {token_info['image']}\n\n"
        response += (
            f"📝 *Name:* {token_info.get('name', 'N/A')}\n"
            f"🔤 *Symbol:* {token_info.get('symbol', 'N/A')}\n"
            f"🔗 *Contract:* `{token_info['token_address']}`\n"
            f"👤 *Creator:* @{token_info.get('twitter_username', 'N/A')}\n"
            f"⭐ *Notable followers:* {token_info.get('notable_followers_count', 0)}\n"
        )
        if token_info.get('top_notables'):
            response += "\n*Top 5 Notable Followers:*\n"
            response += format_notable_followers(token_info['top_notables'])
            response += "\n"
        response += (
            f"\n✅ *Approved:* {'Yes' if token_info.get('approved', False) else 'No'}\n"
            f"🕒 *Timestamp:* {token_info.get('timestamp', 'N/A')}\n"
        )
        await wait_message.delete()
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        logger.info(f"Token info for {token_address} sent to channel")
    except Exception as e:
        await wait_message.delete()
        await update.message.reply_text(f"❌ Error fetching token information: {str(e)}")
        logger.error(f"Error fetching token information for {token_address}: {str(e)}")

async def recent_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recently approved tokens."""
    wait_message = await update.message.reply_text(
        "⏳ Fetching recent tokens...",
    )
    try:
        limit = 5
        if context.args and len(context.args) > 0:
            try:
                limit = int(context.args[0])
                limit = max(1, min(limit, 10))
            except ValueError:
                pass
        recent_tokens = get_recent_tokens(limit)
        if not recent_tokens:
            await wait_message.delete()
            await update.message.reply_text(
                "❌ No recently approved tokens found."
            )
            return
        response = f"🔄 *{len(recent_tokens)} Recently Approved Tokens:*\n\n"
        for token in recent_tokens:
            response += (
                f"*{token.get('name', 'N/A')} ({token.get('symbol', 'N/A')})*\n"
            )
            if token.get('image'):
                response += f"🖼 *Image:* {token['image']}\n"
            response += (
                f"👤 @{token.get('twitter_username', 'N/A')} - 👥 {token.get('notable_followers_count', 0)} notable followers\n"
            )
            if token.get('top_notables'):
                response += "*Top Notable Followers:*\n"
                response += format_notable_followers(token['top_notables'])
                response += "\n"
            response += (
                f"🔗 `{token['token_address']}`\n"
                f"🕒 {token.get('timestamp', 'N/A')}\n\n"
            )
        await wait_message.delete()
        await update.message.reply_text(response, parse_mode='Markdown')
        logger.info("Recent tokens sent to channel")
    except Exception as e:
        await wait_message.delete()
        await update.message.reply_text(f"❌ Error fetching recent tokens: {str(e)}")
        logger.error(f"Error fetching recent tokens: {str(e)}") 