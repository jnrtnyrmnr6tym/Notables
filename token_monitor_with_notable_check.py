#!/usr/bin/env python3
"""
Script integrado para monitorear tokens y verificar notable followers.

Este script:
1. Recibe notificaciones de webhook de Helius sobre nuevos tokens
2. Extrae la información del creador de Twitter del token
3. Verifica si el creador tiene suficientes notable followers
4. Exporta la dirección del contrato si cumple los criterios
"""

import requests
import json
import sys
import argparse
import time
import base64
import re
from pathlib import Path
from flask import Flask, request, jsonify
import threading
import logging
import urllib.parse
import os
from protokols_session_manager import ProtokolsSessionManager
import traceback
from dotenv import load_dotenv
from datetime import datetime
from archive.extract_token_creator import try_decode_metaplex_data
from protokols_smart_followers_fast import get_notables

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Configuración
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
HELIUS_API_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
PROTOKOLS_API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
REQUIRED_NOTABLE_COUNT = 5  # Número mínimo de notable followers requeridos
OUTPUT_FILE = "approved_tokens.json"
LOG_FILE = "token_monitor.log"
COOKIES_FILE = "protokols_cookies.json"  # Archivo con las cookies para autenticación

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar a DEBUG para incluir información de depuración
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurar el handler de consola para Windows
if sys.platform == 'win32':
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setStream(sys.stdout)

# Caché para reducir consultas a APIs externas
token_metadata_cache = {}
ipfs_content_cache = {}
notable_followers_cache = {}

def get_approved_tokens():
    """
    Get the list of approved tokens from the output file.
    
    Returns:
        list: List of approved tokens or empty list if no tokens are found
    """
    try:
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Approved tokens file {OUTPUT_FILE} not found")
            return []
    except Exception as e:
        logger.error(f"Error loading approved tokens: {e}")
        return []

def get_token_metadata(token_address):
    """Obtiene los metadatos de un token usando la API de Helius."""
    # Verificar si está en caché
    if token_address in token_metadata_cache:
        logger.debug(f"Usando metadatos en caché para el token {token_address}")
        return token_metadata_cache[token_address]
    
    url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={HELIUS_API_KEY}&mint={token_address}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        
        # Guardar en caché
        token_metadata_cache[token_address] = result
        
        # Extraer información relevante
        name = result.get("onChainData", {}).get("name", "Unknown")
        symbol = result.get("onChainData", {}).get("symbol", "UNKNOWN")
        description = result.get("offChainData", {}).get("description", "")
        image = result.get("offChainData", {}).get("image")
        
        # Extraer Twitter username
        twitter_username = None
        if "offChainData" in result:
            if "twitter" in result["offChainData"]:
                twitter_username = result["offChainData"]["twitter"]
            elif "twitter_username" in result["offChainData"]:
                twitter_username = result["offChainData"]["twitter_username"]
        
        # Imprimir información del token
        print("\n==================================================")
        print("🪙 Token Information")
        print(f"👤 Creator: @{twitter_username if twitter_username else 'None'}")
        print(f"📝 Name: {name}")
        print(f"🔤 Ticker: {symbol}")
        print(f"🔗 Contract: {token_address}")
        print("==================================================\n")
        
        return {
            "token_address": token_address,
            "name": name,
            "symbol": symbol,
            "description": description,
            "image": image,
            "twitter_username": twitter_username
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener metadatos del token: {e}")
        return None

def extract_ipfs_uri(metadata):
    """Extrae la URI de IPFS de los metadatos del token."""
    if not metadata:
        return None
    
    # Intentar diferentes rutas para encontrar la URI
    if "onChainData" in metadata and "uri" in metadata["onChainData"]:
        return metadata["onChainData"]["uri"]
    elif "offChainData" in metadata and "uri" in metadata["offChainData"]:
        return metadata["offChainData"]["uri"]
    elif "metadata" in metadata and "uri" in metadata["metadata"]:
        return metadata["metadata"]["uri"]
    
    logger.warning("No se pudo encontrar la URI en los metadatos")
    return None

def get_ipfs_content(ipfs_uri):
    """Obtiene el contenido de una URI de IPFS."""
    # Verificar si está en caché
    if ipfs_uri in ipfs_content_cache:
        logger.debug(f"Usando contenido IPFS en caché para {ipfs_uri}")
        return ipfs_content_cache[ipfs_uri]
    
    # Convertir ipfs:// a https://ipfs.io/ipfs/
    if ipfs_uri.startswith("ipfs://"):
        ipfs_uri = "https://ipfs.io/ipfs/" + ipfs_uri[7:]
    
    # Convertir ar:// a https://arweave.net/
    elif ipfs_uri.startswith("ar://"):
        ipfs_uri = "https://arweave.net/" + ipfs_uri[5:]
    
    try:
        response = requests.get(ipfs_uri, timeout=30)
        response.raise_for_status()
        content = response.json()
        
        # Guardar en caché
        ipfs_content_cache[ipfs_uri] = content
        
        return content
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener contenido de IPFS: {e}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error al decodificar JSON de IPFS: {ipfs_uri}")
        return None

def extract_twitter_username(ipfs_content):
    """Extrae el nombre de usuario de Twitter del contenido de IPFS."""
    if not ipfs_content:
        return None
    
    # Caso especial para los metadatos simulados
    if "twitter_username" in ipfs_content and isinstance(ipfs_content["twitter_username"], str):
        return ipfs_content["twitter_username"]
    
    # Buscar en diferentes campos comunes
    if "properties" in ipfs_content and "twitter_username" in ipfs_content["properties"]:
        return ipfs_content["properties"]["twitter_username"]
    elif "properties" in ipfs_content and "twitter" in ipfs_content["properties"]:
        return ipfs_content["properties"]["twitter"]
    elif "twitter_username" in ipfs_content:
        return ipfs_content["twitter_username"]
    elif "twitter" in ipfs_content:
        return ipfs_content["twitter"]
    # Buscar en metadata.tweetCreatorUsername (formato de Launchcoin)
    elif "metadata" in ipfs_content and "tweetCreatorUsername" in ipfs_content["metadata"]:
        return ipfs_content["metadata"]["tweetCreatorUsername"]
    elif "external_url" in ipfs_content and "twitter.com" in ipfs_content["external_url"]:
        # Extraer username de URL de Twitter
        url = ipfs_content["external_url"]
        parts = url.split("twitter.com/")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
            return username
    
    # Buscar en la descripción por menciones de Twitter (@username)
    if "description" in ipfs_content and "@" in ipfs_content["description"]:
        import re
        mentions = re.findall(r'@([A-Za-z0-9_]+)', ipfs_content["description"])
        if mentions and mentions[0] != "launchcoin":  # Ignorar @launchcoin
            return mentions[0]
    
    # Buscar en cualquier campo que contenga "twitter"
    for key, value in ipfs_content.items():
        if isinstance(value, str) and "twitter.com" in value:
            parts = value.split("twitter.com/")
            if len(parts) > 1:
                username = parts[1].split("/")[0].split("?")[0]
                return username
    
    logger.warning("No se pudo encontrar el nombre de usuario de Twitter en el contenido")
    return None

def process_token(token_address):
    """Procesa un token para verificar si cumple con los criterios usando el script rápido de notables."""
    logger.info(f"Procesando token: {token_address}")
    
    # Obtener metadatos del token
    metadata = get_token_metadata(token_address)
    if not metadata:
        logger.error(f"No se pudieron obtener metadatos para el token: {token_address}")
        return None
    
    # Extraer URI de IPFS
    ipfs_uri = extract_ipfs_uri(metadata)
    if not ipfs_uri:
        logger.error(f"No se pudo encontrar la URI de IPFS para el token: {token_address}")
        return None
    
    logger.info(f"URI de IPFS encontrada: {ipfs_uri}")
    
    # Obtener contenido de IPFS
    ipfs_content = get_ipfs_content(ipfs_uri)
    if not ipfs_content:
        logger.error(f"No se pudo obtener el contenido de IPFS para el token: {token_address}")
        return None
    
    # Extraer nombre de usuario de Twitter
    twitter_username = extract_twitter_username(ipfs_content)
    if not twitter_username:
        logger.error(f"No se pudo encontrar el nombre de usuario de Twitter para el token: {token_address}")
        return None
    
    logger.info(f"Nombre de usuario de Twitter encontrado: {twitter_username}")
    
    # Obtener notables usando el script rápido
    try:
        notables_data = get_notables(twitter_username, top_n=5)
        notable_count = notables_data.get('total', 0)
        top_notables = notables_data.get('top', [])
    except Exception as e:
        logger.error(f"Error obteniendo notables: {str(e)}")
        notable_count = 0
        top_notables = []
    logger.info(f"Número de notable followers para {twitter_username}: {notable_count}")
    
    # Extraer información adicional del token
    name = ipfs_content.get('name', 'Unknown')
    symbol = ipfs_content.get('symbol', 'UNKNOWN')
    description = ipfs_content.get('description', '')
    
    # Extraer imagen del token
    image = None
    if 'image' in ipfs_content:
        image = ipfs_content['image']
    elif 'properties' in ipfs_content and 'image' in ipfs_content['properties']:
        image = ipfs_content['properties']['image']
    
    # Crear resultado completo
    result = {
        "token_address": token_address,
        "name": name,
        "symbol": symbol,
        "description": description,
        "image": image,
        "twitter_username": twitter_username,
        "notable_followers_count": notable_count,
        "top_notables": top_notables,
        "approved": notable_count >= REQUIRED_NOTABLE_COUNT,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Guardar en tokens aprobados si cumple los criterios
    if result["approved"]:
        save_approved_token(result)
    
    return result

def save_approved_token(token_data):
    """Guarda un token aprobado en el archivo de salida."""
    try:
        # Cargar tokens existentes
        existing_tokens = []
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_tokens = []
        
        # Verificar si el token ya existe
        for token in existing_tokens:
            if token["token_address"] == token_data["token_address"]:
                logger.info(f"El token {token_data['token_address']} ya está en la lista de aprobados")
                return
        
        # Agregar el nuevo token
        existing_tokens.append(token_data)
        
        # Guardar la lista actualizada
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(existing_tokens, f, indent=2)
        
        logger.info(f"Token {token_data['token_address']} guardado en {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Error al guardar token aprobado: {e}")

def notify_new_approved_token(token_data):
    """
    Notifica a los bots suscritos sobre un nuevo token aprobado.
    Esta función se llama cuando se aprueba un nuevo token.
    Los bots pueden implementar su propia lógica para recibir estas notificaciones.
    """
    # Por ahora, simplemente registramos el evento
    logger.info(f"Notificando sobre nuevo token aprobado: {token_data['token_address']}")
    
    # En el futuro, aquí se podría implementar un sistema de notificaciones
    # para enviar alertas a diferentes canales (Telegram, Discord, etc.)

def process_webhook_notification(notification_data):
    """Procesa una notificación de webhook para extraer la información del token."""
    try:
        # Extraer dirección del token
        token_address = None
        if "tokenTransfers" in notification_data and notification_data["tokenTransfers"]:
            token_address = notification_data["tokenTransfers"][0].get("mint")
            logger.debug(f"Dirección del token encontrada: {token_address}")
        
        if not token_address:
            logger.error("No se pudo encontrar la dirección del token")
            return None
        
        # Extraer información del token directamente del webhook
        name = notification_data.get("tokenTransfers", [{}])[0].get("tokenName", "Unknown")
        symbol = notification_data.get("tokenTransfers", [{}])[0].get("tokenSymbol", "UNKNOWN")
        
        # Si es un Wrapped SOL, usar valores específicos
        if "Wrapped SOL" in notification_data.get("description", ""):
            name = "Wrapped SOL"
            symbol = "WSOL"
            description = "Wrapped SOL token"
            twitter_username = None
            image = None
        else:
            # Intentar obtener metadatos del token
            description = ""
            twitter_username = None
            image = None
            
            # Buscar en las instrucciones de Metaplex
            if "instructions" in notification_data:
                for instruction in notification_data["instructions"]:
                    if "innerInstructions" in instruction:
                        for inner_instruction in instruction["innerInstructions"]:
                            if inner_instruction.get("programId") == "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s":
                                if "data" in inner_instruction:
                                    metadata = try_decode_metaplex_data(inner_instruction['data'])
                                    if metadata and "uri" in metadata:
                                        ipfs_content = get_ipfs_content(metadata["uri"])
                                        if ipfs_content:
                                            description = ipfs_content.get("description", "")
                                            twitter_username = extract_twitter_username(ipfs_content)
                                            image = ipfs_content.get("image")
        
        # Crear resultado inicial sin datos de notables
        result = {
            "token_address": token_address,
            "name": name,
            "symbol": symbol,
            "description": description,
            "image": image,
            "twitter_username": twitter_username,
            "notable_followers_count": 0,  # Se actualizará con Protokols
            "top_notables": []  # Se actualizará con Protokols
        }
        
        # Si tenemos Twitter username, obtener notables de Protokols
        if twitter_username:
            try:
                notables_data = get_notables(twitter_username, top_n=5)
                result["notable_followers_count"] = notables_data.get('total', 0)
                result["top_notables"] = notables_data.get('top', [])
            except Exception as e:
                logger.error(f"Error obteniendo notables de Protokols: {str(e)}")
        
        # Imprimir información del token
        print("\n==================================================")
        print("🪙 New Token Detected!")
        if image:
            print(f"🖼 Image: {image}")
        print(f"📝 Name: {name}")
        print(f"🔤 Ticker: {symbol}")
        print(f"🔗 Contract: {token_address}")
        print(f"👤 Creator: @{twitter_username if twitter_username else 'None'}")
        print(f"⭐ Notable Followers: {result['notable_followers_count']}")
        if result['top_notables']:
            print("\nTop 5 Notable Followers:")
            for notable in result['top_notables']:
                followers = notable.get('followersCount', 0)
                if followers >= 1_000_000:
                    followers_str = f"{followers/1_000_000:.1f}M"
                elif followers >= 1_000:
                    followers_str = f"{followers/1_000:.1f}K"
                else:
                    followers_str = str(followers)
                print(f"- @{notable['username']} ({followers_str} followers)")
        print("==================================================\n")
        
        return result
    except Exception as e:
        logger.error(f"Error procesando notificación: {str(e)}")
        return None

# Crear la aplicación Flask para el servidor webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Manejador de webhook para recibir notificaciones de Helius."""
    try:
        notification = request.json
        logger.info(f"Notificación recibida: {json.dumps(notification)[:100]}...")
        
        # Procesar la notificación en un hilo separado para no bloquear la respuesta
        threading.Thread(target=process_webhook_notification, args=(notification,)).start()
        
        return jsonify({"status": "success", "message": "Notificación recibida y en procesamiento"}), 200
    except Exception as e:
        logger.error(f"Error al procesar notificación de webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Añadir rutas adicionales para API y dashboard
@app.route('/', methods=['GET'])
def home():
    """Página de inicio."""
    return jsonify({
        "status": "running",
        "description": "Sistema de monitoreo de tokens en Solana",
        "endpoints": {
            "/webhook": "Recibe notificaciones de Helius",
            "/status": "Muestra el estado del sistema",
            "/api/tokens": "Lista todos los tokens aprobados",
            "/api/token/<address>": "Muestra información de un token específico",
            "/api/stats": "Muestra estadísticas del sistema"
        }
    })

@app.route('/status', methods=['GET'])
def status():
    """Muestra el estado del sistema."""
    try:
        # Contar tokens aprobados
        approved_tokens = []
        try:
            with open(OUTPUT_FILE, 'r') as f:
                approved_tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            approved_tokens = []
        
        # Tamaños de caché
        cache_sizes = {
            "token_metadata_cache": len(token_metadata_cache),
            "ipfs_content_cache": len(ipfs_content_cache),
            "notable_followers_cache": len(notable_followers_cache)
        }
        
        return jsonify({
            "status": "running",
            "approved_tokens_count": len(approved_tokens),
            "cache_sizes": cache_sizes,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        })
    except Exception as e:
        logger.error(f"Error al obtener estado del sistema: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tokens', methods=['GET'])
def api_tokens():
    """Lista todos los tokens aprobados."""
    try:
        # Leer tokens aprobados
        approved_tokens = []
        try:
            with open(OUTPUT_FILE, 'r') as f:
                approved_tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            approved_tokens = []
        
        # Parámetros de filtrado
        min_notable_followers = request.args.get('min_notable_followers', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Aplicar filtros
        if min_notable_followers is not None:
            approved_tokens = [t for t in approved_tokens if t.get('notable_followers_count', 0) >= min_notable_followers]
        
        # Ordenar por timestamp (más reciente primero)
        approved_tokens.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limitar resultados
        approved_tokens = approved_tokens[:limit]
        
        return jsonify({
            "status": "success",
            "count": len(approved_tokens),
            "tokens": approved_tokens
        })
    except Exception as e:
        logger.error(f"Error al obtener tokens aprobados: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/token/<address>', methods=['GET'])
def api_token(address):
    """Muestra información de un token específico."""
    try:
        # Buscar en tokens aprobados
        try:
            with open(OUTPUT_FILE, 'r') as f:
                approved_tokens = json.load(f)
                
                for token in approved_tokens:
                    if token.get('token_address') == address:
                        return jsonify({
                            "status": "success",
                            "token": token
                        })
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Si no se encuentra en tokens aprobados, intentar procesarlo
        token_info = process_token(address)
        
        if token_info:
            return jsonify({
                "status": "success",
                "token": token_info
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"No se pudo encontrar información para el token {address}"
            }), 404
    except Exception as e:
        logger.error(f"Error al obtener información del token {address}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Muestra estadísticas del sistema."""
    try:
        # Leer tokens aprobados
        approved_tokens = []
        try:
            with open(OUTPUT_FILE, 'r') as f:
                approved_tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            approved_tokens = []
        
        # Calcular estadísticas
        total_tokens = len(approved_tokens)
        
        # Distribución de notable followers
        notable_followers_distribution = {}
        for token in approved_tokens:
            notable_count = token.get('notable_followers_count', 0)
            if notable_count in notable_followers_distribution:
                notable_followers_distribution[notable_count] += 1
            else:
                notable_followers_distribution[notable_count] = 1
        
        # Top creadores por notable followers
        creators = {}
        for token in approved_tokens:
            username = token.get('twitter_username')
            notable_count = token.get('notable_followers_count', 0)
            if username:
                creators[username] = notable_count
        
        top_creators = sorted(creators.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_tokens": total_tokens,
                "notable_followers_distribution": notable_followers_distribution,
                "top_creators": top_creators,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
        })
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del sistema: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def test_cookies():
    """Prueba las cookies actuales para verificar si son válidas."""
    logger.info("Probando cookies de autenticación...")
    try:
        session_manager = ProtokolsSessionManager()
        if not session_manager.load_cookies():
            logger.error("No se pudieron cargar las cookies.")
            return False
        cookies = session_manager.get_cookies_dict()
        logger.info(f"Cookies cargadas: {len(cookies)}")
        # Probar con un usuario conocido (jack)
        test_username = "jack"
        params = {"json": {"username": test_username}}
        input_json = json.dumps(params)
        encoded_input = requests.utils.quote(input_json)
        url = f"{PROTOKOLS_API_URL}?input={encoded_input}"
        headers = session_manager.get_session_headers()
        headers["Referer"] = f"https://www.protokols.io/twitter/{test_username}"
        logger.info(f"Enviando solicitud a {url}")
        response = requests.get(url, headers=headers, cookies=cookies)
        logger.info(f"Código de respuesta: {response.status_code}")
        logger.info(f"Contenido de la respuesta (texto): {response.text[:1000]}")
        try:
            resp_json = response.json()
            logger.info(f"Respuesta JSON completa: {json.dumps(resp_json, indent=2)[:1000]}")
        except Exception as e:
            logger.error(f"No se pudo decodificar la respuesta como JSON: {e}")
            logger.error(f"Contenido de la respuesta: {response.text[:1000]}")
        if response.status_code == 200:
            logger.info("Cookies are valid.")
        else:
            logger.error(f"Invalid cookies. Status code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error inesperado en test_cookies: {e}")
        logger.error(traceback.format_exc())
        return False

def try_decode_metaplex_data(data_str):
    """
    Intenta decodificar los datos de la instrucción de Metaplex.
    Primero intenta decodificar base64 con padding, luego busca URIs directamente.
    """
    try:
        logger.debug(f"Intentando decodificar datos de Metaplex: {data_str[:50]}... (len={len(data_str)})")
        
        # 1. Intentar extraer URI directamente del string de datos
        ipfs_pattern = r'ipfs://[a-zA-Z0-9]+'
        arweave_pattern = r'https://arweave.net/[a-zA-Z0-9]+'
        
        ipfs_matches = re.findall(ipfs_pattern, data_str)
        arweave_matches = re.findall(arweave_pattern, data_str)
        
        if ipfs_matches:
            logger.info(f"URI IPFS encontrada directamente: {ipfs_matches[0]}")
            return {"uri": ipfs_matches[0]}
        if arweave_matches:
            logger.info(f"URI Arweave encontrada directamente: {arweave_matches[0]}")
            return {"uri": arweave_matches[0]}
        
        # 2. Intentar decodificar base64 con padding
        try:
            padding = len(data_str) % 4
            if padding:
                data_str = data_str + ('=' * (4 - padding))
            decoded = base64.b64decode(data_str)
            logger.debug(f"Datos decodificados (hex, primeros 64 bytes): {decoded[:64].hex()} (len={len(decoded)})")
            # También mostrar como string ignorando errores
            logger.debug(f"Datos decodificados (utf-8, ignorando errores): {decoded[:128].decode('utf-8', errors='ignore')}")
            # Buscar URIs en los datos decodificados
            decoded_str = decoded.decode('utf-8', errors='ignore')
            ipfs_matches = re.findall(ipfs_pattern, decoded_str)
            arweave_matches = re.findall(arweave_pattern, decoded_str)
            if ipfs_matches:
                logger.info(f"URI IPFS encontrada en datos decodificados: {ipfs_matches[0]}")
                return {"uri": ipfs_matches[0]}
            if arweave_matches:
                logger.info(f"URI Arweave encontrada en datos decodificados: {arweave_matches[0]}")
                return {"uri": arweave_matches[0]}
            # Si no encontramos URIs, intentar decodificar como JSON
            try:
                metadata = json.loads(decoded_str)
                if isinstance(metadata, dict):
                    logger.info("Metadatos decodificados exitosamente")
                    return metadata
            except json.JSONDecodeError:
                logger.debug("Los datos decodificados no son JSON válido")
        except Exception as e:
            logger.debug(f"Error decodificando base64: {str(e)}")
        
        # 3. Si llegamos aquí, es probable que sea un Wrapped SOL
        logger.info("No se encontró URI en los datos de Metaplex - probablemente es un Wrapped SOL")
        return {"is_wrapped_sol": True}
    except Exception as e:
        logger.error(f"Error procesando datos de Metaplex: {str(e)}")
        return None

def extract_token_metadata(webhook_data):
    try:
        # Extraer la dirección del token
        token_address = webhook_data.get('tokenTransfers', [{}])[0].get('mint')
        if not token_address:
            logger.error("No se pudo encontrar la dirección del token en el webhook")
            return None

        logger.info(f"Obteniendo metadatos para token: {token_address}")
        
        # Llamar a la API de Helius para obtener metadatos
        url = f"https://api.helius.xyz/v0/tokens/metadata?api-key={HELIUS_API_KEY}"
        data = {
            "mintAccounts": [token_address]
        }
        
        logger.info(f"Llamando a Helius API: {url}")
        response = requests.post(url, json=data)
        
        if response.status_code != 200:
            logger.error(f"Error al obtener metadatos de Helius: {response.status_code} - {response.text}")
            return None
            
        metadata = response.json()
        logger.info(f"Metadatos recibidos de Helius: {metadata}")
        
        if not metadata or not metadata[0]:
            logger.error("No se encontraron metadatos para el token")
            return None
            
        return metadata[0]
        
    except Exception as e:
        logger.error(f"Error al extraer metadatos: {str(e)}")
        return None

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Monitor de tokens con verificación de notable followers")
    parser.add_argument("--token", type=str, required=True, help="Dirección del token a consultar")
    args = parser.parse_args()
    
    # Obtener metadatos del token
    token_info = get_token_metadata(args.token)
    if not token_info:
        logger.error(f"No se pudieron obtener metadatos para el token {args.token}")
        return
    
    # Si tenemos Twitter username, obtener notables
    if token_info["twitter_username"]:
        try:
            notables_data = get_notables(token_info["twitter_username"], top_n=5)
            notable_count = notables_data.get('total', 0)
            top_notables = notables_data.get('top', [])
            
            print(f"⭐ Notable Followers: {notable_count}")
            if top_notables:
                print("\nTop Notable Followers:")
                for notable in top_notables:
                    print(f"- @{notable['username']}")
        except Exception as e:
            logger.error(f"Error obteniendo notables: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 