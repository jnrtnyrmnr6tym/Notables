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
El proyecto consiste en un script que procesa webhooks de tokens, obtiene metadatos desde IPFS, verifica seguidores notables y envía notificaciones a Telegram.

## Current Status / Progress Tracking
- ✅ Script principal `test_webhook_local.py` funcionando correctamente
- ✅ Procesamiento de webhooks operativo
- ✅ Extracción de metadatos desde IPFS funcionando
- ✅ Obtención de seguidores notables operativa
- ✅ Envío de mensajes e imágenes a Telegram funcionando
- ✅ Sistema de logging configurado y operativo

## Project Status Board
- [x] Procesamiento de webhooks
- [x] Extracción de metadatos
- [x] Obtención de seguidores notables
- [x] Envío a Telegram
- [x] Manejo de errores
- [x] Logging

## Lessons
- El código actual está funcionando correctamente y no requiere optimizaciones
- Las cookies de Protokols funcionan mejor con la implementación actual
- El sistema de logging actual es útil para debugging
- Los timeouts actuales son apropiados para el funcionamiento del sistema

## Executor's Feedback or Assistance Requests
No se requieren cambios en este momento. El sistema está funcionando según lo esperado.

## Key Challenges and Analysis
- El sistema maneja correctamente los errores en cada etapa
- La integración con Telegram funciona correctamente, incluyendo el envío de imágenes
- El procesamiento de cookies de Protokols es robusto
- Los logs proporcionan información útil para debugging

## High-level Task Breakdown
1. **Documentación del Sistema Actual** ✅
   - [x] Documentar el flujo completo
   - [x] Identificar componentes críticos
   - [x] Registrar configuraciones exitosas

2. **Optimización de Componentes** 🔄
   - [ ] Implementar caché para metadatos de IPFS
   - [ ] Optimizar llamadas a Protokols
   - [ ] Mejorar manejo de rate limits

3. **Mejoras de Escalabilidad**
   - [ ] Implementar procesamiento asíncrono
   - [ ] Añadir sistema de colas
   - [ ] Optimizar uso de memoria

4. **Monitoreo y Métricas**
   - [ ] Implementar métricas de rendimiento
   - [ ] Añadir alertas de sistema
   - [ ] Mejorar logging

## Project Status Board
- [x] Análisis del sistema actual
- [x] Identificación de componentes críticos
- [ ] Implementación de optimizaciones
- [ ] Mejoras de escalabilidad
- [ ] Sistema de monitoreo

## Executor's Feedback or Assistance Requests
El sistema actual funciona correctamente, pero necesitamos:
1. Confirmar si se deben mantener todas las integraciones con bots de trading
2. Verificar si se necesita implementar el sistema de colas
3. Definir métricas específicas para monitoreo

## Lessons
1. El formato del webhook es crítico y debe validarse
2. Los timeouts cortos (5 segundos) son efectivos
3. El logging detallado es esencial para debugging
4. La estructura modular facilita el mantenimiento

## Next Steps
1. Implementar optimizaciones identificadas
2. Mejorar la escalabilidad del sistema
3. Añadir sistema de monitoreo
4. Documentar mejoras y cambios

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

# Prueba de Webhook - Token Monitoring System

## Background and Motivation
Se realizó una prueba completa del sistema de monitoreo de tokens utilizando un webhook de ejemplo que simula el minting de un token Wrapped SOL. El objetivo era verificar el flujo completo desde la recepción del webhook hasta el envío del mensaje a Telegram.

## Key Challenges and Analysis
1. El webhook contiene información detallada sobre una transacción de minting
2. Se requiere procesar múltiples fuentes de datos:
   - Metadatos del token desde Helius
   - Información de IPFS
   - Datos de notables desde Twitter
3. El formato del mensaje debe incluir enlaces y formateo HTML para Telegram

## High-level Task Breakdown
1. ✅ Procesar webhook de entrada
2. ✅ Extraer metadatos del token
3. ✅ Obtener información de IPFS
4. ✅ Consultar datos de notables
5. ✅ Formatear y enviar mensaje a Telegram

## Project Status Board
- [x] Recepción y procesamiento del webhook
- [x] Extracción de metadatos del token
- [x] Obtención de datos de IPFS
- [x] Consulta de notables
- [x] Envío de mensaje a Telegram

## Executor's Feedback or Assistance Requests
La prueba se completó exitosamente. El sistema:
1. Procesó correctamente el webhook
2. Obtuvo los metadatos del token (MOO)
3. Recuperó la información de IPFS
4. Obtuvo los datos de notables del creador (@highfrommemes)
5. Generó y envió el mensaje a Telegram con éxito

## Lessons
1. En PowerShell, usar `Get-Content` en lugar de redirección `<` para pasar datos a scripts Python
2. El sistema maneja correctamente:
   - Tokens con metadatos en IPFS
   - Creadores con seguidores notables
   - Formateo HTML para Telegram
   - Enlaces a bots de trading
3. El mensaje incluye:
   - Nombre y símbolo del token
   - Dirección del contrato
   - Creador y sus seguidores notables
   - Enlaces a plataformas de trading

## Resultados de la Prueba
### Token Detectado
- Nombre: MOO ($MOO)
- CA: A4yYyC4p5jTJd7GzqrtZSi3ULz4ccZqbPLminC64DtuV
- Creador: @highfrommemes
- Total de Notables: 13

### Top 5 Notables
1. @trader1sz (659.7K followers)
2. @SolJakey (196.4K followers)
3. @TylerDurden (185.6K followers)
4. @iamnoahmiller (151.2K followers)
5. @_ShaniceBest (53.7K followers)

### Estado Final
✅ Prueba completada exitosamente
✅ Mensaje enviado a Telegram
✅ Todos los enlaces y formateo funcionando correctamente

# Plan de Acción Post-Prueba

## Análisis de Resultados
La prueba del sistema de monitoreo de tokens ha sido exitosa, demostrando que:
1. El procesamiento de webhooks funciona correctamente
2. La integración con Helius y IPFS es robusta
3. El sistema de notables followers está operativo
4. Las notificaciones de Telegram se envían con el formato correcto

## Próximos Pasos Prioritarios

### 1. Optimización del Sistema (Alta Prioridad)
- [ ] Implementar sistema de caché para metadatos de tokens
- [ ] Optimizar el procesamiento de webhooks para reducir latencia
- [ ] Mejorar el manejo de errores y reintentos
- [ ] Implementar métricas de rendimiento

### 2. Mejoras en la Robustez (Alta Prioridad)
- [ ] Implementar validación más estricta de datos de entrada
- [ ] Mejorar el sistema de logging para debugging
- [ ] Añadir monitoreo de salud
- [ ] Implementar sistema de alertas para fallos

### 3. Documentación y Testing (Media Prioridad)
- [ ] Crear documentación técnica detallada
- [ ] Implementar tests unitarios
- [ ] Añadir tests de integración
- [ ] Crear guías de usuario

### 4. Características Adicionales (Baja Prioridad)
- [ ] Implementar dashboard de monitoreo
- [ ] Añadir más métricas y estadísticas
- [ ] Mejorar el formato de las notificaciones
- [ ] Implementar sistema de filtros personalizados

## Criterios de Éxito
1. Tiempo de procesamiento < 500ms por webhook
2. Tasa de éxito > 99.9% en el procesamiento
3. Cobertura de tests > 80%
4. Documentación completa y actualizada

## Riesgos Identificados
1. **Riesgo**: Latencia en la obtención de metadatos
   - **Mitigación**: Implementar sistema de caché
   - **Prioridad**: Alta

2. **Riesgo**: Fallos en la API de Protokols
   - **Mitigación**: Implementar sistema de reintentos y fallback
   - **Prioridad**: Alta

3. **Riesgo**: Problemas de codificación en Telegram
   - **Mitigación**: Mejorar el manejo de caracteres especiales
   - **Prioridad**: Media

## Plan de Implementación

### Fase 1: Optimización (Sprint 1)
1. Implementar sistema de caché
2. Optimizar procesamiento de webhooks
3. Mejorar manejo de errores

### Fase 2: Robustez (Sprint 2)
1. Implementar validación de datos
2. Mejorar sistema de logging
3. Añadir monitoreo de salud

### Fase 3: Testing y Documentación (Sprint 3)
1. Implementar tests unitarios
2. Crear documentación técnica
3. Añadir guías de usuario

### Fase 4: Características Adicionales (Sprint 4)
1. Implementar dashboard
2. Añadir métricas
3. Mejorar notificaciones

## Métricas de Éxito
- Tiempo de procesamiento por webhook
- Tasa de éxito en el procesamiento
- Cobertura de tests
- Tiempo de respuesta de las APIs
- Uso de recursos del sistema

## Próximos Pasos Inmediatos
1. Comenzar con la implementación del sistema de caché
2. Mejorar el sistema de logging
3. Implementar validación de datos más estricta

¿Deseas que procedamos con alguno de estos pasos o prefieres revisar algún aspecto específico del plan?

## Plan de Refactorización Modular

### Objetivo
Modularizar el sistema actual manteniendo su funcionalidad exacta, creando componentes estancos que se comunican a través de interfaces bien definidas.

### Componentes Identificados
1. **HeliusService** (Módulo: `services/helius_service.py`)
   - Responsabilidad: Interacción con la API de Helius
   - Funciones actuales:
     - `extract_token_metadata(webhook_data)`
   - Interfaz:
     ```python
     def get_token_metadata(mint_address: str) -> Dict[str, Any]
     def validate_webhook(webhook_data: Dict[str, Any]) -> bool
     ```

2. **IPFSService** (Módulo: `services/ipfs_service.py`)
   - Responsabilidad: Obtención de metadatos desde IPFS
   - Funciones actuales:
     - `extract_token_metadata_from_ipfs(ipfs_url, mint_address)`
   - Interfaz:
     ```python
     def get_token_metadata(ipfs_url: str, mint_address: str) -> Dict[str, Any]
     ```

3. **NotableService** (Módulo: `services/notable_service.py`)
   - Responsabilidad: Obtención de datos de notables
   - Funciones actuales:
     - `get_notables(twitter_username)`
   - Interfaz:
     ```python
     def get_notable_followers(twitter_username: str) -> Dict[str, Any]
     ```

4. **TelegramService** (Módulo: `services/telegram_service.py`)
   - Responsabilidad: Formateo y envío de mensajes a Telegram
   - Funciones actuales:
     - `format_telegram_message(token_metadata, notable_data)`
     - `send_telegram_message(message, image_url)`
   - Interfaz:
     ```python
     def format_message(token_metadata: Dict[str, Any], notable_data: Dict[str, Any]) -> str
     def send_message(message: str, image_url: Optional[str] = None) -> bool
     ```

5. **WebhookProcessor** (Módulo: `services/webhook_processor.py`)
   - Responsabilidad: Procesamiento principal del webhook
   - Funciones actuales:
     - `process_webhook(webhook_data)`
   - Interfaz:
     ```python
     def process_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]
     ```

### Plan de Implementación

#### Fase 1: Creación de Estructura Base
1. [ ] Crear estructura de directorios:
   ```
   /src
     /services
       - helius_service.py
       - ipfs_service.py
       - notable_service.py
       - telegram_service.py
       - webhook_processor.py
     /utils
       - formatters.py
       - config.py
     /main.py
   ```

2. [ ] Crear archivo de configuración centralizado:
   ```python
   # config.py
   class Config:
       HELIUS_API_KEY = "133cc99a-6f02-4783-9ada-c013a79343a6"
       TIMEOUT = 5
       # ... otras configuraciones
   ```

#### Fase 2: Implementación de Servicios
1. [ ] Implementar cada servicio manteniendo la lógica actual
2. [ ] Añadir interfaces bien definidas
3. [ ] Implementar logging en cada servicio
4. [ ] Añadir manejo de errores específico

#### Fase 3: Integración
1. [ ] Crear script principal que use los servicios
2. [ ] Implementar pruebas de integración
3. [ ] Verificar que todo funciona igual que antes

### Criterios de Éxito
1. ✅ Cada componente es independiente y testeable
2. ✅ La funcionalidad actual se mantiene exactamente igual
3. ✅ Los logs y manejo de errores son consistentes
4. ✅ Las interfaces son claras y bien documentadas

### Plan de Pruebas
1. [ ] Probar cada servicio individualmente
2. [ ] Probar la integración completa
3. [ ] Verificar que los mensajes de Telegram son idénticos
4. [ ] Comprobar que el manejo de errores es consistente

### Riesgos y Mitigación
1. **Riesgo**: Cambios no intencionales en la funcionalidad
   - **Mitigación**: Mantener tests de integración que verifiquen el comportamiento exacto

2. **Riesgo**: Problemas de configuración
   - **Mitigación**: Centralizar toda la configuración en un solo lugar

3. **Riesgo**: Pérdida de logs o información de debugging
   - **Mitigación**: Mantener el mismo formato de logging en todos los servicios

### Próximos Pasos
1. Crear la estructura de directorios
2. Implementar el primer servicio (HeliusService)
3. Verificar que funciona exactamente igual
4. Continuar con los demás servicios uno por uno

## Lección: Análisis del problema con las cookies en test_webhook_local.py

### ¿Qué ocurrió?
Durante la sesión, el script dejó de funcionar correctamente al intentar cargar las cookies de Protokols. El error era:

    ERROR - No se pudieron cargar las cookies de Protokols
    ERROR - No se pudo generar el mensaje para Telegram

### Causa raíz
El archivo `protokols_cookies.json` contiene una **lista** de objetos cookie (formato estándar exportado por navegadores/playwright), pero la función `load_protokols_cookies()` esperaba un **diccionario**. Al modificar la función para devolver el contenido tal cual (sin convertir la lista a diccionario), la función `get_notables` no recibía el formato esperado y fallaba silenciosamente.

### Qué cambio lo provocó
- Se cambió la función `load_protokols_cookies` para que devolviera el JSON tal cual si era un dict, o un dict vacío si no. Esto rompió la compatibilidad con la función `get_notables`, que espera un diccionario de nombre:valor.
- El formato correcto (que funcionaba al inicio) era convertir la lista de cookies a un diccionario `{name: value}` antes de devolverlo.

### Solución
- Restaurar la función para que convierta la lista de cookies a un diccionario antes de devolverlo.

### Recomendación
- Documentar siempre el formato esperado de los datos de entrada/salida en funciones críticas.
- No modificar funciones que ya están funcionando salvo que sea estrictamente necesario y siempre guardar una copia de seguridad.
- Si un archivo JSON contiene una lista de cookies, convertirlo a diccionario antes de usarlo en requests.

### Estado actual
El sistema funciona correctamente tras restaurar la función original.

## Lessons Learned (actualización crítica)

- **Nunca modificar funciones críticas que ya funcionan sin entender completamente el formato de entrada/salida y sin pruebas exhaustivas.**
- **Si algo funciona, NO LO TOQUES salvo que sea estrictamente necesario y tengas una razón clara y justificada.**
- **Siempre documentar el formato esperado de los datos y validar con ejemplos reales antes de cambiar cualquier función.**
- El error de las cookies fue causado por eliminar la conversión de lista a diccionario, rompiendo la compatibilidad con la función que las usaba. Esto demuestra que "simplificar" sin entender el flujo real puede romper el sistema.
- Antes de "mejorar" o "generalizar" código, revisa el contrato de las funciones y haz pruebas con datos reales.
- Si tienes dudas, consulta la documentación, los ejemplos reales o pregunta antes de cambiar algo que ya está probado.

# Plan de Respaldo del Proyecto

## Background y Motivación
Necesitamos crear un punto de respaldo seguro del proyecto en su estado actual funcional, para poder volver a este punto en cualquier momento si algo sale mal en el futuro.

## Key Challenges y Analysis
- El proyecto tiene múltiples archivos y directorios que necesitan ser respaldados
- Necesitamos asegurarnos de no incluir archivos innecesarios (como __pycache__, .venv, etc.)
- Debemos mantener una estructura organizada del respaldo
- Es importante documentar el estado exacto del respaldo

## High-level Task Breakdown

1. Crear un nuevo directorio de respaldo con timestamp
   - Success Criteria: Directorio creado con nombre que incluye fecha y hora

2. Copiar archivos esenciales del proyecto
   - Success Criteria: Todos los archivos .py, .json, .md, .txt, .bat, .sh copiados
   - Excluir: __pycache__, .venv, .git, .pytest_cache, logs, screenshots, cache

3. Crear un archivo de documentación del respaldo
   - Success Criteria: Archivo README.md creado con:
     - Fecha y hora del respaldo
     - Lista de archivos incluidos
     - Estado funcional del proyecto
     - Instrucciones para restaurar

4. Verificar la integridad del respaldo
   - Success Criteria: Todos los archivos copiados correctamente y accesibles

## Project Status Board
- [ ] Crear directorio de respaldo
- [ ] Copiar archivos esenciales
- [ ] Crear documentación
- [ ] Verificar integridad

## Executor's Feedback o Assistance Requests
(Pendiente de ejecución)

## Lessons
- Mantener respaldos organizados con timestamps
- Documentar el estado del proyecto en cada respaldo
- Excluir archivos innecesarios para mantener el respaldo limpio

# Plan de Producción para Sistema de Webhooks

## Background y Motivación
El sistema actual está funcionando correctamente en desarrollo, pero necesita ser adaptado para un entorno de producción que garantice:
- Procesamiento 24/7 de webhooks
- Alta disponibilidad
- Escalabilidad
- Monitoreo y alertas
- Recuperación automática de fallos

## Key Challenges y Analysis
1. **Alta Disponibilidad**
   - El servidor actual es de desarrollo (Flask)
   - No hay sistema de respaldo
   - No hay monitoreo de salud

2. **Procesamiento de Datos**
   - Necesitamos garantizar que ningún webhook se pierda
   - El procesamiento debe ser asíncrono
   - Necesitamos un sistema de colas

3. **Infraestructura**
   - El servidor debe estar siempre accesible
   - Necesitamos un dominio público
   - SSL/TLS para seguridad

4. **Monitoreo y Logging**
   - Sistema centralizado de logs
   - Alertas en tiempo real
   - Métricas de rendimiento

## High-level Task Breakdown

### 1. Infraestructura Base
- [ ] Configurar servidor de producción (Ubuntu/Debian)
- [ ] Configurar Nginx como reverse proxy
- [ ] Configurar SSL/TLS con Let's Encrypt
- [ ] Configurar dominio público
- [ ] Configurar firewall y seguridad

### 2. Sistema de Procesamiento
- [ ] Migrar de Flask a Gunicorn/uWSGI
- [ ] Implementar sistema de colas (Redis/RabbitMQ)
- [ ] Configurar workers para procesamiento asíncrono
- [ ] Implementar sistema de reintentos
- [ ] Configurar base de datos para persistencia

### 3. Monitoreo y Logging
- [ ] Configurar ELK Stack o similar
- [ ] Implementar sistema de alertas (Telegram/Email)
- [ ] Configurar métricas con Prometheus/Grafana
- [ ] Implementar health checks
- [ ] Configurar backups automáticos

### 4. Automatización y CI/CD
- [ ] Configurar pipeline de CI/CD
- [ ] Automatizar despliegues
- [ ] Implementar tests automatizados
- [ ] Configurar rollbacks automáticos
- [ ] Documentar proceso de despliegue

### 5. Escalabilidad
- [ ] Implementar balanceo de carga
- [ ] Configurar auto-scaling
- [ ] Optimizar base de datos
- [ ] Implementar caché
- [ ] Configurar CDN si es necesario

## Project Status Board
- [ ] Fase 1: Infraestructura Base
- [ ] Fase 2: Sistema de Procesamiento
- [ ] Fase 3: Monitoreo y Logging
- [ ] Fase 4: Automatización
- [ ] Fase 5: Escalabilidad

## Executor's Feedback o Assistance Requests
Pendiente de ejecución

## Lessons
- Usar Gunicorn/uWSGI en lugar de Flask development server
- Implementar sistema de colas para procesamiento asíncrono
- Configurar monitoreo desde el inicio
- Mantener logs centralizados
- Implementar health checks
- Usar SSL/TLS para todas las conexiones
- Configurar backups automáticos

# Análisis de Alternativas a Contabo para Despliegue

## Background y Motivación
El usuario tiene una cuenta en Contabo pero busca una solución más sencilla y eficiente para desplegar el sistema de webhooks. Necesitamos analizar alternativas que sean:
- Más fáciles de configurar
- Más económicas
- Más escalables
- Con mejor rendimiento

## Key Challenges y Analysis

### 1. Requisitos del Sistema
- Procesamiento de webhooks 24/7
- Bajo consumo de recursos (Python + Redis)
- Necesidad de dominio público
- SSL/TLS para seguridad
- Monitoreo básico

### 2. Análisis de Alternativas

#### A. Railway.app
**Ventajas:**
- Despliegue con un solo comando
- SSL/TLS automático
- Dominio gratuito
- Escalado automático
- Monitoreo incluido
- Precio: $5/mes (más que suficiente para nuestro caso)

**Desventajas:**
- Menos control sobre el servidor
- Límites en recursos

#### B. Render.com
**Ventajas:**
- Despliegue automático desde GitHub
- SSL/TLS gratuito
- Dominio gratuito
- Monitoreo incluido
- Precio: $7/mes (suficiente para nuestro caso)

**Desventajas:**
- Menos flexible que un VPS
- Límites en recursos

#### C. DigitalOcean App Platform
**Ventajas:**
- Muy fácil de usar
- SSL/TLS automático
- Dominio gratuito
- Monitoreo incluido
- Precio: $5/mes

**Desventajas:**
- Menos control que un VPS
- Límites en recursos

#### D. Heroku
**Ventajas:**
- Muy fácil de usar
- SSL/TLS automático
- Dominio gratuito
- Monitoreo incluido
- Precio: $5/mes

**Desventajas:**
- Menos control que un VPS
- Límites en recursos

## Recomendación
**Railway.app** sería la mejor opción por:
1. Más económico que Contabo
2. Despliegue más sencillo
3. SSL/TLS automático
4. Monitoreo incluido
5. Escalado automático
6. No requiere configuración de servidor

## High-level Task Breakdown

### 1. Preparación del Proyecto
- [ ] Crear archivo `railway.toml` para configuración
- [ ] Añadir `Procfile` para Railway
- [ ] Configurar variables de entorno
- [ ] Preparar Dockerfile (opcional)

### 2. Despliegue en Railway
- [ ] Crear cuenta en Railway
- [ ] Conectar con GitHub
- [ ] Configurar variables de entorno
- [ ] Desplegar aplicación

### 3. Configuración Post-Despliegue
- [ ] Verificar SSL/TLS
- [ ] Configurar dominio personalizado (opcional)
- [ ] Probar webhook
- [ ] Configurar monitoreo

## Project Status Board
- [ ] Fase 1: Preparación del Proyecto
- [ ] Fase 2: Despliegue en Railway
- [ ] Fase 3: Configuración Post-Despliegue

## Executor's Feedback o Assistance Requests
Pendiente de ejecución

## Lessons
- Railway.app es más económico y sencillo que Contabo
- No requiere configuración de servidor
- SSL/TLS y monitoreo incluidos
- Escalado automático
- Despliegue con un solo comando

# Guía de Despliegue en Railway.app

## Background y Motivación
El usuario quiere conocer el tiempo estimado para desplegar en Railway.app vs Contabo.

## Key Challenges y Analysis
1. **Preparación del Proyecto**
   - Crear archivos de configuración
   - Ajustar variables de entorno
   - Preparar para despliegue

2. **Proceso de Despliegue**
   - Crear cuenta
   - Conectar con GitHub
   - Configurar proyecto
   - Desplegar

## High-level Task Breakdown

### 1. Preparación del Proyecto (15 minutos)
```bash
# 1. Crear railway.toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python webhook_server.py"
healthcheckPath = "/status"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
```

### 2. Despliegue en Railway (10 minutos)
1. Crear cuenta en Railway.app (2 minutos)
2. Conectar con GitHub (1 minuto)
3. Seleccionar repositorio (1 minuto)
4. Configurar variables de entorno (3 minutos)
5. Iniciar despliegue (3 minutos)

## Project Status Board
- [ ] Fase 1: Preparación del Proyecto
- [ ] Fase 2: Despliegue en Railway

## Tiempo Total Estimado
- Tiempo total: ~25 minutos
- Nivel de dificultad: Bajo
- No requiere conocimientos técnicos avanzados

## Comparación de Tiempos
- Railway.app: ~25 minutos
- Contabo: ~2 horas

## Ventajas de Railway.app
1. Despliegue mucho más rápido
2. No requiere configuración manual
3. SSL/TLS automático
4. Dominio gratuito incluido
5. Monitoreo incluido
6. Escalado automático

## Desventajas de Railway.app
1. Menos control sobre el servidor
2. Límites en recursos
3. Precio puede aumentar con uso

## Lessons
- Railway.app es significativamente más rápido que Contabo
- No requiere conocimientos de Linux
- Todo es automático y gestionado
- Ideal para proyectos pequeños/medianos
- Perfecto para webhooks y APIs

# Guía Paso a Paso: Despliegue en Railway.app

## Background y Motivación
El usuario necesita una guía detallada desde el registro hasta el despliegue completo en Railway.app.

## High-level Task Breakdown

### 1. Registro y Configuración Inicial (5 minutos)
1. **Crear cuenta**:
   - Ir a [railway.app](https://railway.app)
   - Click en "Start a New Project"
   - Seleccionar "Sign up with GitHub"
   - Autorizar Railway.app

2. **Crear nuevo proyecto**:
   - Click en "New Project"
   - Seleccionar "Deploy from GitHub repo"
   - Seleccionar tu repositorio

### 2. Preparación del Proyecto (10 minutos)
1. **Crear archivo `railway.toml`**:
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "python webhook_server.py"
healthcheckPath = "/status"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
```

2. **Configurar variables de entorno**:
   - Click en "Variables" en el panel de Railway
   - Añadir las siguientes variables:
     ```
     TELEGRAM_BOT_TOKEN=tu_token
     TELEGRAM_CHANNEL_ID=tu_channel_id
     HELIUS_API_KEY=tu_api_key
     ```

### 3. Despliegue (10 minutos)
1. **Iniciar despliegue**:
   - Click en "Deploy Now"
   - Esperar a que termine el build (2-3 minutos)

2. **Verificar despliegue**:
   - Revisar logs en tiempo real
   - Verificar que el servicio está "Healthy"
   - Copiar la URL generada (será algo como `https://tu-proyecto.up.railway.app`)

### 4. Configuración Final (5 minutos)
1. **Actualizar webhook en Helius**:
   - Ir a [Helius Dashboard](https://dev.helius.xyz/dashboard)
   - Actualizar la URL del webhook con la nueva URL de Railway
   - Añadir `/webhook` al final de la URL

2. **Probar el webhook**:
   - Usar el endpoint de prueba de Helius
   - Verificar que llegan las notificaciones a Telegram

## Project Status Board
- [ ] Registro en Railway.app
- [ ] Preparación del proyecto
- [ ] Despliegue inicial
- [ ] Configuración final

## Verificación de Éxito
1. El servicio está "Healthy" en Railway
2. Los logs muestran que el servidor está corriendo
3. El webhook responde a las pruebas de Helius
4. Las notificaciones llegan a Telegram

## Troubleshooting Común
1. **Error en build**:
   - Verificar `requirements.txt`
   - Revisar logs de build

2. **Error en despliegue**:
   - Verificar variables de entorno
   - Revisar logs de despliegue

3. **Webhook no responde**:
   - Verificar URL en Helius
   - Comprobar logs del servidor

## Lessons
- Siempre verificar las variables de entorno
- Mantener los logs abiertos durante el despliegue
- Probar el webhook después de cada cambio
- Guardar la URL del proyecto