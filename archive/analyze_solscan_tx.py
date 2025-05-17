"""
Script para analizar una transacción de token en Solscan y buscar información del creador.
"""

import requests
import json
import time
import re
from playwright.sync_api import sync_playwright

def analyze_solscan_tx(tx_hash):
    print(f"Analizando transacción: {tx_hash}")
    
    try:
        with sync_playwright() as p:
            # Iniciar navegador
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navegar a la página de la transacción
            tx_url = f"https://solscan.io/tx/{tx_hash}"
            print(f"Accediendo a: {tx_url}")
            page.goto(tx_url)
            
            # Esperar a que la página cargue
            page.wait_for_load_state("networkidle")
            time.sleep(3)  # Espera adicional para asegurar carga completa
            
            # Tomar captura de pantalla
            page.screenshot(path="solscan_tx.png")
            print("Captura de pantalla guardada como 'solscan_tx.png'")
            
            # Extraer información de la transacción
            print("\nExtrayendo información de la transacción...")
            
            # Buscar la dirección del creador (signer)
            signer_elements = page.locator("text=/Signer|Creator|Fee payer/i").all()
            signers = []
            
            for element in signer_elements:
                try:
                    # Buscar elemento padre que pueda contener la dirección
                    parent = element.evaluate("el => el.closest('tr') || el.closest('div')")
                    parent_text = page.evaluate("el => el.innerText", parent)
                    
                    # Buscar direcciones Solana en el texto (formato base58)
                    address_match = re.search(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', parent_text)
                    if address_match:
                        address = address_match.group(0)
                        signers.append({
                            "role": element.inner_text().strip(),
                            "address": address,
                            "context": parent_text.strip()
                        })
                except Exception as e:
                    print(f"Error al extraer signer: {str(e)}")
            
            if signers:
                print(f"Encontrados {len(signers)} signers/creadores:")
                for i, signer in enumerate(signers):
                    print(f"  {i+1}. Rol: {signer['role']}, Dirección: {signer['address']}")
            else:
                print("No se encontraron signers explícitos")
            
            # Buscar información del token
            token_info = {}
            try:
                # Buscar direcciones de token
                token_elements = page.locator("a[href*='/token/']").all()
                if token_elements:
                    for token_element in token_elements:
                        href = token_element.get_attribute("href")
                        if href and "/token/" in href:
                            token_address = href.split("/token/")[1]
                            token_name = token_element.inner_text().strip()
                            token_info["address"] = token_address
                            token_info["name"] = token_name
                            break
                
                # Buscar información adicional del token
                if token_info:
                    print(f"\nToken encontrado: {token_info['name']} ({token_info['address']})")
                    
                    # Intentar encontrar otros datos como símbolo, cantidad, etc.
                    amount_elements = page.locator("text=/Amount|Quantity|Supply/i").all()
                    for element in amount_elements:
                        try:
                            parent = element.evaluate("el => el.closest('tr') || el.closest('div')")
                            parent_text = page.evaluate("el => el.innerText", parent)
                            token_info["amount_data"] = parent_text.strip()
                            print(f"  Información de cantidad: {parent_text.strip()}")
                            break
                        except:
                            pass
            except Exception as e:
                print(f"Error al extraer información del token: {str(e)}")
            
            # Buscar información de Twitter o redes sociales
            twitter_info = {}
            try:
                # Buscar enlaces a Twitter
                twitter_elements = page.locator("a[href*='twitter.com']").all()
                if twitter_elements:
                    for twitter_element in twitter_elements:
                        href = twitter_element.get_attribute("href")
                        twitter_info["url"] = href
                        twitter_info["text"] = twitter_element.inner_text().strip()
                        print(f"\nEnlace a Twitter encontrado: {href}")
                        print(f"  Texto: {twitter_info['text']}")
                
                # Buscar menciones a Twitter en el texto
                if not twitter_elements:
                    twitter_mentions = page.locator("text=/@[a-zA-Z0-9_]+/").all()
                    for mention in twitter_mentions:
                        text = mention.inner_text().strip()
                        twitter_info["mention"] = text
                        print(f"\nMención a Twitter encontrada: {text}")
            except Exception as e:
                print(f"Error al buscar información de Twitter: {str(e)}")
            
            # Buscar conexiones adicionales con el creador
            print("\nBuscando información adicional del creador...")
            
            # Si tenemos una dirección del creador, vamos a su página
            creator_address = None
            for signer in signers:
                if "creator" in signer["role"].lower() or "signer" in signer["role"].lower():
                    creator_address = signer["address"]
                    break
            
            if creator_address:
                print(f"Navegando a la página del creador: {creator_address}")
                creator_url = f"https://solscan.io/account/{creator_address}"
                page.goto(creator_url)
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                
                # Tomar captura de pantalla
                page.screenshot(path="creator_page.png")
                print("Captura de pantalla de la página del creador guardada como 'creator_page.png'")
                
                # Buscar nombre/etiqueta del creador
                labels = page.locator("text=/Label|Name|Tag/i").all()
                for label in labels:
                    try:
                        parent = label.evaluate("el => el.closest('tr') || el.closest('div')")
                        parent_text = page.evaluate("el => el.innerText", parent)
                        print(f"  Información de etiqueta: {parent_text.strip()}")
                    except:
                        pass
                
                # Buscar tokens creados
                tokens_created = page.locator("text=/Tokens created|Created tokens/i").all()
                if tokens_created:
                    print("  Se encontró sección de tokens creados")
            
            # Esperar para que el usuario pueda ver la información
            print("\nManteniendo el navegador abierto por 15 segundos...")
            time.sleep(15)
            
            browser.close()
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    # Hash de la transacción proporcionada
    tx_hash = "3vMCruyZRPnxSJ5UYDs5dGtbuZXmjTER91MjF6Lyxp8fwTww1Ko2waMq1Dzo33Ys68iNCMaVRU4zkhYfnXq3nb1N"
    analyze_solscan_tx(tx_hash) 