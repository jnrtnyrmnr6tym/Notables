"""
Servicio para interactuar con la API de Protokols.
"""

import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.config import config
from ..utils.logger import get_logger
from ..models.notable import NotableData, NotableUser

logger = get_logger(__name__)

class ProtokolsService:
    """
    Servicio para interactuar con la API de Protokols.
    Maneja la obtención de datos de usuarios notables.
    """
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria."""
        self.cookies_file = Path(config.PROTOKOLS_COOKIES_FILE)
        self.timeout = config.REQUEST_TIMEOUT
        self._load_cookies()
    
    def _load_cookies(self) -> None:
        """
        Carga las cookies desde el archivo de configuración.
        """
        try:
            if not self.cookies_file.exists():
                raise FileNotFoundError(f"Archivo de cookies no encontrado: {self.cookies_file}")
            
            with open(self.cookies_file, 'r') as f:
                cookies_data = json.load(f)
            
            # Convertir la lista de cookies a un diccionario para requests
            self.cookies = {cookie['name']: cookie['value'] for cookie in cookies_data}
            logger.info("Cookies de Protokols cargadas correctamente")
            
        except Exception as e:
            logger.error(f"Error al cargar cookies de Protokols: {str(e)}")
            raise
    
    def get_notables(self, username: str) -> Optional[NotableData]:
        """
        Obtiene los datos de usuarios notables para un usuario de Twitter.
        
        Args:
            username: Nombre de usuario de Twitter
            
        Returns:
            Optional[NotableData]: Datos de usuarios notables o None si hay error
        """
        try:
            url = "https://api.protokols.com/graphql"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Query para obtener notables followers
            query = """
            query GetSmartFollowers($username: String!, $limit: Int!, $sortBy: String!, $sortOrder: String!, $cursor: Int!) {
                smartFollowers {
                    getPaginatedSmartFollowers(
                        username: $username
                        limit: $limit
                        sortBy: $sortBy
                        sortOrder: $sortOrder
                        cursor: $cursor
                    ) {
                        items {
                            username
                            followersCount
                        }
                        overallCount
                    }
                }
            }
            """
            
            variables = {
                "username": username,
                "limit": 5,
                "sortBy": "followersCount",
                "sortOrder": "DESC",
                "cursor": 0
            }
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            logger.info(f"Obteniendo notables para @{username}")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                cookies=self.cookies,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extraer datos de la respuesta
            if 'data' in data and 'smartFollowers' in data['data']:
                smart_followers = data['data']['smartFollowers']['getPaginatedSmartFollowers']
                
                # Crear lista de usuarios notables
                notable_users = [
                    NotableUser(
                        username=item['username'],
                        followers_count=item['followersCount']
                    )
                    for item in smart_followers['items']
                ]
                
                return NotableData(
                    total=smart_followers['overallCount'],
                    top=notable_users
                )
            
            logger.error(f"No se encontraron datos de notables para @{username}")
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener notables para @{username}: {str(e)}")
            return None 