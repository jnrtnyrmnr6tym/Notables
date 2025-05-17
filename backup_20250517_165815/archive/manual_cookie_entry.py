#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ingresar manualmente las cookies de sesión de Protokols.

Este script permite al usuario ingresar manualmente las cookies de sesión
obtenidas desde el navegador y las guarda en un archivo JSON.

Instrucciones para obtener cookies manualmente:
1. Inicie sesión en Protokols (https://protokols.com)
2. Abra las herramientas de desarrollador (F12 o Clic derecho -> Inspeccionar)
3. Vaya a la pestaña "Application" (Chrome) o "Storage" (Firefox)
4. En el panel izquierdo, expanda "Cookies" y seleccione "https://protokols.com"
5. Copie los nombres y valores de las cookies relevantes
"""

import json
import logging
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ManualCookieEntry")

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
    print("\n=== ENTRADA MANUAL DE COOKIES DE PROTOKOLS ===")
    print("\nEste script le permite ingresar manualmente las cookies de sesión de Protokols.")
    print("Siga las instrucciones para obtener las cookies desde su navegador.")
    
    # Solicitar el archivo de salida
    output_file = input("\nIngrese el nombre del archivo para guardar las cookies [protokols_cookies.json]: ")
    if not output_file:
        output_file = "protokols_cookies.json"
    
    # Obtener cookies manualmente
    cookies = get_manual_cookie_input()
    
    if not cookies:
        print("\nNo se ingresaron cookies. Saliendo.")
        return
    
    # Guardar cookies
    if save_cookies_to_file(cookies, output_file):
        print(f"\nCookies guardadas exitosamente en {output_file}")
        print(f"Total de cookies guardadas: {len(cookies)}")
    else:
        print(f"\nError al guardar las cookies en {output_file}")

if __name__ == "__main__":
    main() 