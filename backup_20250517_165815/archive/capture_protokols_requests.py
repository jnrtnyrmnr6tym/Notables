#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para capturar las peticiones y respuestas de red de Protokols mientras navegas.
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    print("Iniciando script...")
    
    try:
        async with async_playwright() as p:
            print("Lanzando navegador...")
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Lista para guardar las peticiones y respuestas
            requests = []
            
            async def handle_response(response):
                if "protokols.io/api" in response.url:
                    try:
                        response_body = await response.text()
                        print(f"\nRespuesta recibida para: {response.url}")
                        print(f"Status: {response.status}")
                        print(f"Body: {response_body[:200]}...")  # Mostrar solo los primeros 200 caracteres
                        
                        # Buscar la petición correspondiente
                        for req in requests:
                            if req["url"] == response.url:
                                req["response"] = response_body
                                break
                    except Exception as e:
                        print(f"Error al procesar respuesta: {str(e)}")
            
            async def handle_request(request):
                if "protokols.io/api" in request.url:
                    print(f"\nNueva petición detectada:")
                    print(f"URL: {request.url}")
                    print(f"Método: {request.method}")
                    
                    requests.append({
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "post_data": request.post_data
                    })
            
            # Registrar los eventos
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            print("\nNavegando a la página de login de Protokols...")
            await page.goto("https://www.protokols.io/sign-in")
            
            print("\n=== INSTRUCCIONES ===")
            print("1. Inicia sesión con tus credenciales")
            print("2. Una vez dentro, navega a la página del usuario (ej: /twitter/ironspiderXBT)")
            print("3. Navega a la lista de notable followers")
            print("4. Haz scroll en la lista")
            print("5. Cuando termines, vuelve aquí y pulsa ENTER")
            input("\nPresiona ENTER cuando hayas terminado...")
            
            # Esperar un momento para que se procesen las últimas respuestas
            print("\nEsperando a que se procesen las últimas respuestas...")
            await asyncio.sleep(2)
            
            # Guardar las peticiones
            output_file = "protokols_requests_log.json"
            print(f"\nGuardando {len(requests)} peticiones en {output_file}...")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
            print("¡Peticiones guardadas exitosamente!")
            
            await browser.close()
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript interrumpido por el usuario")
    except Exception as e:
        print(f"\nERROR FATAL: {str(e)}")
        raise 