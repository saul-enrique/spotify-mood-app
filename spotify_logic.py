import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# Usamos la autenticación simple que siempre funciona
auth_manager_logic = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp_logic = spotipy.Spotify(auth_manager=auth_manager_logic)

def buscar_artistas_en_spotify(nombre_artista):
    try:
        resultados = sp_logic.search(q=f'artist:{nombre_artista}', type='artist', limit=5)
        return resultados['artists']['items']
    except Exception as e:
        print(f"Error buscando artistas: {e}")
        return []

def encontrar_album_esencial(artist_id):
    try:
        # Obtenemos los álbumes de estudio
        albums = sp_logic.artist_albums(artist_id, album_type='album', limit=10)
        if not albums['items']: 
            return None, []
            
        # Asumimos que el primero (el más reciente o popular) es el esencial
        album_esencial = albums['items'][0]
        
        canciones = sp_logic.album_tracks(album_esencial['id'])['items']
        
        return album_esencial, canciones
    except Exception as e:
        print(f"Error encontrando álbum esencial: {e}")
        return None, []
