"""
Modelos para manejar los datos de tokens y metadatos.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class TokenMetadata:
    """
    Modelo para los metadatos de un token.
    Contiene la información básica del token como nombre, símbolo, dirección y metadatos sociales.
    """
    address: str
    name: str
    symbol: str
    image: Optional[str] = None
    twitter: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenMetadata':
        """
        Crea una instancia de TokenMetadata desde un diccionario.
        
        Args:
            data: Diccionario con los datos del token
            
        Returns:
            TokenMetadata: Instancia creada
        """
        return cls(
            address=data['address'],
            name=data['name'],
            symbol=data['symbol'],
            image=data.get('image'),
            twitter=data.get('twitter')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del token
        """
        return {
            'address': self.address,
            'name': self.name,
            'symbol': self.symbol,
            'image': self.image,
            'twitter': self.twitter
        } 