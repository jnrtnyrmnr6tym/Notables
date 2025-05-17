"""
Tests unitarios para el servicio TelegramService.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.telegram_service import TelegramService
from src.models.token import TokenMetadata
from src.models.notable import NotableData, NotableUser

@pytest.fixture
def telegram_service():
    """Fixture que proporciona una instancia de TelegramService para testing."""
    return TelegramService()

@pytest.fixture
def token_metadata():
    """Fixture que proporciona metadatos de token simulados."""
    return TokenMetadata(
        address="BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g",
        name="Test Token",
        symbol="TEST",
        image="https://example.com/image.png",
        twitter="testuser"
    )

@pytest.fixture
def notable_data():
    """Fixture que proporciona datos de notables simulados."""
    return NotableData(
        total=1000,
        top=[
            NotableUser(username="user1", followers_count=500000),
            NotableUser(username="user2", followers_count=300000),
            NotableUser(username="user3", followers_count=100000)
        ]
    )

def test_format_followers_count(telegram_service):
    """Test para verificar el formateo de conteos de seguidores."""
    assert telegram_service.format_followers_count(500000) == "500K"
    assert telegram_service.format_followers_count(1500000) == "1.5M"
    assert telegram_service.format_followers_count(999) == "999"

def test_format_message(telegram_service, token_metadata, notable_data):
    """Test para verificar el formateo de mensajes."""
    message = telegram_service.format_message(token_metadata, notable_data)
    
    # Verificar elementos clave en el mensaje
    assert "New Token Detected" in message
    assert token_metadata.name in message
    assert token_metadata.symbol in message
    assert token_metadata.address in message
    assert f"@{token_metadata.twitter}" in message
    assert str(notable_data.total) in message
    
    # Verificar que los notables están incluidos
    for notable in notable_data.top:
        assert notable.username in message
        assert telegram_service.format_followers_count(notable.followers_count) in message
    
    # Verificar enlaces de bots
    assert "AXIOM" in message
    assert "MAESTRO" in message
    assert "TROJAN" in message
    assert "BONK" in message
    assert "PHOTON" in message

def test_send_message_success(telegram_service):
    """Test para verificar el envío exitoso de mensajes."""
    message = "Test message"
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        
        result = telegram_service.send_message(message)
        assert result is True
        
        # Verificar que se hizo la llamada correcta
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "sendMessage" in args[0]
        assert kwargs['data']['text'] == message
        assert kwargs['data']['parse_mode'] == 'HTML'

def test_send_message_with_image(telegram_service):
    """Test para verificar el envío de mensajes con imagen."""
    message = "Test message"
    image_url = "https://example.com/image.png"
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.raise_for_status = MagicMock()
        
        result = telegram_service.send_message(message, image_url)
        assert result is True
        
        # Verificar que se hizo la llamada correcta
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "sendPhoto" in args[0]
        assert kwargs['data']['photo'] == image_url
        assert kwargs['data']['caption'] == message
        assert kwargs['data']['parse_mode'] == 'HTML'

def test_send_message_error(telegram_service):
    """Test para verificar el manejo de errores al enviar mensajes."""
    message = "Test message"
    
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("API Error")
        
        result = telegram_service.send_message(message)
        assert result is False

def test_send_token_notification(telegram_service, token_metadata, notable_data):
    """Test para verificar el envío de notificaciones de token."""
    with patch.object(telegram_service, 'send_message') as mock_send:
        mock_send.return_value = True
        
        result = telegram_service.send_token_notification(token_metadata, notable_data)
        assert result is True
        
        # Verificar que se llamó a send_message con los parámetros correctos
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        assert kwargs.get('image_url') == token_metadata.image 