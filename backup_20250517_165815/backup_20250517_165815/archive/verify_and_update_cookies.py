#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar la validez de las cookies de Protokols y actualizarlas si es necesario.

Este script:
1. Verifica si las cookies actuales son válidas haciendo una solicitud a la API de Protokols
2. Si las cookies no son válidas, guía al usuario para actualizarlas
3. Guarda las nuevas cookies en el archivo de configuración
"""

import json
import requests
import logging
import argparse
import sys
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("CookieVerifier")

# Constantes
COOKIES_FILE = "protokols_cookies.json"
TEST_USERNAME = "jack"  # Usuario de prueba para verificar las cookies
PROTOKOLS_API_URL = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"

def load_cookies_from_file(cookies_file=COOKIES_FILE):
    """Carga cookies desde un archivo JSON."""
    try:
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            logger.info(f"Cookies cargadas correctamente desde {cookies_file}: {len(cookies)} cookies encontradas")
            return cookies
    except Exception as e:
        logger.error(f"Error al cargar cookies desde {cookies_file}: {e}")
        return {}

def verify_cookies(cookies):
    """
    Verifica si las cookies son válidas haciendo una solicitud a la API de Protokols.
    
    Args:
        cookies: Diccionario con las cookies
        
    Returns:
        bool: True si las cookies son válidas, False en caso contrario
    """
    try:
        # Construir la URL con los parámetros codificados
        params = {
            "input": {
                "username": TEST_USERNAME
            }
        }
        url = f"{PROTOKOLS_API_URL}?input={json.dumps(params['input'])}"
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": f"https://www.protokols.io/twitter/{TEST_USERNAME}"
        }
        
        # Realizar la solicitud con cookies
        logger.info(f"Verificando cookies con usuario de prueba: {TEST_USERNAME}")
        response = requests.get(url, headers=headers, cookies=cookies)
        
        # Verificar si la respuesta es exitosa (200 OK)
        if response.status_code == 200:
            logger.info("Las cookies son válidas")
            return True
        else:
            logger.warning(f"Las cookies no son válidas. Código de respuesta: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error al verificar cookies: {e}")
        return False

def get_manual_cookie_input():
    """
    Solicita al usuario que ingrese manualmente las cookies.
    
    Returns:
        dict: Diccionario con las cookies ingresadas
    """
    print("\n=== ENTRADA MANUAL DE COOKIES ===")
    print("Ingrese las cookies de sesión de Protokols.")
    print("Para cada cookie, ingrese el nombre y valor separados por '='.")
    print("Deje una línea en blanco para terminar.")
    print("Ejemplo: _ga=GA1.2.1234567890.1234567890")
    print("         _gid=GA1.2.1234567890.1234567890")
    print("         __Secure-next-auth.session-token=abcdef1234567890")
    print("\nIngrese las cookies a continuación:")
    
    cookies = {}
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            # Dividir por el primer '=' para manejar valores que contienen '='
            parts = line.split('=', 1)
            if len(parts) != 2:
                print(f"Formato incorrecto: '{line}'. Use 'nombre=valor'.")
                continue
            
            name, value = parts
            cookies[name.strip()] = value.strip()
            print(f"Cookie '{name}' añadida.")
        except Exception as e:
            print(f"Error al procesar la entrada: {str(e)}")
    
    return cookies

def extract_cookies_from_browser(browser: str = "chrome", domain: str = "protokols.com"):
    """
    Extrae cookies del navegador para un dominio específico.
    
    Args:
        browser: Navegador del que extraer las cookies ('chrome', 'firefox', 'edge', etc.)
        domain: Dominio para el que extraer las cookies
        
    Returns:
        Dict: Diccionario con las cookies extraídas
    """
    try:
        import browser_cookie3
        
        # Seleccionar la función según el navegador
        cookie_functions = {
            'chrome': browser_cookie3.chrome,
            'firefox': browser_cookie3.firefox,
            'edge': browser_cookie3.edge,
            'opera': browser_cookie3.opera,
            'brave': browser_cookie3.brave,
        }
        
        if browser.lower() not in cookie_functions:
            logger.error(f"Navegador no soportado: {browser}")
            return {}
        
        # Extraer cookies
        cookies = cookie_functions[browser.lower()](domain_name=domain)
        cookie_dict = {cookie.name: cookie.value for cookie in cookies}
        
        logger.info(f"Se extrajeron {len(cookie_dict)} cookies del navegador {browser} para {domain}")
        return cookie_dict
    
    except ImportError:
        logger.error("No se pudo importar browser_cookie3. Instálalo con: pip install browser-cookie3")
        return {}
    except Exception as e:
        logger.error(f"Error al extraer cookies del navegador: {str(e)}")
        return {}

def save_cookies_to_file(cookies, output_file):
    """
    Guarda las cookies en un archivo JSON.
    
    Args:
        cookies: Diccionario con las cookies
        output_file: Ruta al archivo de salida
    
    Returns:
        bool: True si las cookies se guardaron correctamente, False en caso contrario
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        logger.info(f"Cookies guardadas en {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar cookies: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Verificador y actualizador de cookies de Protokols")
    parser.add_argument("--cookies-file", "-c", default=COOKIES_FILE,
                        help="Archivo de cookies a verificar")
    parser.add_argument("--browser", "-b", choices=["chrome", "firefox", "edge", "opera", "brave"], 
                        default="chrome", help="Navegador del que extraer las cookies")
    parser.add_argument("--manual", "-m", action="store_true",
                        help="Ingresar cookies manualmente en lugar de extraerlas del navegador")
    
    args = parser.parse_args()
    
    # Cargar cookies existentes
    cookies = load_cookies_from_file(args.cookies_file)
    
    # Verificar si las cookies son válidas
    if cookies and verify_cookies(cookies):
        print(f"Las cookies en {args.cookies_file} son válidas. No se requiere actualización.")
        return 0
    
    print(f"Las cookies en {args.cookies_file} no son válidas o no existen. Es necesario actualizarlas.")
    
    # Obtener nuevas cookies
    new_cookies = {}
    if args.manual:
        print("\nIngrese las cookies manualmente:")
        new_cookies = get_manual_cookie_input()
    else:
        print(f"\nExtrayendo cookies del navegador {args.browser}...")
        try:
            new_cookies = extract_cookies_from_browser(args.browser)
        except Exception as e:
            print(f"Error al extraer cookies del navegador: {e}")
            print("Cambiando a entrada manual de cookies...")
            new_cookies = get_manual_cookie_input()
    
    if not new_cookies:
        print("No se pudieron obtener nuevas cookies. Saliendo.")
        return 1
    
    # Guardar nuevas cookies
    if save_cookies_to_file(new_cookies, args.cookies_file):
        print(f"Nuevas cookies guardadas en {args.cookies_file}")
    else:
        print(f"Error al guardar las nuevas cookies en {args.cookies_file}")
        return 1
    
    # Verificar las nuevas cookies
    if verify_cookies(new_cookies):
        print("Las nuevas cookies son válidas.")
        return 0
    else:
        print("Las nuevas cookies no son válidas. Puede que necesite iniciar sesión en Protokols nuevamente.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 