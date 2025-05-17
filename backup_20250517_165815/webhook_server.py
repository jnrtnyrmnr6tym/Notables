#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Webhook server to receive Helius notifications.
"""

from flask import Flask, request, jsonify
import logging
from token_monitor_with_notable_check import process_webhook_notification
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("WebhookServer")

# Añadir un print inicial para saber que el servidor está corriendo
print("\n" + "="*50)
print("Servidor webhook iniciado")
print("URLs disponibles:")
print("- http://127.0.0.1:3003/webhook")
print("- http://10.2.0.2:3003/webhook")
print("="*50 + "\n")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhooks from Helius."""
    try:
        print("\n" + "="*50)
        print("[DEBUG] Nueva petición recibida")
        print("[DEBUG] Headers:", dict(request.headers))
        print("[DEBUG] Método:", request.method)
        
        # Manejar la codificación de los datos recibidos
        try:
            data_str = request.get_data().decode('utf-8')
            print("[DEBUG] Datos recibidos:", data_str)
        except UnicodeDecodeError:
            print("[WARNING] Error decodificando datos como UTF-8, intentando con latin-1")
            data_str = request.get_data().decode('latin-1')
            print("[DEBUG] Datos recibidos (latin-1):", data_str)
        
        print("="*50 + "\n")
        
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error decodificando JSON: {str(e)}")
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400
            
        if not data:
            print("[ERROR] No se recibieron datos JSON")
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
            
        print("\n[INCOMING WEBHOOK] Nueva notificación recibida")
        print(f"[DEBUG] Datos recibidos: {json.dumps(data, indent=2)}")
        
        # Procesar la notificación
        result = process_webhook_notification(data)
        
        if result:
            # Formatear el mensaje para Telegram con manejo de codificación
            try:
                message = f"""🪙 New Token Detected!

👤 Creator: @{result['twitter_username']}
⭐ Notable Followers: {result['notable_followers_count']}

📝 Name: {result['name']}
🔤 Ticker: {result['symbol']}
🔗 Contract: {result['token_address']}"""
                
                print("\n" + "="*50)
                print(message)
                print("="*50 + "\n")
            except UnicodeEncodeError:
                # Fallback para Windows
                message = f"""New Token Detected!

Creator: @{result['twitter_username']}
Notable Followers: {result['notable_followers_count']}

Name: {result['name']}
Ticker: {result['symbol']}
Contract: {result['token_address']}"""
                
                print("\n" + "="*50)
                print(message)
                print("="*50 + "\n")
        else:
            print("[WARNING] No se pudo procesar la notificación")
        
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        print(f"[ERROR] Error procesando webhook: {str(e)}")
        print(f"[ERROR] Traceback completo:")
        import traceback
        traceback.print_exc()
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Start the webhook server
    print("Iniciando servidor webhook...")
    print("URLs disponibles:")
    print("- http://127.0.0.1:3003/webhook")
    print("- http://10.2.0.2:3003/webhook")
    print("\nEsperando notificaciones...\n")
    
    # Configurar el servidor para que use threading
    app.run(host='0.0.0.0', port=3003, debug=False, threaded=True) 