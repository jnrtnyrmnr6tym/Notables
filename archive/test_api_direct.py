import requests
import json
import urllib.parse
import sys

# Función para cargar las cookies guardadas
def load_cookies(cookies_file="protokols_cookies.json"):
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        print(f"Cookies cargadas: {len(cookies)}")
        print("Cookies disponibles:")
        for name, value in cookies.items():
            print(f"  {name}: {value[:10]}..." if len(str(value)) > 10 else f"  {name}: {value}")
        return cookies
    except Exception as e:
        print(f"Error al cargar cookies: {str(e)}")
        return {}

# Función para obtener notable followers
def get_notable_followers(username, cookies):
    # Configurar la URL base con el punto correcto
    base_url = "https://api.protokols.io/api/trpc/influencers.getFullTwitterKolInitial"
    
    # Preparar los parámetros para GET
    params = {
        "username": username
    }
    
    # Codificar los parámetros para la URL (formato correcto para tRPC)
    input_json = json.dumps({"json": params})
    encoded_input = urllib.parse.quote(input_json)
    url = f"{base_url}?input={encoded_input}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.protokols.io",
        "Referer": f"https://www.protokols.io/twitter/{username}"
    }
    
    # Crear una sesión y añadir las cookies
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    # Actualizar los headers
    session.headers.update(headers)
    
    print(f"\nConsultando notable followers para @{username}...")
    print(f"URL: {base_url}")
    print(f"URL completa: {url}")
    print(f"Cookies activas en la sesión: {len(session.cookies)}")
    
    # Hacer la solicitud GET
    response = session.get(url)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error en la solicitud: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return None

# Función para formatear y mostrar los resultados
def display_results(data, username):
    if not data:
        print("\nNo se pudieron obtener datos.")
        return
    
    try:
        # Verificar si tenemos datos en la respuesta
        if "result" in data and "data" in data["result"]:
            # La estructura parece ser diferente a la esperada
            # Los datos del usuario están en result.data.json
            user_data = data["result"]["data"].get("json", {})
            
            # Mostrar información del perfil
            print("\n" + "="*50)
            print(f"INFORMACIÓN DEL PERFIL: @{username}")
            print("="*50)
            print(f"Nombre: {user_data.get('displayName', 'N/A')}")
            print(f"Usuario: @{user_data.get('username', 'N/A')}")
            print(f"Seguidores: {user_data.get('followersCount', 'N/A'):,}")
            print(f"Siguiendo: {user_data.get('followingCount', 'N/A'):,}")
            print(f"Verificado: {'Sí' if user_data.get('isVerified', False) else 'No'}")
            print(f"Descripción: {user_data.get('description', 'N/A')}")
            
            # Mostrar datos de engagement si están disponibles
            if "engagement" in user_data:
                engagement = user_data["engagement"]
                print("\n" + "="*50)
                print(f"DATOS DE ENGAGEMENT")
                print("="*50)
                print(f"Smart Followers Count: {engagement.get('smartFollowersCount', 'N/A'):,}")
                print(f"KOL Score: {engagement.get('kolScore', 'N/A'):,}")
                print(f"Promedio de Vistas: {engagement.get('avgViews', 'N/A'):,}")
                print(f"Promedio de Likes: {engagement.get('avgLikes', 'N/A'):,.2f}")
                print(f"Promedio de Retweets: {engagement.get('avgRetweets', 'N/A'):,.2f}")
                print(f"Promedio de Comentarios: {engagement.get('avgComments', 'N/A'):,.2f}")
                print(f"Ratio de Engagement: {engagement.get('engagementRatio', 'N/A'):.6f}")
            
            # Buscar notable followers en la estructura
            # Nota: Parece que la API no devuelve directamente una lista de notable followers
            # Pero podemos mostrar el Smart Followers Count como una aproximación
            if "engagement" in user_data and "smartFollowersCount" in user_data["engagement"]:
                smart_followers = user_data["engagement"]["smartFollowersCount"]
                print("\n" + "="*50)
                print(f"NOTABLE FOLLOWERS (Aproximación)")
                print("="*50)
                print(f"Este usuario tiene aproximadamente {smart_followers:,} seguidores notables.")
                print("La API no proporciona la lista completa de seguidores notables.")
            
        else:
            print("\nEstructura de respuesta desconocida.")
            print(f"Claves en la respuesta: {list(data.keys())}")
            if "result" in data:
                print(f"Claves en result: {list(data['result'].keys())}")
            
    except Exception as e:
        print(f"\nError al procesar la respuesta: {str(e)}")
        print("Raw response:")
        print(json.dumps(data, indent=2)[:1000] + "... (truncado)")

# Función principal
def main():
    # Obtener el nombre de usuario de los argumentos o usar uno predeterminado
    username = sys.argv[1] if len(sys.argv) > 1 else "jack"
    
    # Cargar cookies
    cookies = load_cookies()
    if not cookies:
        print("No se pudieron cargar las cookies. Abortando.")
        return
    
    # Obtener y mostrar datos
    data = get_notable_followers(username, cookies)
    display_results(data, username)
    
    # Opcionalmente guardar los resultados
    if data and "--save" in sys.argv:
        output_file = f"{username}_notable_followers.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"\nDatos guardados en {output_file}")

if __name__ == "__main__":
    main() 