#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Webhook server para recibir notificaciones de Helius, obtener metadatos, buscar notables en Protokols y enviar mensaje a Telegram.
"""

from flask import Flask, request, jsonify
import logging
import json
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from protokols_smart_followers_fast import get_smart_followers_ultrafast as get_notables
from datetime import datetime
import re

# Redeploy trigger Railway v3

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webhook_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Diccionario de wallets conocidas y sus identificadores
KNOWN_WALLETS = {
    "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE": "Believe",
    "5JzRjmLSy5YR4ReFRpCK9k3WuToUpc7vkBhWPyy89kQ4": "Launch On Pump"
}

app = Flask(__name__)

TIMEOUT = 5  # segundos

# --- Funciones de procesamiento y Telegram ---
def extract_token_metadata_from_ipfs(ipfs_url: str, mint_address: str) -> Optional[Dict[str, Any]]:
    try:
        logger.info(f"Descargando metadatos desde IPFS: {ipfs_url}")
        try:
            response = requests.get(ipfs_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            # Si la URL es de cloudflare-ipfs.com, intentar con ipfs.io
            if "cloudflare-ipfs.com" in ipfs_url:
                match = re.search(r"/ipfs/([A-Za-z0-9]+)", ipfs_url)
                if match:
                    ipfs_hash = match.group(1)
                    fallback_url = f"https://ipfs.io/ipfs/{ipfs_hash}"
                    logger.warning(f"Fallo en cloudflare-ipfs.com, intentando con ipfs.io: {fallback_url}")
                    response = requests.get(fallback_url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                else:
                    logger.error(f"No se pudo extraer el hash de IPFS de la URL: {ipfs_url}")
                    return None
            else:
                logger.error(f"Error al extraer metadatos de IPFS: {str(e)}")
                return None
        name = data.get('name')
        symbol = data.get('symbol')
        image = data.get('image')
        twitter = None
        # Caso 1: metadata.tweetCreatorUsername (formato antiguo)
        if 'metadata' in data and data['metadata'] and data['metadata'].get('tweetCreatorUsername'):
            logger.info("Usando formato antiguo (metadata.tweetCreatorUsername)")
            twitter = data['metadata'].get('tweetCreatorUsername')
        # Caso 2: campo twitter como URL (formato nuevo)
        elif 'twitter' in data and isinstance(data['twitter'], str):
            logger.info("Usando formato nuevo (campo twitter)")
            # Si es una URL de Twitter/X, extraer el username
            match = re.search(r'(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)', data['twitter'])
            if match:
                twitter = match.group(1)
            else:
                # Si es un @username directo
                if data['twitter'].startswith('@'):
                    twitter = data['twitter'][1:]
                else:
                    twitter = data['twitter']
        if not all([name, symbol]):
            logger.error(f"Faltan campos requeridos en los metadatos de IPFS para {mint_address}")
            return None
        return {
            'address': mint_address,
            'name': name,
            'symbol': symbol,
            'image': image,
            'twitter': twitter
        }
    except Exception as e:
        logger.error(f"Error al extraer metadatos de IPFS: {str(e)}")
        return None

def extract_token_metadata(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        if not webhook_data or not isinstance(webhook_data, list) or len(webhook_data) == 0:
            logger.error("Webhook vacío o formato inválido")
            return None
        tx = webhook_data[0]
        token_transfers = tx.get('tokenTransfers', [])
        if not token_transfers:
            logger.error("No se encontraron transferencias de token")
            return None
        mint_address = token_transfers[0].get('mint')
        if not mint_address:
            logger.error("No se encontró el mint del token")
            return None
        helius_api_key = os.getenv('HELIUS_API_KEY')
        if not helius_api_key:
            logger.error("HELIUS_API_KEY no está definida en el entorno")
            return None
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={helius_api_key}"
        payload = {"mintAccounts": [mint_address]}
        headers = {"Content-Type": "application/json"}
        logger.info(f"Llamando a la API de Helius para obtener metadatos del token {mint_address}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        token_data = response.json()[0]
        if 'onChainMetadata' in token_data and 'metadata' in token_data['onChainMetadata']:
            metadata = token_data['onChainMetadata']['metadata']
            if 'data' in metadata and 'uri' in metadata['data']:
                ipfs_url = metadata['data']['uri']
                logger.info(f"URI de IPFS encontrada: {ipfs_url}")
                metadata = extract_token_metadata_from_ipfs(ipfs_url, mint_address)
                if not metadata:
                    logger.error(f"No se pudieron extraer los metadatos de IPFS para el token {mint_address}")
                    return None
                logger.info(f"Metadatos del token extraídos exitosamente para {mint_address}")
                return metadata
            else:
                logger.error(f"No se encontró la URI en los metadatos del token {mint_address}")
                return None
        else:
            logger.error(f"No se encontraron metadatos en la respuesta de Helius para el token {mint_address}")
            return None
    except Exception as e:
        logger.error(f"Error al extraer metadatos del token: {str(e)}")
        return None

def format_compact_number(n):
    if n is None:
        return "?"
    if isinstance(n, str):
        return n
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return str(n)

def format_telegram_message(token_metadata: Dict[str, Any], notable_data: Dict[str, Any], wallet_identifier: str = None) -> str:
    total_notables = notable_data.get('total', 0) if notable_data else 0
    top_notables = notable_data.get('top', []) if notable_data else []
    name = token_metadata['name']
    symbol = token_metadata['symbol']
    ca = token_metadata['address']
    twitter = token_metadata['twitter'] if token_metadata['twitter'] else 'Not available'
    creator_link = f'<a href="https://twitter.com/{twitter}">@{twitter}</a>' if twitter != 'Not available' else twitter
    token_link = f'<a href="https://solscan.io/token/{ca}">${symbol}</a>'
    bots_links = [
        ("AXIOM", f"https://axiom.trade/t/{ca}/@notable"),
        ("MAESTRO", f"https://t.me/maestro?start={ca}-sittingbulll"),
        ("TROJAN", f"https://t.me/nestor_trojanbot?start=r-sittingbulll-{ca}"),
        ("BONK", f"https://t.me/bonkbot_bot?start=ref_g8ra9_ca_{ca}"),
        ("PHOTON", f"https://photon-sol.tinyastro.io/en/r/@notable/{ca}")
    ]
    bots_line = " | ".join([f"<a href='{url}'>{name}</a>" for name, url in bots_links])
    
    # Añadir el identificador de la wallet al título si está disponible
    title = f"New {wallet_identifier} Token Detected!" if wallet_identifier else "New Token Detected!"
    
    message = (
        f"<b>{title}</b>\n\n"
        f"<b>Name</b>: {name} ({token_link})\n"
        f"<b>CA</b>: {ca}\n\n"
        f"<b>Creator</b>: {creator_link}\n"
        f"<b>Notable Followers</b>: {total_notables}\n"
        f"<b>Top 5 Notables</b>:\n"
    )
    for i, notable in enumerate(top_notables, 1):
        username = notable['username']
        followers = notable['followersCount']
        followers_str = format_compact_number(followers)
        notable_link = f'<a href="https://twitter.com/{username}">@{username}</a>'
        message += f"– {i}. {notable_link} ({followers_str} followers)\n"
    message += f"\n💰 <b>Trade on:</b>\n{bots_line}\n"
    return message

def load_protokols_cookies() -> Dict:
    try:
        with open('protokols_cookies.json', 'r') as f:
            cookies_data = json.load(f)
        cookies_dict = {}
        for cookie in cookies_data:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict
    except Exception as e:
        logger.error(f"Error al cargar las cookies de Protokols: {str(e)}")
        return {}

def process_webhook(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        # Verificar si es una creación de token y si nuestra wallet es el Payer
        if not webhook_data or not isinstance(webhook_data, list) or len(webhook_data) == 0:
            logger.error("Webhook vacío o formato inválido")
            return None
            
        tx = webhook_data[0]
        fee_payer = tx.get('feePayer')
        
        # Verificar si el feePayer está en nuestra lista de wallets conocidas
        wallet_identifier = KNOWN_WALLETS.get(fee_payer)
        if not wallet_identifier:
            logger.info(f"Token ignorado: feePayer {fee_payer} no está en la lista de wallets conocidas")
            return None
        
        # Verificar si es una creación de token (mint)
        token_transfers = tx.get('tokenTransfers', [])
        if token_transfers and token_transfers[0].get('mint') == token_transfers[0].get('toTokenAccount'):
            # Si es una creación, verificar si nuestra wallet es el Payer
            if fee_payer in KNOWN_WALLETS:
                logger.info(f"Token ignorado: creación fraudulenta detectada (nuestra wallet es el Payer)")
                return None
        
        token_metadata = extract_token_metadata(webhook_data)
        if not token_metadata:
            return None
            
        notable_data = None
        if token_metadata['twitter']:
            logger.info(f"Obteniendo notables para @{token_metadata['twitter']}")
            cookies = load_protokols_cookies()
            if not cookies:
                logger.error("No se pudieron cargar las cookies de Protokols")
                return None
            notable_data = get_notables(token_metadata['twitter'], cookies)
            logger.info(f"Datos de notables obtenidos: {json.dumps(notable_data, indent=2)}")
            if notable_data:
                total_notables = notable_data.get('total', 0)
                logger.info(f"Total de notables encontrados: {total_notables}")
                if total_notables < 5:
                    logger.info("Token ignorado: el creador tiene menos de 5 notables.")
                    return None
                if not notable_data.get('top', []):
                    logger.warning("La lista de top notables está vacía")
        logger.info(f"Procesamiento completado para token {token_metadata['address']}")
        telegram_message = format_telegram_message(token_metadata, notable_data, wallet_identifier)
        return {
            "token_metadata": token_metadata,
            "notable_data": notable_data,
            "telegram_message": telegram_message
        }
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return None

def send_telegram_message(message: str, image_url: str = None) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    if not token or not channel_id:
        logger.error("TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID no están definidos en el entorno.")
        return False
    if not str(channel_id).startswith('-100'):
        channel_id = f"-100{str(channel_id).lstrip('-')}"
        logger.info(f"Channel ID ajustado: {channel_id}")
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                'chat_id': channel_id,
                'photo': image_url,
                'caption': message,
                'parse_mode': 'HTML'
            }
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                'chat_id': channel_id,
                'text': message,
                'parse_mode': 'HTML'
            }
        response = requests.post(url, data=payload, timeout=TIMEOUT)
        response.raise_for_status()
        logger.info(f"Respuesta Telegram: {response.status_code} {response.text}")
        logger.info("Mensaje enviado a Telegram correctamente.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar mensaje a Telegram: {str(e)}")
        return False

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "healthy"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"Webhook recibido: {json.dumps(data)[:500]}...")
        result = process_webhook(data)
        if result and result.get('telegram_message'):
            success = send_telegram_message(result['telegram_message'], result['token_metadata'].get('image'))
            if success:
                logger.info("Notificación enviada exitosamente a Telegram")
            else:
                logger.error("Error al enviar la notificación a Telegram")
        else:
            logger.error("No se pudo generar el mensaje para Telegram")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# El objeto app queda en el scope global para Gunicorn

if __name__ == "__main__":
    # Start the webhook server
    print("Iniciando servidor webhook...")
    print("URLs disponibles:")
    print("- http://127.0.0.1:3003/webhook")
    print("- http://10.2.0.2:3003/webhook")
    print("\nEsperando notificaciones...\n")
    
    # Configurar el servidor para que use threading
    app.run(host='0.0.0.0', port=3003, debug=False, threaded=True) 