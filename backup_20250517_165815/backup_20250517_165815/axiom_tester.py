"""
Script para probar el acceso a Axiom usando cookies guardadas.
Este script intentará acceder a Axiom usando las cookies guardadas previamente
y verificará si podemos acceder a la página de Pulse sin necesidad de iniciar sesión.
"""

import json
import os
from playwright.sync_api import sync_playwright

def test_axiom_access():
    # Verificar que el archivo de cookies exista
    if not os.path.exists("axiom_cookies.json"):
        print("Error: No se encontró el archivo 'axiom_cookies.json'")
        print("Primero debes ejecutar 'axiom_cookie_extractor.py' para guardar las cookies")
        return False
    
    # Cargar las cookies guardadas
    with open("axiom_cookies.json", "r") as f:
        cookies = json.load(f)
    
    print(f"Cargadas {len(cookies)} cookies desde 'axiom_cookies.json'")
    
    with sync_playwright() as p:
        # Iniciar navegador en modo headless (invisible)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # Aplicar las cookies guardadas
        context.add_cookies(cookies)
        
        # Abrir una página y navegar a Axiom
        page = context.new_page()
        print("Intentando acceder a Axiom Pulse...")
        page.goto("https://axiom.trade/pulse")
        
        # Esperar a que la página cargue completamente
        page.wait_for_load_state("networkidle")
        
        # Capturar screenshot para verificación visual
        page.screenshot(path="axiom_test_screenshot.png")
        print("Captura de pantalla guardada como 'axiom_test_screenshot.png'")
        
        # Intentar verificar si estamos logueados comprobando elementos de la UI
        # Esto es un ejemplo y podría necesitar ajustes según la estructura real de la página
        try:
            # Verificar si hay elementos que solo aparecen cuando estás logueado
            # Por ejemplo, buscar un elemento que contenga el texto "Disconnect" (botón para desconectar wallet)
            # o cualquier otro elemento que solo aparezca para usuarios logueados
            logged_in = page.locator("text=Disconnect").is_visible(timeout=5000) or \
                        page.locator("text=Connected").is_visible(timeout=5000)
            
            if logged_in:
                print("\n✅ ÉXITO: Sesión mantenida correctamente. Estás logueado en Axiom.")
                
                # Intentar detectar tokens en la página
                # Esto es solo un ejemplo y necesitaría ajustes según la estructura real
                tokens_table = page.locator("table").first
                if tokens_table.is_visible():
                    print("Se ha detectado una tabla que podría contener tokens.")
                    # Aquí podrías añadir código para extraer datos de la tabla
            else:
                print("\n❌ ERROR: No se detectó una sesión activa. Es posible que las cookies hayan expirado.")
        except Exception as e:
            print(f"\n❌ ERROR durante la verificación: {str(e)}")
            print("Es posible que la estructura de la página haya cambiado o que las cookies hayan expirado.")
        
        browser.close()
    
    return True

if __name__ == "__main__":
    test_axiom_access() 