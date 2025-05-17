#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar sesión manualmente en Protokols y extraer las cookies.

Este script:
1. Abre un navegador con Playwright
2. Navega a la página de inicio de sesión de Protokols
3. Permite al usuario iniciar sesión manualmente
4. Extrae las cookies de sesión automáticamente
5. Guarda las cookies en un archivo JSON para su uso posterior
"""

import asyncio
import json
from playwright.async_api import async_playwright
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("ProtokolsBrowserLogin")

COOKIES_FILE = "protokols_cookies.json"
LOGIN_URL = 'https://www.protokols.io/sign-in'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        print("Abriendo navegador. Inicia sesión manualmente en Protokols...")
        await page.goto(LOGIN_URL)
        input("Presiona ENTER aquí cuando hayas terminado de iniciar sesión en el navegador...")
        cookies = await page.context.cookies()
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main()) 