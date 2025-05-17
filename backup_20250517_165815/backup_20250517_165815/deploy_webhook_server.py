#!/usr/bin/env python3
"""
Script para desplegar el servidor webhook de monitoreo de tokens.

Este script:
1. Inicia el servidor webhook para recibir notificaciones de Helius
2. Implementa monitoreo básico del estado del servidor
3. Configura un sistema de registro avanzado
4. Proporciona endpoints adicionales para verificar el estado y las estadísticas
"""

import os
import sys
import time
import json
import signal
import logging
import argparse
import threading
import subprocess
import shutil  # Agregado para disk_usage
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from logging.handlers import RotatingFileHandler

# Configurar logging primero para capturar errores de importación
LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'webhook_server.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    # Importar el script de monitoreo de tokens
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import token_monitor_with_notable_check as token_monitor
    logger.info("Módulo token_monitor_with_notable_check importado correctamente")
except Exception as e:
    logger.error(f"Error al importar token_monitor_with_notable_check: {e}")
    sys.exit(1)

# Configuración
PORT = 3003
HOST = '0.0.0.0'
STATS_FILE = os.path.join(LOG_DIR, 'server_stats.json')
HEALTH_CHECK_INTERVAL = 60  # segundos
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Número de archivos de respaldo

# Estadísticas del servidor
stats = {
    'start_time': time.time(),
    'notifications_received': 0,
    'tokens_processed': 0,
    'tokens_approved': 0,
    'tokens_rejected': 0,
    'errors': 0,
    'last_notification_time': None,
    'last_processed_token': None,
    'last_error': None
}

# Crear la aplicación Flask
app = Flask(__name__)

def save_stats():
    """Guarda las estadísticas en un archivo JSON."""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error al guardar estadísticas: {e}")

def load_stats():
    """Carga las estadísticas desde un archivo JSON."""
    global stats
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                loaded_stats = json.load(f)
                # Mantener la hora de inicio actual
                start_time = stats['start_time']
                stats = loaded_stats
                stats['start_time'] = start_time
    except Exception as e:
        logger.error(f"Error al cargar estadísticas: {e}")

def update_stats(key, value=None, increment=False):
    """Actualiza las estadísticas del servidor."""
    if key in stats:
        if increment and isinstance(stats[key], (int, float)):
            stats[key] += 1
        else:
            stats[key] = value
        save_stats()

def check_disk_space():
    """Verifica el espacio en disco disponible."""
    try:
        total, used, free = shutil.disk_usage("/")
        disk_percent = used / total * 100
        
        if disk_percent > 90:
            logger.warning(f"Advertencia: Espacio en disco bajo ({disk_percent:.1f}%)")
        
        return True
    except Exception as e:
        logger.error(f"Error al verificar espacio en disco: {e}")
        return False

def health_check():
    """Realiza verificaciones periódicas del estado del servidor."""
    logger.info("Iniciando thread de health check")
    while True:
        try:
            # Verificar espacio en disco
            check_disk_space()
            
            # Verificar tiempo desde la última notificación
            if stats['last_notification_time']:
                last_notification = datetime.fromtimestamp(stats['last_notification_time'])
                time_since_last = datetime.now() - last_notification
                
                if time_since_last > timedelta(hours=24):
                    logger.warning(f"Advertencia: No se han recibido notificaciones en las últimas 24 horas")
            
            # Verificar validez de las cookies
            check_cookies_validity()
            
            # Guardar estadísticas
            save_stats()
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
        
        # Esperar hasta el próximo chequeo
        time.sleep(HEALTH_CHECK_INTERVAL)

def check_cookies_validity():
    """Verifica la validez de las cookies de autenticación."""
    try:
        cookies = token_monitor.load_cookies_from_file()
        if not cookies:
            logger.warning("No se encontraron cookies de autenticación")
            return
        
        # Verificar si hay cookies con tiempo de expiración
        for key, value in cookies.items():
            if isinstance(value, str) and "expires" in value.lower():
                # Implementar lógica para verificar expiración
                logger.info(f"Cookie {key} podría expirar pronto")
    except Exception as e:
        logger.error(f"Error al verificar validez de cookies: {e}")

@app.route('/', methods=['GET'])
def index():
    """Página de inicio básica."""
    return """
    <html>
    <head>
        <title>Monitor de Tokens</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .links { margin-top: 20px; }
            .link-item { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Monitor de Tokens con Verificación de Notable Followers</h1>
        <p>El servidor está funcionando correctamente.</p>
        <div class="links">
            <div class="link-item"><a href="/dashboard">Ver Dashboard</a></div>
            <div class="link-item"><a href="/status">Ver Estado (JSON)</a></div>
        </div>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Manejador de webhook para recibir notificaciones de Helius."""
    try:
        notification = request.json
        logger.info(f"Notificación recibida: {json.dumps(notification)[:100]}...")
        
        # Actualizar estadísticas
        update_stats('notifications_received', increment=True)
        update_stats('last_notification_time', time.time())
        
        # Procesar la notificación en un hilo separado
        threading.Thread(target=process_notification, args=(notification,)).start()
        
        return jsonify({"status": "success", "message": "Notificación recibida y en procesamiento"}), 200
    except Exception as e:
        logger.error(f"Error al procesar notificación de webhook: {e}")
        update_stats('errors', increment=True)
        update_stats('last_error', str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

def process_notification(notification):
    """Procesa una notificación de webhook."""
    try:
        result = token_monitor.process_webhook_notification(notification)
        
        update_stats('tokens_processed', increment=True)
        
        if result:
            update_stats('last_processed_token', result['token_address'])
            
            if result['approved']:
                update_stats('tokens_approved', increment=True)
                logger.info(f"Token aprobado: {result['token_address']} (Usuario: {result['twitter_username']}, Notable followers: {result['notable_followers_count']})")
            else:
                update_stats('tokens_rejected', increment=True)
                logger.info(f"Token rechazado: {result['token_address']} (Usuario: {result['twitter_username']}, Notable followers: {result['notable_followers_count']})")
    except Exception as e:
        logger.error(f"Error al procesar notificación: {e}")
        update_stats('errors', increment=True)
        update_stats('last_error', str(e))

@app.route('/status', methods=['GET'])
def status():
    """Endpoint para verificar el estado del servidor."""
    uptime = time.time() - stats['start_time']
    uptime_str = str(timedelta(seconds=int(uptime)))
    
    return jsonify({
        "status": "online",
        "uptime": uptime_str,
        "stats": stats
    })

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Muestra un panel de control simple."""
    uptime = time.time() - stats['start_time']
    uptime_str = str(timedelta(seconds=int(uptime)))
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monitor de Tokens - Dashboard</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .stats { background: #f5f5f5; padding: 15px; border-radius: 5px; }
            .stat-item { margin-bottom: 10px; }
            .good { color: green; }
            .warning { color: orange; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Monitor de Tokens - Dashboard</h1>
        <div class="stats">
            <div class="stat-item"><strong>Estado:</strong> <span class="good">Online</span></div>
            <div class="stat-item"><strong>Tiempo de actividad:</strong> {{ uptime }}</div>
            <div class="stat-item"><strong>Notificaciones recibidas:</strong> {{ stats.notifications_received }}</div>
            <div class="stat-item"><strong>Tokens procesados:</strong> {{ stats.tokens_processed }}</div>
            <div class="stat-item"><strong>Tokens aprobados:</strong> {{ stats.tokens_approved }}</div>
            <div class="stat-item"><strong>Tokens rechazados:</strong> {{ stats.tokens_rejected }}</div>
            <div class="stat-item"><strong>Errores:</strong> {{ stats.errors }}</div>
            <div class="stat-item"><strong>Última notificación:</strong> {{ last_notification }}</div>
            <div class="stat-item"><strong>Último token procesado:</strong> {{ stats.last_processed_token }}</div>
            <div class="stat-item"><strong>Último error:</strong> {{ stats.last_error }}</div>
        </div>
    </body>
    </html>
    """
    
    last_notification = "Nunca"
    if stats['last_notification_time']:
        last_notification = datetime.fromtimestamp(stats['last_notification_time']).strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(html, stats=stats, uptime=uptime_str, last_notification=last_notification)

def signal_handler(sig, frame):
    """Manejador de señales para salida limpia."""
    logger.info("Deteniendo el servidor...")
    save_stats()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Servidor de webhook para monitoreo de tokens.")
    parser.add_argument("--port", type=int, default=PORT, help="Puerto para el servidor webhook")
    parser.add_argument("--host", default=HOST, help="Host para el servidor webhook")
    parser.add_argument("--debug", action="store_true", help="Ejecutar en modo debug")
    
    args = parser.parse_args()
    
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Cargar estadísticas previas
    load_stats()
    
    # Verificar que el módulo token_monitor funcione correctamente
    try:
        cookies = token_monitor.load_cookies_from_file()
        logger.info(f"Cookies cargadas correctamente: {len(cookies) if cookies else 0} cookies encontradas")
    except Exception as e:
        logger.error(f"Error al cargar cookies: {e}")
    
    # Verificar espacio en disco
    check_disk_space()
    
    # Iniciar thread de health check
    health_thread = threading.Thread(target=health_check, daemon=True)
    health_thread.start()
    
    logger.info(f"Iniciando servidor webhook en {args.host}:{args.port}...")
    
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 