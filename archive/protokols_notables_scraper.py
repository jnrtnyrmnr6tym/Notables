#!/usr/bin/env python3
"""
Script para abrir el perfil de Vitalik en Protokols, permitir login manual y hacer scroll infinito en la lista de notables.
Guarda el HTML final y las peticiones de red para análisis posterior.
"""

import time
from playwright.sync_api import sync_playwright

PROFILE_URL = "https://www.protokols.io/sign-in"  # Ahora apunta a la página de login
SCROLL_PAUSE = 2  # segundos entre scrolls
MAX_SCROLLS = 30  # número máximo de scrolls (ajustable)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        network_requests = []

        def log_request(request):
            try:
                network_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "post_data": request.post_data,
                    "headers": dict(request.headers),
                })
            except Exception:
                pass

        page.on("request", log_request)

        print(f"[INFO] Abriendo {PROFILE_URL}")
        page.goto(PROFILE_URL)
        print("[INFO] Por favor, inicia sesión manualmente en Protokols, navega al perfil que desees y haz scroll en la lista de notables.")
        input("Presiona Enter cuando hayas terminado de navegar y hacer scroll en la lista de notables...")

        print("[INFO] Haciendo scroll infinito para cargar todos los notables...")
        last_height = page.evaluate("document.body.scrollHeight")
        for i in range(MAX_SCROLLS):
            page.mouse.wheel(0, 10000)
            time.sleep(SCROLL_PAUSE)
            new_height = page.evaluate("document.body.scrollHeight")
            print(f"[DEBUG] Scroll {i+1}/{MAX_SCROLLS} - Altura: {new_height}")
            if new_height == last_height:
                print("[INFO] No se detecta más contenido, scroll detenido.")
                break
            last_height = new_height

        # Guardar HTML final
        html = page.content()
        with open("notables_vitalik.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[INFO] HTML guardado en notables_vitalik.html")

        # Guardar todas las peticiones de red
        import json
        with open("notables_requests_log.json", "w", encoding="utf-8") as f:
            json.dump(network_requests, f, indent=2)
        print("[INFO] Peticiones de red guardadas en notables_requests_log.json")

        # Guardar cookies en formato lista (Playwright style)
        cookies = context.cookies()
        with open("protokols_cookies_scraper.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        print("[INFO] Cookies guardadas en protokols_cookies_scraper.json (formato lista)")

        browser.close()

if __name__ == "__main__":
    main() 