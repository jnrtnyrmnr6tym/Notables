"""
Servicio para interactuar con la API de Helius.
"""

import requests
from typing import Dict, Any, Optional, List
from ..utils.config import config
from ..utils.logger import get_logger
from ..models.token import TokenMetadata

logger = get_logger(__name__)

class HeliusService:
    """
    Servicio para interactuar con la API de Helius.
    Maneja la obtención de metadatos de tokens y otras operaciones relacionadas.
    """
    
    def __init__(self):
        """Inicializa el servicio con la configuración necesaria."""
        self.api_key = config.HELIUS_API_KEY
        self.base_url = config.HELIUS_API_URL
        self.timeout = config.REQUEST_TIMEOUT
        
        if not self.api_key:
            raise ValueError("HELIUS_API_KEY no está configurada")
    
    def get_token_metadata(self, mint_address: str) -> Optional[TokenMetadata]:
        """
        Obtiene los metadatos de un token desde la API de Helius.
        
        Args:
            mint_address: Dirección del token
            
        Returns:
            Optional[TokenMetadata]: Metadatos del token o None si hay error
        """
        try:
            url = f"{self.base_url}/token-metadata"
            headers = {"Content-Type": "application/json"}
            payload = {"mintAccounts": [mint_address]}
            
            logger.info(f"Obteniendo metadatos del token {mint_address} desde Helius")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={"api-key": self.api_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            token_data = response.json()[0]
            
            # Extraer la URI de IPFS desde la ubicación correcta
            if 'onChainMetadata' in token_data and 'metadata' in token_data['onChainMetadata']:
                metadata = token_data['onChainMetadata']['metadata']
                if 'data' in metadata and 'uri' in metadata['data']:
                    ipfs_url = metadata['data']['uri']
                    logger.info(f"URI de IPFS encontrada: {ipfs_url}")
                    
                    # Obtener metadatos desde IPFS
                    ipfs_metadata = self._get_ipfs_metadata(ipfs_url, mint_address)
                    if ipfs_metadata:
                        return ipfs_metadata
            
            logger.error(f"No se encontraron metadatos en la respuesta de Helius para el token {mint_address}")
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener metadatos del token {mint_address}: {str(e)}")
            return None
    
    def _get_ipfs_metadata(self, ipfs_url: str, mint_address: str) -> Optional[TokenMetadata]:
        """
        Obtiene los metadatos desde IPFS.
        
        Args:
            ipfs_url: URL de IPFS
            mint_address: Dirección del token
            
        Returns:
            Optional[TokenMetadata]: Metadatos del token o None si hay error
        """
        try:
            logger.info(f"Descargando metadatos desde IPFS: {ipfs_url}")
            response = requests.get(ipfs_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Extraer campos relevantes
            name = data.get('name')
            symbol = data.get('symbol')
            image = data.get('image')
            twitter = None
            
            # Buscar el username de Twitter en los metadatos
            if 'metadata' in data and data['metadata']:
                twitter = data['metadata'].get('tweetCreatorUsername')
            
            # Verificar campos requeridos
            if not all([name, symbol]):
                logger.error(f"Faltan campos requeridos en los metadatos de IPFS para {mint_address}")
                return None
            
            return TokenMetadata(
                address=mint_address,
                name=name,
                symbol=symbol,
                image=image,
                twitter=twitter
            )
            
        except Exception as e:
            logger.error(f"Error al extraer metadatos de IPFS: {str(e)}")
            return None 