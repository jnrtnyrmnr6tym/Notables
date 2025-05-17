"""
Modelos para manejar los datos de webhooks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class TokenTransfer:
    """
    Modelo para una transferencia de token.
    Contiene la información básica de la transferencia.
    """
    mint: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenTransfer':
        """
        Crea una instancia de TokenTransfer desde un diccionario.
        
        Args:
            data: Diccionario con los datos de la transferencia
            
        Returns:
            TokenTransfer: Instancia creada
        """
        return cls(
            mint=data['mint']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos de la transferencia
        """
        return {
            'mint': self.mint
        }

@dataclass
class Transaction:
    """
    Modelo para una transacción.
    Contiene la información básica de la transacción y sus transferencias.
    """
    token_transfers: List[TokenTransfer]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Crea una instancia de Transaction desde un diccionario.
        
        Args:
            data: Diccionario con los datos de la transacción
            
        Returns:
            Transaction: Instancia creada
        """
        return cls(
            token_transfers=[TokenTransfer.from_dict(transfer) for transfer in data.get('tokenTransfers', [])]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia a un diccionario.
        
        Returns:
            Dict[str, Any]: Diccionario con los datos de la transacción
        """
        return {
            'tokenTransfers': [transfer.to_dict() for transfer in self.token_transfers]
        }

@dataclass
class WebhookData:
    """
    Modelo para los datos de un webhook.
    Contiene la lista de transacciones recibidas.
    """
    transactions: List[Transaction]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> 'WebhookData':
        """
        Crea una instancia de WebhookData desde una lista de diccionarios.
        
        Args:
            data: Lista de diccionarios con los datos de las transacciones
            
        Returns:
            WebhookData: Instancia creada
        """
        return cls(
            transactions=[Transaction.from_dict(tx) for tx in data]
        )
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Convierte la instancia a una lista de diccionarios.
        
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos de las transacciones
        """
        return [tx.to_dict() for tx in self.transactions]
    
    def get_first_mint(self) -> Optional[str]:
        """
        Obtiene el mint del primer token transferido en el webhook.
        
        Returns:
            Optional[str]: Mint del token o None si no hay transferencias
        """
        if not self.transactions or not self.transactions[0].token_transfers:
            return None
        return self.transactions[0].token_transfers[0].mint 