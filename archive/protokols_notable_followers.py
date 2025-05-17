#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Protokols Notable Followers Extractor

Este script extrae los "notable followers" (seguidores influyentes) de usuarios de Twitter
utilizando la API interna de Protokols. Requiere autenticación previa manual en Protokols
y utiliza las cookies de sesión para mantener el acceso.

Uso:
    python protokols_notable_followers.py --usernames usuario1 usuario2 --output resultados.json
    
Argumentos:
    --usernames, -u: Nombres de usuario de Twitter para analizar
    --cookies-file, -c: Archivo con las cookies de sesión (default: protokols_cookies.json)
    --output, -o: Archivo de salida para guardar los resultados (default: notable_followers_results.json)
    --format, -f: Formato de salida (json, csv, texto)
"""

import os
import json
import time
import argparse
import requests
import csv
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("protokols_extractor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ProtokolsExtractor")

class ProtokolsNotableFollowersExtractor:
    """
    Extractor de notable followers de Protokols
    """
    
    def __init__(self, cookies_file: Optional[str] = None, cookies_dict: Optional[Dict] = None):
        """
        Inicializa el extractor con cookies de sesión.
        
        Args:
            cookies_file: Ruta al archivo JSON con las cookies de sesión
            cookies_dict: Diccionario con las cookies de sesión
        """
        self.api_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Origin": "https://www.protokols.io",
            "Referer": "https://www.protokols.io/"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cargar cookies
        if cookies_dict:
            self.cookies = cookies_dict
            self._set_cookies_to_session()
        elif cookies_file:
            self.load_cookies(cookies_file)
        else:
            self.cookies = {}
            logger.warning("No se proporcionaron cookies. Las solicitudes pueden fallar si la API requiere autenticación.")
    
    def load_cookies(self, cookies_file: str) -> bool:
        """
        Carga las cookies desde un archivo JSON.
        
        Args:
            cookies_file: Ruta al archivo JSON con las cookies
            
        Returns:
            bool: True si las cookies se cargaron correctamente, False en caso contrario
        """
        try:
            with open(cookies_file, 'r') as f:
                self.cookies = json.load(f)
            
            self._set_cookies_to_session()
            logger.info(f"Cookies cargadas correctamente desde {cookies_file}")
            return True
        except Exception as e:
            logger.error(f"Error al cargar cookies desde {cookies_file}: {str(e)}")
            return False
    
    def _set_cookies_to_session(self) -> None:
        """
        Establece las cookies en la sesión de requests.
        """
        if isinstance(self.cookies, dict):
            # Si es un diccionario simple de cookies
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)
        elif isinstance(self.cookies, list):
            # Si es una lista de cookies (como las exportadas por el navegador)
            for cookie in self.cookies:
                if 'name' in cookie and 'value' in cookie:
                    self.session.cookies.set(cookie['name'], cookie['value'])
    
    def verify_session(self) -> bool:
        """
        Verifica si la sesión actual es válida.
        
        Returns:
            bool: True si la sesión es válida, False en caso contrario
        """
        try:
            # Intentar hacer una solicitud simple para verificar la sesión
            response = self.session.get("https://api.protokols.io/api/trpc/auth.getProfileAndUser?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%7D%7D%7D")
            
            # Verificar si la respuesta es exitosa
            if response.status_code == 200:
                logger.info("Sesión válida")
                return True
            else:
                logger.warning(f"Sesión inválida. Código de estado: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error al verificar la sesión: {str(e)}")
            return False
    
    def extract_notable_followers(self, username: str, max_retries: int = 3, retry_delay: int = 2) -> Dict:
        """
        Extrae los notable followers de un usuario de Twitter.
        
        Args:
            username: Nombre de usuario de Twitter
            max_retries: Número máximo de reintentos en caso de error
            retry_delay: Tiempo de espera entre reintentos (en segundos)
            
        Returns:
            Dict: Datos del usuario incluyendo notable followers si están disponibles
        """
        # Preparar los parámetros para GET
        params = {
            "username": username
        }
        
        # Codificar los parámetros para la URL (formato correcto para tRPC)
        input_json = json.dumps({"json": params})
        encoded_input = urllib.parse.quote(input_json)
        url = f"{self.api_url}?input={encoded_input}"
        
        # Actualizar el referer para este usuario específico
        self.session.headers.update({
            "Referer": f"https://www.protokols.io/twitter/{username}"
        })
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Extrayendo notable followers para @{username} (intento {attempt+1}/{max_retries})")
                response = self.session.get(url)
                
                # Verificar si la respuesta fue exitosa
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Datos extraídos correctamente para @{username}")
                    return data
                
                # Si el error es por autenticación
                elif response.status_code in (401, 403):
                    logger.error(f"Error de autenticación: {response.status_code}. La sesión puede haber expirado.")
                    return {"error": "authentication_error", "message": "La sesión ha expirado o las cookies no son válidas"}
                
                # Otros errores
                else:
                    logger.warning(f"Error al extraer datos (código {response.status_code}): {response.text}")
            
            except Exception as e:
                logger.error(f"Excepción al extraer datos: {str(e)}")
            
            # Esperar antes de reintentar (con backoff exponencial)
            wait_time = retry_delay * (2 ** attempt)
            logger.info(f"Esperando {wait_time} segundos antes de reintentar...")
            time.sleep(wait_time)
        
        return {"error": "max_retries_exceeded", "message": f"Se alcanzó el número máximo de reintentos ({max_retries})"}
    
    def extract_and_parse_notable_followers(self, username: str) -> Dict:
        """
        Extrae y analiza los notable followers de un usuario de Twitter.
        
        Args:
            username: Nombre de usuario de Twitter
            
        Returns:
            Dict: Información procesada del usuario y sus notable followers
        """
        raw_data = self.extract_notable_followers(username)
        
        # Verificar si hay error
        if "error" in raw_data:
            return raw_data
        
        # Intentar extraer los datos relevantes
        try:
            # La estructura parece ser diferente a la esperada
            # Los datos del usuario están en result.data.json
            if "result" in raw_data and "data" in raw_data["result"]:
                user_data = raw_data["result"]["data"].get("json", {})
                
                result = {
                    "username": username,
                    "display_name": user_data.get("displayName", ""),
                    "followers_count": user_data.get("followersCount", 0),
                    "following_count": user_data.get("followingCount", 0),
                    "is_verified": user_data.get("isVerified", False),
                    "description": user_data.get("description", ""),
                    "profile_created_at": user_data.get("profileCreatedAt", ""),
                    "engagement_data": {}
                }
                
                # Extraer datos de engagement
                if "engagement" in user_data:
                    engagement = user_data["engagement"]
                    result["engagement_data"] = {
                        "smart_followers_count": engagement.get("smartFollowersCount", 0),
                        "kol_score": engagement.get("kolScore", 0),
                        "avg_views": engagement.get("avgViews", 0),
                        "avg_likes": engagement.get("avgLikes", 0),
                        "avg_retweets": engagement.get("avgRetweets", 0),
                        "avg_comments": engagement.get("avgComments", 0),
                        "engagement_ratio": engagement.get("engagementRatio", 0)
                    }
                    
                    # Usar smartFollowersCount como aproximación de notable followers
                    result["notable_followers_count"] = engagement.get("smartFollowersCount", 0)
                
                return result
            else:
                logger.error(f"Estructura de datos inesperada para @{username}")
                return {
                    "error": "unexpected_data_structure",
                    "message": "La estructura de datos no es la esperada",
                    "username": username
                }
            
        except Exception as e:
            logger.error(f"Error al procesar los datos: {str(e)}")
            return {
                "error": "parsing_error",
                "message": f"Error al procesar los datos: {str(e)}",
                "username": username
            }
    
    def process_multiple_users(self, usernames: List[str], output_file: Optional[str] = None, 
                              output_format: str = "json", delay: int = 1) -> Dict:
        """
        Procesa múltiples usuarios y opcionalmente guarda los resultados en un archivo.
        
        Args:
            usernames: Lista de nombres de usuario de Twitter
            output_file: Ruta al archivo donde guardar los resultados (opcional)
            output_format: Formato de salida (json, csv, texto)
            delay: Tiempo de espera entre solicitudes (en segundos)
            
        Returns:
            Dict: Resultados para todos los usuarios procesados
        """
        results = {}
        
        # Verificar la sesión antes de comenzar
        if not self.verify_session():
            logger.error("La sesión no es válida. Es posible que necesites iniciar sesión nuevamente.")
            return {"error": "invalid_session", "message": "La sesión no es válida"}
        
        for username in usernames:
            logger.info(f"Procesando usuario: @{username}")
            results[username] = self.extract_and_parse_notable_followers(username)
            
            # Mostrar un resumen de los resultados
            if "error" in results[username]:
                print(f"❌ @{username}: Error - {results[username]['message']}")
            else:
                notable_count = results[username].get("notable_followers_count", 0)
                print(f"✅ @{username}: {notable_count:,} notable followers")
            
            # Esperar un poco entre solicitudes para evitar límites de tasa
            if delay > 0 and username != usernames[-1]:  # No esperar después del último usuario
                time.sleep(delay)
        
        # Guardar resultados si se especificó un archivo de salida
        if output_file and results:
            self._save_results(results, output_file, output_format)
        
        return results
    
    def _save_results(self, results: Dict, output_file: str, output_format: str = "json") -> bool:
        """
        Guarda los resultados en un archivo con el formato especificado.
        
        Args:
            results: Diccionario con los resultados
            output_file: Ruta al archivo de salida
            output_format: Formato de salida (json, csv, texto)
            
        Returns:
            bool: True si los resultados se guardaron correctamente, False en caso contrario
        """
        try:
            if output_format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"Resultados guardados en formato JSON: {output_file}")
                
            elif output_format == "csv":
                # Asegurarse de que la extensión sea .csv
                if not output_file.lower().endswith('.csv'):
                    output_file = f"{os.path.splitext(output_file)[0]}.csv"
                
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    # Determinar los campos basados en el primer resultado válido
                    fieldnames = ["username", "display_name", "followers_count", "following_count", 
                                 "is_verified", "notable_followers_count", "smart_followers_count", 
                                 "kol_score", "engagement_ratio"]
                    
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for username, data in results.items():
                        if "error" not in data:
                            # Preparar una fila plana para CSV
                            row = {
                                "username": data.get("username", ""),
                                "display_name": data.get("display_name", ""),
                                "followers_count": data.get("followers_count", 0),
                                "following_count": data.get("following_count", 0),
                                "is_verified": data.get("is_verified", False),
                                "notable_followers_count": data.get("notable_followers_count", 0)
                            }
                            
                            # Añadir datos de engagement si están disponibles
                            engagement = data.get("engagement_data", {})
                            row["smart_followers_count"] = engagement.get("smart_followers_count", 0)
                            row["kol_score"] = engagement.get("kol_score", 0)
                            row["engagement_ratio"] = engagement.get("engagement_ratio", 0)
                            
                            writer.writerow(row)
                
                logger.info(f"Resultados guardados en formato CSV: {output_file}")
                
            elif output_format == "texto":
                # Asegurarse de que la extensión sea .txt
                if not output_file.lower().endswith('.txt'):
                    output_file = f"{os.path.splitext(output_file)[0]}.txt"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Protokols Notable Followers - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
                    
                    for username, data in results.items():
                        if "error" in data:
                            f.write(f"@{username}: Error - {data['message']}\n\n")
                        else:
                            f.write(f"Usuario: @{username} ({data.get('display_name', '')})\n")
                            f.write(f"Seguidores: {data.get('followers_count', 0):,}\n")
                            f.write(f"Siguiendo: {data.get('following_count', 0):,}\n")
                            f.write(f"Verificado: {'Sí' if data.get('is_verified', False) else 'No'}\n")
                            f.write(f"Notable Followers: {data.get('notable_followers_count', 0):,}\n")
                            
                            # Añadir datos de engagement si están disponibles
                            engagement = data.get("engagement_data", {})
                            if engagement:
                                f.write("\nDatos de Engagement:\n")
                                f.write(f"- Smart Followers Count: {engagement.get('smart_followers_count', 0):,}\n")
                                f.write(f"- KOL Score: {engagement.get('kol_score', 0):,}\n")
                                f.write(f"- Promedio de Vistas: {engagement.get('avg_views', 0):,}\n")
                                f.write(f"- Promedio de Likes: {engagement.get('avg_likes', 0):,.2f}\n")
                                f.write(f"- Promedio de Retweets: {engagement.get('avg_retweets', 0):,.2f}\n")
                                f.write(f"- Promedio de Comentarios: {engagement.get('avg_comments', 0):,.2f}\n")
                                f.write(f"- Ratio de Engagement: {engagement.get('engagement_ratio', 0):.6f}\n")
                            
                            f.write("\n" + "-"*40 + "\n\n")
                
                logger.info(f"Resultados guardados en formato texto: {output_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar resultados en {output_file}: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Extractor de Notable Followers de Protokols")
    parser.add_argument("--usernames", "-u", nargs="+", help="Nombres de usuario de Twitter para analizar")
    parser.add_argument("--cookies-file", "-c", default="protokols_cookies.json",
                       help="Archivo con las cookies de sesión")
    parser.add_argument("--output", "-o", default="notable_followers_results.json",
                       help="Archivo de salida para guardar los resultados")
    parser.add_argument("--format", "-f", choices=["json", "csv", "texto"], default="json",
                       help="Formato de salida")
    parser.add_argument("--delay", "-d", type=int, default=1,
                       help="Tiempo de espera entre solicitudes (en segundos)")
    
    args = parser.parse_args()
    
    # Verificar si se proporcionaron nombres de usuario
    if not args.usernames:
        parser.print_help()
        print("\nError: Debe proporcionar al menos un nombre de usuario.")
        return
    
    # Inicializar el extractor
    extractor = ProtokolsNotableFollowersExtractor(
        cookies_file=args.cookies_file
    )
    
    # Procesar los usuarios
    results = extractor.process_multiple_users(
        usernames=args.usernames,
        output_file=args.output,
        output_format=args.format,
        delay=args.delay
    )
    
    # Mostrar un resumen final
    print("\nResumen:")
    for username, data in results.items():
        if "error" in data:
            print(f"❌ @{username}: Error - {data['message']}")
        else:
            notable_count = data.get("notable_followers_count", 0)
            print(f"✅ @{username}: {notable_count:,} notable followers")
    
    if args.output:
        print(f"\nResultados guardados en: {args.output}")

if __name__ == "__main__":
    main() 