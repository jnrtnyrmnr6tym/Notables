"""
Servicio para consultar información de creadores.
"""

import sys
import logging
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos del proyecto principal
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar funciones del proyecto principal
from token_monitor_with_notable_check import get_notable_followers

# Configuración de logging
logger = logging.getLogger(__name__)

def get_creator_info(username):
    """
    Obtiene información de un creador por su nombre de usuario de Twitter.
    
    Args:
        username (str): Nombre de usuario de Twitter
        
    Returns:
        dict: Información del creador o None si no se encuentra
    """
    try:
        # Obtener notable followers
        notable_followers_count = get_notable_followers(username)
        
        # Construir objeto de creador
        creator_info = {
            "username": username,
            "notable_followers_count": notable_followers_count,
            "approved": notable_followers_count >= 5  # Por defecto, umbral de 5
        }
        
        return creator_info
    except Exception as e:
        logger.error(f"Error al obtener información del creador {username}: {str(e)}")
        return None

def get_creator_from_token(token_address):
    """
    Obtiene información del creador de un token.
    
    Args:
        token_address (str): Dirección del token en Solana
        
    Returns:
        dict: Información del creador o None si no se encuentra
    """
    try:
        # Importar aquí para evitar importación circular
        from services.token_service import get_token_info
        
        # Obtener información del token
        token_info = get_token_info(token_address)
        if not token_info or "twitter_username" not in token_info:
            logger.warning(f"No se encontró información del creador para el token {token_address}")
            return None
        
        # Obtener información del creador
        username = token_info["twitter_username"]
        creator_info = get_creator_info(username)
        
        # Añadir información del token
        if creator_info:
            creator_info["token_address"] = token_address
            creator_info["token_name"] = token_info.get("name", "Unknown")
            creator_info["token_symbol"] = token_info.get("symbol", "???")
        
        return creator_info
    except Exception as e:
        logger.error(f"Error al obtener creador del token {token_address}: {str(e)}")
        return None

def refresh_creator_info(username):
    """
    Actualiza la información de un creador forzando una nueva consulta a la API.
    
    Args:
        username (str): Nombre de usuario de Twitter
        
    Returns:
        dict: Información actualizada del creador o None si hay error
    """
    try:
        # En una implementación real, podríamos limpiar la caché o forzar una nueva consulta
        # Por ahora, simplemente llamamos a get_notable_followers directamente
        notable_followers_count = get_notable_followers(username)
        
        # Construir objeto de creador
        creator_info = {
            "username": username,
            "notable_followers_count": notable_followers_count,
            "approved": notable_followers_count >= 5,  # Por defecto, umbral de 5
            "refreshed": True
        }
        
        return creator_info
    except Exception as e:
        logger.error(f"Error al actualizar información del creador {username}: {str(e)}")
        return None 