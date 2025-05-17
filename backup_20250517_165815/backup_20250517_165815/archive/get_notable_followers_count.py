#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para obtener el número de Notable Followers de una cuenta de Twitter usando Protokols.

Este script:
1. Abre un navegador con Playwright
2. Permite al usuario iniciar sesión en Protokols
3. Navega al perfil de Twitter especificado
4. Captura la solicitud que obtiene los Notable Followers
5. Extrae y muestra el número de Notable Followers
"""

import json
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("NotableFollowersCounter")

async def get_notable_followers_count(twitter_username, headless=False):
    """
    Abre un navegador, navega al perfil de Twitter en Protokols y obtiene el número de Notable Followers.
    
    Args:
        twitter_username: Nombre de usuario de Twitter para analizar
        headless: Si el navegador debe ejecutarse en modo headless
        
    Returns:
        int: Número de Notable Followers, o None si no se pudo obtener
    """
    logger.info(f"Obteniendo Notable Followers para @{twitter_username}")
    notable_followers_data = None
    
    async with async_playwright() as p:
        # Lanzar navegador
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        
        # Configurar interceptor para capturar solicitudes relevantes
        async def on_response(response):
            nonlocal notable_followers_data
            url = response.url
            
            # Buscar respuestas que contengan datos de notable followers
            if ("api.protokols.io" in url and 
                ("twitter" in url.lower() or "kol" in url.lower() or "influencer" in url.lower())):
                
                logger.info(f"Respuesta API detectada: {url}")
                
                try:
                    response_json = await response.json()
                    
                    # Buscar datos de notable followers en la respuesta
                    if "result" in response_json and "data" in response_json["result"]:
                        data = response_json["result"]["data"]
                        
                        if "notableFollowers" in data:
                            notable_followers = data["notableFollowers"]
                            notable_followers_data = {
                                "count": len(notable_followers),
                                "followers": notable_followers
                            }
                            logger.info(f"¡Notable Followers encontrados! Cantidad: {len(notable_followers)}")
                        
                        # También buscar en otras posibles estructuras
                        elif "profile" in data and "notableFollowersCount" in data["profile"]:
                            count = data["profile"]["notableFollowersCount"]
                            notable_followers_data = {
                                "count": count,
                                "followers": []
                            }
                            logger.info(f"¡Contador de Notable Followers encontrado! Cantidad: {count}")
                            
                except Exception as e:
                    logger.error(f"Error al procesar respuesta: {str(e)}")
        
        # Registrar el evento de respuesta
        context.on("response", on_response)
        
        # Crear una nueva página
        page = await context.new_page()
        
        # Navegar a la página de inicio de sesión
        logger.info("Navegando a la página de inicio de sesión...")
        await page.goto("https://www.protokols.io/sign-in")
        
        print("\n" + "="*80)
        print(f"INSTRUCCIONES PARA OBTENER NOTABLE FOLLOWERS DE @{twitter_username}:")
        print("1. Inicia sesión manualmente en Protokols en el navegador que se ha abierto")
        print("2. Una vez iniciada la sesión, el script navegará automáticamente al perfil")
        print("3. Espera mientras se cargan los datos (observa los mensajes en esta terminal)")
        print("="*80 + "\n")
        
        # Esperar a que el usuario inicie sesión
        input("Presiona Enter cuando hayas iniciado sesión en Protokols...")
        
        # Navegar al perfil de Twitter
        twitter_profile_url = f"https://www.protokols.io/twitter/{twitter_username}"
        logger.info(f"Navegando al perfil de Twitter: {twitter_profile_url}")
        
        try:
            await page.goto(twitter_profile_url)
            
            # Esperar a que se cargue la página y posiblemente los datos de notable followers
            logger.info("Esperando a que se carguen los datos...")
            await page.wait_for_timeout(5000)  # Esperar 5 segundos
            
            # Si aún no tenemos los datos, esperar un poco más
            if not notable_followers_data:
                logger.info("Esperando datos adicionales...")
                await page.wait_for_timeout(5000)  # Esperar 5 segundos más
            
            # Intentar buscar elementos en la página que puedan contener la información
            if not notable_followers_data:
                logger.info("Buscando información en la página...")
                
                # Intentar encontrar elementos que puedan contener el número de notable followers
                # Esto dependerá de la estructura HTML de la página
                try:
                    # Ejemplo: buscar texto que contenga "notable followers"
                    notable_text = await page.locator("text=/notable followers/i").all_text_contents()
                    if notable_text:
                        logger.info(f"Texto encontrado en la página: {notable_text}")
                except Exception as e:
                    logger.error(f"Error al buscar en la página: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error al navegar al perfil: {str(e)}")
        
        # Cerrar el navegador
        await browser.close()
        
        return notable_followers_data

def main():
    parser = argparse.ArgumentParser(description="Obtener Notable Followers de una cuenta de Twitter")
    parser.add_argument("username", help="Nombre de usuario de Twitter para analizar")
    parser.add_argument("--output", "-o", help="Archivo de salida para guardar los resultados (opcional)")
    parser.add_argument("--headless", action="store_true", help="Ejecutar en modo headless (sin interfaz gráfica)")
    
    args = parser.parse_args()
    
    try:
        # Obtener el número de Notable Followers
        result = asyncio.run(get_notable_followers_count(args.username, args.headless))
        
        if result:
            print("\n" + "="*50)
            print(f"RESULTADO PARA @{args.username}:")
            print(f"Número de Notable Followers: {result['count']}")
            
            # Mostrar algunos notable followers si están disponibles
            if result['followers'] and len(result['followers']) > 0:
                print("\nAlgunos Notable Followers:")
                for i, follower in enumerate(result['followers'][:5], 1):  # Mostrar hasta 5 followers
                    username = follower.get('username', 'N/A')
                    name = follower.get('name', 'N/A')
                    print(f"{i}. @{username} - {name}")
                
                if len(result['followers']) > 5:
                    print(f"... y {len(result['followers']) - 5} más")
            
            print("="*50)
            
            # Guardar resultados si se especificó un archivo de salida
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\nResultados guardados en {args.output}")
        else:
            print("\nNo se pudieron obtener los Notable Followers.")
            print("Sugerencias:")
            print("1. Asegúrate de haber iniciado sesión correctamente en Protokols")
            print("2. Verifica que el nombre de usuario de Twitter sea correcto")
            print("3. Intenta con otro usuario de Twitter más popular")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"\nError al obtener Notable Followers: {str(e)}")

if __name__ == "__main__":
    main() 