"""
Script para abrir un navegador y guardar las cookies de Axiom una vez el usuario esté logueado con email.
"""

import json
import time
from playwright.sync_api import sync_playwright

def save_axiom_cookies():
    try:
        with sync_playwright() as p:
            # Lanzar navegador en modo visible
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navegar a Axiom
            print("Abriendo el navegador en Axiom...")
            page.goto("https://axiom.trade/pulse")
            
            # Instrucciones para el usuario
            print("\n" + "="*80)
            print("INSTRUCCIONES:")
            print("1. Conéctate a Axiom usando tu email")
            print("2. Una vez que estés logueado y veas la página de Pulse, presiona Enter en la consola")
            print("3. Las cookies se guardarán automáticamente")
            print("="*80 + "\n")
            
            # Esperar a que el usuario inicie sesión
            input("Presiona Enter cuando hayas completado el login en Axiom... ")
            
            # Guardar cookies
            cookies = context.cookies()
            with open("axiom_cookies.json", "w") as f:
                json.dump(cookies, f, indent=2)
                
            print(f"\n✅ ÉXITO: Cookies guardadas en 'axiom_cookies.json'")
            
            # Tomar una captura de pantalla como confirmación
            page.screenshot(path="axiom_logged_in.png")
            print("Captura de pantalla guardada como 'axiom_logged_in.png'")
            
            # Mostrar cookies importantes para verificación
            auth_cookies = [c for c in cookies if "token" in c["name"].lower() or "auth" in c["name"].lower()]
            if auth_cookies:
                print("\nCookies relacionadas con autenticación encontradas:")
                for cookie in auth_cookies:
                    print(f"- {cookie['name']}: {cookie['value'][:10]}...")
            
            # Mantener abierto el navegador un momento para que el usuario pueda ver
            print("\nCerrando el navegador en 5 segundos...")
            time.sleep(5)
            
            browser.close()
            
            print("\nPuedes usar estas cookies para acceder a Axiom en scripts automatizados.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    save_axiom_cookies() 