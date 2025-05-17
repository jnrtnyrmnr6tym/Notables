#!/usr/bin/env python3
"""
Servidor para recibir y procesar notificaciones del webhook de Helius.

Este servidor:
1. Recibe notificaciones POST del webhook de Helius
2. Extrae la dirección del token de la notificación
3. Procesa el token para obtener información del creador
4. Verifica si el creador cumple los criterios de notable followers
"""

from flask import Flask, request, jsonify
import json
import os
import threading
import time
from pathlib import Path
import logging
import argparse
import sys

# Importamos el procesador de tokens
try:
    from extract_token_creator import process_webhook_notification, process_token
    TOKEN_PROCESSOR_AVAILABLE = True
except ImportError:
    TOKEN_PROCESSOR_AVAILABLE = False
    print("Advertencia: No se pudo importar el procesador de tokens. La funcionalidad estará limitada.")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("webhook_server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("helius_webhook")

# Crear directorio para almacenar notificaciones
NOTIFICATIONS_DIR = Path("notifications")
NOTIFICATIONS_DIR.mkdir(exist_ok=True)

# Crear la aplicación Flask
app = Flask(__name__)

# Cola de notificaciones para procesamiento asíncrono
notification_queue = []
processing_thread = None
processing_active = False

def save_notification(data, notification_id=None):
    """
    Guarda una notificación en un archivo JSON.
    
    Args:
        data (dict): Datos de la notificación
        notification_id (str, optional): ID único para la notificación
    
    Returns:
        str: Ruta del archivo donde se guardó la notificación
    """
    if notification_id is None:
        notification_id = str(int(time.time()))
    
    filename = NOTIFICATIONS_DIR / f"notification_{notification_id}.json"
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Notificación guardada en {filename}")
    return str(filename)

def process_notification_queue():
    """
    Procesa las notificaciones en la cola de forma asíncrona.
    """
    global processing_active
    
    logger.info("Iniciando procesamiento de cola de notificaciones")
    processing_active = True
    
    while processing_active and notification_queue:
        try:
            # Obtener la siguiente notificación de la cola
            notification_data = notification_queue.pop(0)
            
            logger.info(f"Procesando notificación {len(notification_queue) + 1} restantes en cola")
            
            # Procesar la notificación si el procesador está disponible
            if TOKEN_PROCESSOR_AVAILABLE:
                try:
                    result = process_webhook_notification(notification_data)
                    
                    if result:
                        logger.info(f"Notificación procesada exitosamente: {result.get('token_address')}")
                        
                        # Aquí se podría implementar la verificación de notable followers
                        # y la exportación al Maestro Bot si cumple los criterios
                    else:
                        logger.warning("No se pudo procesar la notificación correctamente")
                except Exception as e:
                    logger.error(f"Error al procesar notificación: {str(e)}")
            else:
                logger.warning("Procesador de tokens no disponible, notificación guardada pero no procesada")
            
            # Pequeña pausa para no sobrecargar el sistema
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error en el hilo de procesamiento: {str(e)}")
    
    logger.info("Procesamiento de cola finalizado")
    processing_active = False

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """
    Manejador principal para las notificaciones del webhook.
    """
    global processing_thread
    
    try:
        # Obtener los datos de la solicitud
        data = request.json
        
        if not data:
            logger.warning("Solicitud recibida sin datos JSON")
            return jsonify({"status": "error", "message": "No se recibieron datos JSON"}), 400
        
        # Generar un ID único para esta notificación
        notification_id = str(int(time.time()))
        
        # Guardar la notificación
        save_notification(data, notification_id)
        
        # Agregar a la cola de procesamiento
        notification_queue.append(data)
        
        # Iniciar hilo de procesamiento si no está activo
        if processing_thread is None or not processing_thread.is_alive():
            processing_thread = threading.Thread(target=process_notification_queue)
            processing_thread.daemon = True
            processing_thread.start()
        
        logger.info(f"Notificación recibida y agregada a la cola (ID: {notification_id})")
        
        # Responder con éxito
        return jsonify({
            "status": "success",
            "message": "Notificación recibida",
            "notification_id": notification_id
        }), 200
    
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """
    Página de inicio simple para verificar que el servidor está funcionando.
    """
    return jsonify({
        "status": "online",
        "service": "Helius Webhook Server",
        "endpoints": {
            "/webhook": "POST - Endpoint principal para recibir notificaciones",
            "/status": "GET - Verificar estado del servidor y cola de procesamiento"
        }
    })

@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint para verificar el estado del servidor.
    """
    return jsonify({
        "status": "online",
        "queue_size": len(notification_queue),
        "processing_active": processing_active,
        "token_processor_available": TOKEN_PROCESSOR_AVAILABLE,
        "notifications_dir": str(NOTIFICATIONS_DIR),
        "saved_notifications": len(list(NOTIFICATIONS_DIR.glob("*.json")))
    })

def main():
    """
    Función principal para iniciar el servidor.
    """
    parser = argparse.ArgumentParser(description="Servidor para recibir notificaciones del webhook de Helius")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Puerto para el servidor (default: 5000)")
    parser.add_argument("-d", "--debug", action="store_true", help="Ejecutar en modo debug")
    
    args = parser.parse_args()
    
    logger.info(f"Iniciando servidor en el puerto {args.port}")
    logger.info(f"Directorio de notificaciones: {NOTIFICATIONS_DIR}")
    logger.info(f"Procesador de tokens disponible: {TOKEN_PROCESSOR_AVAILABLE}")
    
    # Iniciar el servidor Flask
    app.run(host="0.0.0.0", port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 