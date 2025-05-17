#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Guía para obtener cookies de Protokols manualmente desde el navegador.

Este script muestra instrucciones paso a paso para:
1. Iniciar sesión en Protokols
2. Extraer las cookies necesarias desde las herramientas de desarrollo del navegador
3. Guardarlas en el archivo de configuración
"""

import json
import os
import webbrowser
import time

# Constantes
COOKIES_FILE = "protokols_cookies.json"
PROTOKOLS_URL = "https://protokols.io/login"

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def print_step(step_num, title, description):
    """Imprime un paso formateado."""
    print(f"\n[Paso {step_num}] {title}")
    print("-" * 60)
    for line in description.split("\n"):
        print(f"  {line}")

def save_cookies_to_file(cookies):
    """Guarda las cookies en un archivo JSON."""
    try:
        with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        print(f"\n✅ Cookies guardadas correctamente en {COOKIES_FILE}")
        return True
    except Exception as e:
        print(f"\n❌ Error al guardar cookies: {e}")
        return False

def main():
    print_header("GUÍA PARA OBTENER COOKIES DE PROTOKOLS")
    
    print("""
Esta guía te ayudará a obtener las cookies necesarias para autenticar
las solicitudes a la API de Protokols y actualizar el archivo de configuración.
    """)
    
    # Paso 1: Abrir Protokols en el navegador
    print_step(1, "Abrir Protokols en el navegador", """
Abriendo Protokols en tu navegador predeterminado...
Si no se abre automáticamente, visita: https://protokols.io/login
    """)
    
    try:
        webbrowser.open(PROTOKOLS_URL)
        print("\n✅ Navegador abierto con la página de inicio de sesión de Protokols")
    except Exception as e:
        print(f"\n❌ Error al abrir el navegador: {e}")
        print("Por favor, abre manualmente la página: https://protokols.io/login")
    
    # Paso 2: Iniciar sesión
    print_step(2, "Iniciar sesión en Protokols", """
1. Inicia sesión con tus credenciales de Protokols
2. Asegúrate de marcar "Recordarme" si está disponible
3. Una vez iniciada la sesión, continúa con el siguiente paso
    """)
    
    input("\nPresiona Enter cuando hayas iniciado sesión... ")
    
    # Paso 3: Abrir herramientas de desarrollo
    print_step(3, "Abrir las herramientas de desarrollo del navegador", """
1. Presiona F12 o haz clic derecho en la página y selecciona "Inspeccionar"
2. Ve a la pestaña "Application" (Chrome/Edge) o "Storage" (Firefox)
3. En el panel izquierdo, expande "Cookies" y selecciona "https://protokols.io"
    """)
    
    input("\nPresiona Enter cuando tengas las herramientas de desarrollo abiertas... ")
    
    # Paso 4: Extraer cookies
    print_step(4, "Extraer las cookies necesarias", """
Busca las siguientes cookies (o similares) en la lista:
1. sb-pgddobbqjoggmuwvhfaj-auth-token
2. __cf_bm
3. ph_phc_*

Para cada cookie, copia el nombre y valor exactos.
    """)
    
    # Paso 5: Ingresar cookies
    print_step(5, "Ingresar las cookies manualmente", """
Ahora ingresarás las cookies una por una.
Para cada cookie, ingresa el nombre y valor separados por '='.
Por ejemplo: sb-pgddobbqjoggmuwvhfaj-auth-token=valor_largo_de_la_cookie
    
Deja una línea en blanco cuando hayas terminado.
    """)
    
    cookies = {}
    print("\nIngresa las cookies a continuación:")
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            parts = line.split('=', 1)
            if len(parts) != 2:
                print(f"Formato incorrecto: '{line}'. Use 'nombre=valor'.")
                continue
            
            name, value = parts
            cookies[name.strip()] = value.strip()
            print(f"Cookie '{name}' añadida.")
        except Exception as e:
            print(f"Error al procesar la entrada: {e}")
    
    # Paso 6: Guardar cookies
    print_step(6, "Guardar las cookies", f"""
Guardando las cookies en el archivo {COOKIES_FILE}...
    """)
    
    if not cookies:
        print("\n❌ No se ingresaron cookies. No se realizará ninguna actualización.")
        return
    
    save_cookies_to_file(cookies)
    
    print_header("PROCESO COMPLETADO")
    print(f"""
Has actualizado correctamente las cookies de Protokols.
Ahora el sistema de verificación de notable followers debería funcionar correctamente.

Cookies guardadas: {len(cookies)}
Archivo de cookies: {os.path.abspath(COOKIES_FILE)}

Puedes probar el sistema ejecutando:
python token_monitor_with_notable_check.py --test
    """)

if __name__ == "__main__":
    main() 