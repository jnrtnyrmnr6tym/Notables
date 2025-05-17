@echo off
echo Iniciando servidor de monitoreo de tokens...
echo.

:: Crear directorio de logs si no existe
if not exist logs mkdir logs

:: Iniciar el servidor
python deploy_webhook_server.py --port 5000

echo.
echo Servidor detenido.
pause 