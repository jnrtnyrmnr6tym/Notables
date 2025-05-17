#!/usr/bin/env python3
"""
Script para probar la obtención de metadatos de tokens desde Helius y Protokols.
Flujo completo: IPFS -> Twitter -> Protokols -> Telegram
"""

import json
import requests
import logging
import os
from typing import Dict, Optional, Any, List, Tuple
from datetime import datetime
from protokols_smart_followers_fast import get_notables  # Importamos la función existente
from dotenv import load_dotenv
import time
import sys

# Cargar variables de entorno desde .env automáticamente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webhook_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuración
HELIUS_API_KEY = "133cc99a-6f02-4783-9ada-c013a79343a6"
TIMEOUT = 5  # segundos - timeout corto para ser más rápido

def extract_token_metadata_from_ipfs(ipfs_url: str, mint_address: str) -> Optional[Dict[str, Any]]:
    """
    Descarga y extrae los metadatos relevantes desde un JSON de IPFS.
    """
    try:
        logger.info(f"Descargando metadatos desde IPFS: {ipfs_url}")
        response = requests.get(ipfs_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraer campos relevantes
        name = data.get('name')
        symbol = data.get('symbol')
        image = data.get('image')
        twitter = None
        
        # Buscar el username de Twitter en los metadatos
        if 'metadata' in data and data['metadata']:
            twitter = data['metadata'].get('tweetCreatorUsername')
        
        # Verificar campos requeridos
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
    """
    Extrae el mint del token desde el webhook de Helius.
    """
    try:
        # Verificar que tenemos datos de token
        if not webhook_data or not isinstance(webhook_data, list) or len(webhook_data) == 0:
            logger.error("Webhook vacío o formato inválido")
            return None

        # Obtener la primera transacción
        tx = webhook_data[0]
        
        # Extraer el mint del token
        token_transfers = tx.get('tokenTransfers', [])
        if not token_transfers:
            logger.error("No se encontraron transferencias de token")
            return None

        mint_address = token_transfers[0].get('mint')
        if not mint_address:
            logger.error("No se encontró el mint del token")
            return None

        # Llamar a Helius para obtener la URL de IPFS
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={HELIUS_API_KEY}"
        payload = {"mintAccounts": [mint_address]}
        headers = {"Content-Type": "application/json"}
        
        logger.info(f"Llamando a la API de Helius para obtener metadatos del token {mint_address}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        token_data = response.json()[0]
        
        # Obtener la URI de IPFS desde la ubicación correcta
        if 'onChainMetadata' in token_data and 'metadata' in token_data['onChainMetadata']:
            metadata = token_data['onChainMetadata']['metadata']
            if 'data' in metadata and 'uri' in metadata['data']:
                ipfs_url = metadata['data']['uri']
                logger.info(f"URI de IPFS encontrada: {ipfs_url}")
                
                # Descargar y extraer los metadatos reales desde IPFS
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

def format_followers_count(count: int) -> str:
    """
    Formatea el número de seguidores usando K para miles y M para millones.
    Ejemplo: 659728 -> 659.7K, 1500000 -> 1.5M
    """
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M".replace(".0M", "M")
    elif count >= 1_000:
        return f"{count/1_000:.1f}K".replace(".0K", "K")
    return str(count)

def format_telegram_message(token_metadata: Dict[str, Any], notable_data: Dict[str, Any]) -> str:
    """
    Formatea el mensaje para enviar a Telegram con epígrafes en negrita usando HTML.
    Los nombres de usuario de Twitter son enlaces clickeables.
    El ticker del token es un enlace a Solscan.
    Incluye enlaces a bots de trading en el formato y orden especificado.
    """
    total_notables = notable_data.get('total', 0)
    top_notables = notable_data.get('top', [])
    name = token_metadata['name']
    symbol = token_metadata['symbol']
    ca = token_metadata['address']
    twitter = token_metadata['twitter'] if token_metadata['twitter'] else 'Not available'
    
    # Crear enlace para el creador
    creator_link = f'<a href="https://twitter.com/{twitter}">@{twitter}</a>' if twitter != 'Not available' else twitter
    
    # Crear enlace para el ticker del token
    token_link = f'<a href="https://solscan.io/token/{ca}">${symbol}</a>'
    
    # Enlaces de los bots en el orden especificado
    bots_links = [
        ("AXIOM", f"https://axiom.trade/t/{ca}/@notable"),
        ("MAESTRO", f"https://t.me/maestro?start={ca}-sittingbulll"),
        ("TROJAN", f"https://t.me/nestor_trojanbot?start=r-sittingbulll-{ca}"),
        ("BONK", f"https://t.me/bonkbot_bot?start=ref_g8ra9_ca_{ca}"),
        ("PHOTON", f"https://photon-sol.tinyastro.io/en/r/@notable/{ca}")
    ]
    bots_line = " | ".join([f"<a href='{url}'>{name}</a>" for name, url in bots_links])
    
    message = (
        f"<b>New Token Detected</b>\n\n"
        f"<b>Name</b>: {name} ({token_link})\n"
        f"<b>CA</b>: {ca}\n\n"
        f"<b>Creator</b>: {creator_link}\n"
        f"<b>Notable Followers</b>: {total_notables}\n"
        f"<b>Top 5 Notables</b>:\n"
    )
    
    # Añadir enlaces para cada notable
    for i, notable in enumerate(top_notables, 1):
        username = notable['username']
        followers = notable['followersCount']
        notable_link = f'<a href="https://twitter.com/{username}">@{username}</a>'
        formatted_followers = format_followers_count(followers)
        message += f"– {i}. {notable_link} ({formatted_followers} followers)\n"
    
    # Añadir sección de trading con formato de la imagen
    message += f"\n💰 <b>Trade on:</b>\n{bots_line}\n"
    
    return message

def process_webhook(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Procesa el webhook completo y obtiene toda la información necesaria.
    """
    try:
        # Paso 1: Extraer metadatos del token
        token_metadata = extract_token_metadata(webhook_data)
        
        if not token_metadata:
            logger.error("No se pudieron extraer metadatos del token")
            return None

        # Paso 2: Obtener notable followers si hay Twitter
        if token_metadata['twitter']:
            logger.info(f"Obteniendo notables para @{token_metadata['twitter']}")
            notable_data = get_notables(token_metadata['twitter'])
            logger.info(f"Datos de notables obtenidos: {json.dumps(notable_data, indent=2)}")
            
            if notable_data:
                # Verificar si hay top notables
                top_notables = notable_data.get('top', [])
                logger.info(f"Top notables encontrados: {len(top_notables)}")
                if top_notables:
                    logger.info(f"Detalles de top notables: {json.dumps(top_notables, indent=2)}")
                else:
                    logger.warning("La lista de top notables está vacía")
                
                # Paso 3: Formatear mensaje para Telegram
                telegram_message = format_telegram_message(token_metadata, notable_data)
                logger.info("Mensaje para Telegram generado exitosamente")
                return {
                    "token_metadata": token_metadata,
                    "notable_data": notable_data,
                    "telegram_message": telegram_message
                }
            else:
                logger.error("No se pudieron obtener datos de notables")

        logger.info(f"Procesamiento completado para token {token_metadata['address']}")
        return {
            "token_metadata": token_metadata,
            "notable_data": None,
            "telegram_message": None
        }

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return None

def send_telegram_message(message: str, image_url: str = None) -> bool:
    """
    Envía un mensaje al canal de Telegram. Si hay imagen, la envía junto con el texto como caption.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    logger.info(f"TELEGRAM_CHANNEL_ID: {channel_id}")
    logger.info(f"TELEGRAM_BOT_TOKEN: {token[:5]}...{token[-5:] if token else 'None'}")
    
    if not token or not channel_id:
        logger.error("TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID no están definidos en el entorno.")
        return False
    if not str(channel_id).startswith('-100'):
        channel_id = f"-100{str(channel_id).lstrip('-')}"
        logger.info(f"Channel ID ajustado: {channel_id}")
    success = True
    if image_url:
        url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload_photo = {
            'chat_id': channel_id,
            'photo': image_url,
            'caption': message,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(url_photo, data=payload_photo, timeout=10)
            logger.info(f"Respuesta Telegram sendPhoto: {response.status_code} {response.text}")
            print(f"Respuesta Telegram sendPhoto: {response.status_code} {response.text}")
            response.raise_for_status()
            logger.info("Imagen+mensaje enviados a Telegram correctamente.")
        except Exception as e:
            logger.error(f"Error al enviar imagen+mensaje a Telegram: {str(e)}")
            success = False
    else:
        url_msg = f"https://api.telegram.org/bot{token}/sendMessage"
        payload_msg = {
            'chat_id': channel_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(url_msg, data=payload_msg, timeout=10)
            logger.info(f"Respuesta Telegram sendMessage: {response.status_code} {response.text}")
            print(f"Respuesta Telegram sendMessage: {response.status_code} {response.text}")
            response.raise_for_status()
            logger.info("Mensaje enviado a Telegram correctamente.")
        except Exception as e:
            logger.error(f"Error al enviar mensaje a Telegram: {str(e)}")
            success = False
    return success

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # Leer el JSON de la entrada estándar
        webhook_data = json.loads(sys.stdin.read())
        
        # Procesar el webhook y enviar el mensaje a Telegram
        result = process_webhook(webhook_data)
        if result and result.get('telegram_message'):
            logger.info("Enviando mensaje a Telegram...")
            send_telegram_message(result['telegram_message'], result['token_metadata'].get('image'))
        else:
            logger.error("No se pudo generar el mensaje para Telegram")
            
    except json.JSONDecodeError:
        logger.error("Error: El JSON proporcionado no es válido")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}") 