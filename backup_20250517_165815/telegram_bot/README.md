# Bot de Telegram para Monitoreo de Tokens en Solana

Este bot permite monitorear tokens en Solana y verificar si sus creadores tienen suficientes "notable followers" en Twitter.

## Características

- **Consulta de tokens**: Obtener información detallada sobre tokens en Solana
- **Verificación de notable followers**: Comprobar si un creador tiene suficientes notable followers
- **Notificaciones**: Recibir alertas sobre nuevos tokens aprobados
- **Filtrado personalizado**: Establecer el número mínimo de notable followers para filtrar tokens
- **Botones de trading**: Acceder rápidamente a plataformas de trading populares

## Comandos disponibles

### Comandos básicos
- `/start` - Iniciar el bot
- `/help` - Mostrar ayuda
- `/status` - Ver estado del sistema

### Consulta de tokens
- `/token <dirección>` - Consultar información de un token
- `/creator <username>` - Consultar información de un creador
- `/check <CA o username>` - Verificar notable followers
- `/recent` - Ver tokens aprobados recientemente

### Personalización
- `/setfilter <número>` - Establecer mínimo de notable followers
- `/subscribe` - Suscribirse a notificaciones
- `/unsubscribe` - Cancelar suscripción

### Búsqueda
- `/search <término>` - Buscar tokens por nombre o creador

### Administración
- `/admin stats` - Ver estadísticas del sistema
- `/refresh <username>` - Actualizar datos de un creador
- `/broadcast <mensaje>` - Enviar mensaje a todos los usuarios

## Instalación

1. Clona este repositorio:
   ```
   git clone <url-del-repositorio>
   cd <directorio-del-repositorio>
   ```

2. Instala las dependencias:
   ```
   pip install -r telegram_bot/requirements.txt
   ```

3. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   HELIUS_API_KEY=your_helius_api_key_here
   ADMIN_IDS=123456789,987654321
   ```

4. Inicia el bot:
   ```
   python telegram_bot/bot.py
   ```

## Integración con el sistema existente

Este bot se integra con el sistema existente de monitoreo de tokens (`token_monitor_with_notable_check.py`) para:

1. Consultar información de tokens en Solana
2. Extraer metadatos de IPFS
3. Verificar notable followers en Twitter a través de la API de Protokols
4. Notificar sobre nuevos tokens aprobados

## Estructura del proyecto

```
telegram_bot/
├── bot.py                  # Punto de entrada del bot
├── handlers/               # Manejadores de comandos
│   ├── __init__.py
│   ├── admin_commands.py   # Comandos de administración
│   ├── search_commands.py  # Comandos de búsqueda
│   ├── token_commands.py   # Comandos relacionados con tokens
│   └── user_commands.py    # Comandos básicos de usuario
├── services/               # Servicios para interactuar con sistemas externos
│   ├── __init__.py
│   ├── token_service.py    # Servicio para consultar tokens
│   ├── creator_service.py  # Servicio para consultar creadores
│   └── notification_service.py  # Servicio de notificaciones
├── utils/                  # Utilidades
│   ├── __init__.py
│   ├── config.py           # Configuración del bot
└── data/                   # Datos persistentes
    └── subscriptions.json  # Suscripciones de usuarios
```

## Contribuir

Si quieres contribuir a este proyecto, por favor:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un nuevo Pull Request 