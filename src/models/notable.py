"""
Modelos para manejar los datos de usuarios notables.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class NotableUser:
    """
    Modelo para un usuario notable.
    Contiene la información básica del usuario como username y número de seguidores.
    """
    username: str
    followers_count: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotableUser':
        """
        Crea una instancia de NotableUser desde un diccionario.
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            NotableUser: Instancia creada
        """
        return cls(
            username=data['username'],
            followers_count=data['followersCount']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos del usuario
        """
        return {
            'username': self.username,
            'followersCount': self.followers_count
        }

@dataclass
class NotableData:
    """
    Modelo para los datos de usuarios notables.
    Contiene la lista de usuarios notables y el total.
    """
    total: int
    top: List[NotableUser]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotableData':
        """
        Crea una instancia de NotableData desde un diccionario.
        
        Args:
            data: Diccionario con los datos de notables
            
        Returns:
            NotableData: Instancia creada
        """
        return cls(
            total=data['total'],
            top=[NotableUser.from_dict(user) for user in data['top']]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos de notables
        """
        return {
            'total': self.total,
            'top': [user.to_dict() for user in self.top]
        } 