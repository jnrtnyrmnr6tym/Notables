"""
Módulo de logging centralizado para el proyecto.
Proporciona una configuración estructurada y handlers personalizados.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from .config import config

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Configura y retorna un logger con los handlers apropiados.
    
    Args:
        name: Nombre opcional para el logger. Si no se proporciona, se usa el nombre del módulo.
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear el logger
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Crear el directorio de logs si no existe
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configurar el formato
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        log_dir / config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger global
logger = setup_logger('axiom')

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    Útil para obtener loggers específicos en diferentes módulos.
    
    Args:
        name: Nombre del logger
    
    Returns:
        logging.Logger: Logger configurado
    """
    return setup_logger(name) 