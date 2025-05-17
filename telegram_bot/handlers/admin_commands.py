"""
Admin command handlers.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram_bot.utils.config import ADMIN_IDS

# Logging configuration
logger = logging.getLogger(__name__)

def is_admin(user_id):
    """Check if a user is an administrator."""
    return user_id in ADMIN_IDS

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed system statistics (admin only)."""
    user_id = update.effective_user.id
    
    # Check if the user is an administrator
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ You don't have permission to use this command."
        )
        logger.warning(f"User {user_id} attempted to access admin statistics without permission")
        return
    
    # In a real implementation, we would get detailed statistics from the system
    # For now, we use sample data
    stats = {
        "tokens_monitored": 1245,
        "tokens_approved": 327,
        "active_users": 52,
        "total_users": 128,
        "api_requests_today": 1532,
        "webhook_notifications_today": 87,
        "system_uptime": "5 days, 7 hours, 23 minutes",
        "database_size": "24.7 MB",
        "cache_hit_rate": "78.3%"
    }
    
    # Format response
    response = (
        "📊 *Detailed System Statistics:*\n\n"
        f"*Tokens:*\n"
        f"- Monitored: {stats['tokens_monitored']}\n"
        f"- Approved: {stats['tokens_approved']}\n"
        f"- Approval rate: {(stats['tokens_approved'] / stats['tokens_monitored'] * 100):.1f}%\n\n"
        
        f"*Users:*\n"
        f"- Active: {stats['active_users']}\n"
        f"- Total: {stats['total_users']}\n"
        f"- Activity rate: {(stats['active_users'] / stats['total_users'] * 100):.1f}%\n\n"
        
        f"*System:*\n"
        f"- API requests today: {stats['api_requests_today']}\n"
        f"- Webhook notifications today: {stats['webhook_notifications_today']}\n"
        f"- Uptime: {stats['system_uptime']}\n"
        f"- Database size: {stats['database_size']}\n"
        f"- Cache hit rate: {stats['cache_hit_rate']}\n"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')
    logger.info(f"Admin {user_id} requested detailed statistics")

async def admin_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually refresh creator data (admin only)."""
    user_id = update.effective_user.id
    
    # Check if the user is an administrator
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ You don't have permission to use this command."
        )
        logger.warning(f"User {user_id} attempted to use refresh command without permission")
        return
    
    # Check if a username was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a Twitter username. Example:\n"
            "/refresh Andy_On_Sol"
        )
        return
    
    username = context.args[0]
    
    # Send wait message
    wait_message = await update.message.reply_text(
        f"⏳ Refreshing data for @{username}...",
    )
    
    try:
        # In a real implementation, we would update the creator's data
        # For now, we simulate a successful update
        
        # Format response
        response = (
            f"✅ Data for @{username} successfully updated.\n\n"
            f"👥 Notable followers: 27 (previously: 25)\n"
            f"🔄 Last update: now\n"
        )
        
        # Delete wait message and send response
        await wait_message.delete()
        await update.message.reply_text(response)
        
        logger.info(f"Admin {user_id} refreshed data for {username}")
    except Exception as e:
        await wait_message.delete()
        await update.message.reply_text(f"❌ Error updating data: {str(e)}")
        logger.error(f"Error updating data for {username}: {str(e)}")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to all users (admin only)."""
    user_id = update.effective_user.id
    
    # Check if the user is an administrator
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ You don't have permission to use this command."
        )
        logger.warning(f"User {user_id} attempted to use broadcast command without permission")
        return
    
    # Check if a message was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a message to send to all users. Example:\n"
            "/broadcast New update available!"
        )
        return
    
    message = " ".join(context.args)
    
    # Send wait message
    wait_message = await update.message.reply_text(
        "⏳ Sending message to all users...",
    )
    
    try:
        # In a real implementation, we would send the message to all users
        # For now, we simulate a successful broadcast
        
        # Format response
        response = (
            f"✅ Message sent to 128 users:\n\n"
            f"\"{message}\""
        )
        
        # Delete wait message and send response
        await wait_message.delete()
        await update.message.reply_text(response)
        
        logger.info(f"Admin {user_id} sent broadcast: {message}")
    except Exception as e:
        await wait_message.delete()
        await update.message.reply_text(f"❌ Error sending message: {str(e)}")
        logger.error(f"Error sending broadcast: {str(e)}") 