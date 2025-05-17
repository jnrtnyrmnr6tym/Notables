#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para monitorear las solicitudes de red en Protokols y detectar las llamadas a la API
específicamente relacionadas con notable followers.

Este script:
1. Abre un navegador con Playwright
2. Navega a la página de inicio de sesión de Protokols
3. Permite al usuario iniciar sesión manualmente y navegar libremente
4. Registra todas las solicitudes de red, especialmente las llamadas a la API
5. Guarda las solicitudes relevantes en un archivo JSON para su análisis
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

logger = logging.getLogger("ProtokolsNetworkMonitor")

async def monitor_network_requests(headless=False, timeout=300):
    """
    Abre un navegador con Playwright y monitorea las solicitudes de red.
    
    Args:
        headless: Si el navegador debe ejecutarse en modo headless (sin interfaz gráfica)
        timeout: Tiempo máximo de espera para la interacción del usuario (en segundos)
        
    Returns:
        list: Lista de solicitudes de red relevantes
    """
    logger.info("Iniciando Playwright...")
    api_requests = []
    
    async with async_playwright() as p:
        # Lanzar navegador (Chrome/Chromium)
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        
        # Configurar el evento para capturar solicitudes de red
        async def on_request(request):
            if "api.protokols.io" in request.url:
                logger.info(f"Solicitud API detectada: {request.url}")
                try:
                    # Intentar obtener los datos de la solicitud
                    post_data = request.post_data
                    headers = request.headers
                    method = request.method
                    
                    req_info = {
                        "timestamp": datetime.now().isoformat(),
                        "url": request.url,
                        "method": method,
                        "headers": dict(headers),
                        "post_data": post_data
                    }
                    
                    api_requests.append(req_info)
                    
                    # Imprimir información detallada para solicitudes relacionadas con Twitter o notable followers
                    if ("twitter" in request.url.lower() or 
                        "kol" in request.url.lower() or 
                        "influencer" in request.url.lower() or
                        "notable" in request.url.lower()):
                        logger.info(f"Solicitud relevante detectada:")
                        logger.info(f"  URL: {request.url}")
                        logger.info(f"  Método: {method}")
                        logger.info(f"  Datos: {post_data}")
                    
                except Exception as e:
                    logger.error(f"Error al procesar solicitud: {str(e)}")
        
        # Configurar el evento para capturar respuestas de red
        async def on_response(response):
            if "api.protokols.io" in response.url:
                logger.info(f"Respuesta API detectada: {response.url} (Status: {response.status})")
                try:
                    # Intentar obtener los datos de la respuesta
                    response_data = None
                    try:
                        response_data = await response.json()
                    except:
                        try:
                            response_data = await response.text()
                        except:
                            response_data = "No se pudo extraer el contenido de la respuesta"
                    
                    # Actualizar la solicitud correspondiente con la respuesta
                    for req in api_requests:
                        if req["url"] == response.url:
                            req["response"] = {
                                "status": response.status,
                                "data": response_data
                            }
                            
                            # Imprimir información detallada para respuestas relacionadas con Twitter o notable followers
                            if ("twitter" in response.url.lower() or 
                                "kol" in response.url.lower() or 
                                "influencer" in response.url.lower() or
                                "notable" in response.url.lower()):
                                logger.info(f"Respuesta relevante detectada:")
                                logger.info(f"  URL: {response.url}")
                                logger.info(f"  Status: {response.status}")
                                
                                # Intentar extraer información sobre notable followers
                                if isinstance(response_data, dict):
                                    try:
                                        if "result" in response_data and "data" in response_data["result"]:
                                            data = response_data["result"]["data"]
                                            
                                            if "notableFollowers" in data:
                                                notable_followers = data["notableFollowers"]
                                                logger.info(f"  Notable Followers encontrados: {len(notable_followers)}")
                                            
                                            elif "profile" in data and "notableFollowersCount" in data["profile"]:
                                                count = data["profile"]["notableFollowersCount"]
                                                logger.info(f"  Contador de Notable Followers: {count}")
                                    except Exception as e:
                                        logger.error(f"Error al analizar respuesta: {str(e)}")
                            
                            break
                except Exception as e:
                    logger.error(f"Error al procesar respuesta: {str(e)}")
        
        # Registrar los eventos
        context.on("request", on_request)
        context.on("response", on_response)
        
        # Crear una nueva página
        page = await context.new_page()
        
        # Navegar a la página de inicio de sesión de Protokols
        logger.info("Navegando a la página de inicio de sesión de Protokols...")
        await page.goto("https://www.protokols.io/sign-in")
        
        print("\n" + "="*80)
        print("INSTRUCCIONES PARA CAPTURAR LAS SOLICITUDES DE NOTABLE FOLLOWERS:")
        print("1. Inicia sesión manualmente en Protokols en el navegador que se ha abierto")
        print("2. Una vez iniciada la sesión, busca y navega a cualquier perfil de Twitter que desees")
        print("   - Puedes usar la barra de búsqueda o ir directamente a una URL como:")
        print("     https://www.protokols.io/twitter/elonmusk")
        print("3. Busca específicamente la sección de 'Notable Followers' en la página")
        print("4. Observa las solicitudes que aparecen en esta terminal")
        print("5. Puedes navegar a otros perfiles si lo deseas")
        print("6. Cuando hayas terminado, vuelve aquí y presiona Enter")
        print("="*80 + "\n")
        
        # Esperar a que el usuario confirme que ha terminado
        input("Presiona Enter cuando hayas terminado de navegar y quieras cerrar el navegador...")
        
        # Cerrar el navegador
        await browser.close()
        
        return api_requests

def save_requests_to_file(requests, output_file):
    """
    Guarda las solicitudes de red en un archivo JSON.
    
    Args:
        requests: Lista de solicitudes de red
        output_file: Ruta al archivo de salida
    
    Returns:
        bool: True si las solicitudes se guardaron correctamente, False en caso contrario
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(requests, f, indent=2, default=str)
        logger.info(f"Solicitudes guardadas en {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar solicitudes: {str(e)}")
        return False

async def main_async():
    parser = argparse.ArgumentParser(description="Protokols Network Monitor")
    parser.add_argument("--output", "-o", default="protokols_requests.json",
                        help="Archivo de salida para guardar las solicitudes")
    parser.add_argument("--headless", action="store_true",
                        help="Ejecutar el navegador en modo headless (sin interfaz gráfica)")
    
    args = parser.parse_args()
    
    try:
        # Monitorear solicitudes de red
        requests = await monitor_network_requests(headless=args.headless)
        
        if not requests:
            logger.warning("No se detectaron solicitudes API relevantes.")
            return
        
        # Guardar solicitudes
        if save_requests_to_file(requests, args.output):
            print(f"\nSolicitudes API guardadas exitosamente en {args.output}")
            print(f"Total de solicitudes guardadas: {len(requests)}")
            
            # Mostrar las rutas de API detectadas relacionadas con Twitter o KOL
            print("\nRutas de API relevantes detectadas:")
            relevant_paths = []
            for req in requests:
                url = req["url"]
                if "twitter" in url.lower() or "kol" in url.lower() or "influencer" in url.lower() or "notable" in url.lower():
                    path = url.split("trpc/")[1] if "trpc/" in url else url
                    relevant_paths.append((path, req.get("method", ""), req.get("response", {}).get("status", "")))
            
            if relevant_paths:
                for i, (path, method, status) in enumerate(relevant_paths, 1):
                    print(f"{i}. [{method} - {status}] {path}")
            else:
                print("No se detectaron rutas de API relevantes relacionadas con Twitter o Notable Followers.")
                print("Intenta navegar específicamente a un perfil de Twitter en Protokols.")
        else:
            print(f"\nError al guardar las solicitudes en {args.output}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def main():
    """Punto de entrada principal para ejecutar la función asíncrona"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 