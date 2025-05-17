# Notas de Chat - Proyecto Protokols Notable Followers

## Sesión del 14/05/2025

### Descubrimientos Clave

1. **API correcta identificada**:
   - URL: `https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial`
   - Método: GET
   - Formato: Parámetros codificados en la URL como JSON

2. **Nombres de usuario**:
   - Importante usar el nombre de usuario exacto de Twitter (case sensitive)
   - Ejemplo: "VitalikButerin" funciona, pero "vitalik" no
   - Los nombres deben coincidir con los que aparecen en la URL de Twitter

3. **Pruebas realizadas**:
   - Usuarios probados: jack, elonmusk, VitalikButerin
   - Todos devolvieron datos correctamente
   - Tiempo de respuesta: menos de 1 segundo por consulta

4. **Límites de tasa**:
   - No se detectaron límites explícitos en las pruebas
   - Pudimos hacer consultas con intervalos de 1-5 segundos sin problemas
   - La sesión dura aproximadamente 30 minutos antes de expirar

### Preguntas Resueltas

1. **¿Se puede consultar un usuario cada 30 segundos?**
   - Sí, es perfectamente viable y bastante conservador
   - No se espera ser bloqueado con esta frecuencia de consultas

2. **¿Qué pasa con el nombre de usuario "vitalik"?**
   - No funcionaba porque el nombre correcto es "VitalikButerin"
   - Los nombres de usuario deben ser exactos y respetar mayúsculas/minúsculas

### Próximos Pasos Discutidos

1. **Integración con sistema de monitoreo de tokens**:
   - Implementar caché para evitar consultas repetidas
   - Verificar automáticamente la validez de la sesión
   - Renovar la sesión cuando esté por expirar

2. **Optimizaciones**:
   - Verificar solo usuarios no consultados previamente
   - Mantener registro de errores para detectar patrones de bloqueo
   - Implementar lógica para determinar si un usuario cumple criterios mínimos

### Comandos Útiles Ejecutados

```bash
# Verificar validez de la sesión
python verify_protokols_session.py --verbose

# Consultar usuarios específicos con delay de 5 segundos
python protokols_notable_followers.py -u jack elonmusk -d 5 -f texto

# Consultar un usuario específico directamente
python test_api_direct.py VitalikButerin
```

### Problemas Encontrados y Soluciones

1. **Problema**: El usuario "vitalik" no funcionaba
   **Solución**: Usar el nombre de usuario correcto "VitalikButerin"

2. **Problema**: Necesidad de monitorear la expiración de sesión
   **Solución**: Implementar verificación periódica y renovación automática

### Recursos y Referencias

1. **Archivos principales**:
   - `protokols_notable_followers.py`: Extractor principal
   - `verify_protokols_session.py`: Verificador de sesión
   - `test_api_direct.py`: Script de prueba directa
   - `.cursor/scratchpad.md`: Documentación completa del proyecto

2. **Documentación externa**:
   - No se encontró documentación oficial de la API de Protokols
   - Se ha documentado el comportamiento observado en el scratchpad 

## Sesión del 15/05/2025

### Configuración de Webhook para Monitoreo de Tokens con Helius

1. **Creación de Webhook en Helius**:
   - Se configuró un webhook para monitorear eventos de tipo `TOKEN_MINT`
   - URL del webhook: `https://webhook.site/33596eda-6d55-4acb-87bc-c46a9173202b`
   - Dirección de Solana monitoreada: `5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE`
   - API Key de Helius obtenida: `133cc99a-6f02-4783-9ada-c013a79343a6`

2. **Decisiones tomadas**:
   - Se utilizará la API de Helius en lugar de la solución anterior para monitoreo de tokens
   - Se verificará el número de notable followers en lugar de mutuals
   - Se utilizó webhook.site como receptor temporal para pruebas

3. **Próximos pasos**:
   - Modificar el código de `solana_token_monitor.py` para utilizar la API de Helius
   - Implementar la lógica para procesar las notificaciones recibidas por el webhook
   - Integrar con el verificador de notable followers

## Sesión del 16/05/2025

### Extracción de Información de Tokens y Verificación de Notable Followers

1. **Desarrollo del Extractor de Información de Tokens**:
   - Se creó el script `extract_token_creator.py` para extraer información del creador de un token
   - Se implementó la lógica para procesar notificaciones de webhook y extraer la dirección del token
   - Se logró extraer correctamente el nombre de usuario de Twitter del creador a partir de los metadatos
   - Se confirmó que los metadatos de tokens en formato Launchcoin contienen el nombre de usuario de Twitter en el campo `metadata.tweetCreatorUsername`

2. **Pruebas realizadas**:
   - Se probó con una notificación real recibida en webhook.site
   - Se verificó que el script puede extraer correctamente el nombre de usuario de Twitter "Ballisticdim4o" del token con dirección "GV74pg6zi1Hy19woBW9msKUqxxvw63A7SQ15tGj5wWJ4"
   - Se confirmó que la API de Helius proporciona toda la información necesaria para el análisis de tokens

3. **Integración con Verificación de Notable Followers**:
   - Se desarrolló el script integrado `token_monitor_with_notable_check.py` que combina la extracción de información del token con la verificación de notable followers
   - Se implementó un servidor Flask para recibir y procesar notificaciones de webhook
   - Se creó un sistema de logging detallado para monitoreo y depuración
   - Se implementó el procesamiento de notificaciones en hilos separados para mejorar la capacidad de respuesta del servidor

4. **Funcionalidades implementadas**:
   - Recepción y procesamiento de notificaciones de webhook
   - Extracción de información del creador del token
   - Verificación de notable followers
   - Exportación de tokens aprobados que cumplen con el criterio de notable followers
   - Sistema de caché para evitar consultas repetidas
   - Manejo avanzado de errores y recuperación

5. **Próximos pasos**:
   - Configurar un servidor dedicado para la ejecución continua del sistema
   - Implementar un panel de monitoreo para supervisar el estado del sistema en tiempo real
   - Establecer un sistema de respaldo y recuperación para garantizar la disponibilidad continua

### Comandos Útiles Ejecutados

```bash
# Procesar una notificación de webhook
python extract_token_creator.py -n notifications/notificacion_real.json

# Iniciar el servidor de webhook
python token_monitor_with_notable_check.py --server --port 5000

# Procesar un token específico
python token_monitor_with_notable_check.py --address GV74pg6zi1Hy19woBW9msKUqxxvw63A7SQ15tGj5wWJ4
```

### Problemas Encontrados y Soluciones

1. **Problema**: Dificultad para extraer información de Twitter de los metadatos del token
   **Solución**: Se identificó que los metadatos de Launchcoin contienen el nombre de usuario de Twitter en el campo `metadata.tweetCreatorUsername`

2. **Problema**: Procesamiento de notificaciones de webhook bloqueaba la respuesta al remitente
   **Solución**: Se implementó procesamiento asíncrono en hilos separados para mejorar la capacidad de respuesta

3. **Problema**: Necesidad de un sistema de logging detallado para monitoreo y depuración
   **Solución**: Se implementó un sistema de logging configurable que guarda información en archivo y muestra en consola 

## Notas de la sesión - Monitoreo de Tokens en Solana

### Sesión 14/05/2025

#### Pruebas del sistema de monitoreo de tokens

- Realizamos pruebas exitosas del sistema integrado de monitoreo de tokens
- El sistema funciona correctamente sin necesidad de hardcodear datos:
  - Recibe notificaciones de webhook sobre nuevos tokens
  - Extrae la dirección del token de la notificación
  - Obtiene los metadatos del token usando la API de Helius
  - Extrae la URI de IPFS de los metadatos
  - Obtiene el contenido de IPFS y extrae el nombre de usuario de Twitter
  - Consulta la API de Protokols para verificar los notable followers
  - Aprueba tokens cuyos creadores tienen más de 5 notable followers

- Prueba exitosa con el token ANDY:
  - Dirección: 8wnN6EuyqsNvXD5pbF9MErcL2QB1eZ4pTmb4wwMGVXwj
  - Creador en Twitter: Andy_On_Sol
  - Notable followers: 27
  - Resultado: Aprobado y guardado en approved_tokens.json

- La API de Protokols funciona correctamente para usuarios verificados o con cierta popularidad
- Para usuarios que no existen en la base de datos de Protokols, el sistema maneja correctamente el error 404 y asume 0 notable followers

#### Problemas resueltos:
- Actualizamos las cookies de autenticación para la API de Protokols
- Corregimos el formato de la URL para las solicitudes a la API
- Implementamos manejo adecuado de errores 404 para usuarios no encontrados

#### Próximos pasos:
- Considerar implementar un sistema de caché para reducir las solicitudes a la API
- Monitorear el rendimiento del sistema con un volumen mayor de tokens
- Evaluar la necesidad de ajustar el umbral de notable followers según los resultados obtenidos 