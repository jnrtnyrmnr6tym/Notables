#!/usr/bin/env python3
"""
Script para probar el procesamiento de notificaciones de webhook localmente con un JSON real de Helius.
"""

import json
import re
import base64
from token_monitor_with_notable_check import process_webhook_notification
from borsh_construct import CStruct, Bytes, U16
import requests

# Layout simplificado de Metaplex Metadata (solo campos básicos)
MetaplexMetadataLayout = CStruct(
    "name" / Bytes[32],
    "symbol" / Bytes[10],
    "uri" / Bytes[200],
    "seller_fee_basis_points" / U16,
    # ...otros campos pueden ser añadidos si es necesario
)

def try_decode_metaplex_data(data_str):
    """Intenta decodificar los datos de la instrucción de Metaplex usando Borsh."""
    import binascii
    try:
        print(f"\n[DEBUG] Intentando decodificar datos de Metaplex: {data_str}")
        
        # 1. Intentar extraer URI directamente del string de datos
        ipfs_pattern = r'ipfs://[a-zA-Z0-9]+'
        arweave_pattern = r'https://arweave.net/[a-zA-Z0-9]+'
        
        ipfs_matches = re.findall(ipfs_pattern, data_str)
        arweave_matches = re.findall(arweave_pattern, data_str)
        
        if ipfs_matches:
            print(f"[INFO] URI IPFS encontrada directamente: {ipfs_matches[0]}")
            return {"uri": ipfs_matches[0]}
        if arweave_matches:
            print(f"[INFO] URI Arweave encontrada directamente: {arweave_matches[0]}")
            return {"uri": arweave_matches[0]}
        
        # 2. Intentar decodificar como base64 con padding
        try:
            padding_needed = len(data_str) % 4
            if padding_needed:
                data_str = data_str + "=" * (4 - padding_needed)
                print(f"[DEBUG] Añadido padding: {data_str}")
            decoded = base64.b64decode(data_str)
            print(f"[DEBUG] Binario decodificado (hex): {binascii.hexlify(decoded)[:64]}...")
            
            # 3. Intentar deserializar con Borsh
            try:
                meta = MetaplexMetadataLayout.parse(decoded)
                name = meta.name.decode("utf-8", errors="ignore").rstrip("\x00")
                symbol = meta.symbol.decode("utf-8", errors="ignore").rstrip("\x00")
                uri = meta.uri.decode("utf-8", errors="ignore").rstrip("\x00")
                print(f"[INFO] Metadata Borsh decodificada: name={name}, symbol={symbol}, uri={uri}")
                return {"name": name, "symbol": symbol, "uri": uri}
            except Exception as e:
                print(f"[ERROR] Error al deserializar con Borsh: {e}")
                # Si falla, intentar buscar URIs en el string decodificado
                decoded_str = decoded.decode('utf-8', errors='ignore')
                ipfs_matches = re.findall(ipfs_pattern, decoded_str)
                arweave_matches = re.findall(arweave_pattern, decoded_str)
                if ipfs_matches:
                    print(f"[INFO] URI IPFS encontrada en datos decodificados: {ipfs_matches[0]}")
                    return {"uri": ipfs_matches[0]}
                if arweave_matches:
                    print(f"[INFO] URI Arweave encontrada en datos decodificados: {arweave_matches[0]}")
                    return {"uri": arweave_matches[0]}
                print("[WARN] No se encontraron URIs en los datos decodificados")
                return None
        except Exception as e:
            print(f"[ERROR] Error al decodificar base64: {e}")
            return None
    except Exception as e:
        print(f"[ERROR] Error general al procesar datos de Metaplex: {e}")
        return None

def analizar_metaplex_uri(test_data):
    print("\n[ANÁLISIS] Buscando instrucción de Metaplex...")
    instrucciones = test_data[0].get('instructions', [])
    for idx, instr in enumerate(instrucciones):
        # Buscar en innerInstructions
        inner = instr.get('innerInstructions', [])
        for inner_idx, inner_instr in enumerate(inner):
            if inner_instr.get('programId') == 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s':
                data = inner_instr.get('data')
                print(f"[ENCONTRADO] Instrucción de Metaplex en instructions[{idx}].innerInstructions[{inner_idx}]")
                print(f"[DATA] {data}")
                if data:
                    result = try_decode_metaplex_data(data)
                    if result and result.get('uri'):
                        print(f"[URI ENCONTRADA] {result['uri']}")
                    else:
                        print("[NO SE PUDO EXTRAER URI]")
                return
    print("[NO SE ENCONTRÓ INSTRUCCIÓN DE METAPLEX CON URI EN EL JSON]")

def main():
    # Cargar el JSON desde un archivo externo
    with open('test_notification.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    print("\n[TEST] Procesando notificación de prueba...")
    print(f"[DEBUG] Datos de prueba: {json.dumps(test_data, indent=2)}")

    # --- Análisis de Metaplex ---
    analizar_metaplex_uri(test_data)
    # --- Fin análisis ---
    
    # Procesar la notificación
    result = process_webhook_notification(test_data)
    
    # Mostrar resultado
    if result:
        print("\n[RESULTADO]")
        print(f"📝 Nombre: {result.get('name', 'N/A')}")
        print(f"🔤 Ticker: {result.get('symbol', 'N/A')}")
        print(f"🔗 CA: {result.get('token_address', 'N/A')}")
        print(f"🖼 Imagen: {result.get('image', 'N/A')}")
        print(f"👤 Twitter del creador: @{result.get('twitter_username', 'N/A')}")
    else:
        print("\n[ERROR] No se pudo procesar la notificación")

# URL del webhook
WEBHOOK_URL = "http://127.0.0.1:3003/webhook"

# JSON de prueba en formato string (tal cual lo envía Helius, con null)
test_notification_json = '''
[  {
    "accountData": [
      {"account": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "nativeBalanceChange": -24527905, "tokenBalanceChanges": []},
      {"account": "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "nativeBalanceChange": 1461600, "tokenBalanceChanges": []},
      {"account": "7eSfJhVsTodMHo8JtCDez94v5aspWYzpxwmkL4Mp4YUS", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf", "nativeBalanceChange": 15115600, "tokenBalanceChanges": []},
      {"account": "acopyZBAf5HEDEpCj2cqEQ5NPwLjRwmZ1SE8EsACSWk", "nativeBalanceChange": 2039280, "tokenBalanceChanges": []},
      {"account": "Dxfyg6eoEoYrT3pTWXR1CyLSWwKWvM98j3wgWquuQoCx", "nativeBalanceChange": 3841920, "tokenBalanceChanges": []},
      {"account": "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "nativeBalanceChange": 2039280, "tokenBalanceChanges": [{"mint": "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "rawTokenAmount": {"decimals": 9, "tokenAmount": "1000000000000000000"}, "tokenAccount": "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "userAccount": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"}]},
      {"account": "11111111111111111111111111111111", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "ComputeBudget111111111111111111111111111111", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "J7viPXjP5TmanPiXfP6MZhZVsDPiFb99h6Qfp8Ey2CYe", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "So11111111111111111111111111111111111111112", "nativeBalanceChange": 0, "tokenBalanceChanges": []},
      {"account": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "nativeBalanceChange": 0, "tokenBalanceChanges": []}
    ],
    "description": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE minted 1000000000.00 Wrapped SOL.",
    "events": {"setAuthority": [{"account": "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "from": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "innerInstructionIndex": 12, "instructionIndex": 1, "to": ""}]},
    "fee": 30225,
    "feePayer": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE",
    "instructions": [
      {"accounts": [], "data": "3vxqYwMPxGsR", "innerInstructions": [], "programId": "ComputeBudget111111111111111111111111111111"},
      {"accounts": ["J7viPXjP5TmanPiXfP6MZhZVsDPiFb99h6Qfp8Ey2CYe", "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "7eSfJhVsTodMHo8JtCDez94v5aspWYzpxwmkL4Mp4YUS", "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "So11111111111111111111111111111111111111112", "Dxfyg6eoEoYrT3pTWXR1CyLSWwKWvM98j3wgWquuQoCx", "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "acopyZBAf5HEDEpCj2cqEQ5NPwLjRwmZ1SE8EsACSWk", "6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf", "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s", "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "11111111111111111111111111111111", "8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF", "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"], "data": "3QKJSNs3eBWskYLkN1GJ6WvcTV8uirTvpFZ5wcReEX4g1UwEpc8MXQNtAUT3CEYfSqkNzvQxVSQxxQJQKpCsdTdh5NLsHpREcBe8CxGrKQM5nLVKFQV2Yt9FnD79fJRQZHLTUZCnR1UTDfakofsv58ymxNhdLgkjZMmMihUWMwRWmCMrH2hweSjqe", "innerInstructions": [
        {"accounts": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6"], "data": "11114XtYk9gGfZoo968fyjNUYQJKf9gdmkGoaoBpzFv4vyaSMBn3VKxZdv7mZLzoyX5YNC", "programId": "11111111111111111111111111111111"},
        {"accounts": ["38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6"], "data": "2zy7UagEY9n7vEQ3xcV9DUJ34ntLNsDJr1UovjQv5xgabuvo", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"accounts": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "Dxfyg6eoEoYrT3pTWXR1CyLSWwKWvM98j3wgWquuQoCx"], "data": "11115iewQrmF97gf1nmDekHVspCwF3W1UPSpvmJKdw2UTGkscomrsKi11GyM8E1q9bYQ1N", "programId": "11111111111111111111111111111111"},
        {"accounts": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A"], "data": "11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL", "programId": "11111111111111111111111111111111"},
        {"accounts": ["GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6"], "data": "6bqCTyyN8REmv5mAz7MZQ1CURihLYPK4BepSfmcPaaVLK", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"accounts": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "acopyZBAf5HEDEpCj2cqEQ5NPwLjRwmZ1SE8EsACSWk"], "data": "11119os1e9qSs2u7TsThXqkBSRVFxhmYaFKFZ1waB2X7armDmvK3p5GmLdUxYdg3h7QSrL", "programId": "11111111111111111111111111111111"},
        {"accounts": ["acopyZBAf5HEDEpCj2cqEQ5NPwLjRwmZ1SE8EsACSWk", "So11111111111111111111111111111111111111112"], "data": "6bqCTyyN8REmv5mAz7MZQ1CURihLYPK4BepSfmcPaaVLK", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"accounts": ["6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf", "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "7eSfJhVsTodMHo8JtCDez94v5aspWYzpxwmkL4Mp4YUS", "11111111111111111111111111111111"], "data": "Zt4hCBYNNnESmFsKGWQsfFE1mKksPz86n9CXHLnZQWGJJJE6GjeqBe3EbDQUM6zbwcyJ1kRQYfdVa3yFYUhqjQeRioijS1MLuEFRaEfV3ZeuC3rrYapXSdhDsCjwPz5RPmFjnnMnNG6FWmPu7eVSQpbNt3s9MVnkBx2orUL4Fd71Hf9nCC17SHQ3", "programId": "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"},
        {"accounts": ["5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf"], "data": "3Bxs4EM3hQgDpNyd", "programId": "11111111111111111111111111111111"},
        {"accounts": ["6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf"], "data": "9krTDGKLJBg7SB59", "programId": "11111111111111111111111111111111"},
        {"accounts": ["6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf"], "data": "SYXsBkG6yKW2wWDcW8EDHR6D3P82bKxJGPpM65DD8nHqBfMP", "programId": "11111111111111111111111111111111"},
        {"accounts": ["38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"], "data": "6AjfG4h8qfC8", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"accounts": ["38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"], "data": "31tb", "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"accounts": ["8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF"], "data": "iVCwvZuhjTd6RCN2asiXmqchZhBUh9CB84MDBMvGSo7xD5Dhv66em2KkWSGm7bydpSSFWXk7afVu797VuJwCnuem1wf97UTbFYNSUAwN545rAiMDpqt3jsNu2uboefsKWukRKUotdKSiPe1MYy2KSUvrHRbmJCU3h6TKbQD6Wk4PmsYBiea2pTPJxPWij3FPdjC3tLsPAGUGNZMAw", "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
      ], "programId": "dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN"}
    ],
    "nativeTransfers": [
      {"amount": 1461600, "fromUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "toUserAccount": "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6"},
      {"amount": 3841920, "fromUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "toUserAccount": "Dxfyg6eoEoYrT3pTWXR1CyLSWwKWvM98j3wgWquuQoCx"},
      {"amount": 2039280, "fromUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "toUserAccount": "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A"},
      {"amount": 2039280, "fromUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "toUserAccount": "acopyZBAf5HEDEpCj2cqEQ5NPwLjRwmZ1SE8EsACSWk"},
      {"amount": 15115600, "fromUserAccount": "5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE", "toUserAccount": "6spVoCz9BDdAAHCauxqHEJj4cgQqZzfnXzUzx4hDhiZf"}
    ],
    "signature": "28yEpmyp3G3pgVjzNHT5gwDTu4yW5bLQ2oJpkkAyzb5JmQnjGdbaSmywSptqRLM9AcFCaUtBNKeMAGHmDLVum5h9",
    "slot": 340216754,
    "source": "UNKNOWN",
    "timestamp": 1747327581,
    "tokenTransfers": [
      {"fromTokenAccount": "", "fromUserAccount": "", "mint": "38NwqinmKCpoAfCEY5rawDdWFbVyZY4D8V1Vj4uZ8pe6", "toTokenAccount": "GNCw5JhfTD8c8KzQM5ejeDi6hSaCC9G6uUA7k9rapn4A", "toUserAccount": "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM", "tokenAmount": 1000000000, "tokenStandard": "Fungible"}
    ],
    "transactionError": null,
    "type": "TOKEN_MINT"
  }
]
'''

def send_test_notification():
    print("\nEnviando notificación de prueba (formato string JSON real)...")
    print(test_notification_json[:500] + "...\n[truncado]")
    response = requests.post(
        WEBHOOK_URL,
        data=test_notification_json,
        headers={"Content-Type": "application/json"}
    )
    print(f"\nRespuesta del servidor:")
    print(f"Código de estado: {response.status_code}")
    try:
        print(f"Contenido: {json.dumps(response.json(), indent=2)}")
    except Exception:
        print(f"Contenido: {response.text}")

if __name__ == "__main__":
    send_test_notification() 