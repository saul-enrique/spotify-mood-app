import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
from textblob import TextBlob
import requests
from tqdm import tqdm

load_dotenv()

auth_manager_logic = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp_logic = spotipy.Spotify(auth_manager=auth_manager_logic)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

def analizar_discografia(artist_id, artist_name):
    os.makedirs('cache', exist_ok=True)
    archivo_cache = f"cache/{artist_id}_api_only_v1.json"
    
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
            texto_para_analizar = nombre_cancion
            
            try:
                api_url = f"https.api.genius.com/search?q={requests.utils.quote(nombre_cancion + ' ' + artist_name)}"
                headers = {'Authorization': f'Bearer {genius_token}'}
                respuesta_genius = requests.get(api_url, headers=headers, timeout=15).json()
                
                for hit in respuesta_genius['response']['hits']:
                    if hit['result']['primary_artist']['name'].lower() in artist_name.lower():
                        texto_para_analizar = hit['result']['full_title']
                        break
            except Exception as e:
                print(f"Error en API de Genius para '{nombre_cancion}': {e}")

            polaridad = TextBlob(texto_para_analizar).sentiment.polarity
            
            todas_las_canciones.append({
                'nombre': nombre_cancion,
                'id': id_cancion,
                'polaridad': polaridad
            })
        
        with open(archivo_cache, 'w') as f:
            json.dump(todas_las_canciones, f, indent=4)

    canciones_positivas = [c for c in todas_las_canciones if c.get('polaridad', 0) > 0.1]
    
    return sorted(canciones_positivas, key=lambda x: x['polaridad'], reverse=True)