#!/usr/bin/env python3
"""
Script para simular el envío de datos de webhook al servidor local.
Permite probar el procesamiento de notificaciones sin depender de Helius.
"""

import json
import requests
import argparse
import logging
import sys

# Configuración
SERVER_URL = "http://127.0.0.1:5000/webhook"
LOG_FILE = "webhook_test.log"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def send_webhook_data(data):
    """Envía datos al endpoint webhook del servidor local."""
    try:
        logger.info(f"Enviando datos al servidor: {SERVER_URL}")
        response = requests.post(SERVER_URL, json=data)
        response.raise_for_status()
        
        logger.info(f"Respuesta del servidor: {response.status_code}")
        logger.info(f"Contenido de la respuesta: {response.text}")
        
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al enviar datos al servidor: {e}")
        return False

def load_data_from_file(file_path):
    """Carga datos de webhook desde un archivo JSON."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error al cargar datos desde {file_path}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Simulador de webhook para pruebas locales.")
    parser.add_argument("--file", help="Archivo JSON con datos de webhook")
    parser.add_argument("--token", help="Token específico para simular")
    
    args = parser.parse_args()
    
    if args.file:
        # Cargar datos desde archivo
        data = load_data_from_file(args.file)
        if not data:
            return 1
    elif args.token:
        # Crear datos simulados para un token específico
        data = [{
            "tokenTransfers": [
                {
                    "mint": args.token,
                    "tokenAmount": 1000000000
                }
            ],
            "description": f"Token mint test for {args.token}"
        }]
    else:
        # Usar datos de ejemplo embebidos
        logger.info("Usando datos de ejemplo embebidos")
        
        # Ejemplo 1: SHEIKH BROCCOLI
        data1 = [{
            "accountData":[{"account":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE","nativeBalanceChange":-24527905,"tokenBalanceChanges":[]},{"account":"5ozjRgsNZgNnaa7hLVQBdZSj1kwaztrvvBaLnEUn9piF","nativeBalanceChange":1461600,"tokenBalanceChanges":[]},{"account":"GaEYPqTH4K7R144VDeUNTymg6zbryfsUWZG4y8Yu6X9z","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"72eWk1gwetx2EKUQruDYKaYXVEdjqxef5gjGtJhnH5TR","nativeBalanceChange":2039280,"tokenBalanceChanges":[{"mint":"5ozjRgsNZgNnaa7hLVQBdZSj1kwaztrvvBaLnEUn9piF","rawTokenAmount":{"decimals":9,"tokenAmount":"1000000000000000000"},"tokenAccount":"72eWk1gwetx2EKUQruDYKaYXVEdjqxef5gjGtJhnH5TR","userAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"}]},{"account":"7XikKFE5P4uX4tgQPGZ43jeUT2FXM53oH9GA15atZeX2","nativeBalanceChange":2039280,"tokenBalanceChanges":[]},{"account":"98zkw1EAEvRLMK3sPafiYTCTzLFDbVGnG8hg6NsYoYre","nativeBalanceChange":3841920,"tokenBalanceChanges":[]},{"account":"HGCqHMMAeqH6cKeLCZQ6CL9UCP62kPHcqangLWKbXTzX","nativeBalanceChange":15115600,"tokenBalanceChanges":[]},{"account":"11111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"2WECZukPGAina8GmfPnHACRnhiLnQ6hsmnZsyarvqdws","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"ComputeBudget111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"So11111111111111111111111111111111111111112","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","nativeBalanceChange":0,"tokenBalanceChanges":[]}],
            "description":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE minted 1000000000.00 SHEIKH BROCCOLI.",
            "tokenTransfers":[{"fromTokenAccount":"","fromUserAccount":"","mint":"5ozjRgsNZgNnaa7hLVQBdZSj1kwaztrvvBaLnEUn9piF","toTokenAccount":"72eWk1gwetx2EKUQruDYKaYXVEdjqxef5gjGtJhnH5TR","toUserAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","tokenAmount":1000000000,"tokenStandard":"Fungible"}],
            "type":"TOKEN_MINT"
        }]
        
        # Ejemplo 2: 1st Bitcoin Burger
        data2 = [{
            "accountData":[{"account":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE","nativeBalanceChange":-24527905,"tokenBalanceChanges":[]},{"account":"2UZx37285EFSpohx9CdBJavZN5LcAKVgcryvvxUe4YoS","nativeBalanceChange":1461600,"tokenBalanceChanges":[]},{"account":"ZCiWrw3WcBW2iEL7s3NKyUUNNVDxg7K3TqZjaJhM1gr","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"4nQj75K5VLXB3VrjsvFH5inZvdg9DFVtHobhT186hXST","nativeBalanceChange":3841920,"tokenBalanceChanges":[]},{"account":"Asoy79gYYAKQBMEb5an2t5WXagWKxr7m6R5cJAtPaJm8","nativeBalanceChange":2039280,"tokenBalanceChanges":[{"mint":"2UZx37285EFSpohx9CdBJavZN5LcAKVgcryvvxUe4YoS","rawTokenAmount":{"decimals":9,"tokenAmount":"1000000000000000000"},"tokenAccount":"Asoy79gYYAKQBMEb5an2t5WXagWKxr7m6R5cJAtPaJm8","userAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"}]},{"account":"BsX8echTDiv2Yvru729pCPGi1tTf7wSNNZU4kjoN5eoa","nativeBalanceChange":2039280,"tokenBalanceChanges":[]},{"account":"BW8iTxJvdbkczcUiVgre8boAdHjubB12cnXLDyULfT67","nativeBalanceChange":15115600,"tokenBalanceChanges":[]},{"account":"11111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"AX4m2D2Dnw7je8n2ZJfFt22b8U5Sf2ovLzyzFrQvhDek","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"ComputeBudget111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"So11111111111111111111111111111111111111112","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","nativeBalanceChange":0,"tokenBalanceChanges":[]}],
            "description":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE minted 1000000000.00 1st Bitcoin Burger.",
            "tokenTransfers":[{"fromTokenAccount":"","fromUserAccount":"","mint":"2UZx37285EFSpohx9CdBJavZN5LcAKVgcryvvxUe4YoS","toTokenAccount":"Asoy79gYYAKQBMEb5an2t5WXagWKxr7m6R5cJAtPaJm8","toUserAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","tokenAmount":1000000000,"tokenStandard":"Fungible"}],
            "type":"TOKEN_MINT"
        }]
        
        # Ejemplo 3: LAN
        data3 = [{
            "accountData":[{"account":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE","nativeBalanceChange":-24527905,"tokenBalanceChanges":[]},{"account":"4b4NyG7osWWCuKMXXmeaAmfe38VJostQm9XBP7wzUtR5","nativeBalanceChange":1461600,"tokenBalanceChanges":[]},{"account":"3UnuYCG6MBBzARGtKPgpyF4VJHdVH12mAjsLaWNqox7M","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"4BGKqJPxPYGKwkxiJzMusNjhGDHDTws5QAqpUaK2q2Rk","nativeBalanceChange":15115600,"tokenBalanceChanges":[]},{"account":"7Nu7U6hPXLC1eC5G85qBHjCcy5tizSRZYC1GDGeEPLGT","nativeBalanceChange":3841920,"tokenBalanceChanges":[]},{"account":"CvUGxDZTPVy3ZB5efk6jFrunNRZ86pmetiDEurvUEjL1","nativeBalanceChange":2039280,"tokenBalanceChanges":[{"mint":"4b4NyG7osWWCuKMXXmeaAmfe38VJostQm9XBP7wzUtR5","rawTokenAmount":{"decimals":9,"tokenAmount":"1000000000000000000"},"tokenAccount":"CvUGxDZTPVy3ZB5efk6jFrunNRZ86pmetiDEurvUEjL1","userAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"}]},{"account":"EgY5oAQfeQ7qxAVxU4GQP2xGJ9DTvy7iPFwEYfcSM2Gm","nativeBalanceChange":2039280,"tokenBalanceChanges":[]},{"account":"11111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"4mZYov4wreMpxREkjscFD8a8gSWVCy5QD1hSD41y2PG1","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"ComputeBudget111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"So11111111111111111111111111111111111111112","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","nativeBalanceChange":0,"tokenBalanceChanges":[]}],
            "description":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE minted 1000000000.00 LAN.",
            "tokenTransfers":[{"fromTokenAccount":"","fromUserAccount":"","mint":"4b4NyG7osWWCuKMXXmeaAmfe38VJostQm9XBP7wzUtR5","toTokenAccount":"CvUGxDZTPVy3ZB5efk6jFrunNRZ86pmetiDEurvUEjL1","toUserAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","tokenAmount":1000000000,"tokenStandard":"Fungible"}],
            "type":"TOKEN_MINT"
        }]
        
        # Probar con los tres ejemplos
        logger.info("Probando con el ejemplo 1: SHEIKH BROCCOLI")
        send_webhook_data(data1)
        
        logger.info("Probando con el ejemplo 2: 1st Bitcoin Burger")
        send_webhook_data(data2)
        
        logger.info("Probando con el ejemplo 3: LAN")
        send_webhook_data(data3)
        
        return 0
    
    # Enviar los datos al servidor
    if send_webhook_data(data):
        logger.info("Datos enviados correctamente")
        return 0
    else:
        logger.error("Error al enviar datos")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 