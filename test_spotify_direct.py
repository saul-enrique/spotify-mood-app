import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

print("--- Paso 1: Obteniendo el token de acceso manualmente ---")

# URL de la API de Cuentas de Spotify
auth_url = 'https://accounts.spotify.com/api/token'

# Codificamos el Client ID y el Client Secret como lo pide la API
auth_header_str = f"{client_id}:{client_secret}"
auth_header_bytes = auth_header_str.encode('ascii')
base64_auth_header = base64.b64encode(auth_header_bytes)
auth_header = base64_auth_header.decode('ascii')

# Hacemos la petición POST para obtener el token
auth_response = requests.post(auth_url, {
    'grant_type': 'client_credentials'
}, headers={
    'Authorization': f'Basic {auth_header}'
})

if auth_response.status_code != 200:
    print("¡ERROR! No se pudo obtener el token de acceso.")
    print(auth_response.json())
else:
    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']
    print("¡Token obtenido con éxito!")

    print("n--- Paso 2: Usando el token para pedir Audio Features ---")
    
    # IDs de algunas canciones de Candy66 para la prueba
    track_ids = [
        '5cwRU60H0zyEIr78OkM3Hd',
        '4YXSHChZ9tb9W319m4gaVf',
        '3MqbRdJcTU2NQfUoyHwwNn'
    ]
    
    features_url = f"https://api.spotify.com/v1/audio-features?ids={','.join(track_ids)}"
    
    # Preparamos la cabecera con nuestro token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Hacemos la petición GET
    features_response = requests.get(features_url, headers=headers)
    
    print(f"Código de estado de la petición: {features_response.status_code}")
    print("Respuesta de la API:")
    print(features_response.json())