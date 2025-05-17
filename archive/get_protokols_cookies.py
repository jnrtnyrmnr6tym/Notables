#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar sesión manualmente en Protokols y guardar las cookies.
"""

from playwright.sync_api import sync_playwright
import json
import os

def main():
    print("\n" + "="*80)
    print("PROTOKOLS MANUAL LOGIN")
    print("="*80)
    print("\n1. Se abrirá un navegador")
    print("2. Inicia sesión manualmente en Protokols")
    print("3. Una vez que hayas iniciado sesión, vuelve aquí y presiona Enter")
    print("4. Las cookies se guardarán automáticamente")
    print("\nPresiona Enter para continuar...")
    input()

    with sync_playwright() as p:
        # Iniciar navegador
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Ir a la página de login
        page.goto("https://www.protokols.io/login")
        
        print("\nNavegador abierto. Por favor:")
        print("1. Inicia sesión en Protokols")
        print("2. Navega un poco para asegurarte de que la sesión está activa")
        print("3. Vuelve aquí y presiona Enter para guardar las cookies")
        
        input("\nPresiona Enter cuando hayas iniciado sesión...")
        
        # Guardar cookies
        cookies = context.cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        
        with open("protokols_cookies.json", "w") as f:
            json.dump(cookies_dict, f, indent=2)
        
        print(f"\nCookies guardadas en protokols_cookies.json")
        print(f"Se encontraron {len(cookies_dict)} cookies")
        
        # Cerrar navegador
        browser.close()

if __name__ == "__main__":
    main() 