#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extraer y guardar las cookies de Protokols desde el navegador.

Uso:
    1. Inicie sesión manualmente en Protokols (https://protokols.com)
    2. Ejecute este script para extraer y guardar las cookies
"""

import json
import argparse
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("CookieExtractor")

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
    parser = argparse.ArgumentParser(description="Extractor de cookies de Protokols")
    parser.add_argument("--browser", "-b", choices=["chrome", "firefox", "edge", "opera", "brave"], 
                        default="chrome", help="Navegador del que extraer las cookies")
    parser.add_argument("--output", "-o", default="protokols_cookies.json",
                        help="Archivo de salida para guardar las cookies")
    
    args = parser.parse_args()
    
    # Extraer cookies
    cookies = extract_cookies_from_browser(args.browser)
    
    if not cookies:
        logger.error("No se pudieron extraer cookies. Asegúrate de haber iniciado sesión en Protokols.")
        return
    
    # Guardar cookies
    save_cookies_to_file(cookies, args.output)
    
    # Mostrar información de las cookies
    print(f"\nCookies extraídas: {len(cookies)}")
    print("Nombres de las cookies:")
    for name in cookies.keys():
        print(f"- {name}")

if __name__ == "__main__":
    main() 