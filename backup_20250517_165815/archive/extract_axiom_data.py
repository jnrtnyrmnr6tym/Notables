"""
Script para extraer datos de tokens de Axiom basado en la estructura real de la página.
"""

import json
import time
import os
import datetime
import re
from playwright.sync_api import sync_playwright

def extract_axiom_data():
    # Crear directorios para guardar datos
    data_dir = "data"
    screenshot_dir = "screenshots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        with sync_playwright() as p:
            # Lanzar navegador
            print("Iniciando navegador...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            # Navegar a Axiom Pulse
            print("Navegando a Axiom Pulse...")
            page.goto("https://axiom.trade/pulse")
            
            # Instrucciones para el usuario
            print("\n" + "="*80)
            print("INSTRUCCIONES:")
            print("1. Inicia sesión en Axiom manualmente")
            print("2. Navega a la página Pulse si no lo hace automáticamente")
            print("3. Una vez que veas los datos de tokens, presiona Enter")
            print("="*80)
            
            input("\nPresiona Enter cuando hayas completado el login y puedas ver los tokens... ")
            
            # Obtener URL actual
            current_url = page.url
            print(f"URL actual: {current_url}")
            
            # Tomar captura de pantalla
            screenshot_path = f"{screenshot_dir}/{timestamp}_tokens_data.png"
            page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada: {screenshot_path}")
            
            print("\nExtrayendo datos de tokens...")
            
            # Extraer tokens basados en elementos con precios en dólares
            price_elements = page.locator("text=/\\$[0-9,.]+/").all()
            print(f"Encontrados {len(price_elements)} elementos con precios")
            
            # Intentar extraer tokens y sus precios
            tokens_data = []
            
            # Método: Analizar cada elemento con precio y su contexto
            for i, price_element in enumerate(price_elements[:50]):  # Limitar a 50 elementos
                try:
                    # Obtener el texto del elemento con precio
                    price_text = price_element.inner_text()
                    
                    # Intentar conseguir texto del elemento padre para más contexto
                    parent_text = ""
                    try:
                        # Navegar hacia arriba en el DOM para encontrar un elemento con más contexto
                        for level in range(1, 4):  # Probar hasta 3 niveles hacia arriba
                            parent = price_element.evaluate(f"el => {{ let p = el; for(let i=0; i<{level}; i++) {{ if(p.parentElement) p = p.parentElement; }}; return p; }}")
                            parent_text = page.evaluate("el => el.innerText", parent)
                            
                            # Si encontramos texto suficiente, detenemos la búsqueda
                            if len(parent_text) > 10 and len(parent_text) < 200:
                                break
                    except:
                        pass
                    
                    # Si no tenemos texto del padre, usar el texto del elemento de precio
                    if not parent_text:
                        parent_text = price_text
                    
                    # Limpiar el texto
                    parent_text = parent_text.strip()
                    
                    # Extraer precio con regex (del elemento de precio directamente)
                    price = price_text.strip()
                    
                    # Extraer porcentaje si existe
                    percentage_match = re.search(r'[+-]?\d+(\.\d+)?%', parent_text)
                    percentage = percentage_match.group(0) if percentage_match else "N/A"
                    
                    # Buscar un posible símbolo de token en el texto
                    token_name = "Desconocido"
                    
                    # Intentar diferentes patrones para encontrar el nombre del token
                    # 1. Patrón común: 3-5 letras mayúsculas (SOL, BTC, ETH, etc.)
                    token_match = re.search(r'\b[A-Z0-9]{2,6}\b', parent_text)
                    if token_match:
                        token_name = token_match.group(0)
                    else:
                        # 2. Intentar buscar palabras que pueden ser nombres de token
                        words = [w for w in re.findall(r'\b[A-Za-z0-9]+\b', parent_text) if len(w) > 1]
                        if words:
                            token_name = words[0]  # Tomar la primera palabra como posible token
                    
                    # Crear registro de token
                    token_data = {
                        "token": token_name,
                        "price": price,
                        "change": percentage,
                        "raw_text": parent_text[:100] if len(parent_text) > 100 else parent_text
                    }
                    
                    # Solo agregar si tiene datos significativos y no parece ser una fila duplicada
                    if token_name != "Desconocido" and not any(t["token"] == token_name for t in tokens_data):
                        tokens_data.append(token_data)
                        print(f"Token extraído {i+1}: {token_data}")
                except Exception as e:
                    print(f"Error al procesar elemento {i+1}: {str(e)}")
            
            # Guardar datos extraídos
            if tokens_data:
                data_file = f"{data_dir}/tokens_data_{timestamp}.json"
                with open(data_file, "w") as f:
                    json.dump(tokens_data, f, indent=2)
                print(f"\n✅ ÉXITO: {len(tokens_data)} tokens guardados en '{data_file}'")
            else:
                print("\n❌ ERROR: No se pudieron extraer datos de tokens")
                
                # En caso de error, guardar captura de la estructura para análisis
                full_html = page.content()
                with open(f"{data_dir}/full_page_{timestamp}.html", "w", encoding="utf-8") as f:
                    f.write(full_html)
                print(f"HTML completo guardado en: {data_dir}/full_page_{timestamp}.html")
            
            # Opción para mantener el navegador abierto
            keep_open = input("\n¿Quieres mantener el navegador abierto? (s/n): ")
            if keep_open.lower() == 's' or keep_open.lower() == 'si':
                print("\nManteniendo el navegador abierto. Presiona Enter para cerrarlo cuando termines...")
                input()
            
            browser.close()
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    print("="*80)
    print("EXTRACTOR DE DATOS DE TOKENS DE AXIOM")
    print("="*80)
    extract_axiom_data() 