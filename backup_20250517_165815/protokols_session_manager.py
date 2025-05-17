#!/usr/bin/env python3
"""
Gestor centralizado de sesión para Protokols.
Este script maneja la autenticación, renovación y verificación de cookies de Protokols.
"""

import json
import time
import logging
import requests
from pathlib import Path
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('protokols_session.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProtokolsSessionManager:
    def __init__(self, cookies_file: str = "protokols_cookies.json"):
        """
        Inicializa el gestor de sesión de Protokols.
        
        Args:
            cookies_file: Ruta al archivo donde se guardarán las cookies
        """
        self.cookies_file = cookies_file
        self.cookies: List[Dict] = []
        self.last_verification = 0
        self.verification_interval = 300  # 5 minutos
        
    def load_cookies(self) -> bool:
        """
        Carga las cookies desde el archivo.
        
        Returns:
            bool: True si las cookies se cargaron correctamente
        """
        try:
            with open(self.cookies_file, 'r') as f:
                self.cookies = json.load(f)
                
            if not self._validate_cookies():
                logger.error("Cookies inválidas encontradas en el archivo")
                return False
                
            logger.info(f"Cookies cargadas correctamente desde {self.cookies_file}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Archivo de cookies no encontrado: {self.cookies_file}")
            return False
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar el archivo de cookies: {self.cookies_file}")
            return False
        except Exception as e:
            logger.error(f"Error al cargar cookies: {str(e)}")
            return False
            
    def _validate_cookies(self) -> bool:
        """
        Valida que las cookies tengan el formato correcto.
        
        Returns:
            bool: True si las cookies son válidas
        """
        if not isinstance(self.cookies, list):
            return False
            
        required_fields = ['name', 'value', 'domain']
        for cookie in self.cookies:
            if not all(field in cookie for field in required_fields):
                return False
                
        return True
        
    def get_fresh_cookies(self) -> List[Dict]:
        """
        Obtiene cookies frescas, renovándolas si es necesario.
        
        Returns:
            List[Dict]: Lista de cookies válidas
        """
        current_time = time.time()
        
        # Verificar si necesitamos renovar las cookies
        if current_time - self.last_verification > self.verification_interval:
            if not self.verify_cookies():
                logger.info("Renovando cookies...")
                self.renew_cookies()
                
        return self.cookies
        
    def verify_cookies(self) -> bool:
        """
        Verifica si las cookies actuales son válidas.
        
        Returns:
            bool: True si las cookies son válidas
        """
        if not self.cookies:
            return False
            
        try:
            # Intentar una solicitud simple a la API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Origin': 'https://www.protokols.io',
                'Referer': 'https://www.protokols.io'
            }
            
            response = requests.get(
                "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial",
                headers=headers,
                cookies=self.cookies
            )
            
            self.last_verification = time.time()
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error al verificar cookies: {str(e)}")
            return False
            
    def renew_cookies(self) -> bool:
        """
        Renueva las cookies usando Playwright.
        
        Returns:
            bool: True si las cookies se renovaron correctamente
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                
                # Ir a la página de login
                page.goto("https://www.protokols.io/sign-in")
                logger.info("Por favor, inicia sesión manualmente en la ventana del navegador...")
                input("Presiona ENTER cuando hayas iniciado sesión y veas tu perfil...")
                
                # Obtener las cookies
                self.cookies = context.cookies()
                
                # Guardar las cookies
                with open(self.cookies_file, 'w') as f:
                    json.dump(self.cookies, f, indent=2)
                    
                browser.close()
                logger.info("Cookies renovadas y guardadas correctamente")
                return True
                
        except Exception as e:
            logger.error(f"Error al renovar cookies: {str(e)}")
            return False
            
    def get_session_headers(self) -> Dict[str, str]:
        """
        Obtiene los headers necesarios para las solicitudes a la API.
        
        Returns:
            Dict[str, str]: Headers para las solicitudes
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.protokols.io',
            'Referer': 'https://www.protokols.io'
        }

    def get_cookies_dict(self) -> dict:
        """
        Devuelve las cookies en formato dict {name: value} para requests.
        """
        if not self.cookies or not isinstance(self.cookies, list):
            return {}
        return {cookie['name']: cookie['value'] for cookie in self.cookies if 'name' in cookie and 'value' in cookie}

def main():
    """Función principal para pruebas."""
    manager = ProtokolsSessionManager()
    
    if not manager.load_cookies():
        print("No se pudieron cargar las cookies existentes.")
        if manager.renew_cookies():
            print("Cookies renovadas correctamente.")
        else:
            print("Error al renovar las cookies.")
        return
        
    if manager.verify_cookies():
        print("Las cookies actuales son válidas.")
    else:
        print("Las cookies han caducado.")
        if manager.renew_cookies():
            print("Cookies renovadas correctamente.")
        else:
            print("Error al renovar las cookies.")

if __name__ == "__main__":
    main() 