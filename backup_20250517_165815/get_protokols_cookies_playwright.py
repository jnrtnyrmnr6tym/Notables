import json
from playwright.sync_api import sync_playwright

COOKIES_FILE = "protokols_cookies.json"
LOGIN_URL = "https://www.protokols.io/sign-in"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)
        print("Por favor, inicia sesión manualmente en Protokols en la ventana abierta.")
        input("Cuando hayas terminado el login y veas tu perfil, pulsa ENTER aquí para guardar las cookies...")

        # Guarda las cookies en una lista de objetos
        cookies = context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2)
        print(f"Cookies guardadas en {COOKIES_FILE} (formato lista de objetos)")
        browser.close()

if __name__ == "__main__":
    main() 