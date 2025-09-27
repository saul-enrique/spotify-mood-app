import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

try:
    auth_manager = SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception:
    sp = None

def encontrar_album_esencial(nombre_artista):
    if not sp: return None, [], None
    try:
        resultados = sp.search(q=f'artist:{nombre_artista}', type='artist', limit=1)
        if not resultados['artists']['items']: return None, [], None
        
        artista = resultados['artists']['items'][0]
        id_artista = artista['id']
        
        # Obtenemos los álbumes de estudio, ordenados por popularidad por defecto
        albums = sp.artist_albums(id_artista, album_type='album', limit=1)
        if not albums['items']: return None, [], artista
            
        album_esencial = albums['items'][0]
        id_album = album_esencial['id']
        
        canciones = sp.album_tracks(id_album)['items']
        
        return album_esencial, canciones, artista
    except Exception as e:
        print(f"Error encontrando álbum esencial: {e}")
        return None, [], None