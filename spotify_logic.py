import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
from textblob import TextBlob
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import time

# Cargamos las variables de entorno una sola vez
load_dotenv()

# Inicializamos el cliente de Spotify una sola vez
try:
    auth_manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    sp = None
    print(f"Error al inicializar Spotify: {e}")

def buscar_artistas(nombre_artista):
    """
    Busca artistas en Spotify y devuelve una lista de resultados.
    """
    if not sp:
        return [] # Si Spotify no se inicializó, devuelve una lista vacía
    
    try:
        resultados = sp.search(q='artist:' + nombre_artista, type='artist', limit=10)
        # Devolvemos solo la lista de 'items' que es lo que nos interesa
        return resultados['artists']['items']
    except Exception as e:
        print(f"Error al buscar artistas: {e}")
        return []

# --- Lógica de Análisis de Letras ---

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
        # Aquí usamos el cliente 'sp' que está definido globalmente en este archivo
        resultados_albums = sp.artist_albums(artist_id, album_type='album', limit=50)
        albums = resultados_albums['items']
        
        canciones_spotify = []
        for album in albums:
            canciones_spotify.extend(sp.album_tracks(album['id'])['items'])

        todas_las_canciones = []
        for cancion in tqdm(canciones_spotify, desc="Analizando canciones"):
            nombre_cancion = cancion['name']
            id_cancion = cancion['id']

            # --- LÓGICA RESTAURADA ---
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
            # --- FIN DE LA LÓGICA RESTAURADA ---
            
            todas_las_canciones.append({
                'nombre': nombre_cancion,
                'id': id_cancion,
                'polaridad': polaridad
            })
        
        with open(archivo_cache, 'w') as f:
            json.dump(todas_las_canciones, f, indent=4)

    canciones_positivas = [c for c in todas_las_canciones if c.get('polaridad', 0) > 0.1]
    
    return todas_las_canciones, canciones_positivas

def crear_playlist_spotify(user_id, artist_name, track_ids):
    """
    Crea una nueva playlist pública en la cuenta del usuario y añade las canciones.
    """
    if not sp or not user_id:
        print("Error: El cliente de Spotify no está autenticado correctamente.")
        return None
    
    try:
        nombre_playlist = f"{artist_name} - Canciones Positivas"
        descripcion_playlist = f"Una selección de las canciones más positivas de {artist_name}, generada por Mood Selector."
        
        # 1. Crear la playlist vacía
        playlist = sp.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion_playlist)
        playlist_id = playlist['id']
        
        # 2. Añadir las canciones en lotes de 100
        for i in range(0, len(track_ids), 100):
            lote = track_ids[i:i+100]
            sp.playlist_add_items(playlist_id, lote)
            
        # Devolvemos el objeto completo de la playlist para poder usar su URL
        return playlist
    
    except Exception as e:
        print(f"Error al crear la playlist: {e}")
        return None