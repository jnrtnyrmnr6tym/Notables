# Token Alert Bot

Bot que monitorea nuevos tokens en Solana y envía alertas a un canal de Telegram.

## Funcionalidades

- Detecta nuevos tokens minted en Solana
- Obtiene metadatos del token desde Helius API
- Descarga información adicional desde IPFS
- Envía alertas formateadas a un canal de Telegram con:
  - Imagen del token
  - Nombre y ticker
  - Dirección del contrato
  - Twitter del creador
  - Información de followers notables

## Formato del Mensaje

```
New Token Detected

Name: TokenName ($TICKER)
CA: ContractAddress

Creator: @TwitterHandle
Notable Followers: Count
Top 5 Notables:
1. @User1 (Followers)
2. @User2 (Followers)
...
```

## Configuración

1. Variables de entorno necesarias:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHANNEL_ID=your_channel_id
   HELIUS_API_KEY=your_helius_api_key
   ```

2. El channel_id debe comenzar con -100 para canales de Telegram

## Flujo de Trabajo

1. Recibe webhook de Helius con información del nuevo token
2. Extrae el mint address del token
3. Llama a la API de Helius para obtener la URI de IPFS
4. Descarga los metadatos desde IPFS
5. Formatea el mensaje con la información del token
6. Envía la imagen y el mensaje al canal de Telegram

## Dependencias

- Python 3.x
- requests
- python-dotenv
- logging

## Uso

1. Instalar dependencias:
   ```bash
   pip install requests python-dotenv
   ```

2. Configurar variables de entorno en archivo .env

3. Ejecutar el script:
   ```bash
   python test_webhook_local.py
   ```

## Notas de Implementación

- Se usa HTML para el formato de texto en Telegram (negrita)
- La imagen se envía junto con el mensaje usando sendPhoto
- Se manejan errores para casos donde no hay metadatos o IPFS
- Se incluye logging para debugging

## Cambios Recientes

- Implementado formato HTML para texto en negrita
- Ajustado formato del mensaje para mostrar imagen y datos juntos
- Corregido formato del ticker para mostrar un solo símbolo $
- Eliminados espacios extra entre secciones del mensaje
- Mejorado manejo de errores y logging 