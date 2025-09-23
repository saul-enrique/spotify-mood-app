import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
from tqdm import tqdm

load_dotenv()

# Usamos una instancia separada de Spotipy para búsquedas públicas y rápidas
auth_manager_logic = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp_logic = spotipy.Spotify(auth_manager=auth_manager_logic, requests_timeout=15)

def analizar_discografia(artist_id, artist_name):
    os.makedirs('cache', exist_ok=True)
    # Nueva versión de caché para los audio features
    archivo_cache = f"cache/{artist_id}_audio_features.json"
    
    if os.path.exists(archivo_cache):
        print("Cargando análisis de audio features desde caché...")
        with open(archivo_cache, 'r') as f:
            todas_las_canciones = json.load(f)
    else:
        print(f"Analizando a {artist_name} por primera vez (Audio Features)...")
        resultados_albums = sp_logic.artist_albums(artist_id, album_type='album', limit=50)
        albums = resultados_albums['items']
        
        canciones_spotify = []
        for album in albums:
            canciones_spotify.extend(sp_logic.album_tracks(album['id'])['items'])

        # Filtramos IDs nulos o inválidos antes de la petición
        ids_canciones = [c['id'] for c in canciones_spotify if c and c.get('id')]
        
        todas_las_canciones = []
        
        # Obtenemos los audio features en lotes de 100
        for i in tqdm(range(0, len(ids_canciones), 100), desc="Obteniendo Audio Features"):
            lote_ids = ids_canciones[i:i+100]
            try:
                resultados_lote = sp_logic.audio_features(lote_ids)
                
                # Unimos los features con los nombres de las canciones
                # Esto requiere encontrar la canción original por su ID
                for features in resultados_lote:
                    if features:
                        cancion_original = next((c for c in canciones_spotify if c['id'] == features['id']), None)
                        if cancion_original:
                            todas_las_canciones.append({
                                'nombre': cancion_original['name'],
                                'id': features['id'],
                                'valence': features['valence'] # La "positividad" musical
                            })
            except Exception as e:
                print(f"Error obteniendo lote de audio features: {e}")

        with open(archivo_cache, 'w') as f:
            json.dump(todas_las_canciones, f, indent=4)

    # Filtramos por canciones con alta "valence" (positividad musical)
    canciones_positivas = [c for c in todas_las_canciones if c.get('valence', 0) > 0.6]
    
    return sorted(canciones_positivas, key=lambda x: x['valence'], reverse=True)