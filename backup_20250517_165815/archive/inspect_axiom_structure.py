"""
Script para inspeccionar la estructura de Axiom y encontrar elementos con datos de tokens.
"""

import json
import time
import os
import datetime
from playwright.sync_api import sync_playwright

def inspect_axiom_structure():
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
            print("3. Una vez que puedas ver los datos de tokens, presiona Enter")
            print("="*80)
            
            input("\nPresiona Enter cuando hayas completado el login y puedas ver los tokens... ")
            
            # Obtener URL actual
            current_url = page.url
            print(f"URL actual: {current_url}")
            
            # Tomar captura de pantalla para verificación
            screenshot_path = f"{screenshot_dir}/{timestamp}_page_structure.png"
            page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada: {screenshot_path}")
            
            # Inspeccionar estructura de la página
            print("\nInspeccionando estructura de la página...")
            
            # Buscar elementos comunes que podrían contener datos
            print("\n1. Buscando tablas...")
            tables = page.locator("table").count()
            print(f"Tablas encontradas: {tables}")
            
            print("\n2. Buscando elementos div con posibles datos de tokens...")
            # Buscar divs que podrían contener listas de tokens
            token_containers = [
                page.locator("div.token-list").count(),
                page.locator("div.token-container").count(),
                page.locator("div.tokens").count(),
                page.locator("div[data-tokens]").count(),
                page.locator("div.token-item").count(),
                page.locator("div.pulse-token").count(),
                page.locator("div.token-row").count(),
                page.locator("div[role='table']").count(),
                page.locator("div[role='grid']").count(),
                page.locator("div.token-grid").count(),
                page.locator("div.pulse-grid").count()
            ]
            print(f"Posibles contenedores de tokens encontrados: {sum(token_containers)}")
            
            print("\n3. Buscando listas (ul/li)...")
            lists = page.locator("ul").count()
            list_items = page.locator("li").count()
            print(f"Listas (ul): {lists}, Elementos de lista (li): {list_items}")
            
            print("\n4. Buscando elementos con texto que puedan ser tokens...")
            token_keywords = ["token", "price", "volume", "market cap", "24h", "buy", "sell"]
            for keyword in token_keywords:
                count = page.locator(f"text=/{keyword}/i").count()
                print(f"Elementos con texto '{keyword}': {count}")
            
            # Guardar HTML de la página para análisis
            html_content = page.content()
            html_file = f"{data_dir}/axiom_page_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\nHTML de la página guardado en: {html_file}")
            
            # Analizar estructura específica de la página
            print("\nAnalizando elementos visibles con posibles datos...")
            visible_elements = [
                "div.grid", "div.flex", "div.container", 
                ".table", ".grid", ".list",
                "[data-testid]", "[data-token]", "[data-id]"
            ]
            
            for selector in visible_elements:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"Selector '{selector}': {count} elementos")
                        # Extraer texto del primer elemento para mostrar ejemplo
                        try:
                            sample_text = page.locator(selector).first.inner_text()
                            if len(sample_text) > 100:
                                sample_text = sample_text[:100] + "..."
                            print(f"  Muestra: {sample_text}")
                        except:
                            pass
                except:
                    print(f"Error al buscar selector '{selector}'")
            
            # Buscar elementos que puedan contener información de precios
            print("\nBuscando elementos con posible información de precios...")
            price_selectors = [
                "text=/\\$[0-9,.]+/", "text=/\\€[0-9,.]+/", 
                "text=/[0-9,.]+%/", "text=/[0-9,.]+\\s*(USD|EUR|SOL)/",
                ".price", ".value", ".amount", ".percentage"
            ]
            
            for selector in price_selectors:
                try:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"Selector de precio '{selector}': {count} elementos")
                        # Mostrar los primeros 3 valores encontrados
                        for i in range(min(3, count)):
                            try:
                                text = page.locator(selector).nth(i).inner_text().strip()
                                print(f"  Valor {i+1}: {text}")
                            except:
                                pass
                except:
                    pass
            
            # Permitir al usuario explorar la página
            print("\n" + "="*80)
            print("La página está abierta para que puedas explorarla.")
            print("Puedes inspeccionar elementos para encontrar dónde están los datos de tokens.")
            print("Cuando termines, presiona Enter para cerrar el navegador.")
            print("="*80)
            
            input("\nPresiona Enter para cerrar el navegador... ")
            browser.close()
            
    except Exception as e:
        print(f"Error general: {str(e)}")

if __name__ == "__main__":
    print("="*80)
    print("INSPECTOR DE ESTRUCTURA DE AXIOM")
    print("="*80)
    inspect_axiom_structure() 