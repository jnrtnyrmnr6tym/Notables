"""
Monitor de tokens de Solana para detectar nuevos tokens creados por una cuenta específica.

Este módulo:
1. Se conecta a la red Solana mediante RPC y servicios de Solscan
2. Monitorea nuevos tokens creados por una dirección específica
3. Extrae información básica sobre los tokens
4. Integra con el extractor de metadatos IPFS
"""

import time
import json
import hashlib
import threading
import requests
from pathlib import Path
from datetime import datetime

# Importamos nuestro extractor de metadatos IPFS
from ipfs_metadata_extractor import IPFSMetadataExtractor

class SolanaTokenMonitor:
    def __init__(self, creator_address, data_dir="data", check_interval=30, test_mode=False):
        """
        Inicializa el monitor de tokens de Solana.
        
        Args:
            creator_address (str): Dirección de Solana a monitorear
            data_dir (str): Directorio para almacenar datos
            check_interval (int): Intervalo en segundos entre verificaciones
            test_mode (bool): Si True, usa tokens de prueba en lugar de consultar la API
        """
        self.creator_address = creator_address
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.check_interval = check_interval
        self.test_mode = test_mode
        
        # Archivo para almacenar tokens procesados
        self.processed_tokens_file = self.data_dir / "processed_tokens.json"
        self.processed_tokens = self._load_processed_tokens()
        
        # Archivo para almacenar transferencias procesadas
        self.processed_transfers_file = self.data_dir / "processed_transfers.json"
        self.processed_transfers = self._load_processed_transfers()
        
        # Archivo para el registro de actividad
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.data_dir / f"monitor_log_{timestamp}.txt"
        
        # Endpoints RPC de Solana (con fallback)
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        
        # Endpoints de Solscan
        self.solscan_base_url = "https://public-api.solscan.io"
        
        # Headers para simular un navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Inicializar el extractor de metadatos IPFS
        self.ipfs_extractor = IPFSMetadataExtractor(cache_dir=str(self.data_dir / "ipfs_cache"))
        
        # Para controlar el hilo de monitoreo
        self.running = False
        self.monitor_thread = None
        
        # Tokens de prueba conocidos (para modo de prueba)
        self.test_tokens = [
            {
                "address": "2YQwCagdDrtxtMVU1mKa51PAyabDbshsMDg74fV4KirB",
                "uri": "https://ipfs.io/ipfs/bafkreifx3xe26o5pdqefmprih2wlflwnv2wh2stqf57kjamgdvf7pqr7k4"
            }
        ]
    
    def _load_processed_tokens(self):
        """Carga la lista de tokens ya procesados desde un archivo JSON."""
        if self.processed_tokens_file.exists():
            try:
                with open(self.processed_tokens_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self._log(f"Error al cargar tokens procesados: {str(e)}")
        return []
    
    def _save_processed_tokens(self):
        """Guarda la lista de tokens procesados en un archivo JSON."""
        try:
            with open(self.processed_tokens_file, 'w') as f:
                json.dump(self.processed_tokens, f, indent=2)
        except Exception as e:
            self._log(f"Error al guardar tokens procesados: {str(e)}")
    
    def _load_processed_transfers(self):
        """Carga el conjunto de transferencias ya procesadas."""
        if self.processed_transfers_file.exists():
            try:
                with open(self.processed_transfers_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                self._log(f"Error al cargar transferencias procesadas: {str(e)}")
        return set()
    
    def _save_processed_transfers(self):
        """Guarda el conjunto de transferencias procesadas."""
        try:
            with open(self.processed_transfers_file, 'w') as f:
                json.dump(list(self.processed_transfers), f)
        except Exception as e:
            self._log(f"Error al guardar transferencias procesadas: {str(e)}")
    
    def _cache_transfer_hash(self, transfer):
        """
        Genera un hash único para una transferencia.
        
        Args:
            transfer (dict): Datos de la transferencia
            
        Returns:
            str: Hash único para la transferencia
        """
        # Crear un hash basado en campos relevantes
        relevant_data = {
            "token_address": transfer.get("token_address", ""),
            "from_address": transfer.get("from_address", ""),
            "to_address": transfer.get("to_address", ""),
            "trans_id": transfer.get("trans_id", ""),
            "block_time": transfer.get("block_time", 0)
        }
        return hashlib.md5(json.dumps(relevant_data, sort_keys=True).encode()).hexdigest()
    
    def _is_transfer_processed(self, transfer):
        """
        Verifica si una transferencia ya ha sido procesada.
        
        Args:
            transfer (dict): Datos de la transferencia
            
        Returns:
            bool: True si ya fue procesada, False en caso contrario
        """
        transfer_hash = self._cache_transfer_hash(transfer)
        return transfer_hash in self.processed_transfers
    
    def _mark_transfer_processed(self, transfer):
        """
        Marca una transferencia como procesada.
        
        Args:
            transfer (dict): Datos de la transferencia
        """
        transfer_hash = self._cache_transfer_hash(transfer)
        self.processed_transfers.add(transfer_hash)
        # Guardar periódicamente la caché de transferencias procesadas
        if len(self.processed_transfers) % 10 == 0:
            self._save_processed_transfers()
    
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
    
    def _make_api_request_with_retry(self, url, params=None, max_retries=3):
        """
        Realiza una solicitud a una API con sistema de reintentos.
        
        Args:
            url (str): URL de la API
            params (dict): Parámetros para la solicitud
            max_retries (int): Número máximo de reintentos
            
        Returns:
            dict: Respuesta de la API o None si hay error
        """
        if params is None:
            params = {}
            
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = min(2 ** attempt, 60)  # Backoff exponencial con máximo de 60 segundos
                    self._log(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    self._log(f"Error en la API: {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Backoff exponencial
                    
            except Exception as e:
                self._log(f"Error en la solicitud: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                    
        return None
    
    def _make_rpc_request(self, method, params=None):
        """
        Realiza una solicitud RPC a la API de Solana con fallback a múltiples endpoints.
        
        Args:
            method (str): Método RPC a llamar
            params (list): Parámetros para el método
            
        Returns:
            dict: Respuesta de la API o None si hay error
        """
        if params is None:
            params = []
            
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        # Intentar con cada endpoint hasta que uno funcione
        for endpoint in self.rpc_endpoints:
            try:
                self._log(f"Conectando con endpoint: {endpoint}")
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        return result["result"]
                    elif "error" in result:
                        self._log(f"Error RPC: {result['error']}")
                
            except Exception as e:
                self._log(f"Error con endpoint {endpoint}: {str(e)}")
                continue
                
        self._log("Todos los endpoints RPC fallaron")
        return None
    
    def get_solscan_transfers(self, limit=50, offset=0):
        """
        Obtiene las transferencias recientes de la cuenta desde Solscan.
        
        Args:
            limit (int): Número máximo de transferencias a obtener
            offset (int): Desplazamiento para paginación
            
        Returns:
            list: Lista de transferencias
        """
        self._log(f"Obteniendo transacciones desde Solscan para {self.creator_address} (offset: {offset}, limit: {limit})...")
        
        # Endpoint para obtener transacciones de la cuenta
        url = f"{self.solscan_base_url}/account/transactions"
        params = {
            "account": self.creator_address,
            "limit": min(limit, 50)  # La API pública tiene un límite máximo de 50
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                transactions = response.json()
                self._log(f"Se encontraron {len(transactions)} transacciones")
                return transactions
            else:
                self._log(f"Error al obtener transacciones: {response.status_code} - {response.text}")
        except Exception as e:
            self._log(f"Error al consultar Solscan: {str(e)}")
        
        return []
    
    def get_all_recent_transfers(self, max_pages=5, limit_per_page=50):
        """
        Obtiene múltiples páginas de transferencias recientes.
        
        Args:
            max_pages (int): Número máximo de páginas a consultar
            limit_per_page (int): Número de transferencias por página
            
        Returns:
            list: Lista combinada de todas las transferencias
        """
        all_transfers = []
        
        for page in range(max_pages):
            offset = page * limit_per_page
            transfers = self.get_solscan_transfers(limit=limit_per_page, offset=offset)
            
            if not transfers:
                break
                
            all_transfers.extend(transfers)
            
            # Si obtenemos menos transferencias que el límite, hemos llegado al final
            if len(transfers) < limit_per_page:
                break
                
            # Pequeña pausa para no sobrecargar la API
            time.sleep(1)
        
        self._log(f"Total de transferencias obtenidas: {len(all_transfers)}")
        return all_transfers
    
    def process_transfers_for_tokens(self, transactions):
        """
        Procesa las transacciones para extraer tokens creados.
        
        Args:
            transactions (list): Lista de transacciones de Solscan
            
        Returns:
            list: Lista de tokens extraídos
        """
        tokens = []
        seen_addresses = set()
        
        for tx in transactions:
            try:
                # Verificar si ya procesamos esta transacción
                tx_hash = tx.get("txHash") or tx.get("tx_hash")
                if not tx_hash or tx_hash in self.processed_transfers:
                    continue
                
                # Marcar como procesada para evitar duplicados en futuras ejecuciones
                self.processed_transfers.add(tx_hash)
                
                # Obtener detalles de la transacción para verificar si es una creación de token
                token_info = self._check_for_token_creation(tx_hash)
                if token_info:
                    token_address = token_info.get("address")
                    if token_address and token_address not in seen_addresses:
                        seen_addresses.add(token_address)
                        tokens.append(token_info)
                        self._log(f"Nuevo token encontrado: {token_address}")
            except Exception as e:
                self._log(f"Error al procesar transacción: {str(e)}")
        
        return tokens
    
    def _check_for_token_creation(self, tx_hash):
        """
        Verifica si una transacción contiene instrucciones de creación de token.
        
        Args:
            tx_hash (str): Hash de la transacción
            
        Returns:
            dict: Información del token o None si no es una creación de token
        """
        self._log(f"Analizando transacción {tx_hash} para buscar creación de token...")
        
        # Endpoint para obtener detalles de la transacción
        url = f"{self.solscan_base_url}/transaction/{tx_hash}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                self._log(f"Error al obtener detalles de transacción: {response.status_code}")
                return None
                
            tx_data = response.json()
            
            # Verificar si la transacción contiene instrucciones del programa de tokens
            token_program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
            
            # Buscar instrucciones que involucren al programa de tokens
            instructions = tx_data.get("parsedInstruction", [])
            for instruction in instructions:
                program_id = instruction.get("programId")
                if program_id == token_program_id:
                    # Verificar si es una instrucción InitializeMint o MintTo
                    type_name = instruction.get("type")
                    if type_name in ["initializeMint", "createMint"]:
                        # Extraer la dirección del token (mint)
                        params = instruction.get("params", {})
                        mint = params.get("mint") or params.get("mintAccount")
                        if mint:
                            # Obtener metadatos del token
                            token_metadata = self._get_token_metadata(mint)
                            if token_metadata:
                                return {
                                    "address": mint,
                                    "name": token_metadata.get("name", "Unknown"),
                                    "symbol": token_metadata.get("symbol", ""),
                                    "decimals": token_metadata.get("decimals", 0),
                                    "uri": token_metadata.get("uri", ""),
                                    "tx_hash": tx_hash,
                                    "created_at": tx_data.get("blockTime", 0)
                                }
            
            self._log(f"No se encontró creación de token en la transacción {tx_hash}")
            
        except Exception as e:
            self._log(f"Error al analizar transacción {tx_hash}: {str(e)}")
            
        return None
        
    def _get_token_metadata(self, token_address):
        """
        Obtiene los metadatos de un token.
        
        Args:
            token_address (str): Dirección del token
            
        Returns:
            dict: Metadatos del token o None si hay error
        """
        self._log(f"Obteniendo metadatos para token {token_address}...")
        
        # Endpoint para obtener metadatos del token
        url = f"{self.solscan_base_url}/token/meta"
        params = {
            "token": token_address
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                metadata = response.json()
                # Extraer URI de metadatos si existe
                uri = metadata.get("uri", "")
                if uri:
                    self._log(f"URI de metadatos encontrada: {uri}")
                return metadata
            else:
                self._log(f"Error al obtener metadatos: {response.status_code}")
        except Exception as e:
            self._log(f"Error al consultar metadatos: {str(e)}")
            
        return None
    
    def get_token_mint_txs(self, limit=20):
        """
        Obtiene las transacciones recientes relacionadas con la creación de tokens.
        
        Args:
            limit (int): Número máximo de transacciones a obtener
            
        Returns:
            list: Lista de transacciones relacionadas con tokens
        """
        self._log(f"Buscando transacciones de creación de tokens para {self.creator_address}...")
        
        # Endpoint para transacciones
        url = f"{self.solscan_base_url}/account/transactions"
        params = {
            "account": self.creator_address,
            "limit": limit
        }
        
        # Usar nuestro método de solicitud con reintentos
        data = self._make_api_request_with_retry(url, params)
        
        if data and isinstance(data, list) and len(data) > 0:
            # Filtrar transacciones que podrían ser creación de tokens
            token_txs = []
            for tx in data:
                # Buscar transacciones que involucren programas de token
                if 'tokenProgram' in str(tx) or 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA' in str(tx):
                    token_txs.append(tx)
            
            self._log(f"Se encontraron {len(token_txs)} transacciones relacionadas con tokens")
            return token_txs
        else:
            self._log("No se encontraron transacciones relacionadas con tokens")
        
        return []
    
    def get_tokens_by_creator(self, limit=100):
        """
        Obtiene tokens creados por la dirección especificada.
        
        Args:
            limit (int): Número máximo de tokens a obtener
            
        Returns:
            list: Lista de tokens o lista vacía si hay error
        """
        # En modo de prueba, devolver tokens de prueba
        if self.test_mode:
            self._log("Modo de prueba activado: Usando tokens de prueba predefinidos")
            return self.test_tokens
            
        self._log(f"Buscando tokens creados por {self.creator_address}...")
        
        # Método 1: Buscar tokens directamente por creador
        tokens = self._get_tokens_by_creator_direct()
        
        # Si no encontramos tokens, intentar método alternativo
        if not tokens:
            self._log("No se encontraron tokens directamente. Intentando método alternativo...")
            tokens = self._get_tokens_by_transactions()
        
        self._log(f"Se encontraron {len(tokens)} tokens")
        return tokens
    
    def _get_tokens_by_creator_direct(self):
        """
        Intenta obtener tokens creados directamente usando la API de Solscan.
        
        Returns:
            list: Lista de tokens encontrados
        """
        tokens = []
        
        try:
            # Intentar obtener tokens directamente a través de la API de Solscan
            url = f"{self.solscan_base_url}/token/list"
            params = {
                "sortBy": "createTime",
                "sortType": "desc",
                "limit": 50
            }
            
            data = self._make_api_request_with_retry(url, params)
            
            if data and isinstance(data, list):
                self._log(f"Se encontraron {len(data)} tokens recientes en Solscan")
                
                # Filtrar tokens creados por nuestra dirección objetivo
                for token in data:
                    if token.get("creator") == self.creator_address:
                        self._log(f"Token creado por dirección objetivo: {token.get('address')} - {token.get('name', 'Unknown')}")
                        
                        # Crear objeto de token
                        token_obj = {
                            "address": token.get("address"),
                            "uri": token.get("metadataUri", ""),
                            "name": token.get("name", "Unknown"),
                            "symbol": token.get("symbol", "???")
                        }
                        
                        tokens.append(token_obj)
        except Exception as e:
            self._log(f"Error al obtener tokens por creador: {str(e)}")
        
        return tokens
    
    def _get_tokens_by_transactions(self):
        """
        Obtiene tokens buscando transacciones de creación de tokens.
        
        Returns:
            list: Lista de tokens encontrados
        """
        tokens = []
        
        try:
            # Obtener transacciones recientes
            url = f"{self.solscan_base_url}/account/transactions"
            params = {
                "account": self.creator_address,
                "limit": 50
            }
            
            data = self._make_api_request_with_retry(url, params)
            
            if data and isinstance(data, list):
                self._log(f"Se encontraron {len(data)} transacciones recientes")
                
                # Buscar transacciones relacionadas con creación de tokens
                for tx in data:
                    tx_hash = tx.get("txHash") or tx.get("tx_hash")
                    if not tx_hash:
                        continue
                    
                    # Verificar si es una transacción relacionada con tokens
                    program_ids = []
                    if "parsed_instructions" in tx and isinstance(tx["parsed_instructions"], list):
                        for instruction in tx["parsed_instructions"]:
                            if isinstance(instruction, dict) and "programId" in instruction:
                                program_ids.append(instruction["programId"])
                    
                    # Si la transacción involucra al Token Program o Metaplex, analizarla
                    token_program_id = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                    metaplex_program_id = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
                    
                    if token_program_id in program_ids or metaplex_program_id in program_ids:
                        self._log(f"Analizando transacción relacionada con tokens: {tx_hash}")
                        
                        # Obtener detalles de la transacción
                        tx_details = self._get_transaction_details(tx_hash)
                        if tx_details:
                            # Buscar instrucciones de creación de tokens (mint)
                            mint_addresses = self._extract_mint_addresses_from_tx(tx_details)
                            
                            for mint_address in mint_addresses:
                                # Obtener detalles del token
                                token_details = self._get_token_details(mint_address)
                                if token_details:
                                    tokens.append(token_details)
                                    self._log(f"Token encontrado en transacción: {mint_address}")
            
        except Exception as e:
            self._log(f"Error al obtener tokens por transacciones: {str(e)}")
        
        return tokens
    
    def _extract_mint_addresses_from_tx(self, tx_details):
        """
        Extrae direcciones de mint (creación) de tokens de los detalles de una transacción.
        
        Args:
            tx_details (dict): Detalles de la transacción
            
        Returns:
            list: Lista de direcciones de mint
        """
        mint_addresses = set()
        
        try:
            # Buscar en tokenTransfers si existe
            token_transfers = tx_details.get("tokenTransfers", [])
            for transfer in token_transfers:
                # Si es una transferencia de mint (creación)
                if transfer.get("type") == "mint":
                    token_address = transfer.get("tokenAddress")
                    if token_address:
                        mint_addresses.add(token_address)
            
            # Buscar en parsedInstruction para instrucciones de mint
            parsed_instructions = tx_details.get("parsedInstruction", [])
            for instruction in parsed_instructions:
                if isinstance(instruction, dict):
                    # Buscar instrucciones de mint
                    program = instruction.get("program")
                    type_str = instruction.get("type")
                    
                    if program == "spl-token" and type_str in ["mintTo", "initializeMint"]:
                        # Buscar en params para direcciones de mint
                        params = instruction.get("params", {})
                        if isinstance(params, dict):
                            mint = params.get("mint") or params.get("mintAccount")
                            if mint:
                                mint_addresses.add(mint)
        
        except Exception as e:
            self._log(f"Error al extraer direcciones de mint: {str(e)}")
        
        return list(mint_addresses)
    
    def _get_token_details(self, token_address):
        """
        Obtiene información detallada sobre un token específico.
        
        Args:
            token_address (str): Dirección del token
            
        Returns:
            dict: Información del token o None si hay error
        """
        # Verificar si el token ya fue procesado
        if token_address in self.processed_tokens:
            self._log(f"Token {token_address} ya fue procesado anteriormente")
            return None
            
        self._log(f"Obteniendo detalles del token {token_address}")
        
        # Consultar metadatos del token en Solscan
        url = f"{self.solscan_base_url}/token/meta"
        params = {"tokenAddress": token_address}
        
        data = self._make_api_request_with_retry(url, params)
        
        if data:
            metadata_uri = data.get("metadataUri")
            
            if metadata_uri:
                self._log(f"URI de metadatos encontrada: {metadata_uri}")
                
                # Construir objeto de token
                token = {
                    "address": token_address,
                    "uri": metadata_uri,
                    "name": data.get("name", "Unknown"),
                    "symbol": data.get("symbol", "???")
                }
                
                return token
            else:
                self._log(f"No se encontró URI de metadatos para {token_address}")
        else:
            self._log(f"No se pudieron obtener metadatos para {token_address}")
            
        # Si falló Solscan, intentar con RPC de Solana
        try:
            params = [token_address, {"encoding": "jsonParsed"}]
            token_info = self._make_rpc_request("getAccountInfo", params)
            
            if token_info:
                self._log(f"Se obtuvo información básica del token {token_address} via RPC")
                # En una implementación real, necesitaríamos extraer la URI de metadatos
                # de Metaplex, lo cual es más complejo y requiere llamadas adicionales
                # Este enfoque es más complejo y se omite en esta versión simplificada
        except Exception as e:
            self._log(f"Error al obtener detalles via RPC: {str(e)}")
            
        return None
    
    def process_new_tokens(self):
        """Busca y procesa nuevos tokens."""
        self._log("Iniciando búsqueda de nuevos tokens...")
        
        # Obtener tokens recientes
        tokens = self.get_tokens_by_creator()
        
        # Filtrar tokens ya procesados
        new_tokens = []
        for token in tokens:
            if token["address"] not in self.processed_tokens:
                new_tokens.append(token)
        
        if not new_tokens:
            self._log("No se encontraron nuevos tokens")
            return []
        
        self._log(f"Se encontraron {len(new_tokens)} nuevos tokens")
        
        # Procesar cada nuevo token
        processed_results = []
        for token in new_tokens:
            self._log(f"Procesando token: {token['address']}")
            
            # Extraer metadatos IPFS y datos de Twitter
            result = self.ipfs_extractor.process_token(token)
            
            if result:
                # Marcarlo como procesado
                self.processed_tokens.append(token["address"])
                processed_results.append(result)
                
                # Log detallado
                twitter_info = result["twitter_info"]
                self._log(f"Token procesado: {token['address']}")
                if twitter_info.get("usernames"):
                    self._log(f"  - Creador Twitter: @{twitter_info['usernames'][0]}")
                if twitter_info.get("mentions"):
                    self._log(f"  - Menciones: {', '.join(twitter_info['mentions'])}")
                
                # Guardar después de cada token procesado para no perder progreso
                self._save_processed_tokens()
            
        return processed_results
    
    def reset_processed_tokens(self):
        """Reinicia la lista de tokens procesados."""
        self._log("Reiniciando lista de tokens procesados")
        self.processed_tokens = []
        self._save_processed_tokens()
    
    def reset_processed_transfers(self):
        """Reinicia la caché de transferencias procesadas."""
        self._log("Reiniciando caché de transferencias procesadas")
        self.processed_transfers = set()
        self._save_processed_transfers()
    
    def _monitor_loop(self):
        """Bucle principal de monitoreo que se ejecuta en un hilo separado."""
        self._log(f"Iniciando monitoreo de tokens para {self.creator_address}")
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
        
        self._log("Monitoreo iniciado exitosamente")
    
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


# Ejemplo de uso
if __name__ == "__main__":
    # Dirección de Solana a monitorear
    CREATOR_ADDRESS = "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE"
    
    # Crear monitor con modo de prueba desactivado para usar la API real
    monitor = SolanaTokenMonitor(CREATOR_ADDRESS, check_interval=30, test_mode=False)
    
    # Opcional: Reiniciar tokens procesados para detectar todos los tokens
    # monitor.reset_processed_tokens()
    
    try:
        # Iniciar monitoreo
        monitor.start_monitoring()
        
        # Mantener el programa en ejecución
        print("\nMonitor de tokens en ejecución. Presiona Ctrl+C para detener...\n")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Detener el monitoreo cuando se presiona Ctrl+C
        monitor.stop_monitoring()
        print("\nMonitor detenido por el usuario") 