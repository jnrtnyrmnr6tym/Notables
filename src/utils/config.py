"""
Módulo de configuración centralizado para el proyecto.
Maneja la carga de variables de entorno y configuración por defecto.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Clase base para la configuración del proyecto."""
    
    # Configuración de Helius
    HELIUS_API_KEY: str = os.getenv('HELIUS_API_KEY', '')
    HELIUS_API_URL: str = "https://api.helius.xyz/v0"
    
    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHANNEL_ID: str = os.getenv('TELEGRAM_CHANNEL_ID', '')
    
    # Configuración de timeouts
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '10'))
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_FILE: str = os.getenv('LOG_FILE', 'app.log')
    
    # Configuración de Protokols
    PROTOKOLS_COOKIES_FILE: str = os.getenv('PROTOKOLS_COOKIES_FILE', 'protokols_cookies.json')
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida que las configuraciones críticas estén presentes.
        Retorna True si todo está correcto, False si falta alguna configuración crítica.
        """
        required_vars = [
            'HELIUS_API_KEY',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHANNEL_ID'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            print(f"Error: Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
            return False
            
        return True
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """
        Retorna todas las configuraciones como un diccionario.
        Útil para debugging y logging.
        """
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and isinstance(value, (str, int, float, bool))
        }

# Instancia global de configuración
config = Config() 