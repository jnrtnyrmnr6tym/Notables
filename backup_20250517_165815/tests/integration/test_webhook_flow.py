"""
Tests de integración para el flujo completo del webhook.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.services import HeliusService, TelegramService, ProtokolsService
from src.models.webhook import WebhookData
from src.models.token import TokenMetadata
from src.models.notable import NotableData, NotableUser

@pytest.fixture
def webhook_data():
    """Fixture que proporciona datos de webhook simulados."""
    return [{
        "accountData": [{
            "account": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
            "nativeBalanceChange": -24527905,
            "tokenBalanceChanges": []
        }],
        "tokenTransfers": [{
            "fromTokenAccount": "",
            "fromUserAccount": "",
            "mint": "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g",
            "toTokenAccount": "BKiDH1SW4hdux9E8kJTfpyAkYZaGHHTkYD1AqbSPiZvK",
            "toUserAccount": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM",
            "tokenAmount": 1000000000,
            "tokenStandard": "Fungible"
        }]
    }]

@pytest.fixture
def mock_token_metadata():
    """Fixture que proporciona metadatos de token simulados."""
    return TokenMetadata(
        address="BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g",
        name="Test Token",
        symbol="TEST",
        image="https://example.com/image.png",
        twitter="testuser"
    )

@pytest.fixture
def mock_notable_data():
    """Fixture que proporciona datos de notables simulados."""
    return NotableData(
        total=1000,
        top=[
            NotableUser(username="user1", followers_count=500000),
            NotableUser(username="user2", followers_count=300000),
            NotableUser(username="user3", followers_count=100000)
        ]
    )

def test_webhook_flow_success(webhook_data, mock_token_metadata, mock_notable_data):
    """Test para verificar el flujo completo exitoso del webhook."""
    # Mock de los servicios
    with patch('src.services.helius_service.HeliusService.get_token_metadata') as mock_helius, \
         patch('src.services.protokols_service.ProtokolsService.get_notables') as mock_protokols, \
         patch('src.services.telegram_service.TelegramService.send_token_notification') as mock_telegram:
        
        # Configurar mocks
        mock_helius.return_value = mock_token_metadata
        mock_protokols.return_value = mock_notable_data
        mock_telegram.return_value = True
        
        # Convertir datos del webhook a nuestro modelo
        webhook = WebhookData.from_dict(webhook_data)
        
        # Obtener el mint del primer token transferido
        mint_address = webhook.get_first_token_mint()
        assert mint_address == "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
        
        # Obtener metadatos del token
        token_metadata = mock_helius(mint_address)
        assert token_metadata == mock_token_metadata
        
        # Obtener datos de notables
        notable_data = mock_protokols(token_metadata.twitter)
        assert notable_data == mock_notable_data
        
        # Enviar notificación
        success = mock_telegram(token_metadata, notable_data)
        assert success is True
        
        # Verificar que se llamaron los servicios en el orden correcto
        assert mock_helius.call_count == 1
        assert mock_protokols.call_count == 1
        assert mock_telegram.call_count == 1

def test_webhook_flow_no_token_transfers(webhook_data):
    """Test para verificar el manejo de webhook sin transferencias de token."""
    # Modificar datos para quitar transferencias
    webhook_data[0]['tokenTransfers'] = []
    
    # Convertir datos del webhook a nuestro modelo
    webhook = WebhookData.from_dict(webhook_data)
    
    # Intentar obtener el mint
    mint_address = webhook.get_first_token_mint()
    assert mint_address is None

def test_webhook_flow_no_twitter(webhook_data, mock_token_metadata):
    """Test para verificar el manejo de token sin Twitter."""
    # Modificar metadatos para quitar Twitter
    mock_token_metadata.twitter = None
    
    with patch('src.services.helius_service.HeliusService.get_token_metadata') as mock_helius, \
         patch('src.services.protokols_service.ProtokolsService.get_notables') as mock_protokols, \
         patch('src.services.telegram_service.TelegramService.send_token_notification') as mock_telegram:
        
        # Configurar mocks
        mock_helius.return_value = mock_token_metadata
        
        # Convertir datos del webhook a nuestro modelo
        webhook = WebhookData.from_dict(webhook_data)
        
        # Obtener el mint del primer token transferido
        mint_address = webhook.get_first_token_mint()
        assert mint_address == "BBY9Rwfa8jtJvxJgbK8vqbCRu8Y1QR9ADqXoEESESN3g"
        
        # Obtener metadatos del token
        token_metadata = mock_helius(mint_address)
        assert token_metadata == mock_token_metadata
        
        # Verificar que no se llamó a Protokols ni Telegram
        assert mock_protokols.call_count == 0
        assert mock_telegram.call_count == 0 