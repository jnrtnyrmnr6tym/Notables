"""
Sistema de Monitoreo de Tokens con Verificación de Mutuals de Twitter

Este módulo integra:
1. Monitor de tokens de Solana para detectar nuevos tokens
2. Extractor de metadatos IPFS para obtener información de Twitter
3. Verificador de mutuals de Twitter para filtrar tokens relevantes
4. Exportador para enviar tokens aprobados al Maestro Bot

Flujo de trabajo:
1. Monitorear continuamente nuevos tokens en Solana
2. Extraer información de Twitter desde los metadatos IPFS
3. Verificar si el creador del token tiene suficientes mutuals con el usuario
4. Si cumple los criterios, exportar la dirección del token al Maestro Bot
"""

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime

# Importar nuestros componentes
from solana_token_monitor import SolanaTokenMonitor
from ipfs_metadata_extractor import IPFSMetadataExtractor
from twitter_mutual_checker import TwitterMutualChecker

class TokenMonitorWithTwitter:
    def __init__(self, 
                 creator_address,
                 user_twitter_handle,
                 min_mutuals=5,
                 data_dir="data",
                 check_interval=60,
                 use_twitter_api=False,
                 twitter_api_credentials=None,
                 test_mode=False):
        """
        Inicializa el sistema de monitoreo con verificación de Twitter.
        
        Args:
            creator_address (str): Dirección de Solana a monitorear
            user_twitter_handle (str): Nombre de usuario de Twitter del usuario
            min_mutuals (int): Número mínimo de mutuals requeridos
            data_dir (str): Directorio para almacenar datos
            check_interval (int): Intervalo en segundos entre verificaciones
            use_twitter_api (bool): Si True, usa la API oficial de Twitter
            twitter_api_credentials (dict): Credenciales para la API de Twitter
            test_mode (bool): Si True, usa datos de prueba
        """
        self.creator_address = creator_address
        self.user_twitter_handle = user_twitter_handle.lower().strip('@')
        self.min_mutuals = min_mutuals
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.check_interval = check_interval
        self.test_mode = test_mode
        
        # Archivo para el registro de actividad
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.data_dir / f"integrated_monitor_log_{timestamp}.txt"
        
        # Archivo para almacenar tokens aprobados
        self.approved_tokens_file = self.data_dir / "approved_tokens.json"
        self.approved_tokens = self._load_approved_tokens()
        
        # Archivo para almacenar tokens rechazados
        self.rejected_tokens_file = self.data_dir / "rejected_tokens.json"
        self.rejected_tokens = self._load_rejected_tokens()
        
        # Inicializar componentes
        self._log("Inicializando componentes...")
        
        # Monitor de tokens de Solana
        self.token_monitor = SolanaTokenMonitor(
            creator_address=creator_address,
            data_dir=str(self.data_dir / "solana_data"),
            check_interval=check_interval,
            test_mode=test_mode
        )
        
        # Verificador de mutuals de Twitter
        self.twitter_checker = TwitterMutualChecker(
            cache_dir=str(self.data_dir / "twitter_cache"),
            use_api=use_twitter_api,
            api_credentials=twitter_api_credentials
        )
        
        # Para controlar el hilo de monitoreo
        self.running = False
        self.monitor_thread = None
        
        self._log(f"Sistema inicializado para monitorear tokens de {creator_address}")
        self._log(f"Verificando mutuals con @{user_twitter_handle} (mínimo: {min_mutuals})")
    
    def _load_approved_tokens(self):
        """Carga la lista de tokens aprobados desde un archivo JSON."""
        if self.approved_tokens_file.exists():
            try:
                with open(self.approved_tokens_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"Error al cargar tokens aprobados: {str(e)}")
        return []
    
    def _save_approved_tokens(self):
        """Guarda la lista de tokens aprobados en un archivo JSON."""
        try:
            with open(self.approved_tokens_file, 'w') as f:
                json.dump(self.approved_tokens, f, indent=2)
        except Exception as e:
            self._log(f"Error al guardar tokens aprobados: {str(e)}")
    
    def _load_rejected_tokens(self):
        """Carga la lista de tokens rechazados desde un archivo JSON."""
        if self.rejected_tokens_file.exists():
            try:
                with open(self.rejected_tokens_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"Error al cargar tokens rechazados: {str(e)}")
        return []
    
    def _save_rejected_tokens(self):
        """Guarda la lista de tokens rechazados en un archivo JSON."""
        try:
            with open(self.rejected_tokens_file, 'w') as f:
                json.dump(self.rejected_tokens, f, indent=2)
        except Exception as e:
            self._log(f"Error al guardar tokens rechazados: {str(e)}")
    
    def _log(self, message):
        """Registra un mensaje en el archivo de log y en la consola."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Error al escribir en el log: {str(e)}")
    
    def process_token(self, token_result):
        """
        Procesa un token para verificar si cumple los criterios.
        
        Args:
            token_result (dict): Resultado del procesamiento del token
            
        Returns:
            bool: True si el token fue aprobado, False en caso contrario
        """
        token_address = token_result.get("token_address")
        if not token_address:
            self._log("Error: Token sin dirección")
            return False
            
        # Verificar si ya fue procesado
        if token_address in self.approved_tokens:
            self._log(f"Token {token_address} ya fue aprobado anteriormente")
            return True
            
        if token_address in self.rejected_tokens:
            self._log(f"Token {token_address} ya fue rechazado anteriormente")
            return False
            
        # Extraer información de Twitter
        twitter_info = token_result.get("twitter_info", {})
        twitter_usernames = twitter_info.get("usernames", [])
        
        if not twitter_usernames:
            self._log(f"Token {token_address} no tiene información de Twitter")
            self.rejected_tokens.append(token_address)
            self._save_rejected_tokens()
            return False
            
        # Verificar mutuals con el primer username encontrado
        creator_twitter = twitter_usernames[0]
        self._log(f"Verificando mutuals entre @{self.user_twitter_handle} y @{creator_twitter}...")
        
        has_enough_mutuals, common_mutuals = self.twitter_checker.check_common_mutuals(
            self.user_twitter_handle, 
            creator_twitter, 
            self.min_mutuals
        )
        
        if has_enough_mutuals:
            self._log(f"¡Token {token_address} aprobado! Creador: @{creator_twitter}")
            self._log(f"Mutuals comunes ({len(common_mutuals)}): {', '.join(common_mutuals[:5])}...")
            
            # Guardar token aprobado
            token_data = {
                "address": token_address,
                "creator_twitter": creator_twitter,
                "common_mutuals": common_mutuals,
                "approval_time": datetime.now().isoformat()
            }
            self.approved_tokens.append(token_data)
            self._save_approved_tokens()
            
            # Exportar al Maestro Bot
            self.export_to_master_bot(token_data)
            
            return True
        else:
            self._log(f"Token {token_address} rechazado. No hay suficientes mutuals con @{creator_twitter}")
            self.rejected_tokens.append(token_address)
            self._save_rejected_tokens()
            return False
    
    def export_to_master_bot(self, token_data):
        """
        Exporta un token aprobado al Maestro Bot.
        
        Args:
            token_data (dict): Datos del token aprobado
        """
        self._log(f"Exportando token {token_data['address']} al Maestro Bot...")
        
        # Aquí implementaríamos la lógica para enviar los datos al Maestro Bot
        # Por ejemplo, mediante una API, archivo compartido, etc.
        
        # En esta implementación de ejemplo, simplemente guardamos en un archivo
        export_file = self.data_dir / "master_bot_export.json"
        
        try:
            # Cargar datos existentes o crear lista vacía
            if export_file.exists():
                with open(export_file, 'r') as f:
                    export_data = json.load(f)
            else:
                export_data = []
                
            # Añadir nuevo token
            export_data.append({
                "token_address": token_data["address"],
                "creator_twitter": token_data["creator_twitter"],
                "export_time": datetime.now().isoformat()
            })
            
            # Guardar archivo actualizado
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            self._log(f"Token {token_data['address']} exportado exitosamente")
            
        except Exception as e:
            self._log(f"Error al exportar token al Maestro Bot: {str(e)}")
    
    def process_new_tokens(self):
        """Procesa nuevos tokens y verifica si cumplen los criterios."""
        self._log("Buscando nuevos tokens...")
        
        # Utilizar el monitor de tokens para obtener nuevos tokens
        token_results = self.token_monitor.process_new_tokens()
        
        if not token_results:
            self._log("No se encontraron nuevos tokens")
            return
            
        self._log(f"Procesando {len(token_results)} nuevos tokens...")
        
        # Procesar cada token
        approved_count = 0
        for token_result in token_results:
            if self.process_token(token_result):
                approved_count += 1
                
        self._log(f"Procesamiento completado. Tokens aprobados: {approved_count}/{len(token_results)}")
    
    def _monitor_loop(self):
        """Bucle principal de monitoreo que se ejecuta en un hilo separado."""
        self._log(f"Iniciando monitoreo integrado")
        self._log(f"Intervalo de verificación: {self.check_interval} segundos")
        
        while self.running:
            try:
                self.process_new_tokens()
            except Exception as e:
                self._log(f"Error durante el monitoreo: {str(e)}")
            
            # Esperar hasta la próxima verificación
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def start_monitoring(self):
        """Inicia el monitoreo en un hilo separado."""
        if self.running:
            self._log("El monitoreo ya está en ejecución")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self._log("Monitoreo integrado iniciado exitosamente")
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        if not self.running:
            self._log("El monitoreo no está en ejecución")
            return
        
        self._log("Deteniendo monitoreo...")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
        self._log("Monitoreo detenido")
    
    def reset_approved_tokens(self):
        """Reinicia la lista de tokens aprobados."""
        self._log("Reiniciando lista de tokens aprobados")
        self.approved_tokens = []
        self._save_approved_tokens()
    
    def reset_rejected_tokens(self):
        """Reinicia la lista de tokens rechazados."""
        self._log("Reiniciando lista de tokens rechazados")
        self.rejected_tokens = []
        self._save_rejected_tokens()


# Ejemplo de uso
if __name__ == "__main__":
    # Dirección de Solana a monitorear
    CREATOR_ADDRESS = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    
    # Nombre de usuario de Twitter del usuario
    USER_TWITTER_HANDLE = "tu_usuario_de_twitter"
    
    # Número mínimo de mutuals requeridos
    MIN_MUTUALS = 5
    
    # Crear monitor integrado (modo de prueba activado por defecto)
    monitor = TokenMonitorWithTwitter(
        creator_address=CREATOR_ADDRESS,
        user_twitter_handle=USER_TWITTER_HANDLE,
        min_mutuals=MIN_MUTUALS,
        check_interval=60,
        test_mode=True
    )
    
    # Para usar la API oficial de Twitter, descomentar y proporcionar credenciales
    """
    twitter_api_credentials = {
        'consumer_key': 'TU_CONSUMER_KEY',
        'consumer_secret': 'TU_CONSUMER_SECRET',
        'access_token': 'TU_ACCESS_TOKEN',
        'access_token_secret': 'TU_ACCESS_TOKEN_SECRET'
    }
    
    monitor = TokenMonitorWithTwitter(
        creator_address=CREATOR_ADDRESS,
        user_twitter_handle=USER_TWITTER_HANDLE,
        min_mutuals=MIN_MUTUALS,
        check_interval=60,
        use_twitter_api=True,
        twitter_api_credentials=twitter_api_credentials,
        test_mode=True
    )
    """
    
    try:
        # Iniciar monitoreo
        monitor.start_monitoring()
        
        # Mantener el programa en ejecución
        print("\nMonitor integrado en ejecución. Presiona Ctrl+C para detener...\n")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Detener el monitoreo cuando se presiona Ctrl+C
        monitor.stop_monitoring()
        print("\nMonitor integrado detenido por el usuario") 