#!/usr/bin/env python3
"""
Script para probar el webhook local con datos reales del token ANDY.
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

# Datos reales del token ANDY
real_data = {
    "accountData": [
        {
            "account": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
            "nativeBalanceChange": 0,
            "tokenBalanceChanges": []
        }
    ],
    "description": "Initialize Virtual Pool with SPL Token",
    "events": {},
    "fee": 30220,
    "feePayer": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
    "nativeTransfers": [],
    "signature": "2fwFy9jchWjAf6EactUu76QBdgPLz6TraahYPm92wXkwNUkoiKkWWqFNFZtWWKq5UirH5zUEnjSzteVGnFNdYPpN",
    "slot": 339977396,
    "source": "SYSTEM",
    "timestamp": 1715698995, # May 14, 2025 14:23:15 +UTC
    "tokenTransfers": [
        {
            "fromTokenAccount": "11111111111111111111111111111111",
            "fromUserAccount": "11111111111111111111111111111111",
            "mint": "8wnN6EuyqsNvXD5pbF9MErcL2QB1eZ4pTmb4wwMGVXwj", # ANDY token mint address
            "toTokenAccount": "3TPQW64JvTAUT6g2RP3mH486L3PrckP7hA7Pvh11wCfC",
            "toUserAccount": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM",
            "tokenAmount": 1000000000,
            "tokenStandard": "Fungible"
        }
    ],
    "type": "TRANSFER"
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
    logger.info("Enviando notificación con datos reales del token ANDY")
    send_to_webhook([real_data])

if __name__ == "__main__":
    main() 