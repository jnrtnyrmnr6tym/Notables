"""
Tests unitarios para el servicio HeliusService.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.helius_service import HeliusService
from src.models.token import TokenMetadata

@pytest.fixture
def helius_service():
    """Fixture que proporciona una instancia de HeliusService para testing."""
    return HeliusService()

@pytest.fixture
def mock_token_data():
    """Fixture que proporciona datos de token simulados."""
    return {
        "onChainMetadata": {
            "metadata": {
                "data": {
                    "uri": "https://arweave.net/example"
                }
            }
        }
    }

@pytest.fixture
def mock_ipfs_data():
    """Fixture que proporciona datos de IPFS simulados."""
    return {
        "name": "Test Token",
        "symbol": "TEST",
        "image": "https://example.com/image.png",
        "metadata": {
            "tweetCreatorUsername": "testuser"
        }
    }

def test_get_token_metadata_success(helius_service, mock_token_data, mock_ipfs_data):
    """Test para verificar la obtención exitosa de metadatos de token."""
    mint_address = "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
    
    # Mock de las respuestas HTTP
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Configurar mock para la llamada a Helius
        mock_post.return_value.json.return_value = [mock_token_data]
        mock_post.return_value.raise_for_status = MagicMock()
        
        # Configurar mock para la llamada a IPFS
        mock_get.return_value.json.return_value = mock_ipfs_data
        mock_get.return_value.raise_for_status = MagicMock()
        
        # Llamar al método
        result = helius_service.get_token_metadata(mint_address)
        
        # Verificar el resultado
        assert isinstance(result, TokenMetadata)
        assert result.address == mint_address
        assert result.name == "Test Token"
        assert result.symbol == "TEST"
        assert result.image == "https://example.com/image.png"
        assert result.twitter == "testuser"
        
        # Verificar que se hicieron las llamadas correctas
        mock_post.assert_called_once()
        mock_get.assert_called_once_with("https://arweave.net/example", timeout=helius_service.timeout)

def test_get_token_metadata_no_ipfs_uri(helius_service, mock_token_data):
    """Test para verificar el manejo de tokens sin URI de IPFS."""
    mint_address = "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
    mock_token_data["onChainMetadata"]["metadata"]["data"] = {}
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = [mock_token_data]
        mock_post.return_value.raise_for_status = MagicMock()
        
        result = helius_service.get_token_metadata(mint_address)
        assert result is None

def test_get_token_metadata_http_error(helius_service):
    """Test para verificar el manejo de errores HTTP."""
    mint_address = "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
    
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("HTTP Error")
        
        result = helius_service.get_token_metadata(mint_address)
        assert result is None

def test_get_token_metadata_missing_required_fields(helius_service, mock_token_data, mock_ipfs_data):
    """Test para verificar el manejo de metadatos con campos requeridos faltantes."""
    mint_address = "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
    mock_ipfs_data.pop("name")  # Eliminar campo requerido
    
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        mock_post.return_value.json.return_value = [mock_token_data]
        mock_post.return_value.raise_for_status = MagicMock()
        mock_get.return_value.json.return_value = mock_ipfs_data
        mock_get.return_value.raise_for_status = MagicMock()
        
        result = helius_service.get_token_metadata(mint_address)
        assert result is None 