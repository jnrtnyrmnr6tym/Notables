"""
Tests unitarios para el servicio ProtokolsService.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from src.services.protokols_service import ProtokolsService
from src.models.notable import NotableData, NotableUser

@pytest.fixture
def mock_cookies():
    """Fixture que proporciona cookies simuladas."""
    return [
        {"name": "cookie1", "value": "value1"},
        {"name": "cookie2", "value": "value2"}
    ]

@pytest.fixture
def mock_protokols_response():
    """Fixture que proporciona una respuesta simulada de Protokols."""
    return {
        "data": {
            "smartFollowers": {
                "getPaginatedSmartFollowers": {
                    "items": [
                        {"username": "user1", "followersCount": 500000},
                        {"username": "user2", "followersCount": 300000},
                        {"username": "user3", "followersCount": 100000}
                    ],
                    "overallCount": 1000
                }
            }
        }
    }

def test_load_cookies_success(mock_cookies):
    """Test para verificar la carga exitosa de cookies."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_cookies))):
        service = ProtokolsService()
        assert service.cookies == {
            "cookie1": "value1",
            "cookie2": "value2"
        }

def test_load_cookies_file_not_found():
    """Test para verificar el manejo de archivo de cookies no encontrado."""
    with patch('pathlib.Path.exists', return_value=False):
        with pytest.raises(FileNotFoundError):
            ProtokolsService()

def test_load_cookies_invalid_json():
    """Test para verificar el manejo de JSON inválido en el archivo de cookies."""
    with patch('builtins.open', mock_open(read_data="invalid json")):
        with pytest.raises(json.JSONDecodeError):
            ProtokolsService()

def test_get_notables_success(mock_cookies, mock_protokols_response):
    """Test para verificar la obtención exitosa de notables."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_cookies))), \
         patch('requests.post') as mock_post:
        
        # Configurar mock de la respuesta
        mock_post.return_value.json.return_value = mock_protokols_response
        mock_post.return_value.raise_for_status = MagicMock()
        
        # Crear servicio y obtener notables
        service = ProtokolsService()
        result = service.get_notables("testuser")
        
        # Verificar resultado
        assert isinstance(result, NotableData)
        assert result.total == 1000
        assert len(result.top) == 3
        
        # Verificar datos de notables
        notable1 = result.top[0]
        assert isinstance(notable1, NotableUser)
        assert notable1.username == "user1"
        assert notable1.followers_count == 500000
        
        # Verificar que se hizo la llamada correcta
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "api.protokols.com/graphql" in args[0]
        assert kwargs['json']['variables']['username'] == "testuser"

def test_get_notables_no_data(mock_cookies):
    """Test para verificar el manejo de respuesta sin datos."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_cookies))), \
         patch('requests.post') as mock_post:
        
        # Configurar mock de la respuesta sin datos
        mock_post.return_value.json.return_value = {"data": {}}
        mock_post.return_value.raise_for_status = MagicMock()
        
        service = ProtokolsService()
        result = service.get_notables("testuser")
        assert result is None

def test_get_notables_http_error(mock_cookies):
    """Test para verificar el manejo de errores HTTP."""
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_cookies))), \
         patch('requests.post') as mock_post:
        
        mock_post.side_effect = Exception("API Error")
        
        service = ProtokolsService()
        result = service.get_notables("testuser")
        assert result is None 