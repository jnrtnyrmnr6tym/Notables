#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar la API de Protokols para obtener notable followers.

Este script:
1. Carga las cookies guardadas de Protokols
2. Hace una solicitud POST a la API específica
3. Muestra los resultados, especialmente los notable followers
"""

import json
import requests
import logging
from pprint import pprint

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ProtokolsAPIVerifier")

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

def verify_protokols_api(cookies, username="play_noodle"):
    """
    Verifica la API de Protokols para obtener notable followers.
    
    Args:
        cookies: Diccionario con las cookies de sesión
        username: Nombre de usuario de Twitter para consultar
        
    Returns:
        dict: Respuesta de la API
    """
    url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    
    payload = {
        "input": {
            "json": {
                "username": username
            }
        }
    }
    
    # Crear sesión con cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    session.headers.update(headers)
    
    try:
        logger.info(f"Enviando solicitud para el usuario @{username}")
        print(f"\nVerificando API para @{username}...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = session.post(url, json=payload)
        
        logger.info(f"Código de respuesta: {response.status_code}")
        print(f"\nCódigo de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error en la solicitud: {response.status_code} - {response.text}")
            print(f"\nError en la solicitud: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Excepción al realizar la solicitud: {str(e)}")
        print(f"\nError: {str(e)}")
        return None

def main():
    cookies_file = "protokols_cookies.json"
    username = "play_noodle"
    
    # Cargar cookies
    cookies = load_cookies(cookies_file)
    if not cookies:
        logger.error("No se pudieron cargar las cookies. Abortando.")
        print("\nNo se pudieron cargar las cookies. Por favor, ejecuta primero protokols_browser_login.py")
        return
    
    # Verificar la API
    response = verify_protokols_api(cookies, username)
    
    if response:
        print("\nRespuesta exitosa. Analizando datos...")
        
        # Intentar extraer información relevante
        try:
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
                    
                    # Verificar si hay información de notable followers
                    if "notableFollowersCount" in profile:
                        print(f"Número de Notable Followers: {profile['notableFollowersCount']}")
                
                # Extraer notable followers
                if "notableFollowers" in data:
                    notable_followers = data["notableFollowers"]
                    print(f"\n=== NOTABLE FOLLOWERS ({len(notable_followers)}) ===")
                    for i, follower in enumerate(notable_followers[:10], 1):  # Mostrar solo los primeros 10
                        print(f"{i}. @{follower.get('username', 'N/A')} - {follower.get('name', 'N/A')}")
                    
                    if len(notable_followers) > 10:
                        print(f"... y {len(notable_followers) - 10} más")
                
                # Si no encontramos la estructura esperada
                elif "notableFollowers" not in data and "notableFollowersCount" not in data.get("profile", {}):
                    print("\nNo se encontró información de Notable Followers.")
                    print("\nEstructura de datos disponible:")
                    print(f"Claves en data: {list(data.keys())}")
                    if "profile" in data:
                        print(f"Claves en profile: {list(data['profile'].keys())}")
            else:
                print("\nEstructura de respuesta desconocida. Mostrando las claves principales:")
                pprint(list(response.keys()))
                if "result" in response:
                    print(f"Claves en result: {list(response['result'].keys())}")
        
        except Exception as e:
            logger.error(f"Error al procesar la respuesta: {str(e)}")
            print(f"\nError al procesar la respuesta: {str(e)}")
            print("\nMostrando estructura completa de la respuesta:")
            pprint(response)
    else:
        print("\nNo se pudo obtener una respuesta válida de la API.")
        print("\nSugerencias:")
        print("1. Verifica que las cookies sean válidas (vuelve a ejecutar protokols_browser_login.py)")
        print("2. Comprueba que el nombre de usuario sea correcto")
        print("3. Verifica que la URL de la API sea correcta")

if __name__ == "__main__":
    main() 