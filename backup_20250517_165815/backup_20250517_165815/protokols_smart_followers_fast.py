#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script rápido para obtener el número total de smart followers y el top N más influyentes de un usuario de Twitter usando solo el endpoint smartFollowers.getPaginatedSmartFollowers de Protokols.

Uso:
    python protokols_smart_followers_fast.py <twitter_username> [top_N]

Requiere cookies válidas en 'protokols_cookies.json'.
"""

import requests
import json
import urllib.parse
import sys
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import time
import argparse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartFollowersFast")

COOKIES_FILE = "protokols_cookies.json"
SMART_FOLLOWERS_URL = "https://api.protokols.io/api/trpc/smartFollowers.getPaginatedSmartFollowers"
MAX_WORKERS = 5  # Número máximo de hilos para peticiones concurrentes
REQUEST_TIMEOUT = 10  # Timeout en segundos para las peticiones

def load_cookies(cookies_file: str) -> Dict:
    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
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

def fetch_page(username: str, cookies: Dict, cursor: int, limit: int = 50) -> List[Dict]:
    """Obtiene una página de notable followers"""
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
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            logger.error(f"Error en la solicitud: {response.status_code}")
            return []
        data = response.json()
        json_data = data.get("result", {}).get("data", {}).get("json", {}).get("data", {})
        return json_data.get("items", [])
    except Exception as e:
        logger.error(f"Error al obtener página {cursor}: {str(e)}")
        return []

def get_smart_followers_ultrafast(username: str, cookies: Dict, top_n: int = 5) -> Dict:
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

    params = {
        "limit": top_n,
        "followerType": "all",
        "username": username,
        "sortBy": "followersCount",
        "sortOrder": "desc",
        "cursor": 0
    }
    input_json = json.dumps({"json": params})
    encoded_input = urllib.parse.quote(input_json)
    url = f"{SMART_FOLLOWERS_URL}?input={encoded_input}"
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            logger.error(f"Error in request: {response.status_code}")
            return {"error": f"HTTP {response.status_code}"}
        data = response.json()
        json_data = data.get("result", {}).get("data", {}).get("json", {}).get("data", {})
        items = json_data.get("items", [])
        total = json_data.get("overallCount", None)
        top_followers = []
        for follower in items[:top_n]:
            profile = follower.get("twitterProfile", {})
            top_followers.append({
                "username": profile.get("username", ""),
                "displayName": profile.get("displayName", ""),
                "followersCount": profile.get("followersCount", 0)
            })
        return {"total": total, "top": top_followers}
    except Exception as e:
        logger.error(f"Error fetching notables: {str(e)}")
        return {"error": str(e)}

def get_user_metrics(username: str, cookies: Dict) -> dict:
    """Obtiene followersCount y kolScore del usuario objetivo usando influencers.getFullTwitterKolInitial"""
    API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
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
    params = {"username": username}
    input_json = json.dumps({"json": params})
    encoded_input = urllib.parse.quote(input_json)
    url = f"{API_URL}?input={encoded_input}"
    response = session.get(url)
    if response.status_code != 200:
        return {"followersCount": None, "kolScore": None}
    data = response.json()
    user_data = data.get("result", {}).get("data", {}).get("json", {})
    followers_count = user_data.get("followersCount", None)
    kol_score = user_data.get("engagement", {}).get("kolScore", None)
    return {"followersCount": followers_count, "kolScore": kol_score}

def format_compact_number(n):
    if n is None:
        return "?"
    if isinstance(n, str):
        return n
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}k"
    else:
        return str(n)

def print_raw_api_response(username: str, cookies: Dict, limit: int = 5):
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

    params = {
        "limit": limit,
        "followerType": "all",
        "username": username,
        "sortBy": "followersCount",
        "sortOrder": "desc",
        "cursor": 0
    }
    input_json = json.dumps({"json": params})
    encoded_input = urllib.parse.quote(input_json)
    url = f"{SMART_FOLLOWERS_URL}?input={encoded_input}"
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    print("\n--- RAW API RESPONSE ---\n")
    print(json.dumps(response.json(), indent=2))
    print("\n--- END RAW API RESPONSE ---\n")

def get_notables(username, top_n=5):
    """
    Get the total number of notable followers and the top N notables for a given Twitter username.
    Returns a dict: {"total": int, "top": list of dicts}
    Raises Exception on error.
    """
    cookies = load_cookies(COOKIES_FILE)
    if not cookies:
        raise Exception("Could not load cookies.")
    result = get_smart_followers_ultrafast(username, cookies, top_n)
    if "error" in result:
        raise Exception(result["error"])
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get top notable followers for a Twitter user using Protokols API.")
    parser.add_argument("username", help="Twitter username (without @)")
    parser.add_argument("--top", type=int, default=5, help="Number of top notables to show (default: 5)")
    args = parser.parse_args()

    print(f"\nAnalyzing notables for @{args.username}...")
    try:
        result = get_notables(args.username, args.top)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    print(f"\nTotal notable followers: {result['total']}")
    print(f"\nTop {args.top} notable followers:")
    print("-" * 50)
    for i, follower in enumerate(result['top'], 1):
        followers_str = format_compact_number(follower['followersCount'])
        print(f"{i}. @{follower['username']}")
        print(f"   Name: {follower['displayName']}")
        print(f"   Followers: {followers_str}")
        print("-" * 50)

"""
USAGE AS MODULE:
from protokols_smart_followers_fast import get_notables
result = get_notables("Jeremyybtc", top_n=5)
print(result)

USAGE FROM TERMINAL:
python protokols_smart_followers_fast.py Jeremyybtc --top 5
""" 