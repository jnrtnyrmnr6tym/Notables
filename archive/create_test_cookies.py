#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear un archivo de cookies de prueba.

Este script crea un archivo JSON con cookies de prueba para verificar
la funcionalidad básica de los scripts de extracción de notable followers.
"""

import json
import argparse

def create_test_cookies(output_file="test_cookies.json"):
    """
    Crea un archivo JSON con cookies de prueba.
    
    Args:
        output_file: Ruta al archivo de salida
        
    Returns:
        bool: True si el archivo se creó correctamente, False en caso contrario
    """
    # Cookies de prueba (estas NO son cookies reales válidas)
    test_cookies = {
        "_ga": "GA1.2.123456789.123456789",
        "_gid": "GA1.2.987654321.987654321",
        "protokols_session": "test_session_value_123456789",
        "protokols_auth": "test_auth_value_987654321",
        "next-auth.csrf-token": "abcdef1234567890",
        "next-auth.callback-url": "https://protokols.com",
        "next-auth.session-token": "test_session_token_123456789",
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(test_cookies, f, indent=2)
        print(f"Archivo de cookies de prueba creado: {output_file}")
        return True
    except Exception as e:
        print(f"Error al crear el archivo de cookies: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Creador de cookies de prueba")
    parser.add_argument("--output", "-o", default="test_cookies.json",
                        help="Archivo de salida para guardar las cookies de prueba")
    
    args = parser.parse_args()
    
    create_test_cookies(args.output)
    
    print("\nIMPORTANTE: Estas cookies de prueba NO son válidas para autenticación real.")
    print("Son solo para verificar la funcionalidad básica de los scripts.")
    print("Para usar la API de Protokols, necesitará cookies reales obtenidas después de iniciar sesión.")

if __name__ == "__main__":
    main() 