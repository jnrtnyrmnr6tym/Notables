import requests
import json
import urllib.parse

def test_protokols_api():
    # Cargar cookies
    try:
        with open("protokols_cookies.json", "r") as f:
            cookies = json.load(f)
        print(f"Cookies cargadas: {len(cookies)} cookies")
    except Exception as e:
        print(f"Error al cargar cookies: {e}")
        return
    
    # Configurar URL y parámetros
    username = "jack"
    base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
    params = {"username": username}
    input_json = json.dumps({"json": params})
    
    # URL completa
    encoded_input = urllib.parse.quote(input_json)
    url = f"{base_url}?input={encoded_input}"
    
    print(f"URL: {url}")
    
    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    
    # Crear sesión y añadir cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Hacer la solicitud
    try:
        response = session.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("La API está funcionando correctamente")
            data = response.json()
            if "result" in data and "data" in data["result"] and "json" in data["result"]["data"]:
                user_data = data["result"]["data"]["json"]
                if "engagement" in user_data and "smartFollowersCount" in user_data["engagement"]:
                    smart_followers = user_data["engagement"]["smartFollowersCount"]
                    print(f"Notable followers: {smart_followers}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Respuesta: {response.text[:500]}")
    except Exception as e:
        print(f"Error en la solicitud: {e}")

if __name__ == "__main__":
    test_protokols_api() 