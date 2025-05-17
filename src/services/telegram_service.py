"""
Servicio para interactuar con la API de Telegram.
"""

import requests
from typing import Optional
from ..utils.config import config
from ..utils.logger import get_logger
from ..models.token import TokenMetadata
from ..models.notable import NotableData

logger = get_logger(__name__)

class TelegramService:
    """
    Servicio para interactuar con la API de Telegram.
    Maneja el envío de mensajes y notificaciones.
    """
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria."""
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.channel_id = config.TELEGRAM_CHANNEL_ID
        self.timeout = config.REQUEST_TIMEOUT
        
        if not self.bot_token or not self.channel_id:
            raise ValueError("TELEGRAM_BOT_TOKEN o TELEGRAM_CHANNEL_ID no están configurados")
        
        # Asegurar que el channel_id tenga el formato correcto
        if not str(self.channel_id).startswith('-100'):
            self.channel_id = f"-100{str(self.channel_id).lstrip('-')}"
    
    def format_followers_count(self, count: int) -> str:
        """
        Formatea el número de seguidores usando K para miles y M para millones.
        Ejemplo: 659728 -> 659.7K, 1500000 -> 1.5M
        """
        if count >= 1_000_000:
            return f"{count/1_000_000:.1f}M".replace(".0M", "M")
        elif count >= 1_000:
            return f"{count/1_000:.1f}K".replace(".0K", "K")
        return str(count)
    
    def format_message(self, token_metadata: TokenMetadata, notable_data: NotableData) -> str:
        """
        Formatea el mensaje para enviar a Telegram.
        
        Args:
            token_metadata: Metadatos del token
            notable_data: Datos de usuarios notables
            
        Returns:
            str: Mensaje formateado
        """
        total_notables = notable_data.total
        top_notables = notable_data.top
        name = token_metadata.name
        symbol = token_metadata.symbol
        ca = token_metadata.address
        twitter = token_metadata.twitter if token_metadata.twitter else 'Not available'
        
        # Crear enlace para el creador
        creator_link = f'<a href="https://twitter.com/{twitter}">@{twitter}</a>' if twitter != 'Not available' else twitter
        
        # Crear enlace para el ticker del token
        token_link = f'<a href="https://solscan.io/token/{ca}">${symbol}</a>'
        
        # Enlaces de los bots en el orden especificado
        bots_links = [
            ("AXIOM", f"https://axiom.trade/t/{ca}/@notable"),
            ("MAESTRO", f"https://t.me/maestro?start={ca}-sittingbulll"),
            ("TROJAN", f"https://t.me/nestor_trojanbot?start=r-sittingbulll-{ca}"),
            ("BONK", f"https://t.me/bonkbot_bot?start=ref_g8ra9_ca_{ca}"),
            ("PHOTON", f"https://photon-sol.tinyastro.io/en/r/@notable/{ca}")
        ]
        bots_line = " | ".join([f"<a href='{url}'>{name}</a>" for name, url in bots_links])
        
        message = (
            f"<b>New Token Detected</b>\n\n"
            f"<b>Name</b>: {name} ({token_link})\n"
            f"<b>CA</b>: {ca}\n\n"
            f"<b>Creator</b>: {creator_link}\n"
            f"<b>Notable Followers</b>: {total_notables}\n"
            f"<b>Top 5 Notables</b>:\n"
        )
        
        # Añadir enlaces para cada notable
        for i, notable in enumerate(top_notables, 1):
            username = notable.username
            followers = notable.followers_count
            notable_link = f'<a href="https://twitter.com/{username}">@{username}</a>'
            formatted_followers = self.format_followers_count(followers)
            message += f"– {i}. {notable_link} ({formatted_followers} followers)\n"
        
        # Añadir sección de trading con formato de la imagen
        message += f"\n💰 <b>Trade on:</b>\n{bots_line}\n"
        
        return message
    
    def send_message(self, message: str, image_url: Optional[str] = None) -> bool:
        """
        Envía un mensaje al canal de Telegram.
        
        Args:
            message: Mensaje a enviar
            image_url: URL opcional de una imagen para enviar con el mensaje
            
        Returns:
            bool: True si el mensaje se envió correctamente, False en caso contrario
        """
        success = True
        
        if image_url:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            payload = {
                'chat_id': self.channel_id,
                'photo': image_url,
                'caption': message,
                'parse_mode': 'HTML'
            }
        else:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'HTML'
            }
        
        try:
            logger.info(f"Enviando mensaje a Telegram...")
            response = requests.post(url, data=payload, timeout=self.timeout)
            response.raise_for_status()
            logger.info("Mensaje enviado a Telegram correctamente.")
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje a Telegram: {str(e)}")
            success = False
            
        return success
    
    def send_token_notification(self, token_metadata: TokenMetadata, notable_data: NotableData) -> bool:
        """
        Envía una notificación sobre un nuevo token al canal de Telegram.
        
        Args:
            token_metadata: Metadatos del token
            notable_data: Datos de usuarios notables
            
        Returns:
            bool: True si la notificación se envió correctamente, False en caso contrario
        """
        message = self.format_message(token_metadata, notable_data)
        return self.send_message(message, image_url=token_metadata.image) 