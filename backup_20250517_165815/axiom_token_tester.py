"""
Script para probar el acceso a Axiom usando tokens JWT.
Este script intentará acceder a Axiom usando los tokens JWT proporcionados.
"""

import json
from playwright.sync_api import sync_playwright

def test_axiom_with_tokens():
    # Tokens JWT proporcionados
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRoZW50aWNhdGVkVXNlcklkIjoiZjE1MzQzNzQtMDQ5NC00NmVhLTg1NjgtYjdkMWZkN2ZhNTA1IiwiaWF0IjoxNzQ3MTgxNzMyLCJleHAiOjE3NDcxODI2OTJ9.mWs6C74CL_6IMM_9MhWMSf2HRn42Ll2d2WWbdLEosAg"
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWZyZXNoVG9rZW5JZCI6ImNlMmMwNjA1LWJmNWEtNGFiYy1hNTI0LWQwYjNkYzgxNzhmZiIsImlhdCI6MTc0NzE4MTI4OX0.2-1laFIb1wRjK41CbBjGQJ25SekRY-73xZC_oWpDJnk"
    
    # Crear cookies basadas en los tokens JWT
    cookies = [
        {
            "name": "sb-access-token",
            "value": access_token,
            "domain": "axiom.trade",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        },
        {
            "name": "sb-refresh-token",
            "value": refresh_token,
            "domain": "axiom.trade",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }
    ]
    
    # Guardar las cookies para uso futuro
    with open("axiom_tokens.json", "w") as f:
        json.dump(cookies, f, indent=2)
    
    print(f"Tokens guardados en 'axiom_tokens.json'")
    
    try:
        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            
            # Aplicar las cookies con los tokens
            context.add_cookies(cookies)
            
            # Navegar a Axiom
            page = context.new_page()
            print("Navegando a Axiom Pulse...")
            page.goto("https://axiom.trade/pulse")
            
            # Esperar a que la página cargue completamente
            page.wait_for_load_state("networkidle")
            
            # Tomar una captura de pantalla
            page.screenshot(path="axiom_token_test.png")
            print("Captura de pantalla guardada como 'axiom_token_test.png'")
            
            # Verificar si estamos autenticados
            try:
                # Ajustar estos selectores según la estructura real de la página
                logged_in = page.locator("text=Disconnect").is_visible(timeout=5000) or \
                           page.locator("text=Connected").is_visible(timeout=5000)
                
                if logged_in:
                    print("\n✅ ÉXITO: Los tokens JWT funcionan correctamente. Estás logueado en Axiom.")
                    
                    # Intentar detectar elementos que contengan datos de tokens
                    tokens_element = page.locator("table").first
                    if tokens_element.is_visible(timeout=5000):
                        print("Se ha detectado una tabla que podría contener tokens.")
                        
                        # Opcional: extraer algunos datos para verificar
                        tokens_html = tokens_element.inner_html()
                        print(f"Primeros 200 caracteres del contenido HTML: {tokens_html[:200]}...")
                    else:
                        print("No se detectó una tabla de tokens en la página.")
                else:
                    print("\n❌ ERROR: No se detectó una sesión activa. Es posible que los tokens hayan expirado.")
            except Exception as e:
                print(f"\n❌ ERROR durante la verificación: {str(e)}")
                print("Es posible que la estructura de la página haya cambiado o que los tokens hayan expirado.")
            
            browser.close()
    except Exception as e:
        print(f"Error al ejecutar Playwright: {str(e)}")

if __name__ == "__main__":
    test_axiom_with_tokens() 