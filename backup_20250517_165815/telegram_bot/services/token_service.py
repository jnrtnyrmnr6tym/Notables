"""
Token service for the Telegram bot.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from functools import lru_cache

# Add root directory to path to import modules from the main project
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the fast notable followers script
from protokols_smart_followers_fast import get_notables

# Logging configuration
logger = logging.getLogger(__name__)

# Cache for token information
TOKEN_CACHE = {}
CACHE_EXPIRY = 300  # 5 minutes

def get_token_info(token_address: str) -> Optional[Dict]:
    """
    Get detailed information about a token.
    
    Args:
        token_address (str): The token's address
        
    Returns:
        dict: Token information or None if not found
    """
    try:
        # Check cache first
        if token_address in TOKEN_CACHE:
            cache_entry = TOKEN_CACHE[token_address]
            if (datetime.now() - cache_entry['timestamp']).total_seconds() < CACHE_EXPIRY:
                return cache_entry['data']
        
        # Get token metadata
        token_metadata = get_token_metadata(token_address)
        if not token_metadata:
            return None
        
        # Extract Twitter username
        twitter_username = extract_twitter_username(token_metadata)
        if not twitter_username:
            return None
        
        # Get notable followers
        notables_data = get_notables(twitter_username, top_n=5)
        if not notables_data:
            return None
        
        # Build result
        result = {
            'token_address': token_address,
            'name': token_metadata.get('name', 'N/A'),
            'symbol': token_metadata.get('symbol', 'N/A'),
            'image': token_metadata.get('image', None),
            'twitter_username': twitter_username,
            'notable_followers_count': notables_data['overallCount'],
            'top_notables': notables_data['notables'],
            'approved': True,  # Since we're getting data, it's approved
            'timestamp': datetime.now().isoformat()
        }
        
        # Update cache
        TOKEN_CACHE[token_address] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
    except Exception as e:
        logger.error(f"Error getting token info for {token_address}: {str(e)}")
        return None

@lru_cache(maxsize=100)
def get_token_metadata(token_address: str) -> Optional[Dict]:
    """
    Get token metadata from the blockchain.
    
    Args:
        token_address (str): The token's address
        
    Returns:
        dict: Token metadata or None if not found
    """
    try:
        # Import here to avoid circular imports
        from ..utils.blockchain import get_token_metadata
        
        return get_token_metadata(token_address)
    except Exception as e:
        logger.error(f"Error getting token metadata for {token_address}: {str(e)}")
        return None

def extract_twitter_username(metadata: Dict) -> Optional[str]:
    """
    Extract Twitter username from token metadata.
    
    Args:
        metadata (dict): Token metadata
        
    Returns:
        str: Twitter username or None if not found
    """
    try:
        # Try to get from social links
        social_links = metadata.get('social_links', {})
        twitter_url = social_links.get('twitter')
        
        if twitter_url:
            # Extract username from URL
            username = twitter_url.split('/')[-1]
            if username:
                return username
        
        # Try to get from description
        description = metadata.get('description', '')
        if 'twitter.com/' in description:
            # Extract username from description
            parts = description.split('twitter.com/')
            if len(parts) > 1:
                username = parts[1].split()[0]  # Get first word after URL
                if username:
                    return username
        
        return None
    except Exception as e:
        logger.error(f"Error extracting Twitter username: {str(e)}")
        return None

def get_recent_tokens(limit: int = 5) -> List[Dict]:
    """
    Get recently approved tokens.
    
    Args:
        limit (int): Maximum number of tokens to return
        
    Returns:
        list: List of recent tokens
    """
    try:
        # Import here to avoid circular imports
        from ..utils.blockchain import get_approved_tokens
        
        # Get approved tokens
        tokens = get_approved_tokens()
        
        # Sort by timestamp (most recent first)
        tokens.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Get detailed info for each token
        detailed_tokens = []
        for token in tokens[:limit]:
            token_info = get_token_info(token['token_address'])
            if token_info:
                detailed_tokens.append(token_info)
        
        return detailed_tokens
    except Exception as e:
        logger.error(f"Error getting recent tokens: {str(e)}")
        return [] 