"""
Script para extraer cookies de Axiom después de un login manual.
Este script abrirá un navegador donde podrás iniciar sesión manualmente en Axiom.
Una vez iniciada la sesión, el script esperará 60 segundos para que inicies sesión.
"""

import json
import time
from playwright.sync_api import sync_playwright

def extract_cookies():
    with sync_playwright() as p:
        # Lanzar navegador visible
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navegar a Axiom
        print("Navegando a Axiom...")
        page.goto("https://axiom.trade/pulse")
        
        # Instrucciones en la consola
        print("\nPor favor, inicia sesión en Axiom manualmente con tu wallet.")
        print("Tienes 60 segundos para iniciar sesión antes de que el script continue.")
        
        # Esperar un tiempo fijo para que el usuario inicie sesión (60 segundos)
        for i in range(60, 0, -1):
            print(f"\rTiempo restante: {i} segundos...", end="")
            time.sleep(1)
        
        print("\n\nTiempo completado. Extrayendo cookies...")
        
        # Guardar las cookies
        cookies = context.cookies()
        with open("axiom_cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
        
        print(f"Se han guardado {len(cookies)} cookies en 'axiom_cookies.json'")
        
        # Opcional: mostrar algunas cookies (sin mostrar valores completos por seguridad)
        if cookies:
            print("\nAlgunas cookies guardadas (nombres):")
            for i, cookie in enumerate(cookies[:5]):  # Mostrar solo hasta 5 cookies
                name = cookie.get('name', 'N/A')
                domain = cookie.get('domain', 'N/A')
                print(f"  {i+1}. {name} (dominio: {domain})")
            
            if len(cookies) > 5:
                print(f"  ... y {len(cookies) - 5} más")
        
        # Tomar una captura de pantalla para verificación
        page.screenshot(path="axiom_login_screenshot.png")
        print("Captura de pantalla guardada como 'axiom_login_screenshot.png'")
        
        browser.close()
        print("\nProceso completado. Ahora puedes usar estas cookies para mantener la sesión.")

if __name__ == "__main__":
    extract_cookies() 