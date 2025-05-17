#!/usr/bin/env python3
"""
Script simple para probar el webhook con un solo token.
"""

import requests
import json
import sys

# Configuración
SERVER_URL = "http://127.0.0.1:5000/webhook"
TOKEN_ADDRESS = "GV74pg6zi1Hy19woBW9msKUqxxvw63A7SQ15tGj5wWJ4"

def main():
    # Crear datos de prueba
    data = {
        "tokenTransfers": [
            {
                "mint": TOKEN_ADDRESS,
                "tokenAmount": 1000000000
            }
        ],
        "description": f"Test mint for {TOKEN_ADDRESS}"
    }
    
    print(f"Enviando datos al servidor: {SERVER_URL}")
    print(f"Token a probar: {TOKEN_ADDRESS}")
    
    try:
        response = requests.post(SERVER_URL, json=data)
        print(f"Código de respuesta: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")
        
        return 0
    except Exception as e:
        print(f"Error al enviar datos: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 