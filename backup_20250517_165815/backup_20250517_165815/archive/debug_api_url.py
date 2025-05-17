import requests
import json
import urllib.parse
import sys

def test_user(username, cookies, session):
    base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
    params = {"username": username}
    input_json = json.dumps({"json": params})
    encoded_input = urllib.parse.quote(input_json)
    url = f"{base_url}?input={encoded_input}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    
    try:
        print(f"\nProbando usuario: @{username}")
        response = session.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"API funciona correctamente para @{username}")
            data = response.json()
            if "result" in data and "data" in data["result"] and "json" in data["result"]["data"]:
                user_data = data["result"]["data"]["json"]
                if "engagement" in user_data and "smartFollowersCount" in user_data["engagement"]:
                    smart_followers = user_data["engagement"]["smartFollowersCount"]
                    print(f"Notable followers: {smart_followers}")
                else:
                    print("No se encontraron datos de engagement")
            else:
                print("Estructura de respuesta inesperada")
        else:
            print(f"Error con usuario @{username}: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error en la solicitud para @{username}: {e}")
        return False

def compare_users():
    # Cargar cookies
    try:
        with open("protokols_cookies.json", "r") as f:
            cookies = json.load(f)
        print(f"Cookies cargadas: {len(cookies)} cookies")
    except Exception as e:
        print(f"Error al cargar cookies: {e}")
        return
    
    # Crear sesión y añadir cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Lista de usuarios para probar
    users = ["jack", "elonmusk", "syekhbroccoli", "ASCIIpunxs", "yue1231234"]
    
    # Probar cada usuario
    results = {}
    for user in users:
        results[user] = test_user(user, cookies, session)
    
    # Mostrar resumen
    print("\nResumen de resultados:")
    for user, success in results.items():
        print(f"@{user}: {'✓' if success else '✗'}")

if __name__ == "__main__":
    compare_users() 