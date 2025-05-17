#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to start the Protokols session keeper.

This script:
1. Checks if the cookies are valid
2. If not valid, guides the user to update them manually
3. Starts the session keeper to maintain the cookies active
"""

import os
import sys
import subprocess
import argparse
import logging
import json
import requests
import urllib.parse
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("protokols_session.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProtokolsSessionStarter")

# Constants
DEFAULT_COOKIES_FILE = "protokols_cookies.json"
PROTOKOLS_API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
TEST_USERNAME = "jack"

def check_cookies(cookies_file=DEFAULT_COOKIES_FILE):
    """
    Check if the cookies file exists and if the cookies are valid.
    
    Args:
        cookies_file (str): Path to the cookies file
        
    Returns:
        bool: True if cookies are valid, False otherwise
    """
    # Check if the file exists
    if not os.path.exists(cookies_file):
        logger.error(f"Cookies file {cookies_file} not found")
        return False
    
    try:
        # Load cookies
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        
        if not cookies:
            logger.error("No cookies found in the file")
            return False
        
        # Build API request
        params = {"username": TEST_USERNAME}
        input_json = json.dumps({"json": params})
        encoded_input = urllib.parse.quote(input_json)
        url = f"{PROTOKOLS_API_URL}?input={encoded_input}"
        
        # Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Origin": "https://www.protokols.io",
            "Referer": f"https://www.protokols.io/twitter/{TEST_USERNAME}"
        }
        
        # Create session and add cookies
        session = requests.Session()
        for name, value in cookies.items():
            session.cookies.set(name, value)
        
        # Make request
        logger.info(f"Checking cookies validity with API request")
        response = session.get(url, headers=headers)
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "data" in data["result"]:
                logger.info("Cookies are valid")
                return True
        
        logger.warning(f"Cookies are not valid. Status code: {response.status_code}")
        return False
    except Exception as e:
        logger.error(f"Error checking cookies: {str(e)}")
        return False

def update_cookies(cookies_file=DEFAULT_COOKIES_FILE):
    """
    Update cookies by running the browser login script.
    
    Args:
        cookies_file (str): Path to the cookies file
        
    Returns:
        bool: True if cookies were updated successfully, False otherwise
    """
    try:
        print("\n" + "="*80)
        print("UPDATING PROTOKOLS COOKIES")
        print("="*80)
        print("The current cookies are not valid. You need to login manually to update them.")
        print("A browser window will open. Please login to Protokols and follow the instructions.")
        print("="*80 + "\n")
        
        # Wait for user confirmation
        input("Press Enter to continue...")
        
        # Run the browser login script
        cmd = [sys.executable, "protokols_browser_login.py", "--output", cookies_file]
        process = subprocess.run(cmd, check=True)
        
        if process.returncode == 0:
            logger.info("Cookies updated successfully")
            return True
        else:
            logger.error(f"Failed to update cookies. Return code: {process.returncode}")
            return False
    except Exception as e:
        logger.error(f"Error updating cookies: {str(e)}")
        return False

def start_session_keeper(cookies_file=DEFAULT_COOKIES_FILE, interval=15, daemon=False):
    """
    Start the session keeper.
    
    Args:
        cookies_file (str): Path to the cookies file
        interval (int): Interval between API calls in minutes
        daemon (bool): Whether to run in daemon mode
        
    Returns:
        bool: True if the session keeper was started successfully, False otherwise
    """
    try:
        # Build command
        cmd = [
            sys.executable, 
            "keep_protokols_session_alive.py",
            "--cookies-file", cookies_file,
            "--interval", str(interval)
        ]
        
        if daemon:
            cmd.append("--daemon")
        
        # Start the session keeper
        logger.info(f"Starting session keeper: {' '.join(cmd)}")
        
        if daemon:
            # Start as a separate process
            if os.name == 'nt':  # Windows
                from subprocess import DEVNULL, STARTUPINFO, STARTF_USESHOWWINDOW
                startupinfo = STARTUPINFO()
                startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                process = subprocess.Popen(
                    cmd,
                    stdout=DEVNULL,
                    stderr=DEVNULL,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Unix/Linux
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            logger.info(f"Session keeper started in daemon mode (PID: {process.pid})")
            print(f"\nSession keeper started in daemon mode (PID: {process.pid})")
            return True
        else:
            # Start in foreground
            process = subprocess.run(cmd)
            return process.returncode == 0
    except Exception as e:
        logger.error(f"Error starting session keeper: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Start Protokols session keeper")
    parser.add_argument("--cookies-file", "-c", default=DEFAULT_COOKIES_FILE,
                        help=f"Path to cookies file (default: {DEFAULT_COOKIES_FILE})")
    parser.add_argument("--interval", "-i", type=int, default=15,
                        help="Interval between API calls in minutes (default: 15)")
    parser.add_argument("--daemon", "-d", action="store_true",
                        help="Run session keeper in daemon mode")
    parser.add_argument("--force-update", "-f", action="store_true",
                        help="Force cookies update even if they are valid")
    
    args = parser.parse_args()
    
    # Check if cookies are valid
    cookies_valid = check_cookies(args.cookies_file)
    
    # Update cookies if needed or forced
    if not cookies_valid or args.force_update:
        print("Cookies are not valid or update is forced.")
        if not update_cookies(args.cookies_file):
            print("Failed to update cookies. Exiting.")
            return 1
        
        # Verify the updated cookies
        if not check_cookies(args.cookies_file):
            print("Updated cookies are still not valid. Please try again.")
            return 1
    
    # Start the session keeper
    print("\nStarting session keeper...")
    success = start_session_keeper(args.cookies_file, args.interval, args.daemon)
    
    if success:
        if args.daemon:
            print("Session keeper is running in the background.")
            print("You can close this terminal and the process will continue running.")
        return 0
    else:
        print("Failed to start session keeper.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 