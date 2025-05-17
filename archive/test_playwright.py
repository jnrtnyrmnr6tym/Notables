"""
Script simple para probar si Playwright está funcionando correctamente.
"""

from playwright.sync_api import sync_playwright

def test_playwright():
    print("Iniciando test de Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        print("Navegando a ejemplo.com...")
        page.goto("https://ejemplo.com")
        print("Título de la página:", page.title())
        browser.close()
    print("Test completado con éxito!")

if __name__ == "__main__":
    test_playwright() 