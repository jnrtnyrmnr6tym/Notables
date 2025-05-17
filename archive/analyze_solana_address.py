"""
Script para analizar una dirección de Solana y buscar información relacionada con tokens y Twitter.
"""

import time
import re
import os
from playwright.sync_api import sync_playwright

def analyze_solana_address(address):
    print(f"Analizando dirección de Solana: {address}")
    
    # Crear directorio para capturas de pantalla
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
            print(f"Accediendo a: {account_url}")
            page.goto(account_url, timeout=60000)  # Aumentar timeout a 60 segundos
            
            # Esperar a que la página cargue
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Espera adicional para asegurar carga completa
            
            # Tomar captura de pantalla
            screenshot_path = f"{screenshot_dir}/account_{address[:8]}.png"
            page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada como '{screenshot_path}'")
            
            # Extraer información de la cuenta
            print("\nExtrayendo información de la cuenta...")
            
            # Buscar etiqueta/nombre de la cuenta
            account_info = {}
            try:
                # Buscar etiquetas/labels
                label_elements = page.locator("text=/Label|Name|Tag/i").all()
                for element in label_elements:
                    try:
                        parent = element.evaluate("el => el.closest('tr') || el.closest('div')")
                        parent_text = page.evaluate("el => el.innerText", parent)
                        if "Label" in parent_text or "Name" in parent_text or "Tag" in parent_text:
                            account_info["label"] = parent_text.strip()
                            print(f"Etiqueta/nombre: {parent_text.strip()}")
                            break
                    except:
                        pass
            except Exception as e:
                print(f"Error al extraer etiqueta: {str(e)}")
            
            # Buscar balance y otros detalles
            try:
                balance_elements = page.locator("text=/Balance|SOL|Total/i").all()
                for element in balance_elements:
                    try:
                        parent = element.evaluate("el => el.closest('tr') || el.closest('div')")
                        parent_text = page.evaluate("el => el.innerText", parent)
                        if "Balance" in parent_text or "SOL" in parent_text:
                            account_info["balance"] = parent_text.strip()
                            print(f"Balance: {parent_text.strip()}")
                            break
                    except:
                        pass
            except Exception as e:
                print(f"Error al extraer balance: {str(e)}")
            
            # Buscar tokens creados
            print("\nBuscando tokens creados por esta cuenta...")
            try:
                # Buscar sección de tokens creados
                tokens_sections = page.locator("text=/Tokens Created|Created Tokens/i").all()
                
                if tokens_sections:
                    print("Se encontró sección de tokens creados")
                    
                    # Intentar encontrar tokens en esta sección
                    token_elements = []
                    for section in tokens_sections:
                        try:
                            # Buscar el contenedor que contiene la sección
                            container = section.evaluate("el => el.closest('.card') || el.closest('section') || el.closest('div[class*=\"container\"]')")
                            # Buscar enlaces a tokens dentro de este contenedor
                            token_links = page.evaluate("""(container) => {
                                const links = container.querySelectorAll('a[href*="/token/"]');
                                return Array.from(links).map(link => {
                                    return {
                                        href: link.href,
                                        text: link.innerText.trim()
                                    };
                                });
                            }""", container)
                            
                            if token_links and len(token_links) > 0:
                                print(f"Se encontraron {len(token_links)} tokens creados:")
                                for i, token in enumerate(token_links):
                                    print(f"  {i+1}. {token['text']} - {token['href']}")
                                    token_elements.append(token)
                        except Exception as e:
                            print(f"Error al procesar sección de tokens: {str(e)}")
                else:
                    # Buscar cualquier token relacionado con esta cuenta
                    all_token_links = page.locator("a[href*='/token/']").all()
                    if all_token_links:
                        print(f"Se encontraron {len(all_token_links)} tokens relacionados:")
                        for i, link in enumerate(all_token_links[:10]):  # Limitar a 10 para evitar spam
                            try:
                                href = link.get_attribute("href")
                                text = link.inner_text().strip()
                                print(f"  {i+1}. {text} - {href}")
                            except:
                                pass
            except Exception as e:
                print(f"Error al buscar tokens: {str(e)}")
            
            # Buscar información de Twitter
            print("\nBuscando conexiones con Twitter...")
            try:
                # Buscar enlaces a Twitter
                twitter_elements = page.locator("a[href*='twitter.com']").all()
                if twitter_elements:
                    print(f"Se encontraron {len(twitter_elements)} enlaces a Twitter:")
                    for i, element in enumerate(twitter_elements):
                        try:
                            href = element.get_attribute("href")
                            text = element.inner_text().strip()
                            print(f"  {i+1}. Enlace: {href}")
                            print(f"     Texto: {text}")
                            
                            # Extraer nombre de usuario de Twitter
                            twitter_username = None
                            if "twitter.com/" in href:
                                match = re.search(r'twitter\.com/([^/\?]+)', href)
                                if match:
                                    twitter_username = match.group(1)
                                    print(f"     Usuario: @{twitter_username}")
                        except:
                            pass
                
                # Buscar menciones a Twitter en el texto
                if not twitter_elements:
                    # Buscar patrones que parezcan @usuario
                    page_text = page.evaluate("() => document.body.innerText")
                    twitter_mentions = re.findall(r'@([A-Za-z0-9_]+)', page_text)
                    if twitter_mentions:
                        print(f"Se encontraron {len(twitter_mentions)} posibles menciones a Twitter:")
                        for i, username in enumerate(set(twitter_mentions)):
                            print(f"  {i+1}. @{username}")
            except Exception as e:
                print(f"Error al buscar conexiones con Twitter: {str(e)}")
            
            # Navegar a la página de transacciones para ver actividad reciente
            print("\nRevisando transacciones recientes...")
            try:
                txn_url = f"https://solscan.io/account/{address}#txs"
                page.goto(txn_url, timeout=60000)
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                
                # Tomar captura de pantalla
                txn_screenshot = f"{screenshot_dir}/transactions_{address[:8]}.png"
                page.screenshot(path=txn_screenshot)
                print(f"Captura de transacciones guardada como '{txn_screenshot}'")
                
                # Extraer información de transacciones recientes
                txn_elements = page.locator("tr").all()
                if len(txn_elements) > 1:  # Ignorar fila de encabezado
                    print(f"Se encontraron {len(txn_elements)-1} transacciones recientes")
                    
                    # Analizar las primeras 5 transacciones
                    for i in range(1, min(6, len(txn_elements))):
                        try:
                            row = txn_elements[i]
                            row_text = row.inner_text()
                            
                            # Buscar enlaces a transacciones
                            txn_link = row.locator("a[href*='/tx/']").first
                            if txn_link:
                                href = txn_link.get_attribute("href")
                                if href:
                                    txn_hash = href.split("/tx/")[1]
                                    print(f"  Transacción {i}: {txn_hash[:10]}...")
                        except:
                            pass
            except Exception as e:
                print(f"Error al revisar transacciones: {str(e)}")
            
            # Mantener el navegador abierto para que el usuario pueda explorar
            print("\n" + "="*80)
            print("El navegador permanecerá abierto para que puedas explorar la información.")
            print("Presiona Enter cuando hayas terminado de revisar.")
            print("="*80)
            
            input()
            
            browser.close()
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    # Dirección de Solana proporcionada
    address = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    analyze_solana_address(address) 