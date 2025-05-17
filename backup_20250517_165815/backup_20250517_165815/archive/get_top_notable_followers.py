#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para obtener los notable followers de una cuenta de Twitter usando Protokols.
"""

import json
import requests
import urllib.parse
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pprint import pprint
import time
import base58
from solana.rpc.api import Client

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("TopNotableFollowers")

class TopNotableFollowersExtractor:
    def __init__(self, cookies_file: str = "protokols_cookies.json"):
        """
        Inicializa el extractor con las cookies de sesión.
        
        Args:
            cookies_file: Ruta al archivo JSON con las cookies de sesión
        """
        self.api_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
        self.smart_followers_url = "https://api.protokols.io/api/trpc/smartFollowers.getPaginatedSmartFollowers"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Origin": "https://www.protokols.io",
            "Referer": "https://www.protokols.io/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.solana_client = Client("https://api.mainnet-beta.solana.com")
        
        # Cargar cookies
        try:
            with open(cookies_file, 'r') as f:
                self.cookies = json.load(f)
                for cookie in self.cookies:
                    self.session.cookies.set(
                        cookie['name'],
                        cookie['value'],
                        domain=cookie.get('domain', '.protokols.io'),
                        path=cookie.get('path', '/')
                    )
            logger.info("Cookies loaded successfully")
            logger.debug(f"Cookies loaded: {self.cookies}")
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            self.cookies = {}

    def get_token_image(self, token_mint: str) -> str:
        """
        Obtiene la imagen del token desde los metadatos.
        
        Args:
            token_mint: Dirección del token mint
            
        Returns:
            str: URL de la imagen del token
        """
        try:
            # Obtener metadatos del token
            response = self.solana_client.get_account_info(token_mint)
            if response and response.value:
                # Decodificar metadatos
                metadata = base58.b58decode(response.value.data)
                # Extraer URI de la imagen
                # Nota: La estructura exacta dependerá del formato de los metadatos
                # Este es un ejemplo simplificado
                uri_start = metadata.find(b"uri")
                if uri_start != -1:
                    uri_end = metadata.find(b"\0", uri_start)
                    if uri_end != -1:
                        uri = metadata[uri_start+4:uri_end].decode('utf-8')
                        # Obtener imagen desde IPFS o URI
                        if uri.startswith('ipfs://'):
                            ipfs_hash = uri.replace('ipfs://', '')
                            return f"https://ipfs.io/ipfs/{ipfs_hash}"
                        return uri
            return ""
        except Exception as e:
            logger.error(f"Error getting token image: {str(e)}")
            return ""

    def get_trading_links(self, token_mint: str) -> Dict[str, str]:
        """
        Genera links para diferentes bots de trading.
        
        Args:
            token_mint: Dirección del token mint
            
        Returns:
            Dict[str, str]: Diccionario con los links de los bots
        """
        return {
            "Maestro": f"https://t.me/MaestroSniperBot?start={token_mint}",
            "Photon": f"https://t.me/PhotonSniperBot?start={token_mint}",
            "BullX": f"https://t.me/BullXSniperBot?start={token_mint}",
            "Axiom": f"https://t.me/AxiomSniperBot?start={token_mint}",
            "Bonk": f"https://t.me/BonkSniperBot?start={token_mint}",
            "Trojan": f"https://t.me/TrojanSniperBot?start={token_mint}"
        }

    def get_user_metrics(self, username: str) -> Dict:
        """
        Obtiene las métricas generales de un usuario de Twitter.
        
        Args:
            username: Nombre de usuario de Twitter
            
        Returns:
            Dict: Diccionario con las métricas del usuario
        """
        try:
            params = {"username": username}
            input_json = json.dumps({"json": params})
            encoded_input = urllib.parse.quote(input_json)
            url = f"{self.api_url}?input={encoded_input}"
            
            self.session.headers.update({
                "Referer": f"https://www.protokols.io/twitter/{username}"
            })
            
            time.sleep(1)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "result" in data and "data" in data["result"]:
                user_data = data["result"]["data"].get("json", {})
                if "engagementData" in user_data:
                    # Obtener token mint si está disponible
                    token_mint = user_data.get("tokenMint", "")
                    token_image = self.get_token_image(token_mint) if token_mint else ""
                    trading_links = self.get_trading_links(token_mint) if token_mint else {}
                    
                    return {
                        "total_followers": user_data.get("followersCount", 0),
                        "notable_followers_count": user_data["engagementData"].get("smartFollowersCount", 0),
                        "kol_score": user_data["engagementData"].get("kolScore", 0),
                        "token_image": token_image,
                        "trading_links": trading_links
                    }
            
            return {
                "total_followers": 0,
                "notable_followers_count": 0,
                "kol_score": 0,
                "token_image": "",
                "trading_links": {}
            }
            
        except Exception as e:
            logger.error(f"Error getting user metrics: {str(e)}")
            return {
                "total_followers": 0,
                "notable_followers_count": 0,
                "kol_score": 0,
                "token_image": "",
                "trading_links": {}
            }

    def get_top_influencers(self, username: str, limit: int = 5) -> List[Dict]:
        """
        Obtiene los followers más influyentes de un usuario.
        
        Args:
            username: Nombre de usuario de Twitter
            limit: Número de influencers a obtener
            
        Returns:
            List[Dict]: Lista de los followers más influyentes
        """
        notable_followers = self.get_notable_followers(username)
        if notable_followers:
            # Ordenar por número de seguidores
            sorted_followers = sorted(
                notable_followers,
                key=lambda x: x.get('followersCount', 0),
                reverse=True
            )
            return sorted_followers[:limit]
        return []

    def get_notable_followers(self, username: str) -> List[Dict]:
        """
        Obtiene la lista de notable followers de un usuario de Twitter.
        
        Args:
            username: Nombre de usuario de Twitter
            
        Returns:
            List[Dict]: Lista de notable followers
        """
        try:
            # Primero obtenemos el ID del influencer
            params = {"username": username}
            input_json = json.dumps({"json": params})
            encoded_input = urllib.parse.quote(input_json)
            url = f"{self.api_url}?input={encoded_input}"
            
            logger.debug(f"API URL: {url}")
            
            # Actualizar el referer para este usuario específico
            self.session.headers.update({
                "Referer": f"https://www.protokols.io/twitter/{username}"
            })
            
            # Hacer la solicitud GET para obtener el ID
            time.sleep(1)  # Simula comportamiento humano
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            logger.debug(f"Initial response: {json.dumps(data, indent=2)}")
            
            if "result" in data and "data" in data["result"]:
                user_data = data["result"]["data"].get("json", {})
                if "engagementData" in user_data:
                    influencer_id = user_data["engagementData"].get("influencerId")
                    
                    if influencer_id:
                        # Intentar obtener los notable followers
                        notable_params = {
                            "limit": 20,
                            "followerType": "all",
                            "username": username,
                            "sortBy": "followersCount",
                            "sortOrder": "desc",
                            "cursor": 0
                        }
                        notable_input = json.dumps({"json": notable_params})
                        notable_url = f"{self.smart_followers_url}?input={urllib.parse.quote(notable_input)}"
                        
                        logger.debug(f"Notable Followers URL: {notable_url}")
                        logger.debug(f"Parameters: {json.dumps(notable_params, indent=2)}")
                        
                        time.sleep(1)  # Simula comportamiento humano
                        notable_response = self.session.get(notable_url)
                        logger.debug(f"Status code: {notable_response.status_code}")
                        logger.debug(f"Response headers: {notable_response.headers}")
                        
                        try:
                            notable_data = notable_response.json()
                            logger.debug(f"Notable Followers response:")
                            logger.debug(json.dumps(notable_data, indent=2))
                            
                            if "result" in notable_data and "data" in notable_data["result"]:
                                notable_followers = notable_data["result"]["data"].get("json", {}).get("data", {}).get("items", [])
                                if notable_followers:
                                    return [follower["twitterProfile"] for follower in notable_followers]
                            else:
                                logger.error("Unexpected response structure for Notable Followers")
                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON: {str(e)}")
                            logger.error(f"Response content: {notable_response.text}")
                    else:
                        logger.error("Could not get influencer ID")
                else:
                    logger.error("No engagement data found")
            else:
                logger.error("Unexpected response structure")
                
        except Exception as e:
            logger.error(f"Error getting notable followers: {str(e)}")
        
        return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Get notable followers of a Twitter account')
    parser.add_argument('username', help='Twitter username (without @)')
    parser.add_argument('--save', help='Save results to a JSON file')
    args = parser.parse_args()
    
    extractor = TopNotableFollowersExtractor()
    
    # Obtener métricas del usuario
    metrics = extractor.get_user_metrics(args.username)
    
    # Obtener notable followers
    notable_followers = extractor.get_notable_followers(args.username)
    
    if notable_followers:
        # Si hay imagen del token, mostrarla primero
        if metrics.get('token_image'):
            print(f"Token Image: {metrics['token_image']}")
            
        print(f"User: <a href='https://twitter.com/{args.username}'>{args.username}</a>")
        print(f"Total followers: {metrics['total_followers']:,}")
        print(f"Notable followers: {metrics['notable_followers_count']:,}")
        print(f"\nTop 5 notable followers:")
        top_influencers = extractor.get_top_influencers(args.username, 5)
        for i, influencer in enumerate(top_influencers, 1):
            print(f"{i}. <a href='https://twitter.com/{influencer['username']}'>@{influencer['username']}</a> - {influencer['followersCount']:,} followers")
        print(f"\nKOL Score: {metrics['kol_score']:,}")
        
        # Mostrar links de trading si están disponibles
        if metrics.get('trading_links'):
            print("\nTrading Links:")
            for bot_name, link in metrics['trading_links'].items():
                print(f"<a href='{link}'>{bot_name}</a>")
        
        if args.save:
            output = {
                "metrics": metrics,
                "notable_followers": notable_followers
            }
            with open(args.save, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\nResults saved to {args.save}")
    else:
        print(f"Could not get notable followers for @{args.username}")
        print("Suggestions:")
        print("1. Verify the username is correct")
        print("2. Ensure the account has notable followers")
        print("3. Verify the session cookies are valid")

if __name__ == "__main__":
    main()