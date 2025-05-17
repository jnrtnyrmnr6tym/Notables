@echo off
start /B pythonw webhook_server.py
echo Servidor iniciado en segundo plano en el puerto 3003
echo URLs disponibles:
echo - http://127.0.0.1:3003/webhook
echo - http://10.2.0.2:3003/webhook 