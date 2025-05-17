"""
Script para extraer datos de tokens de Axiom mediante inicio de sesión manual.
"""

import json
import time
import os
import datetime
from playwright.sync_api import sync_playwright

def extract_axiom_tokens():
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
            
            # Tomar captura de pantalla para verificación
            screenshot_path = f"{screenshot_dir}/{timestamp}_tokens_page.png"
            page.screenshot(path=screenshot_path)
            print(f"Captura de pantalla guardada: {screenshot_path}")
            
            # Intentar extraer datos de tokens
            print("\nBuscando datos de tokens...")
            
            # Verificar URL actual
            current_url = page.url
            print(f"URL actual: {current_url}")
            
            # Buscar tablas en la página
            tables = page.locator("table").count()
            print(f"Tablas encontradas: {tables}")
            
            if tables > 0:
                # Extraer datos de la primera tabla
                table = page.locator("table").first
                
                # Extraer filas
                rows = table.locator("tr").count()
                print(f"La tabla contiene {rows} filas")
                
                # Extraer datos
                tokens_data = []
                
                # Intentar extraer encabezados
                headers = []
                try:
                    header_row = table.locator("tr").first
                    header_cells = header_row.locator("th")
                    for i in range(header_cells.count()):
                        headers.append(header_cells.nth(i).inner_text().strip())
                    print(f"Encabezados detectados: {headers}")
                except Exception as e:
                    print(f"No se pudieron extraer encabezados: {str(e)}")
                    headers = ["column_0", "column_1", "column_2", "column_3", "column_4", "column_5"]
                
                # Extraer datos de cada fila
                for i in range(1, min(rows, 20)):  # Procesar hasta 20 filas (excluyendo el encabezado)
                    try:
                        row = table.locator("tr").nth(i)
                        cells = row.locator("td")
                        cells_count = cells.count()
                        
                        if cells_count > 0:
                            token_data = {}
                            
                            # Extraer datos de cada celda
                            for j in range(cells_count):
                                cell_text = cells.nth(j).inner_text().strip()
                                if j < len(headers):
                                    column_name = headers[j]
                                else:
                                    column_name = f"column_{j}"
                                token_data[column_name] = cell_text
                            
                            tokens_data.append(token_data)
                            print(f"Token extraído {i}: {token_data}")
                    except Exception as e:
                        print(f"Error al procesar fila {i}: {str(e)}")
                
                # Guardar datos extraídos
                if tokens_data:
                    data_file = f"{data_dir}/tokens_{timestamp}.json"
                    with open(data_file, "w") as f:
                        json.dump(tokens_data, f, indent=2)
                    print(f"\n✅ ÉXITO: {len(tokens_data)} tokens guardados en '{data_file}'")
                else:
                    print("\n❌ ERROR: No se pudieron extraer datos de tokens")
            else:
                print("\n❌ ERROR: No se encontraron tablas en la página")
            
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
    print("EXTRACTOR DE TOKENS DE AXIOM")
    print("="*80)
    extract_axiom_tokens() 