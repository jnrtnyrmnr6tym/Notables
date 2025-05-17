"""
Script simple para abrir un navegador en la dirección de Solana especificada.
Este script solo abre el navegador y no realiza ninguna automatización adicional.
"""

import os
import webbrowser
import time

def open_solana_address(address):
    print(f"Abriendo navegador para explorar la dirección: {address}")
    
    # URL de Solscan para la dirección
    url = f"https://solscan.io/account/{address}"
    
    # Abrir la URL en el navegador predeterminado
    print(f"Abriendo: {url}")
    webbrowser.open(url)
    
    print("\n" + "="*80)
    print("INSTRUCCIONES:")
    print("1. Ahora deberías ver tu navegador predeterminado abierto con la página de Solscan")
    print("2. Resuelve manualmente el captcha de Cloudflare si aparece")
    print("3. Explora la información de la dirección")
    print("4. Puedes buscar información de Twitter y otros detalles del creador del token")
    print("="*80)
    
    print("\nPara explorar una transacción específica, puedes abrir:")
    print("https://solscan.io/tx/3vMCruyZRPnxSJ5UYDs5dGtbuZXmjTER91MjF6Lyxp8fwTww1Ko2waMq1Dzo33Ys68iNCMaVRU4zkhYfnXq3nb1N")
    
    # Crear un directorio para capturas de pantalla manuales
    screenshot_dir = "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print("\nPuedes guardar capturas de pantalla manualmente en la carpeta:")
    print(os.path.abspath(screenshot_dir))
    
    # Esperar para que el usuario pueda leer las instrucciones
    try:
        input("\nPresiona Enter cuando hayas terminado de explorar...")
    except KeyboardInterrupt:
        pass
    
    print("Script finalizado. Puedes cerrar el navegador manualmente.")

if __name__ == "__main__":
    # Dirección de Solana proporcionada
    address = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    open_solana_address(address) 