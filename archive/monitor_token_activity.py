#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to monitor token activity in real-time using Helius, webhook.site, and Protokols.
"""

import json
import requests
import logging
import time
import os
from typing import Dict, Optional, List
from datetime import datetime
import asyncio
import aiohttp
from dotenv import load_dotenv
import base58
from solana.rpc.api import Client
from protokols_smart_followers_fast import get_notables

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("TokenMonitor")

class TokenMonitor:
    def __init__(self):
        """
        Initialize the monitor with necessary credentials and configurations.
        """
        self.helius_api_key = os.getenv('HELIUS_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel = os.getenv('TELEGRAM_CHANNEL')  # e.g. @your_channel_name
        self.webhook_url = "https://webhook.site/00c4fb6a-04cb-460e-a4d2-4ca2055f1dd6"
        self.protokols_cookies_file = "protokols_cookies.json"
        self.solana_client = Client("https://api.mainnet-beta.solana.com")
        
        # Headers for different APIs
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Load Protokols cookies
        self.load_protokols_cookies()
        
        # API URLs
        self.helius_webhook_url = f"https://api.helius.xyz/v0/webhooks?api-key={self.helius_api_key}"
        self.protokols_api_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
        self.smart_followers_url = "https://api.protokols.io/api/trpc/smartFollowers.getPaginatedSmartFollowers"
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

    def load_protokols_cookies(self):
        """Load Protokols cookies from file."""
        try:
            with open(self.protokols_cookies_file, 'r') as f:
                self.protokols_cookies = json.load(f)
            logger.info("Protokols cookies loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Protokols cookies: {str(e)}")
            self.protokols_cookies = []

    def get_token_image(self, token_mint: str) -> str:
        """
        Get token image from metadata.
        
        Args:
            token_mint: Token mint address
            
        Returns:
            str: Token image URL
        """
        try:
            # Get token metadata
            response = self.solana_client.get_account_info(token_mint)
            if response and response.value:
                # Decode metadata
                metadata = base58.b58decode(response.value.data)
                # Extract image URI
                uri_start = metadata.find(b"uri")
                if uri_start != -1:
                    uri_end = metadata.find(b"\0", uri_start)
                    if uri_end != -1:
                        uri = metadata[uri_start+4:uri_end].decode('utf-8')
                        # Get image from IPFS or URI
                        if uri.startswith('ipfs://'):
                            ipfs_hash = uri.replace('ipfs://', '')
                            return f"https://ipfs.io/ipfs/{ipfs_hash}"
                        return uri
            return ""
        except Exception as e:
            logger.error(f"Error getting token image: {str(e)}")
            return ""

    def get_trading_links(self, token_mint: str) -> Dict[str, str]:
        """Generate trading links for different bots."""
        return {
            "Maestro": f"https://t.me/MaestroSniperBot?start={token_mint}",
            "Photon": f"https://t.me/PhotonSniperBot?start={token_mint}",
            "BullX": f"https://t.me/BullXSniperBot?start={token_mint}",
            "Axiom": f"https://t.me/AxiomSniperBot?start={token_mint}",
            "Bonk": f"https://t.me/BonkSniperBot?start={token_mint}",
            "Trojan": f"https://t.me/TrojanSniperBot?start={token_mint}"
        }

    def get_notable_followers(self, username: str, top_n: int = 5):
        """Get list of notable followers from Protokols using the fast script."""
        try:
            result = get_notables(username, top_n)
            return result
        except Exception as e:
            logger.error(f"Error getting notable followers: {str(e)}")
            return {"total": 0, "top": []}

    async def get_user_metrics(self, username: str) -> Dict:
        """Get user metrics from Protokols."""
        try:
            params = {"username": username}
            input_json = json.dumps({"json": params})
            encoded_input = requests.utils.quote(input_json)
            url = f"{self.protokols_api_url}?input={encoded_input}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, cookies=self.protokols_cookies) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and "data" in data["result"]:
                            user_data = data["result"]["data"].get("json", {})
                            if "engagementData" in user_data:
                                token_mint = user_data.get("tokenMint", "")
                                token_image = self.get_token_image(token_mint) if token_mint else ""
                                trading_links = self.get_trading_links(token_mint) if token_mint else {}
                                
                                return {
                                    "total_followers": user_data.get("followersCount", 0),
                                    "notable_followers_count": user_data["engagementData"].get("smartFollowersCount", 0),
                                    "kol_score": user_data["engagementData"].get("kolScore", 0),
                                    "trading_links": trading_links,
                                    "token_image": token_image
                                }
            return {}
        except Exception as e:
            logger.error(f"Error getting user metrics: {str(e)}")
            return {}

    async def send_telegram_message(self, message: str):
        """Send message to Telegram channel."""
        try:
            data = {
                "chat_id": self.telegram_channel,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False  # Enable link previews
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.telegram_api_url, json=data) as response:
                    if response.status != 200:
                        logger.error(f"Error sending Telegram message: {await response.text()}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")

    async def process_token_event(self, event: Dict):
        """Process token event and send information to Telegram channel."""
        try:
            logger.info(f"[DEBUG] Evento recibido: {json.dumps(event)[:500]}")
            token_mint = event.get("tokenMint")
            logger.info(f"[DEBUG] token_mint extraído: {token_mint}")
            if not token_mint:
                logger.warning("[DEBUG] No se encontró tokenMint en el evento")
                return

            username = event.get("username")
            logger.info(f"[DEBUG] username extraído: {username}")
            if username:
                metrics = await self.get_user_metrics(username)
                logger.info(f"[DEBUG] Métricas obtenidas: {metrics}")
                notable_data = self.get_notable_followers(username, 5)
                logger.info(f"[DEBUG] Notable followers: {notable_data}")
                total_notables = notable_data.get("total", 0)
                top_notables = notable_data.get("top", [])

                if metrics:
                    message = f"🔔 <b>New Token Activity Detected</b>\n\n"
                    if metrics.get('token_image'):
                        message += f"<a href='{metrics['token_image']}'>🖼 Token Image</a>\n\n"
                    message += f"💎 <b>Token:</b> <code>{token_mint}</code>\n"
                    message += f"👤 <b>Creator:</b> <a href='https://twitter.com/{username}'>@{username}</a>\n"
                    message += f"📊 <b>Metrics:</b>\n"
                    message += f"   • Total followers: {metrics['total_followers']:,}\n"
                    message += f"   • Notable followers: {total_notables:,}\n"
                    message += f"   • KOL Score: {metrics['kol_score']:,}\n\n"
                    if top_notables:
                        message += "🌟 <b>Top 5 Notable Followers:</b>\n"
                        for i, follower in enumerate(top_notables, 1):
                            message += f"{i}. <a href='https://twitter.com/{follower['username']}'>@{follower['username']}</a> - {follower['followersCount']:,} followers\n"
                        message += "\n"
                    if metrics.get('trading_links'):
                        message += "🤖 <b>Trading Links:</b>\n"
                        for bot_name, link in metrics['trading_links'].items():
                            message += f"• <a href='{link}'>{bot_name}</a>\n"
                    logger.info(f"[DEBUG] Enviando mensaje a Telegram: {message[:500]}")
                    await self.send_telegram_message(message)
                else:
                    logger.warning("[DEBUG] No se obtuvieron métricas para el usuario")
            else:
                logger.warning("[DEBUG] No se encontró username en el evento")
        except Exception as e:
            logger.error(f"Error processing token event: {str(e)}")

    async def setup_helius_webhook(self):
        """Set up Helius webhook."""
        try:
            webhook_data = {
                "webhookURL": self.webhook_url,
                "transactionTypes": ["TOKEN_MINT", "TOKEN_TRANSFER"],
                "accountAddresses": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"],
                "webhookType": "enhanced"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.helius_webhook_url, json=webhook_data) as response:
                    if response.status == 200:
                        logger.info("Helius webhook configured successfully")
                    else:
                        logger.error(f"Error configuring Helius webhook: {await response.text()}")
        except Exception as e:
            logger.error(f"Error setting up Helius webhook: {str(e)}")

    async def start_monitoring(self):
        """Start monitoring events."""
        # Configure Helius webhook
        await self.setup_helius_webhook()
        
        # Send startup message to channel
        logger.info("Token monitoring started")
        await self.send_telegram_message(
            "🚀 <b>Token Monitor Started</b>\n\n"
            "Monitoring token activity in real-time...\n\n"
            "You'll receive notifications about:\n"
            "• New token mints\n"
            "• Notable followers\n"
            "• Trading opportunities\n\n"
            "Stay tuned! 📈"
        )

async def main():
    monitor = TokenMonitor()
    await monitor.start_monitoring()
    
    # Keep the script running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main()) 