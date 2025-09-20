import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
from textblob import TextBlob
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

load_dotenv()

# Usamos una instancia separada de Spotipy solo para búsquedas públicas y rápidas
auth_manager_logic = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp_logic = spotipy.Spotify(auth_manager=auth_manager_logic, requests_timeout=20)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

def obtener_letra(url_cancion):
    try:
        pagina = requests.get(url_cancion)
        soup = BeautifulSoup(pagina.text, 'lxml')
        contenedor_letra = soup.find('div', class_=lambda c: c and c.startswith('Lyrics__Container'))
        if not contenedor_letra:
            contenedor_letra = soup.find('div', attrs={'data-lyrics-container': 'true'})
        if contenedor_letra:
            letra = contenedor_letra.get_text(separator='n').strip()
            return letra
        else:
            return "No se pudo encontrar el contenedor de la letra en la página."
    except Exception as e:
        return f"Error haciendo scraping: {e}"

def analizar_discografia(artist_id, artist_name):
    os.makedirs('cache', exist_ok=True)
    archivo_cache = f"cache/{artist_id}_letras_ids.json"
    
    if os.path.exists(archivo_cache):
        print("Cargando análisis desde caché...")
        with open(archivo_cache, 'r') as f:
            todas_las_canciones = json.load(f)
    else:
        print(f"Analizando a {artist_name} por primera vez...")
        resultados_albums = sp_logic.artist_albums(artist_id, album_type='album', limit=50)
        albums = resultados_albums['items']
        
        canciones_spotify = []
        for album in albums:
            canciones_spotify.extend(sp_logic.album_tracks(album['id'])['items'])

        todas_las_canciones = []
        for cancion in tqdm(canciones_spotify, desc="Analizando canciones"):
            nombre_cancion = cancion['name']
            id_cancion = cancion['id']

            letra = "Letra no encontrada."
            try:
                api_url = f"https://api.genius.com/search?q={requests.utils.quote(nombre_cancion + ' ' + artist_name)}"
                headers = {'Authorization': f'Bearer {genius_token}'}
                respuesta_genius = requests.get(api_url, headers=headers).json()
                url_cancion_genius = None
                for hit in respuesta_genius['response']['hits']:
                    if hit['result']['primary_artist']['name'].lower() in artist_name.lower() or artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                        url_cancion_genius = hit['result']['url']
                        break
                if url_cancion_genius:
                    letra = obtener_letra(url_cancion_genius)
            except Exception:
                letra = "Error buscando en Genius."

            polaridad = 0.0
            if "Letra no encontrada" not in letra and "Error" not in letra:
                analisis = TextBlob(letra)
                polaridad = analisis.sentiment.polarity
            
            todas_las_canciones.append({
                'nombre': nombre_cancion,
                'id': id_cancion,
                'polaridad': polaridad
            })
        
        with open(archivo_cache, 'w') as f:
            json.dump(todas_las_canciones, f, indent=4)

    canciones_positivas = [c for c in todas_las_canciones if c.get('polaridad', 0) > 0.1]
    
    return canciones_positivas