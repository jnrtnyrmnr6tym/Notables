#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to start both the Protokols session keeper and the Telegram bot.

This script:
1. Checks if the Protokols cookies are valid
2. Updates them if necessary
3. Starts the session keeper in daemon mode
4. Starts the Telegram bot
"""

import os
import sys
import subprocess
import argparse
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("start_telegram_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramBotStarter")

def start_session_keeper(daemon=True):
    """
    Start the Protokols session keeper.
    
    Args:
        daemon (bool): Whether to run in daemon mode
        
    Returns:
        bool: True if the session keeper was started successfully, False otherwise
    """
    try:
        # Build command
        cmd = [sys.executable, "start_protokols_session.py"]
        
        if daemon:
            cmd.append("--daemon")
        
        # Start the session keeper
        logger.info(f"Starting Protokols session keeper: {' '.join(cmd)}")
        process = subprocess.run(cmd)
        
        if process.returncode == 0:
            logger.info("Protokols session keeper started successfully")
            return True
        else:
            logger.error(f"Failed to start Protokols session keeper. Return code: {process.returncode}")
            return False
    except Exception as e:
        logger.error(f"Error starting Protokols session keeper: {str(e)}")
        return False

def start_telegram_bot():
    """
    Start the Telegram bot.
    
    Returns:
        bool: True if the bot was started successfully, False otherwise
    """
    try:
        # Build command
        cmd = [sys.executable, "-m", "telegram_bot.bot"]
        
        # Start the bot
        logger.info(f"Starting Telegram bot: {' '.join(cmd)}")
        process = subprocess.run(cmd)
        
        return process.returncode == 0
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Start Protokols session keeper and Telegram bot")
    parser.add_argument("--skip-session-keeper", "-s", action="store_true",
                        help="Skip starting the Protokols session keeper")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("STARTING TELEGRAM BOT WITH PROTOKOLS SESSION KEEPER")
    print("="*80)
    
    # Start the session keeper if not skipped
    if not args.skip_session_keeper:
        print("\nStep 1: Starting Protokols session keeper...")
        if not start_session_keeper(daemon=True):
            print("Failed to start Protokols session keeper. Exiting.")
            return 1
        
        # Wait a moment for the session keeper to initialize
        print("Waiting for session keeper to initialize...")
        time.sleep(2)
    else:
        print("\nSkipping Protokols session keeper as requested.")
    
    # Start the Telegram bot
    print("\nStep 2: Starting Telegram bot...")
    if not start_telegram_bot():
        print("Failed to start Telegram bot.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 