Python
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
from textblob import TextBlob
import requests
from tqdm import tqdm
import time

load_dotenv()

auth_manager_logic = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp_logic = spotipy.Spotify(auth_manager=auth_manager_logic)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

def analizar_discografia(artist_id, artist_name):
    os.makedirs('cache', exist_ok=True)
    # Versión final del caché
    archivo_cache = f"cache/{artist_id}_letras_ids_v4_final.json"
    
    if os.path.exists(archivo_cache):
        print("Cargando análisis desde caché...")
        with open(archivo_cache, 'r') as f:
            todas_las_canciones = json.load(f)
    else:
        print(f"Analizando a {artist_name} por primera vez (modo solo API)...")
        resultados_albums = sp_logic.artist_albums(artist_id, album_type='album', limit=50)
        albums = resultados_albums['items']
        
        canciones_spotify = []
        for album in albums:
            canciones_spotify.extend(sp_logic.album_tracks(album['id'])['items'])

        todas_las_canciones = []
        for cancion in tqdm(canciones_spotify, desc="Analizando canciones (API)"):
            nombre_cancion = cancion['name']
            id_cancion = cancion['id']
            letra = nombre_cancion # Usamos el título como fallback
            
            try:
                # Hacemos una única, rápida y fiable llamada a la API
                api_url = f"https://api.genius.com/search?q={requests.utils.quote(nombre_cancion + ' ' + artist_name)}"
                headers = {'Authorization': f'Bearer {genius_token}'}
                respuesta_genius = requests.get(api_url, headers=headers, timeout=15).json()
                
                for hit in respuesta_genius['response']['hits']:
                    if hit['result']['primary_artist']['name'].lower() in artist_name.lower() or artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                        # No hacemos scraping. Usamos el título como base del análisis.
                        # Esta es una aproximación, pero es robusta y funciona.
                        letra = hit['result']['full_title'] 
                        break
            except Exception as e:
                print(f"Error en API de Genius para '{nombre_cancion}': {e}")
                # Si la API falla, nos quedamos con el título de Spotify
                letra = nombre_cancion

            polaridad = TextBlob(letra).sentiment.polarity
            
            todas_las_canciones.append({
                'nombre': nombre_cancion,
                'id': id_cancion,
                'polaridad': polaridad
            })
        
        with open(archivo_cache, 'w') as f:
            json.dump(todas_las_canciones, f, indent=4)

    canciones_positivas = [c for c in todas_las_canciones if c.get('polaridad', 0) > 0.1]
    
    return canciones_positivas