#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descargar la lista completa de notable followers de un usuario de Twitter usando Protokols.

- Requiere cookies de sesión válidas en 'protokols_cookies.json'.
- Descarga todos los followers notables usando paginación.
- Guarda la lista en un archivo CSV.
"""

import requests
import json
import urllib.parse
import time
import csv
import logging
import sys
from typing import List, Dict

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DownloadNotableFollowers")

COOKIES_FILE = "protokols_cookies.json"
SMART_FOLLOWERS_URL = "https://api.protokols.io/api/trpc/smartFollowers.getPaginatedSmartFollowers"

# Cargar cookies desde archivo JSON
def load_cookies(cookies_file: str) -> Dict:
    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
        # Si es lista, convertir a dict {name: value}
        if isinstance(cookies_data, list):
            cookies = {c['name']: c['value'] for c in cookies_data if 'name' in c and 'value' in c}
        elif isinstance(cookies_data, dict):
            cookies = cookies_data
        else:
            cookies = {}
        return cookies
    except Exception as e:
        logger.error(f"No se pudieron cargar las cookies: {e}")
        return {}

def get_notable_followers(username: str, cookies: Dict, limit: int = 50, delay: float = 1.0) -> List[Dict]:
    """
    Descarga la lista completa de notable followers usando paginación.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    session = requests.Session()
    session.headers.update(headers)
    for name, value in cookies.items():
        session.cookies.set(name, value)

    all_followers = []
    cursor = 0
    while True:
        params = {
            "limit": limit,
            "followerType": "all",
            "username": username,
            "sortBy": "followersCount",
            "sortOrder": "desc",
            "cursor": cursor
        }
        input_json = json.dumps({"json": params})
        encoded_input = urllib.parse.quote(input_json)
        url = f"{SMART_FOLLOWERS_URL}?input={encoded_input}"
        logger.info(f"Consultando: {url}")
        response = session.get(url)
        if response.status_code != 200:
            logger.error(f"Error en la solicitud: {response.status_code} - {response.text}")
            break
        data = response.json()
        items = data.get("result", {}).get("data", {}).get("json", {}).get("data", {}).get("items", [])
        if not items:
            logger.info("No se encontraron más followers.")
            break
        all_followers.extend(items)
        logger.info(f"Descargados {len(items)} followers (total: {len(all_followers)})")
        # Paginación: si hay menos de 'limit', terminamos
        if len(items) < limit:
            break
        cursor += limit
        time.sleep(delay)
    return all_followers

def save_followers_to_csv(followers: List[Dict], output_file: str):
    if not followers:
        logger.warning("No hay followers para guardar.")
        return
    # Determinar campos principales
    fieldnames = [
        "twitterProfileId", "username", "displayName", "avatarUrl", "followersCount", "kolScore", "smartFollowersCount", "followedAt", "tags"
    ]
    with open(output_file, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for follower in followers:
            profile = follower.get("twitterProfile", {})
            row = {
                "twitterProfileId": profile.get("id", ""),
                "username": profile.get("username", ""),
                "displayName": profile.get("displayName", ""),
                "avatarUrl": profile.get("avatarUrl", ""),
                "followersCount": profile.get("followersCount", 0),
                "kolScore": profile.get("kolScore", 0),
                "smartFollowersCount": profile.get("smartFollowersCount", 0),
                "followedAt": follower.get("followedAt", ""),
                "tags": ",".join(profile.get("tags", []))
            }
            writer.writerow(row)
    logger.info(f"Followers guardados en {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python protokols_download_notable_followers.py <twitter_username> [output_file.csv]")
        sys.exit(1)
    username = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{username}_notable_followers.csv"
    cookies = load_cookies(COOKIES_FILE)
    if not cookies:
        print("No se pudieron cargar las cookies. Abortando.")
        sys.exit(1)
    followers = get_notable_followers(username, cookies)
    save_followers_to_csv(followers, output_file)
    print(f"Descarga completada. Total followers: {len(followers)}. Archivo: {output_file}")

if __name__ == "__main__":
    main() 