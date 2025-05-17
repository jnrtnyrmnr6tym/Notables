# Scratchpad para el Proyecto de Monitoreo de Tokens en Solana

## Instrucciones para el Agente
⚠️ **IMPORTANTE**: Antes de realizar cualquier acción, el agente DEBE:

1. **Revisar el Estado Actual**:
   - Leer completamente la sección "Current Status / Progress Tracking"
   - Verificar las tareas pendientes en "Project Status Board"
   - Consultar "Lessons Learned" para evitar errores conocidos

2. **Proceso de Cookies de Protokols**:
   - SIEMPRE verificar el formato de las cookies antes de usarlas
   - Si hay errores 401, seguir el proceso documentado en "Lessons Learned"
   - NUNCA intentar modificar el formato de las cookies manualmente

3. **Manejo de Errores**:
   - Si se encuentra un error de codificación Unicode, consultar la sección de errores conocidos
   - Si hay problemas con las cookies, seguir el proceso de renovación documentado
   - SIEMPRE incluir información útil para debugging en la salida del programa

4. **Proceso de Pruebas**:
   - Probar primero en local antes de subir cambios al servidor
   - Verificar que las cookies estén frescas antes de cada prueba
   - Seguir el proceso de prueba documentado en "Plan de Acción"

5. **Documentación**:
   - Actualizar "Current Status" después de cada cambio
   - Documentar cualquier nuevo error o solución en "Lessons Learned"
   - Mantener el historial de cambios en "Resumen de la sesión"

## Background and Motivation
Hemos implementado un sistema de webhooks para detectar nuevos tokens en Solana y enviar notificaciones a Telegram. El sistema está diseñado para:
1. Recibir webhooks de Helius con información sobre nuevos tokens
2. Procesar la información del token, incluyendo metadatos y datos de notables
3. Enviar notificaciones formateadas a un canal de Telegram

## Cambio de estrategia: migración a canal de Telegram

Se decidió migrar el sistema para que las notificaciones se publiquen en un **canal de Telegram** en vez de enviarse a usuarios individuales. Esto centraliza la información, facilita la difusión y simplifica la arquitectura.

### Ventajas del canal
- Centralización y visibilidad pública de los resultados.
- Eliminación de la gestión de usuarios y filtros individuales.
- Menor complejidad y mantenimiento.
- Más fácil de compartir y viralizar.

## Cambios realizados

1. **Configuración**
   - Se agregó la variable `TELEGRAM_CHANNEL_ID` al archivo `.env` y a la configuración del bot.
   - Se eliminó la variable `TELEGRAM_CHANNEL` basada en username.

2. **Servicio de notificaciones**
   - Se eliminó toda la lógica de registro de usuarios, filtros y métodos relacionados.
   - Ahora, cada notificación se envía directamente al canal usando el `chat_id` configurado.
   - El formato de los mensajes y los botones de trading se mantiene igual.

3. **Código más simple y robusto**
   - Menos dependencias y menor riesgo de errores por gestión de usuarios.
   - El monitoreo sigue funcionando en tiempo real, pero ahora todo el canal recibe la misma información.

## Nuevo flujo
- El sistema detecta un nuevo token aprobado.
- Se genera el mensaje con la información relevante y los notables followers.
- El bot publica automáticamente el mensaje en el canal de Telegram configurado.

## Recomendaciones y próximos pasos
- Probar el sistema enviando un mensaje de ejemplo al canal para verificar permisos y formato.
- Limpiar comandos de usuario en los handlers si ya no se requieren (opcional).
- Documentar en el README el nuevo flujo y cómo configurar el canal.
- Si en el futuro se desea volver a notificaciones personalizadas, se puede restaurar la lógica eliminada.

---

¿Listo para probar el sistema en el canal o deseas limpiar los comandos de usuario antes?

## Requisitos Actualizados del Usuario

El usuario ha solicitado las siguientes funcionalidades adicionales:

1. **Filtrado personalizado por notable followers**:
   - ✅ Permitir al usuario seleccionar el número mínimo de notable followers (no solo el umbral fijo de 5)
   - ✅ Mostrar tokens que cumplan con el criterio personalizado

2. **Consulta directa de creadores**:
   - ✅ Permitir al usuario introducir una dirección de contrato (CA) o un nombre de usuario de Twitter
   - ✅ Devolver el número de notable followers del creador

3. **Integración con bots de trading**:
   - ✅ Añadir botones en los mensajes que redireccionen al usuario a su bot de Telegram de preferencia
   - ✅ Facilitar la compra directa de tokens a través de estos bots

4. **Despliegue simple para pruebas**:
   - ✅ Implementar la solución más sencilla para que el usuario pueda probar el sistema completamente funcional

## Implementación del Bot de Telegram

### Arquitectura Implementada

Hemos implementado el bot de Telegram con la siguiente arquitectura:

```
[Webhook Helius] --> [Procesador de Tokens] --> [Base de Datos] --> [Bot de Telegram] --> [Usuarios]
                           |                         ^                    |
                           v                         |                    v
                      [API Protokols] -------------- + ------------ [Notificaciones]
```

### Componentes Principales Implementados

1. **Servidor Core**: 
   - ✅ Mantiene la funcionalidad actual de recepción de webhooks y procesamiento de tokens
   - ✅ Almacena datos en la base de datos
   - ✅ Expone una API interna para que el bot pueda consultar información

2. **Bot de Telegram**:
   - ✅ Interfaz de usuario a través de Telegram
   - ✅ Procesa comandos de los usuarios
   - ✅ Envía notificaciones sobre nuevos tokens aprobados
   - ✅ Consulta datos al servidor core

3. **Base de Datos**:
   - ✅ Almacena información sobre tokens, creadores y notable followers
   - ✅ Guarda preferencias de usuarios y suscripciones
   - ✅ Mantiene registro de consultas y comandos

### Funcionalidades Implementadas

#### Comandos Básicos
- ✅ `/start` - Inicia el bot y muestra información de bienvenida
- ✅ `/help` - Muestra la lista de comandos disponibles
- ✅ `/status` - Muestra el estado actual del sistema

#### Consulta de Tokens
- ✅ `/token <dirección>` - Muestra información detallada sobre un token específico
- ✅ `/check <CA o username>` - Verifica los notable followers de un creador específico
- ✅ `/recent` - Muestra los tokens aprobados más recientes

#### Funcionalidades Personalizadas
- ✅ `/setfilter <número>` - Establece el número mínimo de notable followers para filtrar tokens
- ✅ Botones inline para redireccionar a bots de trading populares

#### Suscripciones y Notificaciones
- ✅ `/subscribe` - Suscribe al usuario para recibir notificaciones de nuevos tokens aprobados
- ✅ `/unsubscribe` - Cancela la suscripción a notificaciones

#### Administración
- ✅ `/admin stats` - Muestra estadísticas detalladas del sistema
- ✅ `/admin refresh` - Actualiza manualmente los datos de un creador
- ✅ `/admin broadcast` - Envía un mensaje a todos los usuarios suscritos

## Key Challenges and Analysis
1. Formato del Webhook:
   - El webhook debe tener un formato específico para ser procesado correctamente
   - La estructura actual espera un array con objetos que contienen 'type' y 'tokenTransfers'

2. Procesamiento de Datos:
   - Necesitamos obtener metadatos del token usando la API de Helius
   - Debemos procesar información de notables (followers importantes)
   - El sistema maneja diferentes tipos de tokens (Fungible, NonFungible)

3. Notificaciones de Telegram:
   - El mensaje debe tener un formato específico y atractivo
   - Incluye información crucial como nombre, símbolo, CA, creador y notables
   - Se envían imágenes del token cuando están disponibles

# High-level Task Breakdown
1. ✅ Implementación del procesamiento de webhooks
2. ✅ Integración con API de Helius para metadatos
3. ✅ Sistema de notificaciones de Telegram
4. ✅ Manejo de errores y logging
5. ✅ Formato de mensajes optimizado

# Project Status Board
- [x] Procesamiento básico de webhooks
- [x] Obtención de metadatos de tokens
- [x] Formato de mensajes de Telegram
- [x] Envío de notificaciones
- [x] Manejo de errores
- [x] Logging del sistema

# Executor's Feedback or Assistance Requests
El sistema está funcionando correctamente con el siguiente flujo:
1. Recibe webhook de ejemplo
2. Procesa la información del token
3. Obtiene metadatos y datos de notables
4. Formatea y envía el mensaje a Telegram

# Lessons
1. El formato del webhook es crítico para el funcionamiento del sistema
2. Es importante mantener el formato exacto del mensaje de Telegram
3. Los logs son esenciales para el debugging
4. La estructura del webhook debe ser un array con objetos específicos
5. El manejo de errores debe ser robusto para cada paso del proceso

# Current Status / Progress Tracking
El sistema está funcionando correctamente con las siguientes características:
- Procesamiento de webhooks de Helius
- Obtención de metadatos de tokens
- Formato de mensajes de Telegram optimizado
- Sistema de logging implementado
- Manejo de errores robusto

# Next Steps
1. Crear un branch para mantener el código seguro
2. Documentar el código con comentarios detallados
3. Considerar la implementación de tests unitarios
4. Evaluar la posibilidad de agregar más funcionalidades

## Análisis de Problemas Actuales

Después de analizar el sistema y las pruebas realizadas, hemos identificado los siguientes problemas:

1. **Problema con las cookies de Protokols**: Las cookies de autenticación para la API de Protokols han caducado, lo que impide la verificación en tiempo real de los notable followers.

2. **Error de codificación en las notificaciones**: Hay un error de codificación de caracteres Unicode en el servicio de notificaciones (`UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'`).

## Plan de Optimización para Tokens Nuevos

### Objetivo
Optimizar el proceso de obtención de metadatos para tokens nuevos, enfocándonos en velocidad máxima y procesamiento en tiempo real.

### Tareas de Alto Nivel

1. **Optimización del Webhook Handler** ✅
   - [x] Modificar el handler para extraer metadatos directamente del webhook
   - [x] Implementar validación de datos del webhook
   - [x] Añadir logging detallado para debugging

2. **Optimización de Llamadas a API** ✅
   - [x] Eliminar reintentos innecesarios
   - [x] Configurar timeout corto (5 segundos)
   - [x] Simplificar manejo de errores

3. **Mejoras de Rendimiento**
   - [ ] Optimizar el procesamiento de datos en memoria
   - [ ] Implementar procesamiento asíncrono
   - [ ] Añadir métricas de rendimiento

### Criterios de Éxito
- Tiempo de procesamiento < 1 segundo por token
- Tasa de éxito > 99.9% en la obtención de metadatos
- Logging detallado para debugging
- Manejo robusto de errores

### Plan de Implementación

1. **Fase 1: Optimización del Webhook** ✅
   - Modificar `test_webhook_local.py` para procesar datos del webhook
   - Implementar validación de datos
   - Añadir logging detallado

2. **Fase 2: Optimización de APIs** ✅
   - Eliminar reintentos innecesarios
   - Configurar timeout corto
   - Simplificar manejo de errores

3. **Fase 3: Mejoras de Rendimiento**
   - Implementar procesamiento asíncrono
   - Optimizar uso de memoria
   - Añadir métricas

### Métricas de Monitoreo
- Tiempo de procesamiento por token
- Tasa de éxito en obtención de metadatos
- Uso de memoria

## Estado Actualizado del Sistema

Según la información proporcionada por el usuario, se confirma que:

- ✅ **Helius está funcionando correctamente**: El sistema está recibiendo correctamente los webhooks de Helius con información sobre nuevos tokens.
- ✅ **El endpoint del webhook está funcionando**: El sistema está recibiendo correctamente las notificaciones.
- ✅ **La funcionalidad core está probada y funciona**: Todo el sistema ha sido probado y funciona correctamente en su lógica principal.

El problema principal ahora es hacer que el sistema funcione correctamente en Telegram, específicamente:

1. Mantener activas las cookies de Protokols después de un login manual
2. Solucionar el error de codificación en las notificaciones de Telegram

## Plan de Acción para Configuración y Prueba del Sistema

### 1. Configuración de Helius y Webhook
- **Objetivo**: Asegurar que Helius esté correctamente configurado y enviando webhooks
- **Acciones**:
  1. Verificar la configuración actual:
     - API key de Helius: `133cc99a-6f02-4783-9ada-c013a79343a6`
     - Endpoint del webhook: `http://127.0.0.1:5000/webhook`
     - Eventos configurados: `TOKEN_MINT`, `TOKEN_TRANSFER`
  2. Probar el webhook localmente:
     - Usar `test_webhook_local.py` para simular notificaciones
     - Verificar que el servidor recibe y procesa correctamente
     - Confirmar que los datos se almacenan en la base de datos
  3. Configurar el webhook en Helius:
     - Usar el endpoint público (necesitamos configurar ngrok o similar)
     - Verificar que Helius puede acceder al endpoint
     - Confirmar que las notificaciones llegan correctamente

### 2. Prueba del Sistema de Notificaciones
- **Objetivo**: Verificar que las notificaciones lleguen correctamente al canal de Telegram
- **Acciones**:
  1. Configurar el bot de Telegram:
     - Token del bot: `7845358074:AAHGF0KGHmfC7khO3zrcLxo1zwzcQhEz5bw`
     - Verificar permisos del bot en el canal
     - Confirmar que el bot puede enviar mensajes
  2. Probar el flujo completo:
     - Simular la creación de un nuevo token usando `test_webhook_local.py`
     - Verificar que se procesa correctamente
     - Confirmar que la notificación llega al canal
  3. Verificar el formato de las notificaciones:
     - Comprobar que los emojis se muestran correctamente
     - Verificar que los botones funcionan
     - Confirmar que los enlaces son válidos

### 3. Monitoreo y Logging
- **Objetivo**: Implementar un sistema de monitoreo para detectar problemas
- **Acciones**:
  1. Configurar logging detallado:
     - Archivo de log: `token_monitor.log`
     - Nivel de log: DEBUG
     - Formato: `%(asctime)s [%(levelname)s] %(message)s`
  2. Establecer alertas:
     - Monitorear errores en el procesamiento de webhooks
     - Verificar la salud del sistema
     - Registrar métricas de rendimiento

## Criterios de Éxito
1. Helius envía webhooks correctamente al sistema
2. El sistema procesa los webhooks y extrae la información necesaria
3. Las notificaciones llegan al canal de Telegram con el formato correcto
4. Los botones y enlaces en las notificaciones funcionan correctamente
5. El sistema maneja correctamente los errores y excepciones
6. Los logs proporcionan información útil para debugging

## Próximos Pasos
1. Iniciar el servidor webhook local:
   ```bash
   python webhook_server.py
   ```
2. Probar el webhook localmente:
   ```bash
   python test_webhook_local.py
   ```
3. Configurar ngrok para exponer el servidor local:
   ```bash
   ngrok http 5000
   ```
4. Actualizar el webhook en Helius con la URL de ngrok
5. Monitorear los logs para detectar posibles problemas
6. Realizar ajustes según sea necesario

## Project Status Board

### Completed Tasks
- [x] Implement token monitoring system
- [x] Extract information from IPFS
- [x] Verify notable followers
- [x] Create basic structure for Telegram bot
- [x] Implement token query command
- [x] Implement recent tokens command
- [x] Implement notification system
- [x] Add trading bot links
- [x] Implement user filtering system
- [x] Add token image to notifications
- [x] Update message format to include all requested fields
- [x] Add fallback values for missing fields
- [x] Optimize webhook handler for direct metadata extraction
- [x] Implement detailed logging system
- [x] Add data validation for webhook processing
- [x] Simplify API calls for maximum speed
- [x] Configure short timeouts
- [x] Implement asynchronous processing
- [x] Add performance metrics tracking
- [x] Optimize memory usage

### Pending Tasks
- [ ] Improve session maintenance system for Protokols
- [ ] Fix encoding errors in notifications
- [ ] Conduct comprehensive testing of Telegram system
- [ ] Implement additional error handling for missing fields
- [ ] Add image preview in Telegram messages
- [ ] Optimize notification delivery system
- [ ] Add rate limiting for API calls

## Current Status / Progress Tracking

- **Última actualización**: 2025-05-17
- **Estado actual**: El script ha dejado de funcionar correctamente al procesar el webhook proporcionado. Se ha identificado que los cambios realizados para soportar CA personalizados han alterado el formato esperado del webhook, lo que impide la extracción de metadatos del token.
- **Acciones inmediatas**:
  1. Revertir los cambios en la función `test_with_ca` y cualquier modificación relacionada con el manejo de CA personalizados.
  2. Restaurar el webhook de ejemplo original para garantizar que el flujo de procesamiento funcione como antes.
  3. Verificar que el script procese correctamente el webhook de ejemplo y envíe el mensaje a Telegram.
- **Próximos pasos**:
  - Revisar el log completo (`webhook_test.log`) para identificar cualquier error adicional.
  - Considerar la implementación de un mecanismo de validación de formato de webhook para evitar errores similares en el futuro.
  - Documentar las lecciones aprendidas en la sección "Lessons Learned".

## Executor's Feedback or Assistance Requests
- Se ha completado la optimización del webhook handler
- Se ha implementado un sistema de logging detallado
- Se ha mejorado la validación de datos
- Se ha simplificado el código para máxima velocidad
- Se ha implementado procesamiento asíncrono para mejor rendimiento
- Se han añadido métricas de rendimiento
- Se necesita probar el sistema con tokens reales para verificar el rendimiento
- Se recomienda probar el sistema con múltiples tokens para validar el procesamiento asíncrono

## Lessons Learned
1. **Formato de Cookies de Protokols**:
   - Las cookies de Protokols DEBEN estar en formato de lista de objetos (como las exporta Playwright)
   - El formato incorrecto (diccionario) causa errores de "string indices must be integers"
   - Para obtener cookies frescas:
     1. Ejecutar `get_protokols_cookies_playwright.py`
     2. Iniciar sesión manualmente en la ventana del navegador
     3. Presionar ENTER cuando se vea el perfil
     4. Las cookies se guardarán automáticamente en el formato correcto
   - Verificar periódicamente que las cookies no hayan caducado
   - Si hay errores 401, renovar las cookies siguiendo el proceso anterior

2. **Actualización de test_cookies y manejo de cookies**:
   - El cambio en la función test_cookies para usar ProtokolsSessionManager y el ajuste en el formato del parámetro input solo afecta la verificación manual de cookies (opción --test). No afecta el flujo de producción ni el procesamiento de tokens, webhooks o notificaciones.
   - Centralizar el manejo de cookies con ProtokolsSessionManager mejora la robustez y previene errores de formato, sin modificar la lógica de negocio principal.

3. **Conversión automática de cookies para requests**:
   - El sistema ahora convierte automáticamente la lista de cookies exportada por Playwright a un diccionario `{name: value}` compatible con la librería `requests`.
   - Esto soluciona el error `list indices must be integers or slices, not dict` y permite que la autenticación y las consultas a la API de Protokols funcionen correctamente.
   - La función de test (`--test`) y el flujo principal usan este formato, garantizando robustez y compatibilidad.

## Executor's Feedback or Assistance Requests
- Se ha completado la optimización del webhook handler
- Se ha implementado un sistema de logging detallado
- Se ha mejorado la validación de datos
- Se ha simplificado el código para máxima velocidad
- Se ha implementado procesamiento asíncrono para mejor rendimiento
- Se han añadido métricas de rendimiento
- Se necesita probar el sistema con tokens reales para verificar el rendimiento
- Se recomienda probar el sistema con múltiples tokens para validar el procesamiento asíncrono

## Lessons
- Las cookies de autenticación para APIs externas pueden caducar y necesitan ser mantenidas activas
- Es importante verificar que todas las rutas del servidor web estén correctamente definidas y registradas
- Para probar webhooks localmente, es útil crear scripts de simulación que envíen datos de prueba
- La API de Helius es más confiable para monitoreo de tokens que soluciones anteriores
- El procesamiento asíncrono de notificaciones mejora la capacidad de respuesta del servidor
- Incluir información útil para depuración en la salida del programa
- Leer el archivo antes de intentar editarlo
- Verificar vulnerabilidades que aparecen en la terminal ejecutando npm audit antes de continuar
- Siempre preguntar antes de usar el comando git -force
- Implementar un sistema de caché reduce significativamente las consultas a APIs externas y mejora el rendimiento
- Windows tiene problemas específicos con la codificación de caracteres Unicode en la consola
- Es crucial probar el sistema en el mismo entorno donde se ejecutará en producción
- Mantener el manejo de errores existente
- Asegurar que las cookies de sesión sean válidas
- Implementar delays entre requests para evitar rate limiting

# Resumen de la sesión (Contabo, Bot de Telegram y entorno)

## Pasos realizados hoy

1. **Configuración del servidor Contabo**
   - Acceso por SSH y creación de usuario `botuser`.
   - Instalación de dependencias del sistema y Python.
   - Creación y activación de entorno virtual Python (`venv`).

2. **Transferencia y organización del proyecto**
   - Subida de archivos y carpetas del proyecto (`token-bot`, `telegram_bot`, etc.).
   - Separación de requirements: uno para Flask/API web y otro para el bot de Telegram.

3. **Gestión de dependencias**
   - Instalación de dependencias para Flask en `requirements.txt` (raíz).
   - Creación y uso de `telegram_bot/requirements.txt` para el bot:
     ```
     python-telegram-bot==13.15
     requests==2.32.3
     python-dotenv==1.0.1
     solana==0.31.0
     ```
   - Resolución de conflictos de dependencias entre `python-telegram-bot` y `solana`.

4. **Adaptación del código del bot**
   - Migración del bot a la sintaxis de `python-telegram-bot==13.15` (uso de `Updater`, `Dispatcher`, sin async/await).
   - Inserción del token real de Telegram en el código.
   - Ejemplo de código base en inglés proporcionado y adaptado.

5. **Configuración de Supervisor**
   - Creación de archivos `.conf` para `protokols-session` y `telegram-bot`.
   - Solución de errores de rutas, permisos y logs.
   - Reinicio y verificación de servicios con `sudo supervisorctl status`.

6. **Depuración de errores**
   - Solución de errores por falta de módulos (`requests`, `telegram`, etc.).
   - Solución de errores por conflictos de dependencias y archivos mal ubicados.
   - Verificación de logs y corrección de errores de importación.

7. **Pruebas y recomendaciones**
   - Prueba del bot en local antes de subir cambios al servidor.
   - Confirmación de que ambos servicios (`protokols-session` y `telegram-bot`) están en RUNNING.
   - Recomendación de mantener requirements separados para evitar conflictos.

## Notas importantes
- El error principal NO fue solo por el token, sino por conflictos de dependencias entre librerías.
- El entorno de Flask/API web y el del bot de Telegram deben mantenerse separados para evitar problemas.
- El bot de Telegram ahora funciona con la versión 13.15, que es compatible con Solana 0.31.0.
- Puedes cerrar la terminal SSH de Contabo sin problema, los servicios seguirán funcionando.
- Para futuras modificaciones, prueba siempre primero en local y luego sube los cambios al servidor.

## Próximos pasos sugeridos
- Si quieres usar versiones modernas de las librerías, deberás separar los entornos virtuales.
- Si quieres agregar comandos personalizados al bot, puedes hacerlo sobre la base del código actual.
- Para revisar logs en el futuro:
  ```bash
  tail -f ~/token-bot/logs/telegram_bot.log
  tail -f ~/token-bot/logs/protokols_session.log
  ```
- Para reiniciar servicios:
  ```bash
  sudo systemctl restart supervisor
  sudo supervisorctl status
  ```

---

**Todo lo realizado está documentado aquí para que puedas retomarlo fácilmente mañana.**

## Resumen y Notas: Extracción de Notable Followers de @ironspiderXBT (Protokols)

### Resumen del Proceso

1. **Objetivo**: Obtener la lista de notables followers ("smart followers") de la cuenta de Twitter @ironspiderXBT usando la API de Protokols.

2. **Desafío Inicial**: La API de Protokols había cambiado y los endpoints antiguos devolvían errores 404 o 400. Además, la documentación pública no reflejaba los endpoints actuales para obtener la lista de notables followers.

3. **Solución**:
   - Se utilizó Playwright para capturar el tráfico de red real de la web de Protokols mientras se navegaba por la lista de notables followers.
   - Se identificó el endpoint correcto: `smartFollowers.getPaginatedSmartFollowers`.
   - Se ajustó el script `get_top_notable_followers.py` para usar este endpoint, pasando los parámetros correctos (`username`, `limit`, `sortBy`, `sortOrder`, `cursor`).
   - Se corrigió un error de tipo en el parámetro `cursor` (de `null` a `0`).
   - Se implementó logging detallado para depuración y manejo de errores.

4. **Resultado**:
   - El script ahora obtiene correctamente la lista de notables followers de @ironspiderXBT.
   - Se guardó la lista de los primeros 20 notables followers en el archivo `notable_followers_ironspiderXBT.json`.
   - Entre los primeros 5 notables followers se encuentra el usuario `@orangie`.

### Notas Técnicas

- El endpoint correcto requiere el parámetro `cursor` como número entero (0 para la primera página).
- El script utiliza cookies de sesión válidas exportadas desde el navegador para autenticarse.
- El logging detallado permite identificar rápidamente problemas de autenticación, estructura de respuesta o parámetros.
- El script puede adaptarse fácilmente para paginar y obtener la lista completa de notables followers (hasta 215 en este caso).

### Lecciones Aprendidas

- Es fundamental analizar el tráfico real de la web cuando la documentación de la API no está actualizada.
- Los endpoints pueden requerir parámetros estrictos de tipo (por ejemplo, `cursor: 0` y no `null`).
- El manejo de errores y el logging detallado son clave para depurar integraciones con APIs de terceros.

### Siguiente Paso

- Si se requiere la lista completa de notables followers, basta con paginar usando el parámetro `cursor`.
- El archivo `notable_followers_ironspiderXBT.json` contiene los primeros 20 notables followers extraídos exitosamente.

---

## Auditoría de Seguridad: Claves, Tokens y Datos Sensibles

### Estado actual
- Todos los scripts principales de producción (`token_monitor_with_notable_check.py`, `telegram_bot/utils/config.py`, etc.) ya NO exponen claves, tokens ni secretos en el código fuente. Ahora usan variables de entorno y la librería `python-dotenv`.
- Los scripts de pruebas, utilidades y ejemplos que contenían claves de ejemplo han sido movidos a la carpeta `archive/` y no afectan el flujo de producción.
- No se detectaron contraseñas ni secretos de bases de datos en los scripts principales.

### Recomendaciones
- Mantener SIEMPRE las claves y tokens en variables de entorno, nunca en el código fuente.
- No subir el archivo `.env` a repositorios públicos o compartidos.
- Si algún script auxiliar vuelve a producción, revisarlo antes para asegurar que no exponga datos sensibles.
- Si alguna clave/token fue expuesta, rotarla en el proveedor correspondiente.
- Usar un archivo `.env.example` como plantilla para compartir la estructura de variables necesarias sin exponer valores reales.

### Estado: Cumplido ✅

- El script `protokols_download_notable_followers.py` ha sido creado. Permite descargar la lista completa de followers notables de un usuario de Twitter usando la API de Protokols, manejando la paginación y guardando los resultados en un archivo CSV. 
- El usuario debe asegurarse de tener el archivo `protokols_cookies.json` válido en el directorio raíz.
- Para usarlo: `python protokols_download_notable_followers.py <twitter_username> [output_file.csv]`
- El script reporta el progreso y el total de followers descargados.

¿Deseas probarlo ahora o necesitas algún ajuste adicional?

---

## Limitaciones del script rápido de notables

- El script rápido solo permite acceder a:
  - El número total de notables (notable followers) de un usuario objetivo (contando los elementos paginados).
  - La lista de notables (y sus métricas individuales, si se desea).
- **No permite acceder a ninguna otra métrica del usuario objetivo** (followersCount, KOL score, descripción, avatar, engagement, etc.).
- Toda la información adicional del usuario objetivo solo está disponible (cuando funciona) en el endpoint `influencers.getFullTwitterKolInitial`.
- Si ese endpoint falla, no hay forma de obtener esas métricas a través de Protokols.

**Resumen:**
- El script rápido es robusto para saber cuántos notables tiene un usuario y quiénes son, pero no para obtener datos generales del usuario objetivo.

## Mejoras recientes en el script rápido de notables

- El script ahora muestra el número de seguidores de los notables en formato compacto (ej: 300k, 3M).
- El usuario ha confirmado que le gusta el resultado y desea guardar todo el progreso y la configuración actual.

## Plan de Implementación para Nuevos Campos de Token

### Objetivos
1. Incluir información adicional de los tokens en las notificaciones del webhook
2. Mantener la compatibilidad con el sistema existente
3. Asegurar que la información se presente de manera clara y organizada

### Análisis Técnico
1. **Fuente de Datos**:
   - Los metadatos del token se obtienen actualmente del webhook de Helius
   - La información adicional se puede extraer de la respuesta de la API de Protokols
   - Necesitamos asegurarnos de que todos los campos estén disponibles antes de procesar

2. **Consideraciones**:
   - Algunos tokens pueden no tener todos los campos disponibles
   - Debemos manejar casos donde falte información
   - La imagen del token debe ser accesible públicamente

### Plan de Implementación

1. **Modificación del Procesador de Webhook**
   - [ ] Actualizar la función de procesamiento de webhook para extraer campos adicionales
   - [ ] Implementar validación de campos requeridos
   - [ ] Añadir manejo de errores para campos faltantes

2. **Actualización del Formato de Notificación**
   - [ ] Rediseñar el formato de mensaje para incluir nuevos campos
   - [ ] Implementar formato condicional para campos opcionales
   - [ ] Añadir enlaces a la imagen del token

3. **Pruebas y Validación**
   - [ ] Crear casos de prueba para diferentes escenarios
   - [ ] Verificar el formato de las notificaciones
   - [ ] Probar con tokens reales

### Criterios de Éxito
1. Las notificaciones incluyen todos los campos solicitados
2. El sistema maneja correctamente casos donde faltan campos
3. Las imágenes de los tokens se muestran correctamente
4. El formato de las notificaciones es claro y legible

# Configuración del Servidor de Monitoreo de Tokens

## Estado Actual
- Servidor webhook funcionando en puerto 3003
- Nginx configurado como proxy inverso
- Servicio systemd configurado y activo
- Logs configurados en `/var/www/token_monitor/logs`

## Estructura de Archivos
```
/var/www/token_monitor/
├── deploy_webhook_server.py
├── token_monitor_with_notable_check.py
├── protokols_session_manager.py
├── protokols_cookies.json
├── .env
├── logs/
└── venv/
```

## Configuración de Servicios
1. Nginx:
   - Configurado en `/etc/nginx/sites-available/token_monitor`
   - Proxy inverso al puerto 3003
   - Accesible en puerto 80

2. Systemd:
   - Servicio: `token_monitor.service`
   - Configurado para iniciar automáticamente
   - Usuario: www-data

## Endpoints Disponibles
- Panel de control: `http://localhost:3003/`
- Estado del servidor: `http://localhost:3003/status`
- Dashboard: `http://localhost:3003/dashboard`
- Webhook: `http://localhost:3003/webhook`

## Próximos Pasos
1. Configurar webhook en Helius
2. Probar monitoreo de tokens
3. Configurar alertas/notificaciones
4. Verificar integración con Protokols

## Notas Importantes
- El servidor está corriendo como servicio systemd
- Los logs se guardan en `/var/www/token_monitor/logs`
- Las cookies de Protokols se guardan en `protokols_cookies.json`
- La API key de Helius debe estar en el archivo `.env`

## Comandos Útiles
```bash
# Ver estado del servicio
systemctl status token_monitor

# Ver logs del servicio
journalctl -u token_monitor -n 50

# Reiniciar servicio
systemctl restart token_monitor

# Ver logs de Nginx
tail -f /var/log/nginx/error.log
```

# Resumen de la sesión: Optimización y análisis del script rápido de notables (junio 2024)

## 1. Optimización del script rápido
- Se identificó que el endpoint `smartFollowers.getPaginatedSmartFollowers` de Protokols devuelve el campo `overallCount` en la respuesta, que corresponde al total de notables followers.
- Se modificó el script rápido para que solo haga **una petición** con `limit=5`, extrayendo:
  - El top 5 de notables followers (array `items`)
  - El total de notables (`overallCount`)
- El script ahora es ultra-rápido y robusto, sin necesidad de paginar ni hacer múltiples requests.

## 2. Comparación con el script general
- El script general, en versiones anteriores, podía usar otros endpoints o paginar para obtener el total, lo que lo hacía más lento y propenso a fallos.
- Se recomienda unificar ambos scripts para que usen el método rápido: una sola petición al endpoint de notables, extrayendo el top N y el total de `overallCount`.

## 3. Qué datos se pueden obtener con el script rápido
- Solo se pueden obtener datos de los notables followers:
  - username, displayName, avatarUrl, followersCount, tags, kolScore, smartFollowersCount, followedAt, etc.
  - Estadísticas agregadas: overallCount, projectCount, kolCount, vcCount, founderCount, otherCount.
- **No se pueden obtener datos del usuario objetivo** (followers, bio, avatar, engagement, etc.) con este endpoint.
- Para datos del usuario objetivo, es necesario usar el endpoint `influencers.getFullTwitterKolInitial`, que es más lento y menos robusto.

## 4. Limitaciones y recomendaciones
- El método rápido es ideal para monitoreo masivo y alertas, por su velocidad y robustez.
- El método combinado (usando ambos endpoints) permite análisis más completos, pero introduce más latencia y posibilidad de fallos.
- Se recomienda documentar y mantener ambos enfoques según el caso de uso.

## 5. Próximos pasos sugeridos
- Unificar la lógica de obtención de notables en todos los scripts del proyecto.
- Si se requiere información del usuario objetivo, implementar manejo de errores y fallback para el endpoint adicional.
- Mantener este resumen como referencia para futuras optimizaciones y troubleshooting.

# [Actualización junio 2024] Integración definitiva del script rápido de notables en el monitor de tokens

### Cambios realizados
- Eliminada completamente la función interna `get_notable_followers` y todas sus llamadas en `token_monitor_with_notable_check.py`.
- Ahora **toda la lógica de obtención de notables** se realiza exclusivamente a través de la función `get_notables` importada de `protokols_smart_followers_fast.py`.
- El resultado de `get_notables` (total y top 5 notables) se utiliza tanto en el procesamiento de tokens como en la respuesta a webhooks y endpoints de la API.
- Se garantiza que no queda código legacy ni duplicado para la obtención de notables followers.

### Ventajas
- **Centralización y mantenibilidad:** Si la API de Protokols cambia, solo hay que actualizar el script rápido.
- **Eficiencia:** El monitor es más rápido y robusto, sin duplicidad de código ni riesgo de desincronización.
- **Transparencia:** El resultado incluye tanto el total como el top de notables followers, facilitando la integración con Telegram y otros sistemas.

### Estado actual
- ✅ El monitor de tokens usa exclusivamente el script rápido para notables.
- ✅ No quedan llamadas a la función antigua.
- ✅ El sistema está listo para pruebas y futuras optimizaciones.

### Próximos pasos sugeridos
- Probar el flujo completo con tokens reales y verificar la integración con Telegram.
- Documentar en el README que la única forma recomendada de obtener notables es usando el script rápido centralizado.
- Mantener este patrón en todos los componentes del proyecto.

---

## Análisis Detallado del Campo Data

1. **Ubicación de la Instrucción**:
   - Se encuentra en `instructions[1].innerInstructions[7]`
   - `programId`: "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
   - `data`: "ACPcWCwiYQeZb9rB2qFwisRQ8rLpvHbZ5TR5RWFXkGsWyPVsZSjRrBMqxHC3vnZfy3Y3KJfeVUeEMG4brTDj5wfwcpkRCvXuhF7cUC45G5sZipHcTfkJh38zUSk1hV1USCpviWa5q2aRi3HSZbNE1hCkz3DSf"

2. **Características del Campo Data**:
   - Longitud: 157 caracteres
   - Contiene solo caracteres base64 válidos (A-Z, a-z, 0-9, +, /)
   - No tiene padding (=) al final
   - El error de padding sugiere que necesitamos añadir 3 caracteres de padding

3. **Estrategia de Decodificación**:
   - Añadir padding al final: "ACPcWCwiYQeZb9rB2qFwisRQ8rLpvHbZ5TR5RWFXkGsWyPVsZSjRrBMqxHC3vnZfy3Y3KJfeVUeEMG4brTDj5wfwcpkRCvXuhF7cUC45G5sZipHcTfkJh38zUSk1hV1USCpviWa5q2aRi3HSZbNE1hCkz3DSf==="
   - Intentar decodificar con el padding añadido
   - Si falla, buscar patrones de URI directamente en el string

4. **Plan de Implementación**:
   - [ ] Modificar la función `try_decode_metaplex_data` para:
     1. Añadir padding automáticamente si falta
     2. Intentar decodificar con el padding
     3. Si falla, buscar patrones de URI directamente
   - [ ] Implementar manejo de errores robusto
   - [ ] Añadir logging detallado para debugging

### Próximos Pasos Inmediatos
1. Modificar el script `test_webhook.py` para implementar la nueva estrategia de decodificación
2. Probar con el JSON actual
3. Verificar la extracción de metadatos

---

### Plan de Refactorización

1. **Reorganización de la Estructura del Proyecto**
   - [ ] Crear una estructura de directorios más clara:
     ```
     /src
       /api
         - helius.py
         - protokols.py
       /services
         - token_service.py
         - notification_service.py
       /models
         - token.py
         - notable.py
       /utils
         - logging.py
         - config.py
     /tests
       /unit
       /integration
     ```

2. **Mejoras en el Manejo de Configuración**
   - [ ] Crear una clase `Config` centralizada para manejar todas las variables de entorno
   - [ ] Implementar validación de configuración al inicio
   - [ ] Añadir tipos para las configuraciones

3. **Optimización del Procesamiento de Tokens**
   - [ ] Crear una clase `TokenProcessor` que encapsule toda la lógica de procesamiento
   - [ ] Implementar un sistema de caché para metadatos de tokens
   - [ ] Añadir validación de datos más robusta

4. **Mejoras en el Sistema de Notificaciones**
   - [ ] Crear una clase `NotificationService` para manejar todos los tipos de notificaciones
   - [ ] Implementar un sistema de colas para notificaciones
   - [ ] Añadir retry logic para envíos fallidos

5. **Mejoras en el Logging y Monitoreo**
   - [ ] Implementar un sistema de logging estructurado
   - [ ] Añadir métricas de rendimiento
   - [ ] Crear un dashboard de monitoreo

6. **Tests y Documentación**
   - [ ] Añadir tests unitarios para cada componente
   - [ ] Implementar tests de integración
   - [ ] Mejorar la documentación del código
   - [ ] Crear guías de contribución

### Criterios de Éxito para la Refactorización
- Código más mantenible y testeable
- Mejor manejo de errores y logging
- Documentación completa
- Tests con cobertura > 80%
- Tiempo de respuesta < 500ms

### Plan de Implementación por Fases

#### Fase 1: Estructura Base
1. [ ] Crear nueva estructura de directorios
2. [ ] Implementar sistema de configuración
3. [ ] Configurar logging estructurado

#### Fase 2: Core Services
1. [ ] Refactorizar procesamiento de tokens
2. [ ] Implementar sistema de notificaciones
3. [ ] Añadir sistema de caché

#### Fase 3: Testing y Documentación
1. [ ] Implementar tests unitarios
2. [ ] Añadir tests de integración
3. [ ] Mejorar documentación

#### Fase 4: Monitoreo y Optimización
1. [ ] Implementar métricas de rendimiento
2. [ ] Crear dashboard de monitoreo
3. [ ] Optimizar rendimiento

### Riesgos y Mitigación
1. **Riesgo**: Tiempo de inactividad durante la refactorización
   - **Mitigación**: Implementar cambios gradualmente y mantener sistema actual funcionando

2. **Riesgo**: Pérdida de datos durante la migración
   - **Mitigación**: Implementar backups y validaciones

3. **Riesgo**: Problemas de compatibilidad con APIs externas
   - **Mitigación**: Mantener versiones anteriores de integraciones

### Próximos Pasos Inmediatos
1. Crear nueva estructura de directorios
2. Implementar sistema de configuración
3. Comenzar con la refactorización del procesamiento de tokens

---