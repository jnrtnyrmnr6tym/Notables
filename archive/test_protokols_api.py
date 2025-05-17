#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el acceso a la API de Protokols.

Este script intenta acceder a la API de Protokols utilizando cookies de sesión
y extraer información básica de un usuario de Twitter.

Uso:
    python test_protokols_api.py --cookies-file protokols_cookies.json --username jack
"""

import json
import argparse
import requests
import logging
from pprint import pprint
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ProtokolsAPITester")

def load_cookies(cookies_file):
    """
    Carga las cookies desde un archivo JSON.
    
    Args:
        cookies_file: Ruta al archivo JSON con las cookies
        
    Returns:
        dict: Diccionario con las cookies cargadas
    """
    try:
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        logger.info(f"Cookies cargadas desde {cookies_file}: {len(cookies)} cookies")
        return cookies
    except Exception as e:
        logger.error(f"Error al cargar cookies desde {cookies_file}: {str(e)}")
        return {}

def test_protokols_api():
    # Cargar cookies
    try:
        with open("protokols_cookies.json", "r") as f:
            cookies = json.load(f)
        print(f"Cookies cargadas: {len(cookies)} cookies")
    except Exception as e:
        print(f"Error al cargar cookies: {e}")
        return
    
    # Configurar URL y parámetros
    username = "jack"
    base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
    params = {"username": username}
    input_json = json.dumps({"json": params})
    
    # URL completa
    import urllib.parse
    encoded_input = urllib.parse.quote(input_json)
    url = f"{base_url}?input={encoded_input}"
    
    print(f"URL: {url}")
    
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    
    # Crear sesión y añadir cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Hacer la solicitud
    try:
        response = session.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("La API está funcionando correctamente")
            data = response.json()
            if "result" in data and "data" in data["result"] and "json" in data["result"]["data"]:
                user_data = data["result"]["data"]["json"]
                if "engagement" in user_data and "smartFollowersCount" in user_data["engagement"]:
                    smart_followers = user_data["engagement"]["smartFollowersCount"]
                    print(f"Notable followers: {smart_followers}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")

def main():
    parser = argparse.ArgumentParser(description="Prueba de acceso a la API de Protokols")
    parser.add_argument("--cookies-file", "-c", required=True, 
                        help="Archivo JSON con las cookies de sesión")
    parser.add_argument("--username", "-u", required=True,
                        help="Nombre de usuario de Twitter para consultar")
    parser.add_argument("--save-response", "-s", 
                        help="Guardar la respuesta en un archivo JSON")
    
    args = parser.parse_args()
    
    # Cargar cookies
    cookies = load_cookies(args.cookies_file)
    if not cookies:
        logger.error("No se pudieron cargar las cookies. Abortando.")
        return
    
    # Probar la API
    test_protokols_api()
    
    if response:
        logger.info("Solicitud exitosa. Mostrando estructura de la respuesta:")
        
        # Guardar respuesta si se especificó un archivo
        if args.save_response:
            try:
                with open(args.save_response, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2)
                logger.info(f"Respuesta guardada en {args.save_response}")
            except Exception as e:
                logger.error(f"Error al guardar la respuesta: {str(e)}")
        
        # Intentar extraer información básica
        try:
            # Navegar por la estructura para encontrar datos relevantes
            # Esto es un intento básico - la estructura exacta debe ser analizada
            if "result" in response and "data" in response["result"]:
                data = response["result"]["data"]
                
                # Extraer información del perfil
                if "profile" in data:
                    profile = data["profile"]
                    print("\n=== INFORMACIÓN DEL PERFIL ===")
                    print(f"Nombre: {profile.get('name', 'N/A')}")
                    print(f"Usuario: @{profile.get('username', 'N/A')}")
                    print(f"Seguidores: {profile.get('followersCount', 'N/A')}")
                    print(f"Siguiendo: {profile.get('followingCount', 'N/A')}")
                    print(f"Verificado: {'Sí' if profile.get('verified') else 'No'}")
                
                # Extraer notable followers
                if "notableFollowers" in data:
                    notable_followers = data["notableFollowers"]
                    print(f"\n=== NOTABLE FOLLOWERS ({len(notable_followers)}) ===")
                    for i, follower in enumerate(notable_followers[:10], 1):  # Mostrar solo los primeros 10
                        print(f"{i}. @{follower.get('username', 'N/A')} - {follower.get('name', 'N/A')}")
                    
                    if len(notable_followers) > 10:
                        print(f"... y {len(notable_followers) - 10} más")
                
                # Si no encontramos la estructura esperada
                else:
                    print("\nEstructura de datos desconocida. Mostrando las claves principales:")
                    pprint(list(data.keys()))
            else:
                print("\nEstructura de respuesta desconocida. Mostrando las claves principales:")
                pprint(list(response.keys()))
        
        except Exception as e:
            logger.error(f"Error al procesar la respuesta: {str(e)}")
            print("\nError al procesar la respuesta. Mostrando estructura completa:")
            pprint(response)
    else:
        logger.error("No se pudo obtener una respuesta válida de la API.")

if __name__ == "__main__":
    main() 