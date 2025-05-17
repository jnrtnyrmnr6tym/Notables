"""
Verificador de Mutuals en Twitter

Este módulo permite:
1. Obtener la lista de seguidores y seguidos de una cuenta de Twitter
2. Identificar mutuals (cuentas que se siguen mutuamente)
3. Verificar si hay suficientes mutuals en común entre dos cuentas

Implementa dos enfoques:
- API oficial de Twitter (requiere credenciales)
- Web scraping (sin necesidad de credenciales, pero más propenso a fallos)
"""

import os
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional, Union

class TwitterMutualChecker:
    def __init__(self, cache_dir="data/twitter_cache", use_api=False, api_credentials=None):
        """
        Inicializa el verificador de mutuals de Twitter.
        
        Args:
            cache_dir (str): Directorio para almacenar caché de datos de Twitter
            use_api (bool): Si True, usa la API oficial de Twitter; si False, usa web scraping
            api_credentials (dict): Credenciales para la API de Twitter (solo si use_api=True)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_api = use_api
        self.api_credentials = api_credentials
        
        # Headers para simular un navegador real (para web scraping)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://twitter.com/',
            'Origin': 'https://twitter.com',
        }
        
        # Inicializar cliente de API si es necesario
        if self.use_api and self.api_credentials:
            self._init_api_client()
    
    def _init_api_client(self):
        """Inicializa el cliente de la API de Twitter."""
        try:
            import tweepy
            
            auth = tweepy.OAuth1UserHandler(
                self.api_credentials.get('consumer_key'),
                self.api_credentials.get('consumer_secret'),
                self.api_credentials.get('access_token'),
                self.api_credentials.get('access_token_secret')
            )
            
            self.api = tweepy.API(auth)
            # Verificar credenciales
            self.api.verify_credentials()
            print("Autenticación con API de Twitter exitosa")
            
        except ImportError:
            print("Error: La biblioteca tweepy no está instalada. Ejecute 'pip install tweepy'")
            self.use_api = False
        except Exception as e:
            print(f"Error al inicializar la API de Twitter: {str(e)}")
            self.use_api = False
    
    def _get_cache_path(self, username: str, data_type: str) -> Path:
        """
        Genera la ruta del archivo de caché para un usuario y tipo de datos.
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
            
        Returns:
            Path: Ruta del archivo de caché
        """
        # Normalizar el nombre de usuario (eliminar @, convertir a minúsculas)
        username = username.lower().strip('@')
        return self.cache_dir / f"{username}_{data_type}.json"
    
    def _get_cache_expiry_path(self, username: str, data_type: str) -> Path:
        """
        Genera la ruta del archivo de caducidad de caché.
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
            
        Returns:
            Path: Ruta del archivo de caducidad
        """
        username = username.lower().strip('@')
        return self.cache_dir / f"{username}_{data_type}_expiry.txt"
    
    def _is_cache_valid(self, username: str, data_type: str, max_age_hours: int = 24) -> bool:
        """
        Verifica si la caché para un usuario es válida (no ha expirado).
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
            max_age_hours (int): Edad máxima de la caché en horas
            
        Returns:
            bool: True si la caché es válida, False en caso contrario
        """
        expiry_path = self._get_cache_expiry_path(username, data_type)
        if not expiry_path.exists():
            return False
            
        try:
            with open(expiry_path, 'r') as f:
                expiry_time = float(f.read().strip())
                
            # Verificar si ha pasado el tiempo máximo
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            return current_time < expiry_time + max_age_seconds
        except Exception:
            return False
    
    def _set_cache_expiry(self, username: str, data_type: str):
        """
        Establece el tiempo de expiración de la caché para un usuario.
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
        """
        expiry_path = self._get_cache_expiry_path(username, data_type)
        try:
            with open(expiry_path, 'w') as f:
                f.write(str(time.time()))
        except Exception as e:
            print(f"Error al establecer expiración de caché: {str(e)}")
    
    def _get_from_cache(self, username: str, data_type: str) -> Optional[List[str]]:
        """
        Obtiene datos de la caché para un usuario.
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
            
        Returns:
            List[str] o None: Lista de nombres de usuario o None si no hay caché válida
        """
        if not self._is_cache_valid(username, data_type):
            return None
            
        cache_path = self._get_cache_path(username, data_type)
        if not cache_path.exists():
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al leer caché para {username}_{data_type}: {str(e)}")
            return None
    
    def _save_to_cache(self, username: str, data_type: str, data: List[str]):
        """
        Guarda datos en la caché para un usuario.
        
        Args:
            username (str): Nombre de usuario de Twitter
            data_type (str): Tipo de datos ('followers', 'following', o 'mutuals')
            data (List[str]): Datos a guardar
        """
        cache_path = self._get_cache_path(username, data_type)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Establecer tiempo de expiración
            self._set_cache_expiry(username, data_type)
            
        except Exception as e:
            print(f"Error al guardar caché para {username}_{data_type}: {str(e)}")
    
    def get_followers(self, username: str, use_cache: bool = True, max_cache_age_hours: int = 24) -> List[str]:
        """
        Obtiene la lista de seguidores de un usuario de Twitter.
        
        Args:
            username (str): Nombre de usuario de Twitter
            use_cache (bool): Si True, usa la caché si está disponible
            max_cache_age_hours (int): Edad máxima de la caché en horas
            
        Returns:
            List[str]: Lista de nombres de usuario de los seguidores
        """
        # Normalizar el nombre de usuario
        username = username.lower().strip('@')
        
        # Verificar caché
        if use_cache:
            cached_data = self._get_from_cache(username, 'followers')
            if cached_data is not None:
                print(f"Usando datos en caché para seguidores de @{username}")
                return cached_data
        
        print(f"Obteniendo seguidores para @{username}...")
        
        # Usar el método apropiado según la configuración
        if self.use_api:
            followers = self._get_followers_api(username)
        else:
            followers = self._get_followers_scraping(username)
        
        # Guardar en caché si se obtuvieron datos
        if followers:
            self._save_to_cache(username, 'followers', followers)
        
        return followers
    
    def get_following(self, username: str, use_cache: bool = True, max_cache_age_hours: int = 24) -> List[str]:
        """
        Obtiene la lista de cuentas que sigue un usuario de Twitter.
        
        Args:
            username (str): Nombre de usuario de Twitter
            use_cache (bool): Si True, usa la caché si está disponible
            max_cache_age_hours (int): Edad máxima de la caché en horas
            
        Returns:
            List[str]: Lista de nombres de usuario de las cuentas seguidas
        """
        # Normalizar el nombre de usuario
        username = username.lower().strip('@')
        
        # Verificar caché
        if use_cache:
            cached_data = self._get_from_cache(username, 'following')
            if cached_data is not None:
                print(f"Usando datos en caché para seguidos de @{username}")
                return cached_data
        
        print(f"Obteniendo seguidos para @{username}...")
        
        # Usar el método apropiado según la configuración
        if self.use_api:
            following = self._get_following_api(username)
        else:
            following = self._get_following_scraping(username)
        
        # Guardar en caché si se obtuvieron datos
        if following:
            self._save_to_cache(username, 'following', following)
        
        return following
    
    def _get_followers_api(self, username: str) -> List[str]:
        """
        Obtiene seguidores usando la API oficial de Twitter.
        
        Args:
            username (str): Nombre de usuario de Twitter
            
        Returns:
            List[str]: Lista de nombres de usuario de los seguidores
        """
        if not hasattr(self, 'api'):
            print("Error: API de Twitter no inicializada")
            return []
            
        try:
            followers = []
            # Usar Cursor para manejar paginación automáticamente
            import tweepy
            for follower in tweepy.Cursor(self.api.get_followers, screen_name=username).items():
                followers.append(follower.screen_name)
                # Pequeña pausa para evitar límites de rate
                if len(followers) % 100 == 0:
                    time.sleep(1)
            
            print(f"Se encontraron {len(followers)} seguidores para @{username} via API")
            return followers
            
        except Exception as e:
            print(f"Error al obtener seguidores via API: {str(e)}")
            return []
    
    def _get_following_api(self, username: str) -> List[str]:
        """
        Obtiene seguidos usando la API oficial de Twitter.
        
        Args:
            username (str): Nombre de usuario de Twitter
            
        Returns:
            List[str]: Lista de nombres de usuario de las cuentas seguidas
        """
        if not hasattr(self, 'api'):
            print("Error: API de Twitter no inicializada")
            return []
            
        try:
            following = []
            # Usar Cursor para manejar paginación automáticamente
            import tweepy
            for followed in tweepy.Cursor(self.api.get_friends, screen_name=username).items():
                following.append(followed.screen_name)
                # Pequeña pausa para evitar límites de rate
                if len(following) % 100 == 0:
                    time.sleep(1)
            
            print(f"Se encontraron {len(following)} seguidos para @{username} via API")
            return following
            
        except Exception as e:
            print(f"Error al obtener seguidos via API: {str(e)}")
            return []
    
    def _get_followers_scraping(self, username: str) -> List[str]:
        """
        Obtiene seguidores usando web scraping.
        
        Args:
            username (str): Nombre de usuario de Twitter
            
        Returns:
            List[str]: Lista de nombres de usuario de los seguidores
        """
        # NOTA: Esta es una implementación simulada ya que el web scraping
        # real de Twitter es complejo debido a su naturaleza dinámica y protecciones.
        # En una implementación real, se necesitaría usar Selenium o Playwright.
        print("ADVERTENCIA: El web scraping de seguidores no está completamente implementado")
        print("En una implementación real, se necesitaría usar Selenium o Playwright")
        
        # Simulación para propósitos de prueba
        # En una implementación real, este método extraería los datos de Twitter
        return []
    
    def _get_following_scraping(self, username: str) -> List[str]:
        """
        Obtiene seguidos usando web scraping.
        
        Args:
            username (str): Nombre de usuario de Twitter
            
        Returns:
            List[str]: Lista de nombres de usuario de las cuentas seguidas
        """
        # NOTA: Esta es una implementación simulada ya que el web scraping
        # real de Twitter es complejo debido a su naturaleza dinámica y protecciones.
        # En una implementación real, se necesitaría usar Selenium o Playwright.
        print("ADVERTENCIA: El web scraping de seguidos no está completamente implementado")
        print("En una implementación real, se necesitaría usar Selenium o Playwright")
        
        # Simulación para propósitos de prueba
        # En una implementación real, este método extraería los datos de Twitter
        return []
    
    def get_mutuals(self, username: str, use_cache: bool = True) -> List[str]:
        """
        Obtiene la lista de mutuals (cuentas que siguen y son seguidas por el usuario).
        
        Args:
            username (str): Nombre de usuario de Twitter
            use_cache (bool): Si True, usa la caché si está disponible
            
        Returns:
            List[str]: Lista de nombres de usuario de los mutuals
        """
        # Normalizar el nombre de usuario
        username = username.lower().strip('@')
        
        # Verificar caché
        if use_cache:
            cached_data = self._get_from_cache(username, 'mutuals')
            if cached_data is not None:
                print(f"Usando datos en caché para mutuals de @{username}")
                return cached_data
        
        # Obtener seguidores y seguidos
        followers = set(self.get_followers(username, use_cache))
        following = set(self.get_following(username, use_cache))
        
        # Calcular intersección (mutuals)
        mutuals = list(followers.intersection(following))
        
        print(f"Se encontraron {len(mutuals)} mutuals para @{username}")
        
        # Guardar en caché
        if mutuals:
            self._save_to_cache(username, 'mutuals', mutuals)
        
        return mutuals
    
    def check_common_mutuals(self, username1: str, username2: str, min_mutuals: int = 5) -> Tuple[bool, List[str]]:
        """
        Verifica si dos usuarios tienen un número mínimo de mutuals en común.
        
        Args:
            username1 (str): Primer nombre de usuario de Twitter
            username2 (str): Segundo nombre de usuario de Twitter
            min_mutuals (int): Número mínimo de mutuals requeridos
            
        Returns:
            Tuple[bool, List[str]]: (True si tienen suficientes mutuals, lista de mutuals comunes)
        """
        # Normalizar nombres de usuario
        username1 = username1.lower().strip('@')
        username2 = username2.lower().strip('@')
        
        print(f"Verificando mutuals comunes entre @{username1} y @{username2}...")
        
        # Obtener mutuals de cada usuario
        mutuals1 = set(self.get_mutuals(username1))
        mutuals2 = set(self.get_mutuals(username2))
        
        # Calcular mutuals comunes
        common_mutuals = list(mutuals1.intersection(mutuals2))
        
        has_enough_mutuals = len(common_mutuals) >= min_mutuals
        
        print(f"Mutuals comunes encontrados: {len(common_mutuals)}")
        print(f"¿Tienen al menos {min_mutuals} mutuals en común? {has_enough_mutuals}")
        
        return has_enough_mutuals, common_mutuals


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo con web scraping (sin credenciales)
    checker = TwitterMutualChecker()
    
    # Para usar la API oficial, descomentar y proporcionar credenciales
    """
    api_credentials = {
        'consumer_key': 'TU_CONSUMER_KEY',
        'consumer_secret': 'TU_CONSUMER_SECRET',
        'access_token': 'TU_ACCESS_TOKEN',
        'access_token_secret': 'TU_ACCESS_TOKEN_SECRET'
    }
    checker = TwitterMutualChecker(use_api=True, api_credentials=api_credentials)
    """
    
    # Ejemplo de verificación de mutuals
    username1 = "elonmusk"  # Ejemplo: cuenta del usuario
    username2 = "jack"      # Ejemplo: cuenta del creador del token
    
    has_enough_mutuals, common_mutuals = checker.check_common_mutuals(username1, username2)
    
    if has_enough_mutuals:
        print(f"¡@{username1} y @{username2} tienen suficientes mutuals en común!")
        print(f"Mutuals comunes: {', '.join(common_mutuals)}")
    else:
        print(f"@{username1} y @{username2} no tienen suficientes mutuals en común.") 