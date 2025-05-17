# Respaldo del Proyecto AXIOM - 17/05/2025 16:58:15

## Estado del Proyecto
Este respaldo contiene el estado funcional del proyecto AXIOM en la fecha indicada. El sistema está completamente operativo con las siguientes características:

- ✅ Procesamiento de webhooks de Helius
- ✅ Extracción de metadatos de tokens
- ✅ Verificación de notable followers
- ✅ Envío de notificaciones a Telegram
- ✅ Sistema de logging implementado
- ✅ Manejo de errores robusto

## Archivos Incluidos
- Scripts Python (*.py)
- Archivos de configuración (*.json)
- Documentación (*.md)
- Scripts de inicio (*.bat, *.sh)
- Archivos de texto (*.txt)

## Archivos Excluidos
- __pycache__
- .venv
- .git
- .pytest_cache
- logs
- screenshots
- cache
- .cursor

## Instrucciones para Restaurar
1. Copiar todos los archivos del respaldo a la ubicación deseada
2. Crear un entorno virtual nuevo:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Configurar variables de entorno en el archivo .env
5. Iniciar el servidor:
   ```
   python webhook_server.py
   ```

## Notas Importantes
- Este respaldo representa un punto de restauración seguro del proyecto
- Todos los archivos están en su estado funcional
- Las cookies de Protokols deben renovarse si han caducado
- El sistema está configurado para usar el canal de Telegram especificado

## Contacto
Para cualquier duda sobre este respaldo o el proyecto, consultar la documentación principal del proyecto. 