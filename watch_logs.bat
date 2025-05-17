@echo off
echo Esperando nuevos logs...
echo Presiona Ctrl+C para salir
powershell -Command "Get-Content -Path 'webhook_server.log' -Wait" 