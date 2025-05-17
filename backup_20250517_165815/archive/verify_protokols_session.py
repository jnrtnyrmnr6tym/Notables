#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificador de Sesión de Protokols

Este script verifica si las cookies de sesión de Protokols son válidas y ofrece
opciones para renovarlas si han expirado.

Uso:
    python verify_protokols_session.py [--cookies-file ARCHIVO_COOKIES]
"""

import os
import json
import argparse
import requests
import logging
import sys
import time
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ProtokolsSessionVerifier")

class ProtokolsSessionVerifier:
    """
    Verificador de sesión de Protokols
    """
    
    def __init__(self, cookies_file: str = "protokols_cookies.json"):
        """
        Inicializa el verificador con un archivo de cookies.
        
        Args:
            cookies_file: Ruta al archivo JSON con las cookies de sesión
        """
        self.cookies_file = cookies_file
        self.cookies = {}
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Origin": "https://www.protokols.io",
            "Referer": "https://www.protokols.io/"
        }
        self.session.headers.update(self.headers)
        
        # Cargar cookies si el archivo existe
        if os.path.exists(cookies_file):
            self.load_cookies()
    
    def load_cookies(self) -> bool:
        """
        Carga las cookies desde el archivo.
        
        Returns:
            bool: True si las cookies se cargaron correctamente, False en caso contrario
        """
        try:
            with open(self.cookies_file, 'r') as f:
                self.cookies = json.load(f)
            
            # Establecer cookies en la sesión
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)
            
            logger.info(f"Cookies cargadas correctamente desde {self.cookies_file}")
            return True
        except Exception as e:
            logger.error(f"Error al cargar cookies desde {self.cookies_file}: {str(e)}")
            return False
    
    def verify_session(self) -> bool:
        """
        Verifica si la sesión actual es válida.
        
        Returns:
            bool: True si la sesión es válida, False en caso contrario
        """
        try:
            # Hacer una solicitud de prueba a la API que usamos para obtener notable followers
            # Esto asegura que la sesión es válida para el propósito específico que necesitamos
            username = "jack"  # Usuario de prueba
            base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
            
            # Preparar los parámetros para GET
            params = {
                "username": username
            }
            
            # Codificar los parámetros para la URL
            import urllib.parse
            input_json = json.dumps({"json": params})
            encoded_input = urllib.parse.quote(input_json)
            url = f"{base_url}?input={encoded_input}"
            
            # Actualizar el referer para este usuario específico
            self.session.headers.update({
                "Referer": f"https://www.protokols.io/twitter/{username}"
            })
            
            # Hacer la solicitud GET
            response = self.session.get(url)
            
            # Verificar si la respuesta es exitosa y contiene datos
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "data" in data["result"]:
                    logger.info("Sesión válida - Respuesta exitosa con datos")
                    return True
            
            logger.warning(f"Sesión inválida. Código de estado: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error al verificar la sesión: {str(e)}")
            return False
    
    def check_session_expiration(self) -> dict:
        """
        Verifica cuándo expira la sesión.
        
        Returns:
            dict: Información sobre la expiración de la sesión
        """
        result = {
            "is_valid": False,
            "expires_at": None,
            "expires_in_seconds": None,
            "expires_in_human": None
        }
        
        # Verificar si la sesión es válida
        result["is_valid"] = self.verify_session()
        
        if result["is_valid"]:
            # Intentar extraer información de expiración del token
            auth_token = self.cookies.get("sb-pgddobbqjoggmuwvhfaj-auth-token", "")
            if auth_token.startswith("base64-"):
                try:
                    import base64
                    
                    # Extraer y decodificar el token
                    token_data = auth_token.replace("base64-", "")
                    decoded_data = base64.b64decode(token_data).decode('utf-8')
                    token_json = json.loads(decoded_data)
                    
                    # Obtener tiempo de expiración
                    if "expires_at" in token_json:
                        expires_at = int(token_json["expires_at"])
                        now = int(time.time())
                        expires_in_seconds = expires_at - now
                        
                        result["expires_at"] = datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')
                        result["expires_in_seconds"] = expires_in_seconds
                        
                        # Formato humano
                        days = expires_in_seconds // (24 * 3600)
                        hours = (expires_in_seconds % (24 * 3600)) // 3600
                        minutes = (expires_in_seconds % 3600) // 60
                        seconds = expires_in_seconds % 60
                        
                        if days > 0:
                            result["expires_in_human"] = f"{days} días, {hours} horas, {minutes} minutos"
                        elif hours > 0:
                            result["expires_in_human"] = f"{hours} horas, {minutes} minutos"
                        elif minutes > 0:
                            result["expires_in_human"] = f"{minutes} minutos, {seconds} segundos"
                        else:
                            result["expires_in_human"] = f"{seconds} segundos"
                except Exception as e:
                    logger.error(f"Error al decodificar token: {str(e)}")
        
        return result
    
    def get_renewal_instructions(self) -> str:
        """
        Obtiene instrucciones para renovar la sesión.
        
        Returns:
            str: Instrucciones para renovar la sesión
        """
        instructions = """
Para renovar la sesión de Protokols, sigue estos pasos:

1. Ejecuta el script de inicio de sesión manual:
   python protokols_browser_login.py

2. Inicia sesión en Protokols en el navegador que se abrirá
   
3. Una vez iniciada la sesión, presiona Enter en la terminal para guardar las cookies

4. Verifica que la sesión sea válida ejecutando:
   python verify_protokols_session.py

Si necesitas más ayuda, consulta la documentación o contacta al administrador.
"""
        return instructions

def main():
    parser = argparse.ArgumentParser(description="Verificador de Sesión de Protokols")
    parser.add_argument("--cookies-file", "-c", default="protokols_cookies.json",
                       help="Archivo con las cookies de sesión")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Mostrar información detallada")
    parser.add_argument("--test-api", "-t", action="store_true",
                       help="Probar la API con un usuario de ejemplo")
    
    args = parser.parse_args()
    
    # Inicializar el verificador
    verifier = ProtokolsSessionVerifier(cookies_file=args.cookies_file)
    
    # Verificar la existencia del archivo de cookies
    if not os.path.exists(args.cookies_file):
        print(f"❌ El archivo de cookies {args.cookies_file} no existe.")
        print("\nNecesitas iniciar sesión en Protokols primero. Ejecuta:")
        print(f"  python protokols_browser_login.py -o {args.cookies_file}")
        return
    
    # Si se solicita probar la API
    if args.test_api:
        print("Probando la API con el usuario 'jack'...")
        import urllib.parse
        
        username = "jack"
        base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
        
        # Preparar los parámetros para GET
        params = {
            "username": username
        }
        
        # Codificar los parámetros para la URL
        input_json = json.dumps({"json": params})
        encoded_input = urllib.parse.quote(input_json)
        url = f"{base_url}?input={encoded_input}"
        
        # Actualizar el referer
        verifier.session.headers.update({
            "Referer": f"https://www.protokols.io/twitter/{username}"
        })
        
        # Hacer la solicitud
        response = verifier.session.get(url)
        print(f"Código de estado: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "data" in data["result"]:
                print("✅ API funcionando correctamente")
                if args.verbose:
                    print("\nPrimeras líneas de la respuesta:")
                    print(json.dumps(data, indent=2)[:500] + "...")
            else:
                print("❌ La API respondió pero con un formato inesperado")
        else:
            print(f"❌ Error al acceder a la API: {response.status_code}")
            print(response.text)
    
    # Verificar la sesión
    session_info = verifier.check_session_expiration()
    
    if session_info["is_valid"]:
        print(f"✅ Sesión válida")
        
        if session_info["expires_in_human"]:
            print(f"⏰ La sesión expira en: {session_info['expires_in_human']}")
            print(f"📅 Fecha de expiración: {session_info['expires_at']}")
        
        # Mostrar información adicional si se solicita
        if args.verbose:
            print("\nCookies disponibles:")
            for name, value in verifier.cookies.items():
                print(f"  {name}: {value[:10]}..." if len(str(value)) > 10 else f"  {name}: {value}")
    else:
        print("❌ La sesión no es válida o ha expirado.")
        print("\nPara renovar la sesión:")
        print(verifier.get_renewal_instructions())

if __name__ == "__main__":
    main() 