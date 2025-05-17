"""
Script para explorar direcciones de Solana con navegación manual para superar la protección de Cloudflare.
"""

import time
import re
import os
from playwright.sync_api import sync_playwright

def manual_explore_solana(address):
    print(f"Preparando explorador para la dirección: {address}")
    
    # Crear directorios para capturas
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    try:
        with sync_playwright() as p:
            # Iniciar navegador
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navegar a la página de la dirección
            account_url = f"https://solscan.io/account/{address}"
            print(f"Abriendo: {account_url}")
            page.goto(account_url, timeout=60000)
            
            print("\n" + "="*80)
            print("INSTRUCCIONES:")
            print("1. Resuelve manualmente el captcha de Cloudflare si aparece")
            print("2. Navega por la página para ver la información de la dirección")
            print("3. Cuando estés en una página con información relevante, presiona Enter")
            print("4. El script capturará la información visible y continuará")
            print("="*80)
            
            input("\nPresiona Enter cuando hayas superado Cloudflare y estés viendo la información... ")
            
            # Capturar la URL actual
            current_url = page.url
            print(f"\nURL actual: {current_url}")
            
            # Tomar captura de pantalla
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"{screenshot_dir}/solana_{address[:8]}_{timestamp}.png"
            page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada como '{screenshot_path}'")
            
            # Extraer información visible
            print("\nExtrayendo información visible en la página...")
            
            # Buscar etiquetas y nombres
            try:
                labels = page.locator("text=/Label|Name|Tag/i").all()
                if labels:
                    print("\nEtiquetas/nombres encontrados:")
                    for label in labels:
                        try:
                            parent = label.evaluate("el => el.closest('tr') || el.closest('div')")
                            parent_text = page.evaluate("el => el.innerText", parent)
                            print(f"  {parent_text.strip()}")
                        except:
                            pass
            except Exception as e:
                print(f"Error al buscar etiquetas: {str(e)}")
            
            # Buscar tokens
            try:
                token_links = page.locator("a[href*='/token/']").all()
                if token_links:
                    print("\nTokens relacionados:")
                    seen_tokens = set()
                    for link in token_links[:15]:  # Limitar a 15 tokens
                        try:
                            href = link.get_attribute("href")
                            text = link.inner_text().strip()
                            if text and href and text not in seen_tokens:
                                seen_tokens.add(text)
                                print(f"  {text} - {href}")
                        except:
                            pass
            except Exception as e:
                print(f"Error al buscar tokens: {str(e)}")
                
            # Buscar información de Twitter
            try:
                twitter_links = page.locator("a[href*='twitter.com']").all()
                if twitter_links:
                    print("\nEnlaces a Twitter:")
                    for link in twitter_links:
                        try:
                            href = link.get_attribute("href")
                            text = link.inner_text().strip()
                            print(f"  {text} - {href}")
                            
                            # Extraer nombre de usuario de Twitter
                            if "twitter.com/" in href:
                                match = re.search(r'twitter\.com/([^/\?]+)', href)
                                if match:
                                    twitter_username = match.group(1)
                                    print(f"  → Usuario: @{twitter_username}")
                        except:
                            pass
                
                # Buscar menciones a Twitter en el texto
                if not twitter_links:
                    body_text = page.evaluate("() => document.body.innerText")
                    twitter_handles = re.findall(r'@([A-Za-z0-9_]+)', body_text)
                    if twitter_handles:
                        unique_handles = set(twitter_handles)
                        print("\nPosibles usuarios de Twitter mencionados:")
                        for handle in unique_handles:
                            # Filtrar handles que parecen nombres de usuario de Twitter válidos
                            if len(handle) > 2 and len(handle) < 16:
                                print(f"  @{handle}")
            except Exception as e:
                print(f"Error al buscar información de Twitter: {str(e)}")
            
            # Opciones para explorar más
            while True:
                print("\n" + "="*80)
                print("OPCIONES:")
                print("1. Capturar información de la página actual")
                print("2. Navegar a la sección de transacciones")
                print("3. Navegar a la sección de tokens (si está disponible)")
                print("4. Buscar creador del token (si es un token)")
                print("5. Tomar otra captura de pantalla")
                print("6. Salir")
                print("="*80)
                
                choice = input("\nSelecciona una opción (1-6): ")
                
                if choice == "1":
                    # Capturar información actualizada
                    print("\nCapturando información actualizada...")
                    current_url = page.url
                    print(f"URL actual: {current_url}")
                    
                    # Guardar HTML de la página para análisis posterior
                    html_content = page.content()
                    html_file = f"solana_page_{address[:8]}_{timestamp}.html"
                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"HTML guardado como '{html_file}'")
                    
                    # Tomar captura actualizada
                    new_screenshot = f"{screenshot_dir}/solana_{address[:8]}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=new_screenshot)
                    print(f"Nueva captura guardada como '{new_screenshot}'")
                    
                elif choice == "2":
                    # Navegar a transacciones
                    print("\nNavegando a la sección de transacciones...")
                    if "token" in current_url:
                        txn_url = f"{current_url}/txs"
                    else:
                        txn_url = f"https://solscan.io/account/{address}#txs"
                    
                    page.goto(txn_url, timeout=60000)
                    print("Espera mientras carga la página de transacciones...")
                    time.sleep(5)
                    
                    # Tomar captura
                    txn_screenshot = f"{screenshot_dir}/transactions_{address[:8]}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=txn_screenshot)
                    print(f"Captura de transacciones guardada como '{txn_screenshot}'")
                    
                elif choice == "3":
                    # Navegar a tokens
                    print("\nNavegando a la sección de tokens...")
                    if "token" in current_url:
                        token_url = f"{current_url}/holders"
                    else:
                        token_url = f"https://solscan.io/account/{address}#splTransfer"
                    
                    page.goto(token_url, timeout=60000)
                    print("Espera mientras carga la página de tokens...")
                    time.sleep(5)
                    
                    # Tomar captura
                    token_screenshot = f"{screenshot_dir}/tokens_{address[:8]}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=token_screenshot)
                    print(f"Captura de tokens guardada como '{token_screenshot}'")
                    
                elif choice == "4":
                    # Buscar creador del token
                    print("\nBuscando información del creador...")
                    
                    # Buscar enlaces que podrían ser el creador
                    creator_links = page.locator("text=/Creator|Mint|Authority/i").all()
                    if creator_links:
                        print("Posibles enlaces a creadores:")
                        for link in creator_links:
                            try:
                                parent = link.evaluate("el => el.closest('tr') || el.closest('div')")
                                parent_text = page.evaluate("el => el.innerText", parent)
                                print(f"  {parent_text.strip()}")
                                
                                # Buscar direcciones Solana en el texto
                                address_match = re.search(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', parent_text)
                                if address_match:
                                    creator_address = address_match.group(0)
                                    print(f"  → Posible dirección: {creator_address}")
                                    
                                    # Preguntar si quiere navegar a esta dirección
                                    nav = input("  ¿Navegar a esta dirección? (s/n): ")
                                    if nav.lower() == 's':
                                        creator_url = f"https://solscan.io/account/{creator_address}"
                                        page.goto(creator_url, timeout=60000)
                                        print("  Navegando a la dirección del creador...")
                                        time.sleep(5)
                                        break
                            except:
                                pass
                    else:
                        print("No se encontraron links claros al creador en esta página.")
                
                elif choice == "5":
                    # Tomar captura de pantalla
                    screenshot = f"{screenshot_dir}/solana_manual_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=screenshot)
                    print(f"\nCaptura guardada como '{screenshot}'")
                    
                elif choice == "6":
                    print("\nSaliendo del explorador...")
                    break
                    
                else:
                    print("\nOpción no válida. Introduce un número del 1 al 6.")
            
            browser.close()
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Dirección para explorar
    address = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    manual_explore_solana(address) 