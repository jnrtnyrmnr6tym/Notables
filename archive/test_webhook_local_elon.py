#!/usr/bin/env python3
"""
Script para probar el webhook local con un token que tiene a Elon Musk como creador.
"""

import requests
import json
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# URL del webhook local
WEBHOOK_URL = "http://127.0.0.1:5000/webhook"

# Datos de ejemplo de un token con Elon Musk como creador
example_data = {
    "accountData": [
        {
            "account": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
            "nativeBalanceChange": 0,
            "tokenBalanceChanges": []
        }
    ],
    "description": "Mint 1 ELON",
    "events": {},
    "fee": 5000,
    "feePayer": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
    "nativeTransfers": [],
    "signature": "5ozjRgsNZgNnaa7hLVQBdZSj1kwaztrvvBaLnEUn9piF",
    "slot": 245631953,
    "source": "SYSTEM",
    "timestamp": 1715617483,
    "tokenTransfers": [
        {
            "fromTokenAccount": "11111111111111111111111111111111",
            "fromUserAccount": "11111111111111111111111111111111",
            "mint": "ElonMuskToken123456789",
            "toTokenAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
            "toUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
            "tokenAmount": 1,
            "tokenStandard": "Fungible"
        }
    ],
    "type": "TRANSFER"
}

# Función para simular los metadatos del token
def mock_token_metadata():
    return {
        "result": {
            "content": {
                "json_uri": "https://ipfs.io/ipfs/elon_musk_token_metadata",
                "metadata": {
                    "name": "Elon Musk Token",
                    "symbol": "ELON",
                    "description": "Token created by Elon Musk",
                    "twitter_username": "elonmusk"
                }
            }
        }
    }

# Función para enviar datos al webhook
def send_to_webhook(data):
    try:
        logger.info(f"Enviando datos al servidor: {WEBHOOK_URL}")
        response = requests.post(WEBHOOK_URL, json=data)
        logger.info(f"Respuesta del servidor: {response.status_code}")
        logger.info(f"Contenido de la respuesta: {response.text}")
        return response
    except Exception as e:
        logger.error(f"Error al enviar datos al webhook: {e}")
        return None

# Función principal
def main():
    logger.info("Enviando notificación con token de Elon Musk")
    send_to_webhook([example_data])

if __name__ == "__main__":
    main() 