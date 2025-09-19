import os
import requests
from dotenv import load_dotenv

print("Cargando el archivo .env...")
load_dotenv()

token = os.getenv("GENIUS_ACCESS_TOKEN")

if not token:
    print("ERROR: No se pudo encontrar el GENIUS_ACCESS_TOKEN en el archivo .env")
else:
    print("Token encontrado. Intentando conectar con la API de Genius...")
    
    # Preparamos la petición directa
    search_term = "Muse"
    api_url = f"https://api.genius.com/search?q={search_term}"
    headers = {'Authorization': f'Bearer {token}'}
    
    # Hacemos la llamada
    response = requests.get(api_url, headers=headers)
    
    # Imprimimos el resultado crudo
    print("n--- RESULTADO DE LA CONEXIÓN DIRECTA ---")
    print(f"Código de estado HTTP: {response.status_code}")
    print("Respuesta recibida:")
    print(response.json())
    print("------------------------------------")