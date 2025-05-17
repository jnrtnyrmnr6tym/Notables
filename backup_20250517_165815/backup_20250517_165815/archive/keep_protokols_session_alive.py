#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to keep Protokols session cookies alive.

This script:
1. Periodically makes requests to Protokols API to keep the session active
2. Verifies if cookies are still valid
3. Logs activity and session status
4. Can run as a background process

Usage:
    python keep_protokols_session_alive.py [--interval MINUTES] [--cookies-file FILE]
"""

import os
import json
import time
import logging
import argparse
import requests
import urllib.parse
import threading
import signal
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("protokols_session_keeper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProtokolsSessionKeeper")

# Constants
DEFAULT_COOKIES_FILE = "protokols_cookies.json"
DEFAULT_INTERVAL_MINUTES = 15  # Make request every 15 minutes
PROTOKOLS_API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
TEST_USERNAMES = ["jack", "elonmusk", "vitalikbuterin"]  # Rotate between these users for API calls

class ProtokolsSessionKeeper:
    """Class to keep Protokols session cookies alive."""
    
    def __init__(self, cookies_file=DEFAULT_COOKIES_FILE, interval_minutes=DEFAULT_INTERVAL_MINUTES):
        """
        Initialize the session keeper.
        
        Args:
            cookies_file (str): Path to the cookies JSON file
            interval_minutes (int): Interval between API calls in minutes
        """
        self.cookies_file = cookies_file
        self.interval_minutes = interval_minutes
        self.cookies = {}
        self.session = requests.Session()
        self.running = False
        self.last_success = None
        self.username_index = 0
        self.keep_alive_thread = None
        
        # Load cookies
        self.load_cookies()
    
    def load_cookies(self):
        """Load cookies from file."""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    self.cookies = json.load(f)
                
                # Update session cookies
                for name, value in self.cookies.items():
                    self.session.cookies.set(name, value)
                
                logger.info(f"Loaded {len(self.cookies)} cookies from {self.cookies_file}")
                return True
            else:
                logger.error(f"Cookies file {self.cookies_file} not found")
                return False
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False
    
    def verify_cookies(self):
        """
        Verify if the cookies are still valid.
        
        Returns:
            bool: True if cookies are valid, False otherwise
        """
        try:
            # Get next test username
            username = TEST_USERNAMES[self.username_index % len(TEST_USERNAMES)]
            self.username_index += 1
            
            # Build API request
            params = {"username": username}
            input_json = json.dumps({"json": params})
            encoded_input = urllib.parse.quote(input_json)
            url = f"{PROTOKOLS_API_URL}?input={encoded_input}"
            
            # Headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json",
                "Origin": "https://www.protokols.io",
                "Referer": f"https://www.protokols.io/twitter/{username}"
            }
            
            # Make request
            logger.debug(f"Making API request for user: {username}")
            response = self.session.get(url, headers=headers)
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "data" in data["result"]:
                    self.last_success = datetime.now()
                    logger.info(f"Session is active. API request successful for user: {username}")
                    return True
            
            logger.warning(f"Session may be expired. Status code: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error verifying cookies: {str(e)}")
            return False
    
    def keep_alive_loop(self):
        """Main loop to keep the session alive."""
        while self.running:
            try:
                is_valid = self.verify_cookies()
                
                if is_valid:
                    next_check = datetime.now() + timedelta(minutes=self.interval_minutes)
                    logger.info(f"Session is active. Next check at {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning("Session appears to be expired. Please login manually again.")
                    logger.warning("Run: python protokols_browser_login.py")
                
                # Sleep for the specified interval
                for _ in range(self.interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in keep alive loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
    
    def start(self):
        """Start the session keeper."""
        if self.running:
            logger.warning("Session keeper is already running")
            return
        
        if not self.cookies:
            logger.error("No cookies loaded. Cannot start session keeper")
            return
        
        self.running = True
        self.keep_alive_thread = threading.Thread(target=self.keep_alive_loop)
        self.keep_alive_thread.daemon = True
        self.keep_alive_thread.start()
        
        logger.info(f"Session keeper started. Interval: {self.interval_minutes} minutes")
    
    def stop(self):
        """Stop the session keeper."""
        self.running = False
        if self.keep_alive_thread:
            self.keep_alive_thread.join(timeout=5.0)
        logger.info("Session keeper stopped")
    
    def get_status(self):
        """Get current status of the session keeper."""
        status = {
            "running": self.running,
            "cookies_file": self.cookies_file,
            "cookies_count": len(self.cookies),
            "interval_minutes": self.interval_minutes,
            "last_success": self.last_success.strftime("%Y-%m-%d %H:%M:%S") if self.last_success else None
        }
        return status

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    logger.info("Received interrupt signal. Stopping session keeper...")
    if session_keeper:
        session_keeper.stop()
    sys.exit(0)

# Global session keeper instance
session_keeper = None

def main():
    """Main function."""
    global session_keeper
    
    parser = argparse.ArgumentParser(description="Keep Protokols session cookies alive")
    parser.add_argument("--interval", "-i", type=int, default=DEFAULT_INTERVAL_MINUTES,
                        help=f"Interval between API calls in minutes (default: {DEFAULT_INTERVAL_MINUTES})")
    parser.add_argument("--cookies-file", "-c", default=DEFAULT_COOKIES_FILE,
                        help=f"Path to cookies file (default: {DEFAULT_COOKIES_FILE})")
    parser.add_argument("--daemon", "-d", action="store_true",
                        help="Run as a background process")
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start session keeper
    session_keeper = ProtokolsSessionKeeper(
        cookies_file=args.cookies_file,
        interval_minutes=args.interval
    )
    
    # Verify cookies before starting
    if not session_keeper.verify_cookies():
        logger.error("Initial cookie verification failed. Please login manually first.")
        logger.error("Run: python protokols_browser_login.py")
        return 1
    
    # Start session keeper
    session_keeper.start()
    
    print("\n" + "="*80)
    print("PROTOKOLS SESSION KEEPER")
    print("="*80)
    print(f"Session keeper started with interval: {args.interval} minutes")
    print(f"Using cookies file: {args.cookies_file}")
    print(f"Log file: protokols_session_keeper.log")
    
    if args.daemon:
        print("\nRunning in background mode. Press Ctrl+C to stop.")
        print("You can close this terminal and the process will continue running.")
    else:
        print("\nPress Ctrl+C to stop.")
    
    # Keep the main thread alive if not in daemon mode
    if not args.daemon:
        try:
            while session_keeper.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping session keeper...")
            session_keeper.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 