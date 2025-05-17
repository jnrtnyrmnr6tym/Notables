"""
Script para probar el acceso a Axiom usando las cookies guardadas.
"""

import json
import time
from playwright.sync_api import sync_playwright

def test_axiom_with_cookies():
    try:
        # Cargar las cookies desde el archivo
        try:
            with open("axiom_cookies.json", "r") as f:
                cookies = json.load(f)
            print(f"✅ Cookies cargadas correctamente. Encontradas {len(cookies)} cookies.")
        except Exception as e:
            print(f"❌ Error al cargar las cookies: {str(e)}")
            return
        
        # Mostrar cookies de autenticación
        auth_cookies = [c for c in cookies if "token" in c["name"].lower() or "auth" in c["name"].lower()]
        if auth_cookies:
            print("\nCookies relacionadas con autenticación:")
            for cookie in auth_cookies:
                print(f"- {cookie['name']}: {cookie['value'][:15]}...")
        
        with sync_playwright() as p:
            # Lanzar navegador
            print("\nIniciando navegador...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            
            # Aplicar las cookies guardadas
            context.add_cookies(cookies)
            
            # Navegar a Axiom Pulse
            page = context.new_page()
            print("Navegando a Axiom Pulse...")
            page.goto("https://axiom.trade/pulse")
            
            # Esperar a que la página cargue
            page.wait_for_load_state("networkidle")
            
            # Tomar captura de pantalla
            page.screenshot(path="axiom_test_result.png")
            print("Captura de pantalla guardada como 'axiom_test_result.png'")
            
            # Verificar si estamos autenticados
            print("\nComprobando estado de autenticación...")
            
            # Dar tiempo para que la página se cargue completamente
            time.sleep(3)
            
            # Verificar si hay elementos que indiquen sesión iniciada
            try:
                # Buscar elementos que indiquen sesión iniciada
                # Verificamos si hay un botón de 'Sign in'/'Login'/'Connect'
                login_button_exists = False
                try:
                    # Usar selectores más precisos para los botones de login
                    login_button_exists = page.get_by_role("button", name="Sign In").is_visible(timeout=2000) or \
                                         page.get_by_role("button", name="Login").is_visible(timeout=2000) or \
                                         page.get_by_role("button", name="Connect").is_visible(timeout=2000)
                except:
                    # Si falla, es posible que los botones no existan, lo cual es bueno si estamos logueados
                    pass
                
                # Verificamos la URL después de la navegación
                current_url = page.url
                print(f"URL actual: {current_url}")
                
                # Verificar si podemos ver elementos que solo deberían ser visibles para usuarios logueados
                elements_logged_in = False
                try:
                    # Intenta encontrar elementos típicos de la UI para usuarios autenticados
                    elements_logged_in = page.get_by_text("My Portfolio").is_visible(timeout=2000) or \
                                        page.get_by_text("Dashboard").is_visible(timeout=2000)
                except:
                    pass
                
                # Si no hay botón de login visible y/o se ven elementos de usuario logueado, asumimos que la sesión está activa
                if (not login_button_exists or elements_logged_in) and "pulse" in current_url:
                    print("\n✅ ÉXITO: Parece que las cookies funcionan correctamente.")
                    
                    # Intentar verificar si hay datos de tokens
                    tables = page.locator("table").count()
                    if tables > 0:
                        print(f"Se detectaron {tables} tablas que pueden contener tokens.")
                    else:
                        print("No se detectaron tablas de datos en la página.")
                else:
                    print("\n❌ ERROR: No se detectó una sesión activa. Es posible que las cookies hayan expirado.")
                    if login_button_exists:
                        print("Se detectó un botón de login, lo que indica que no hay sesión activa.")
            except Exception as e:
                print(f"\n❌ ERROR durante la verificación: {str(e)}")
            
            # Mantener el navegador abierto brevemente
            print("\nManteniendo el navegador abierto por 15 segundos...")
            time.sleep(15)
            
            browser.close()
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    test_axiom_with_cookies() 