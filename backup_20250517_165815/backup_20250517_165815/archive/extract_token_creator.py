#!/usr/bin/env python3
"""
Script para extraer información del creador de un token usando la API de Helius.

Este script:
1. Toma una dirección de token (mint address) como entrada
2. Consulta la API de Helius para obtener los metadatos del token
3. Extrae la URI de IPFS de los metadatos
4. Accede a la URI para obtener información del creador, incluyendo el nombre de usuario de Twitter
"""

import requests
import json
import sys
import argparse
from pathlib import Path
import time
import base64
import re

# Configuración
HELIUS_API_KEY = "133cc99a-6f02-4783-9ada-c013a79343a6"
HELIUS_API_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def get_token_metadata(token_address):
    """Obtiene los metadatos de un token usando la API de Helius."""
    payload = {
        "jsonrpc": "2.0",
        "id": "my-id",
        "method": "getAsset",
        "params": {
            "id": token_address
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(HELIUS_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener metadatos del token: {e}")
        return None

def extract_ipfs_uri(metadata):
    """Extrae la URI de IPFS de los metadatos del token."""
    if not metadata or "result" not in metadata:
        return None
    
    result = metadata["result"]
    
    # Intentar diferentes rutas para encontrar la URI
    if "content" in result and "json_uri" in result["content"]:
        return result["content"]["json_uri"]
    elif "content" in result and "metadata" in result["content"] and "uri" in result["content"]["metadata"]:
        return result["content"]["metadata"]["uri"]
    elif "data" in result and "uri" in result["data"]:
        return result["data"]["uri"]
    
    print("No se pudo encontrar la URI en los metadatos:")
    print(json.dumps(metadata, indent=2))
    return None

def get_ipfs_content(ipfs_uri):
    """Obtiene el contenido de una URI de IPFS."""
    # Convertir ipfs:// a https://ipfs.io/ipfs/
    if ipfs_uri.startswith("ipfs://"):
        ipfs_uri = "https://ipfs.io/ipfs/" + ipfs_uri[7:]
    
    # Convertir ar:// a https://arweave.net/
    elif ipfs_uri.startswith("ar://"):
        ipfs_uri = "https://arweave.net/" + ipfs_uri[5:]
    
    try:
        response = requests.get(ipfs_uri, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener contenido de IPFS: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON de IPFS: {ipfs_uri}")
        return None

def extract_twitter_username(ipfs_content):
    """Extrae el nombre de usuario de Twitter del contenido de IPFS."""
    if not ipfs_content:
        return None
    
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
    
    print("No se pudo encontrar el nombre de usuario de Twitter en el contenido:")
    print(json.dumps(ipfs_content, indent=2))
    return None

def process_token(token_address):
    """Procesa un token para extraer información del creador."""
    print(f"Procesando token: {token_address}")
    
    # Obtener metadatos del token
    metadata = get_token_metadata(token_address)
    if not metadata:
        print(f"No se pudieron obtener metadatos para el token: {token_address}")
        return None
    
    # Extraer URI de IPFS
    ipfs_uri = extract_ipfs_uri(metadata)
    if not ipfs_uri:
        print(f"No se pudo encontrar la URI de IPFS para el token: {token_address}")
        return None
    
    print(f"URI de IPFS encontrada: {ipfs_uri}")
    
    # Obtener contenido de IPFS
    ipfs_content = get_ipfs_content(ipfs_uri)
    if not ipfs_content:
        print(f"No se pudo obtener el contenido de IPFS para el token: {token_address}")
        return None
    
    # Extraer nombre de usuario de Twitter
    twitter_username = extract_twitter_username(ipfs_content)
    if not twitter_username:
        print(f"No se pudo encontrar el nombre de usuario de Twitter para el token: {token_address}")
    else:
        print(f"Nombre de usuario de Twitter encontrado: {twitter_username}")
    
    # Devolver los resultados
    return {
        "token_address": token_address,
        "ipfs_uri": ipfs_uri,
        "twitter_username": twitter_username,
        "metadata": metadata,
        "ipfs_content": ipfs_content
    }

def try_decode_metaplex_data(data_str):
    """Intenta decodificar los datos de la instrucción de Metaplex."""
    try:
        # Intentar extraer URI directamente del string de datos
        # Buscar patrones de URI de IPFS
        ipfs_pattern = r'ipfs://[a-zA-Z0-9]+'
        ipfs_matches = re.findall(ipfs_pattern, data_str)
        if ipfs_matches:
            return {"uri": ipfs_matches[0]}
        
        # Buscar patrones de URI de Arweave
        arweave_pattern = r'https://arweave.net/[a-zA-Z0-9]+'
        arweave_matches = re.findall(arweave_pattern, data_str)
        if arweave_matches:
            return {"uri": arweave_matches[0]}
        
        # Intentar decodificar como base64
        try:
            decoded = base64.b64decode(data_str)
            # Buscar cadenas que parezcan URIs en los bytes decodificados
            decoded_str = decoded.decode('utf-8', errors='ignore')
            ipfs_matches = re.findall(ipfs_pattern, decoded_str)
            if ipfs_matches:
                return {"uri": ipfs_matches[0]}
            
            arweave_matches = re.findall(arweave_pattern, decoded_str)
            if arweave_matches:
                return {"uri": arweave_matches[0]}
        except:
            pass
        
        print("No se pudo decodificar los datos de la instrucción de Metaplex")
        return None
    except Exception as e:
        print(f"Error al intentar decodificar datos de Metaplex: {e}")
        return None

def process_webhook_notification(notification_data):
    """Procesa una notificación de webhook para extraer la dirección del token."""
    if isinstance(notification_data, str):
        try:
            notification_data = json.loads(notification_data)
        except json.JSONDecodeError:
            print("Error: La notificación no es un JSON válido")
            return None
    
    # Si es una lista, tomar el primer elemento
    if isinstance(notification_data, list) and len(notification_data) > 0:
        notification_data = notification_data[0]
    
    # Extraer la dirección del token de la notificación
    token_address = None
    twitter_username = None
    ipfs_uri = None
    
    # Buscar en tokenTransfers
    if "tokenTransfers" in notification_data and len(notification_data["tokenTransfers"]) > 0:
        token_address = notification_data["tokenTransfers"][0]["mint"]
    
    # Buscar metadatos en las instrucciones internas (Metaplex)
    if "instructions" in notification_data:
        for idx, instruction in enumerate(notification_data["instructions"]):
            if "innerInstructions" in instruction:
                for inner_idx, inner_instruction in enumerate(instruction["innerInstructions"]):
                    # Buscar la instrucción de Metaplex para crear metadatos
                    if inner_instruction.get("programId") == "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s":
                        print(f"Encontrada instrucción de Metaplex en instruction[{idx}].innerInstructions[{inner_idx}]")
                        # Intentar decodificar los datos
                        if "data" in inner_instruction:
                            print(f"Datos de la instrucción: {inner_instruction['data'][:50]}...")
                            metadata = try_decode_metaplex_data(inner_instruction['data'])
                            if metadata and "uri" in metadata:
                                ipfs_uri = metadata["uri"]
                                print(f"URI encontrada en los datos de la instrucción: {ipfs_uri}")
    
    # Si no se encontró en tokenTransfers, buscar en otros lugares
    if not token_address:
        print("No se pudo encontrar la dirección del token en la notificación")
        return None
    
    print(f"Dirección del token encontrada en la notificación: {token_address}")
    
    # Si encontramos la URI directamente en los datos, podemos intentar obtener el contenido
    if ipfs_uri:
        ipfs_content = get_ipfs_content(ipfs_uri)
        if ipfs_content:
            twitter_username = extract_twitter_username(ipfs_content)
            if twitter_username:
                print(f"Nombre de usuario de Twitter encontrado directamente de la notificación: {twitter_username}")
                return {
                    "token_address": token_address,
                    "ipfs_uri": ipfs_uri,
                    "twitter_username": twitter_username,
                    "ipfs_content": ipfs_content
                }
    
    # Si no pudimos extraer la información directamente, usar el método API
    return process_token(token_address)

def main():
    parser = argparse.ArgumentParser(description="Extrae información del creador de un token.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--address", help="Dirección del token (mint address)")
    group.add_argument("-n", "--notification", help="Archivo JSON con la notificación del webhook")
    
    args = parser.parse_args()
    
    if args.address:
        result = process_token(args.address)
    elif args.notification:
        try:
            with open(args.notification, 'r') as f:
                notification_data = json.load(f)
            result = process_webhook_notification(notification_data)
        except Exception as e:
            print(f"Error al procesar el archivo de notificación: {e}")
            return 1
    
    if result and result.get("twitter_username"):
        print("\nResumen de resultados:")
        print(f"Token: {result['token_address']}")
        print(f"URI: {result.get('ipfs_uri', 'No disponible')}")
        print(f"Usuario de Twitter: {result['twitter_username']}")
        
        # Guardar resultados en un archivo
        output_file = f"resultados_{result['token_address']}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResultados guardados en: {output_file}")
        
        return 0
    else:
        print("\nNo se pudo extraer la información completa del token.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 