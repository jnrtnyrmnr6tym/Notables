#!/bin/bash

echo "Iniciando servidor de monitoreo de tokens..."
echo

# Crear directorio de logs si no existe
mkdir -p logs

# Iniciar el servidor
python3 deploy_webhook_server.py --port 5000

echo
echo "Servidor detenido." 