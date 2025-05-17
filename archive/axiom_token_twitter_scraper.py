"""
Scraper de tokens Solana para extraer información de Twitter desde URIs de IPFS.

Este script:
1. Obtiene tokens creados por una cuenta específica de Solana
2. Extrae las URIs de IPFS de los metadatos
3. Obtiene la información de Twitter (usuarios, tweets, etc.)
"""

import requests
import json
import time
import os
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class AxiomTokenTwitterScraper:
    def __init__(self, creator_address, output_dir="data"):
        self.creator_address = creator_address
        self.output_dir = output_dir
        self.tokens_data = []
        self.twitter_data = []
        
        # Crear directorios de salida
        os.makedirs(output_dir, exist_ok=True)
        
        # Archivos de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.tokens_file = f"{output_dir}/tokens_{timestamp}.csv"
        self.twitter_file = f"{output_dir}/twitter_data_{timestamp}.csv"
        self.json_file = f"{output_dir}/full_data_{timestamp}.json"
        
        # Headers para simular un navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    
    def get_tokens_by_creator(self, limit=100):
        """
        Obtiene tokens creados por la dirección especificada.
        Primero intenta usando la API de Solscan, y si falla,
        usa Solana FM o Jupiter Aggregator como respaldo.
        """
        print(f"Buscando tokens creados por {self.creator_address}...")
        
        # Intentar con la API de TheGraph para los datos de Solana
        try:
            # Esto es un ejemplo; la consulta real dependerá del indexador que uses
            # Podría ser necesario ajustar esto según la API disponible
            endpoint = "https://api.solscan.io/v2/token/created"
            params = {
                "address": self.creator_address,
                "limit": limit
            }
            response = requests.get(endpoint, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    print(f"Encontrados {len(data['data'])} tokens con Solscan API")
                    return data["data"]
        except Exception as e:
            print(f"Error al usar API de Solscan: {str(e)}")
        
        # Si la API falla, podemos intentar un enfoque alternativo:
        print("Intentando método alternativo...")
        
        # Esta es una implementación simulada; en producción, necesitarías
        # usar una API real o incluso web scraping si es necesario
        alternative_tokens = self._get_tokens_alternative_method()
        if alternative_tokens:
            print(f"Encontrados {len(alternative_tokens)} tokens con método alternativo")
            return alternative_tokens
        
        print("No se pudieron obtener tokens mediante APIs. Utiliza método manual.")
        return []
    
    def _get_tokens_alternative_method(self):
        """
        Método alternativo para obtener tokens creados.
        En un entorno real, esto podría usar otra API o web scraping.
        """
        # Implementación simulada - en producción, usa una API real
        # como Jupiter, Solana FM, o incluso scraping directo
        return []
    
    def fetch_ipfs_metadata(self, uri):
        """
        Obtiene metadatos desde una URI de IPFS.
        Admite URIs en formato ipfs:// y https://ipfs.io/
        """
        print(f"Obteniendo metadatos de: {uri}")
        
        # Normalizar URI de IPFS
        if uri.startswith("ipfs://"):
            # Convertir ipfs:// a https://ipfs.io/ipfs/
            cid = uri.replace("ipfs://", "")
            uri = f"https://ipfs.io/ipfs/{cid}"
        
        try:
            response = requests.get(uri, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error al obtener metadatos IPFS: {str(e)}")
        
        return None
    
    def extract_twitter_data(self, metadata):
        """
        Extrae información de Twitter de los metadatos.
        """
        twitter_data = {
            "token_name": metadata.get("name", ""),
            "token_symbol": metadata.get("symbol", ""),
            "description": metadata.get("description", ""),
            "twitter_mentions": [],
            "twitter_usernames": [],
            "tweet_ids": []
        }
        
        # Buscar menciones de Twitter en la descripción
        description = metadata.get("description", "")
        if description:
            # Buscar menciones (@username)
            import re
            mentions = re.findall(r'@([A-Za-z0-9_]+)', description)
            if mentions:
                twitter_data["twitter_mentions"] = mentions
        
        # Buscar metadatos específicos de Twitter
        meta = metadata.get("metadata", {})
        if meta:
            # Extraer IDs de tweets
            tweet_id = meta.get("tweetId")
            if tweet_id:
                twitter_data["tweet_ids"].append(tweet_id)
            
            # Extraer nombres de usuario
            username = meta.get("tweetCreatorUsername")
            if username:
                twitter_data["twitter_usernames"].append(username)
        
        return twitter_data
    
    def process_token(self, token):
        """
        Procesa un único token para extraer sus metadatos y datos de Twitter.
        """
        try:
            # Extraer URI de metadatos del token
            # Nota: La estructura real de 'token' dependerá de la API que uses
            token_address = token.get("address") or token.get("mint") or token.get("tokenAddress")
            token_name = token.get("name") or token.get("tokenName") or "Unknown"
            token_symbol = token.get("symbol") or token.get("tokenSymbol") or "???"
            metadata_uri = token.get("uri") or token.get("metadataUri")
            
            if not metadata_uri:
                print(f"No se encontró URI para el token {token_address}")
                return None
            
            # Obtener metadatos de IPFS
            metadata = self.fetch_ipfs_metadata(metadata_uri)
            if not metadata:
                print(f"No se pudieron obtener metadatos para {token_address}")
                return None
            
            # Extraer información de Twitter
            twitter_info = self.extract_twitter_data(metadata)
            
            # Crear un registro completo
            token_record = {
                "address": token_address,
                "name": token_name,
                "symbol": token_symbol,
                "uri": metadata_uri,
                "metadata": metadata,
                "twitter_data": twitter_info
            }
            
            print(f"Procesado token: {token_name} ({token_symbol})")
            if twitter_info["twitter_mentions"] or twitter_info["twitter_usernames"]:
                print(f"  - Menciones Twitter: {twitter_info['twitter_mentions']}")
                print(f"  - Usuarios Twitter: {twitter_info['twitter_usernames']}")
            
            return token_record
            
        except Exception as e:
            print(f"Error al procesar token: {str(e)}")
            return None
    
    def save_results(self):
        """
        Guarda los resultados en archivos CSV y JSON.
        """
        # Guardar datos completos en JSON
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.tokens_data, f, indent=2)
        
        # Guardar datos de tokens en CSV
        with open(self.tokens_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Token Address', 'Name', 'Symbol', 'IPFS URI'])
            for token in self.tokens_data:
                writer.writerow([
                    token.get('address', ''),
                    token.get('name', ''),
                    token.get('symbol', ''),
                    token.get('uri', '')
                ])
        
        # Guardar datos de Twitter en CSV
        with open(self.twitter_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Token Name', 'Token Symbol', 'Twitter Mentions', 
                'Twitter Usernames', 'Tweet IDs', 'Description'
            ])
            for token in self.tokens_data:
                twitter = token.get('twitter_data', {})
                writer.writerow([
                    twitter.get('token_name', ''),
                    twitter.get('token_symbol', ''),
                    ', '.join(twitter.get('twitter_mentions', [])),
                    ', '.join(twitter.get('twitter_usernames', [])),
                    ', '.join(twitter.get('tweet_ids', [])),
                    twitter.get('description', '')
                ])
        
        print(f"\nResultados guardados en:")
        print(f"- Datos completos: {self.json_file}")
        print(f"- Datos de tokens: {self.tokens_file}")
        print(f"- Datos de Twitter: {self.twitter_file}")
    
    def run(self):
        """
        Ejecuta el proceso completo de scraping.
        """
        print(f"Iniciando scraping de tokens creados por {self.creator_address}...")
        
        # Obtener lista de tokens
        tokens = self.get_tokens_by_creator()
        
        if not tokens:
            print("\n❌ No se encontraron tokens para la dirección especificada.")
            print("Considera usar un enfoque manual o verificar la dirección.")
            return False
        
        print(f"\nProcesando {len(tokens)} tokens...")
        
        # Procesar tokens de forma paralela
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.process_token, tokens))
        
        # Filtrar resultados nulos
        self.tokens_data = [r for r in results if r]
        
        print(f"\n✅ Se procesaron {len(self.tokens_data)} tokens con éxito.")
        
        # Guardar resultados
        self.save_results()
        
        return True

    def process_manual_token(self, token_address, metadata_uri):
        """
        Procesa un token manualmente proporcionado.
        Útil cuando las APIs fallan y conocemos directamente algunos tokens.
        """
        try:
            # Obtener metadatos
            metadata = self.fetch_ipfs_metadata(metadata_uri)
            if not metadata:
                print(f"No se pudieron obtener metadatos para {token_address}")
                return None
            
            # Extraer información básica
            token_name = metadata.get("name", "Unknown")
            token_symbol = metadata.get("symbol", "???")
            
            # Extraer información de Twitter
            twitter_info = self.extract_twitter_data(metadata)
            
            # Crear registro
            token_record = {
                "address": token_address,
                "name": token_name,
                "symbol": token_symbol,
                "uri": metadata_uri,
                "metadata": metadata,
                "twitter_data": twitter_info
            }
            
            # Añadir a la lista de tokens
            self.tokens_data.append(token_record)
            
            print(f"Procesado token manual: {token_name} ({token_symbol})")
            if twitter_info["twitter_mentions"] or twitter_info["twitter_usernames"]:
                print(f"  - Menciones Twitter: {twitter_info['twitter_mentions']}")
                print(f"  - Usuarios Twitter: {twitter_info['twitter_usernames']}")
            
            return token_record
            
        except Exception as e:
            print(f"Error al procesar token manual: {str(e)}")
            return None

def manual_token_input():
    """
    Permite al usuario ingresar tokens manualmente cuando las APIs fallan.
    """
    tokens = []
    print("\n" + "="*80)
    print("ENTRADA MANUAL DE TOKENS")
    print("Ingresa información sobre tokens conocidos (deja en blanco para terminar)")
    print("="*80)
    
    while True:
        token_address = input("\nDirección del token (o Enter para terminar): ").strip()
        if not token_address:
            break
        
        metadata_uri = input("URI de metadatos IPFS: ").strip()
        if metadata_uri:
            tokens.append({
                "address": token_address,
                "uri": metadata_uri
            })
    
    return tokens

if __name__ == "__main__":
    # Dirección del creador a analizar
    CREATOR_ADDRESS = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    
    # Iniciar scraper
    scraper = AxiomTokenTwitterScraper(CREATOR_ADDRESS)
    
    # Ejecutar scraping automático
    success = scraper.run()
    
    # Si el scraping automático falla, permitir entrada manual
    if not success or len(scraper.tokens_data) == 0:
        print("\nEl scraping automático no encontró resultados.")
        use_manual = input("¿Deseas ingresar tokens manualmente? (s/n): ").lower()
        
        if use_manual == 's':
            manual_tokens = manual_token_input()
            
            if manual_tokens:
                print(f"\nProcesando {len(manual_tokens)} tokens ingresados manualmente...")
                for token in manual_tokens:
                    scraper.process_manual_token(token["address"], token["uri"])
                
                # Guardar resultados
                scraper.save_results()
    
    print("\nProceso completado.") 