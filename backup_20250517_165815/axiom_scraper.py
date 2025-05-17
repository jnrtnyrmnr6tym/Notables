"""
Script para iniciar sesión en Axiom y extraer datos de tokens.
"""

import json
import time
import os
import datetime
from playwright.sync_api import sync_playwright, TimeoutError

class AxiomScraper:
    def __init__(self):
        self.cookies_file = "axiom_cookies.json"
        self.screenshot_dir = "screenshots"
        self.data_dir = "data"
        
        # Crear directorios si no existen
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_screenshot(self, page, name):
        """Guarda una captura de pantalla con un nombre específico."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{timestamp}_{name}.png"
        page.screenshot(path=filename)
        print(f"Captura guardada: {filename}")
        return filename
    
    def login_and_save_cookies(self):
        """Abre un navegador para que el usuario inicie sesión y guarda las cookies."""
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
                print("INSTRUCCIONES PARA INICIAR SESIÓN:")
                print("1. Conéctate a Axiom usando tu email")
                print("2. Una vez que estés logueado completamente y veas la página de Pulse, presiona Enter")
                print("3. Las cookies se guardarán automáticamente")
                print("="*80 + "\n")
                
                # Esperar a que el usuario inicie sesión
                input("Presiona Enter cuando hayas completado el login en Axiom... ")
                
                # Guardar cookies
                cookies = context.cookies()
                with open(self.cookies_file, "w") as f:
                    json.dump(cookies, f, indent=2)
                    
                print(f"\n✅ ÉXITO: Cookies guardadas en '{self.cookies_file}'")
                
                # Tomar una captura de pantalla como confirmación
                self.save_screenshot(page, "login_successful")
                
                # Mostrar cookies importantes para verificación
                auth_cookies = [c for c in cookies if "token" in c["name"].lower() or "auth" in c["name"].lower()]
                if auth_cookies:
                    print("\nCookies relacionadas con autenticación encontradas:")
                    for cookie in auth_cookies:
                        print(f"- {cookie['name']}: {cookie['value'][:15]}...")
                
                browser.close()
                return True
                
        except Exception as e:
            print(f"Error durante el inicio de sesión: {str(e)}")
            return False
    
    def load_cookies(self):
        """Carga las cookies desde el archivo."""
        try:
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
            print(f"✅ Cookies cargadas: {len(cookies)} cookies encontradas")
            return cookies
        except Exception as e:
            print(f"❌ Error al cargar cookies: {str(e)}")
            return None
    
    def check_authentication(self, page):
        """Verifica si estamos autenticados."""
        try:
            # Verificar URL
            current_url = page.url
            print(f"URL actual: {current_url}")
            
            # Verificar si hay botones de login
            login_visible = False
            try:
                login_visible = page.get_by_role("button", name="Sign In").is_visible(timeout=2000) or \
                              page.get_by_role("button", name="Login").is_visible(timeout=2000) or \
                              page.get_by_role("button", name="Connect").is_visible(timeout=2000)
            except:
                pass
            
            # Verificar elementos de sesión iniciada
            logged_in_elements = False
            try:
                logged_in_elements = page.get_by_text("My Portfolio").is_visible(timeout=2000) or \
                                   page.get_by_text("Dashboard").is_visible(timeout=2000)
            except:
                pass
            
            # Determinar estado de autenticación
            is_authenticated = (not login_visible or logged_in_elements) and "/pulse" in current_url
            
            if is_authenticated:
                print("✅ Autenticación verificada: Sesión activa")
            else:
                print("❌ No se detectó sesión activa")
                if login_visible:
                    print("   Se encontró botón de login (no estás logueado)")
                if "/pulse" not in current_url:
                    print(f"   URL incorrecta: {current_url} (debería contener '/pulse')")
            
            return is_authenticated
            
        except Exception as e:
            print(f"Error al verificar autenticación: {str(e)}")
            return False
    
    def scrape_tokens(self):
        """Extrae datos de tokens de Axiom usando cookies guardadas."""
        try:
            # Cargar cookies
            cookies = self.load_cookies()
            if not cookies:
                print("No se pudieron cargar las cookies. Ejecutando inicio de sesión...")
                if not self.login_and_save_cookies():
                    return False
                cookies = self.load_cookies()
                if not cookies:
                    print("No se pudo completar el inicio de sesión.")
                    return False
            
            with sync_playwright() as p:
                # Lanzar navegador
                print("\nIniciando navegador para extracción de datos...")
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                
                # Aplicar cookies
                context.add_cookies(cookies)
                
                # Navegar a Axiom Pulse
                page = context.new_page()
                print("Navegando a Axiom Pulse...")
                page.goto("https://axiom.trade/pulse")
                
                # Esperar a que la página cargue
                page.wait_for_load_state("networkidle")
                time.sleep(2)  # Espera adicional
                
                # Verificar autenticación
                if not self.check_authentication(page):
                    print("Sesión no iniciada. Intentando nuevo login...")
                    browser.close()
                    if self.login_and_save_cookies():
                        print("Login completado. Reiniciando extracción...")
                        return self.scrape_tokens()
                    else:
                        return False
                
                # Tomar captura de pantalla de la página de tokens
                self.save_screenshot(page, "tokens_page")
                
                # Intentar extraer datos de tokens
                print("\nBuscando datos de tokens...")
                
                # Buscar tablas
                tables = page.locator("table").count()
                if tables > 0:
                    print(f"Se encontraron {tables} tablas")
                    
                    # Extraer datos de la primera tabla
                    table = page.locator("table").first
                    
                    # Intentar extraer filas
                    rows = table.locator("tr").count()
                    print(f"La tabla contiene {rows} filas")
                    
                    # Extraer datos de las filas
                    tokens_data = []
                    for i in range(1, min(rows, 10)):  # Procesar hasta 10 filas (omitir header)
                        try:
                            row = table.locator("tr").nth(i)
                            cells = row.locator("td")
                            cells_count = cells.count()
                            
                            if cells_count > 0:
                                token_data = {}
                                # Extraer datos según la estructura de la tabla
                                for j in range(cells_count):
                                    cell_text = cells.nth(j).inner_text().strip()
                                    if j == 0:
                                        token_data["name"] = cell_text
                                    elif j == 1:
                                        token_data["price"] = cell_text
                                    else:
                                        token_data[f"column_{j}"] = cell_text
                                
                                tokens_data.append(token_data)
                                print(f"Token extraído: {token_data}")
                        except Exception as e:
                            print(f"Error al procesar fila {i}: {str(e)}")
                    
                    # Guardar datos extraídos
                    if tokens_data:
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        data_file = f"{self.data_dir}/tokens_{timestamp}.json"
                        with open(data_file, "w") as f:
                            json.dump(tokens_data, f, indent=2)
                        print(f"\n✅ Datos guardados en {data_file}")
                    else:
                        print("No se pudieron extraer datos de tokens")
                else:
                    print("No se encontraron tablas en la página")
                
                print("\nManteniendo navegador abierto por 10 segundos...")
                time.sleep(10)
                browser.close()
                
                return True
                
        except Exception as e:
            print(f"Error durante la extracción de datos: {str(e)}")
            return False
    
def main():
    print("="*80)
    print("INICIANDO AXIOM SCRAPER")
    print("="*80)
    
    scraper = AxiomScraper()
    
    print("\n[1] Iniciar sesión y guardar cookies")
    print("[2] Extraer datos usando cookies existentes")
    print("[3] Ejecutar secuencia completa (login y extracción)")
    
    choice = input("\nSelecciona una opción (1-3): ")
    
    if choice == "1":
        scraper.login_and_save_cookies()
    elif choice == "2":
        scraper.scrape_tokens()
    elif choice == "3":
        if scraper.login_and_save_cookies():
            time.sleep(1)
            scraper.scrape_tokens()
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main() 