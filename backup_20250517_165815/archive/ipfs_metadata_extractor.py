"""
Extractor de Metadatos IPFS optimizado para obtener información de Twitter desde tokens de Solana.

Este módulo proporciona una implementación eficiente para:
1. Acceder a URIs de IPFS mediante múltiples gateways
2. Almacenar en caché los resultados para evitar descargas repetidas
3. Extraer información específica de Twitter de los metadatos
"""

import requests
import re
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class IPFSMetadataExtractor:
    def __init__(self, cache_dir="cache"):
        """
        Inicializa el extractor de metadatos IPFS.
        
        Args:
            cache_dir (str): Directorio donde se almacenará la caché de metadatos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Múltiples gateways para mayor disponibilidad
        self.gateways = [
            "https://ipfs.io/ipfs/",
            "https://cloudflare-ipfs.com/ipfs/",
            "https://gateway.pinata.cloud/ipfs/"
        ]
        
        # Headers para simular un navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def normalize_uri(self, uri):
        """
        Convierte cualquier formato de URI IPFS a un CID normalizado.
        
        Args:
            uri (str): URI de IPFS en cualquier formato (ipfs://, https://ipfs.io/ipfs/, etc.)
            
        Returns:
            str: CID normalizado
        """
        if uri.startswith("ipfs://"):
            cid = uri.replace("ipfs://", "")
            return cid
        elif "/ipfs/" in uri:
            cid = uri.split("/ipfs/")[1]
            return cid
        return uri
    
    def get_cache_path(self, cid):
        """
        Genera la ruta del archivo de caché para un CID específico.
        
        Args:
            cid (str): CID de IPFS
            
        Returns:
            Path: Ruta del archivo de caché
        """
        return self.cache_dir / f"{cid}.json"
    
    def get_from_cache(self, cid):
        """
        Intenta obtener los metadatos desde la caché local.
        
        Args:
            cid (str): CID de IPFS
            
        Returns:
            dict: Metadatos almacenados en caché o None si no existen
        """
        cache_path = self.get_cache_path(cid)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al leer caché ({cid}): {str(e)}")
        return None
    
    def save_to_cache(self, cid, data):
        """
        Guarda los metadatos en la caché local.
        
        Args:
            cid (str): CID de IPFS
            data (dict): Metadatos a guardar
        """
        try:
            cache_path = self.get_cache_path(cid)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar en caché ({cid}): {str(e)}")
    
    def fetch_from_gateway(self, gateway, cid):
        """
        Intenta obtener los metadatos desde un gateway específico.
        
        Args:
            gateway (str): URL base del gateway IPFS
            cid (str): CID de IPFS
            
        Returns:
            dict: Metadatos obtenidos o None si hay error
        """
        url = f"{gateway}{cid}"
        try:
            print(f"Probando gateway: {url}")
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error con gateway {gateway}: {str(e)}")
        return None
    
    def get_metadata(self, uri, max_retries=3):
        """
        Obtiene los metadatos con sistema de reintentos y caché.
        
        Args:
            uri (str): URI de IPFS en cualquier formato
            max_retries (int): Número máximo de reintentos si todos los gateways fallan
            
        Returns:
            dict: Metadatos obtenidos o None si no se pueden obtener
        """
        cid = self.normalize_uri(uri)
        print(f"Obteniendo metadatos para CID: {cid}")
        
        # Revisar caché primero
        cached_data = self.get_from_cache(cid)
        if cached_data:
            print(f"Datos encontrados en caché para {cid}")
            return cached_data
        
        print(f"Intentando obtener metadatos de gateways IPFS...")
        
        # Intentar con múltiples gateways en paralelo
        with ThreadPoolExecutor(max_workers=len(self.gateways)) as executor:
            futures = [executor.submit(self.fetch_from_gateway, gateway, cid) for gateway in self.gateways]
            for future in futures:
                result = future.result()
                if result:
                    print(f"Metadatos obtenidos exitosamente")
                    self.save_to_cache(cid, result)
                    return result
        
        # Si todos los gateways fallan, reintentamos después de un tiempo
        for retry in range(max_retries):
            backoff = 2 ** retry
            print(f"Todos los gateways fallaron. Reintentando en {backoff} segundos... (intento {retry+1}/{max_retries})")
            time.sleep(backoff)  # Backoff exponencial
            for gateway in self.gateways:
                data = self.fetch_from_gateway(gateway, cid)
                if data:
                    print(f"Metadatos obtenidos exitosamente en el reintento")
                    self.save_to_cache(cid, data)
                    return data
        
        print(f"No se pudieron obtener los metadatos después de {max_retries} reintentos")
        return None
    
    def extract_twitter_info(self, metadata):
        """
        Extrae información de Twitter de los metadatos.
        
        Args:
            metadata (dict): Metadatos del token
            
        Returns:
            dict: Información de Twitter extraída
        """
        twitter_info = {
            "usernames": [],
            "mentions": [],
            "tweet_ids": []
        }
        
        if not metadata:
            return twitter_info
        
        # Extraer información del token
        twitter_info["token_name"] = metadata.get("name", "")
        twitter_info["token_symbol"] = metadata.get("symbol", "")
        
        # Extraer información de campos específicos
        meta = metadata.get("metadata", {})
        if meta:
            # Buscar username del creador del tweet
            username = meta.get("tweetCreatorUsername")
            if username:
                twitter_info["usernames"].append(username)
            
            # Buscar ID del tweet
            tweet_id = meta.get("tweetId")
            if tweet_id:
                twitter_info["tweet_ids"].append(tweet_id)
                
            # Buscar cualquier campo que pueda contener información de Twitter
            for key, value in meta.items():
                if isinstance(value, str) and ('twitter' in key.lower() or 'tweet' in key.lower()):
                    if key not in ["tweetCreatorUsername", "tweetId"]:
                        twitter_info[key] = value
        
        # Buscar menciones en la descripción
        description = metadata.get("description", "")
        if description:
            mentions = re.findall(r'@([A-Za-z0-9_]+)', description)
            if mentions:
                twitter_info["mentions"].extend(mentions)
                
        return twitter_info

    def process_token(self, token_info):
        """
        Procesa un token para extraer su información de Twitter.
        
        Args:
            token_info (dict): Información del token (debe contener 'address' y 'uri')
            
        Returns:
            dict: Información completa del token con datos de Twitter
        """
        if not token_info.get('uri'):
            print(f"Error: El token no tiene URI de IPFS")
            return None
            
        # Obtener metadatos
        metadata = self.get_metadata(token_info['uri'])
        if not metadata:
            return None
            
        # Extraer información de Twitter
        twitter_info = self.extract_twitter_info(metadata)
        
        # Crear resultado completo
        result = {
            "token_address": token_info.get('address', ''),
            "uri": token_info.get('uri', ''),
            "metadata": metadata,
            "twitter_info": twitter_info
        }
        
        return result


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo con el token "Hello" que ya hemos identificado
    token_info = {
        "address": "2YQwCagdDrtxtMVU1mKa51PAyabDbshsMDg74fV4KirB",
        "uri": "https://ipfs.io/ipfs/bafkreifx3xe26o5pdqefmprih2wlflwnv2wh2stqf57kjamgdvf7pqr7k4"
    }
    
    extractor = IPFSMetadataExtractor()
    result = extractor.process_token(token_info)
    
    if result:
        print("\n===== INFORMACIÓN EXTRAÍDA =====")
        print(f"Token: {result['token_address']}")
        print(f"URI: {result['uri']}")
        
        twitter = result['twitter_info']
        print("\nInformación de Twitter:")
        print(f"- Nombre del token: {twitter.get('token_name', '')}")
        print(f"- Símbolo: {twitter.get('token_symbol', '')}")
        print(f"- Nombres de usuario: {', '.join(twitter.get('usernames', []))}")
        print(f"- Menciones: {', '.join(twitter.get('mentions', []))}")
        print(f"- IDs de tweets: {', '.join(twitter.get('tweet_ids', []))}")
        
        # Generar URLs útiles
        if twitter.get('tweet_ids'):
            tweet_id = twitter['tweet_ids'][0]
            print(f"\nURL del tweet: https://twitter.com/i/web/status/{tweet_id}")
        
        if twitter.get('usernames'):
            username = twitter['usernames'][0]
            print(f"Perfil del creador: https://twitter.com/{username}")
            
        # Guardar resultado completo
        with open('token_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\nDatos completos guardados en 'token_data.json'")
    else:
        print("No se pudo procesar el token") 