"""
Script para probar la extracción de datos de Twitter del token "Hello" identificado.
"""

import requests
import json

def test_hello_token():
    # Información del token "Hello" que identificamos
    token_info = {
        "address": "2YQwCagdDrtxtMVU1mKa51PAyabDbshsMDg74fV4KirB",
        "uri": "https://ipfs.io/ipfs/bafkreifx3xe26o5pdqefmprih2wlflwnv2wh2stqf57kjamgdvf7pqr7k4"
    }
    
    print(f"Extrayendo datos del token Hello ({token_info['address']})...")
    
    # Obtener metadatos desde IPFS
    try:
        print(f"Accediendo a URI: {token_info['uri']}")
        response = requests.get(token_info['uri'], timeout=10)
        
        if response.status_code == 200:
            metadata = response.json()
            print("\n===== METADATOS DEL TOKEN =====")
            print(f"Nombre: {metadata.get('name')}")
            print(f"Símbolo: {metadata.get('symbol')}")
            print(f"Descripción: {metadata.get('description')}")
            
            # Extraer información de Twitter
            twitter_data = {}
            
            # 1. Buscar menciones en la descripción
            description = metadata.get('description', '')
            if description:
                import re
                mentions = re.findall(r'@([A-Za-z0-9_]+)', description)
                if mentions:
                    twitter_data['menciones'] = mentions
            
            # 2. Extraer datos específicos de Twitter de los metadatos
            meta = metadata.get('metadata', {})
            if meta:
                for key, value in meta.items():
                    if 'tweet' in key.lower() or 'twitter' in key.lower():
                        twitter_data[key] = value
            
            print("\n===== INFORMACIÓN DE TWITTER =====")
            if twitter_data:
                for key, value in twitter_data.items():
                    print(f"{key}: {value}")
                
                # Mostrar URLs útiles si tenemos IDs de tweets
                tweet_id = meta.get('tweetId')
                if tweet_id:
                    print(f"\nURL del tweet: https://twitter.com/i/web/status/{tweet_id}")
                
                twitter_username = meta.get('tweetCreatorUsername')
                if twitter_username:
                    print(f"Perfil del creador: https://twitter.com/{twitter_username}")
            else:
                print("No se encontró información de Twitter")
            
            # Guardar resultados para referencia
            with open('hello_token_data.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'token': token_info,
                    'metadata': metadata,
                    'twitter_data': twitter_data
                }, f, indent=2)
            
            print("\nDatos guardados en 'hello_token_data.json'")
        else:
            print(f"Error al acceder a los metadatos. Código: {response.status_code}")
    
    except Exception as e:
        print(f"Error al procesar el token: {str(e)}")

if __name__ == "__main__":
    test_hello_token() 