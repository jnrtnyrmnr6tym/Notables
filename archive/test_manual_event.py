import json
import requests
import urllib.parse

# JSON de ejemplo recibido en el webhook (reemplazado por el nuevo proporcionado)
json_event = [{"accountData":[{"account":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE","nativeBalanceChange":-24527905,"tokenBalanceChanges":[]},{"account":"DBBmyR6ePQLA6qLYBCcL2BsZBVKNCop3zTsfciUycbyy","nativeBalanceChange":1461600,"tokenBalanceChanges":[]},{"account":"AD5kshkmqnxCWH3RSDtc7iaL6baFcUSgvGtuYTMRq3CB","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"32sRuFWvdPmVBS5wJsgnSj8G2iKDWNiD2qHk9W2nMAmW","nativeBalanceChange":2039280,"tokenBalanceChanges":[{"mint":"DBBmyR6ePQLA6qLYBCcL2BsZBVKNCop3zTsfciUycbyy","rawTokenAmount":{"decimals":9,"tokenAmount":"1000000000000000000"},"tokenAccount":"32sRuFWvdPmVBS5wJsgnSj8G2iKDWNiD2qHk9W2nMAmW","userAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM"}]},{"account":"7HT1wqJ1VZhkpjKpv8rVKSbBP3G9eVX1zLLWvGrGAxnz","nativeBalanceChange":2039280,"tokenBalanceChanges":[]},{"account":"FbpvU8kpvbs3NhyYTfpaiPFi73Q2SuLYLPMiVL8XeH9M","nativeBalanceChange":15115600,"tokenBalanceChanges":[]},{"account":"vejsmtiSyZWkwL3opFHcN2jviMspSfkdR2t3FffBk71","nativeBalanceChange":3841920,"tokenBalanceChanges":[]},{"account":"11111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"8Ks12pbrD6PXxfty1hVQiE9sc289zgU1zHkvXhrSdriF","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"9QQrLNyCF5kPsPYo2SL63BqnuzjyVWy8uC5TLs7VEc5R","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"ComputeBudget111111111111111111111111111111","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"So11111111111111111111111111111111111111112","nativeBalanceChange":0,"tokenBalanceChanges":[]},{"account":"TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA","nativeBalanceChange":0,"tokenBalanceChanges":[]}],"description":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE minted 1000000000.00 name to turn it into a coin. Not.","events":{"setAuthority":[{"account":"DBBmyR6ePQLA6qLYBCcL2BsZBVKNCop3zTsfciUycbyy","from":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","innerInstructionIndex":12,"instructionIndex":1,"to":""}]},"fee":30225,"feePayer":"5qWya6UjwWnGVhdSBL3hyZ7B45jbk6Byt1hwd7ohEGXE","instructions":[],"nativeTransfers":[],"signature":"iVhfYdSXmFkyyUzAa1qt1hNCKAhYe6nPWj8R5xkLzdVXmKjUS7AGxohG96KEX6yUnBk1ivHuejw9X9k4uW2Aqmz","slot":340176306,"source":"UNKNOWN","timestamp":1747311550,"tokenTransfers":[{"fromTokenAccount":"","fromUserAccount":"","mint":"DBBmyR6ePQLA6qLYBCcL2BsZBVKNCop3zTsfciUycbyy","toTokenAccount":"32sRuFWvdPmVBS5wJsgnSj8G2iKDWNiD2qHk9W2nMAmW","toUserAccount":"FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM","tokenAmount":1000000000,"tokenStandard":"Fungible"}],"transactionError":None,"type":"TOKEN_MINT"}]

# 1. Extraer el mint del token
token_transfer = json_event[0]["tokenTransfers"][0]
mint = token_transfer["mint"]
print(f"Mint del token: {mint}")

# 2. Extraer el usuario creador (owner) del token
creator = json_event[0]["events"]["setAuthority"][0]["from"]
print(f"Usuario creador (owner): {creator}")

# 3. Consultar la API de Protokols usando el endpoint correcto
try:
    with open("protokols_cookies.json", "r") as f:
        cookies = json.load(f)
    print(f"Cookies cargadas correctamente: {list(cookies.keys())}")
except Exception as e:
    print(f"Error al cargar las cookies: {e}")
    cookies = {}

# Endpoint y headers correctos
base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
params = {"username": creator}
input_json = json.dumps({"json": params})
encoded_input = urllib.parse.quote(input_json)
url = f"{base_url}?input={encoded_input}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://www.protokols.io",
    "Referer": f"https://www.protokols.io/twitter/{creator}"
}

session = requests.Session()
for name, value in cookies.items():
    session.cookies.set(name, value)

response = session.get(url, headers=headers)
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    try:
        protokols_data = response.json()
        print(f"Info de Protokols del usuario: {protokols_data}")
    except json.JSONDecodeError:
        print(f"Error al decodificar JSON. Respuesta: {response.text}")
else:
    print(f"Error al consultar Protokols: {response.status_code}")

# 4. Empaquetar toda la info en formato Telegram
print("\n--- Mensaje para Telegram ---")
print(f"🔹 Mint: {mint}")
print(f"🔹 Creador: {creator}")
print(f"🔹 URL Protokols API: {url}")
if 'protokols_data' in locals():
    print(f"🔹 Info de Protokols del usuario: {protokols_data}")
else:
    print("🔹 Info de Protokols del usuario: Error al consultar Protokols") 