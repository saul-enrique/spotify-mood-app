import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import time
from tqdm import tqdm
import json

def obtener_letra(url_cancion):
    try:
        pagina = requests.get(url_cancion)
        soup = BeautifulSoup(pagina.text, 'lxml')
        contenedor_letra = soup.find('div', class_=lambda c: c and c.startswith('Lyrics__Container'))
        if not contenedor_letra:
            contenedor_letra = soup.find('div', attrs={'data-lyrics-container': 'true'})
        if contenedor_letra:
            letra = contenedor_letra.get_text(separator='\n').strip()
            return letra
        else:
            return "No se pudo encontrar el contenedor de la letra en la página."
    except Exception as e:
        return f"Error haciendo scraping: {e}"

load_dotenv()
scope = "playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope=scope
),
requests_timeout=20)
user_id = sp.current_user()['id']
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

nombre_artista = input("Escribe el nombre de un artista o banda: ")
resultados = sp.search(q='artist:' + nombre_artista, type='artist', limit=10)
items = resultados['artists']['items']

if not items:
    print(f"No se encontraron artistas con el nombre '{nombre_artista}'.")
else:
    print("Se encontraron los siguientes artistas:")
    for i, artista_item in enumerate(items):
        print(f"  [{i + 1}] {artista_item['name']}")

    try:
        seleccion_artista = int(input("\nEscribe el número del artista correcto: "))
        if 1 <= seleccion_artista <= len(items):
            artista_elegido = items[seleccion_artista - 1]
            id_artista = artista_elegido['id']
            nombre_real_artista = artista_elegido['name']
            print(f"\nHas elegido a: {nombre_real_artista}")

            print("\n¿Qué tipo de canciones buscas?")
            print("  [1] Positivas (Letra alegre)")
            print("  [2] Negativas (Letra triste/enfadada)")
            
            try:
                seleccion_mood = int(input("Elige una opción (1-2): "))
            except ValueError:
                seleccion_mood = 0

            if seleccion_mood in [1, 2]:
                os.makedirs('cache', exist_ok=True)
                archivo_cache = f"cache/{id_artista}_letras_ids.json"
                
                todas_las_canciones_analizadas = []

                if os.path.exists(archivo_cache):
                    print("\nCargando análisis desde caché...")
                    with open(archivo_cache, 'r') as f:
                        todas_las_canciones_analizadas = json.load(f)
                    time.sleep(1)
                else:
                    print("\nAnalizando letras del artista...")
                    resultados_albums = sp.artist_albums(id_artista, album_type='album', limit=50)
                    albums = resultados_albums['items']
                    
                    canciones_spotify = []
                    for album in albums:
                        canciones_spotify.extend(sp.album_tracks(album['id'])['items'])

                    with tqdm(total=len(canciones_spotify), desc="Procesando Canciones") as pbar:
                        for cancion in canciones_spotify:
                            nombre_cancion = cancion['name']
                            id_cancion = cancion['id']
                            
                            letra = "Letra no encontrada."
                            try:
                                api_url = f"https://api.genius.com/search?q={requests.utils.quote(nombre_cancion + ' ' + nombre_real_artista)}"
                                headers = {'Authorization': f'Bearer {genius_token}'}
                                respuesta_genius = requests.get(api_url, headers=headers).json()
                                url_cancion_genius = None
                                for hit in respuesta_genius['response']['hits']:
                                    # Hacemos una comprobación más segura
                                    if hit['result']['primary_artist']['name'].lower() in nombre_real_artista.lower() or nombre_real_artista.lower() in hit['result']['primary_artist']['name'].lower():
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

                            todas_las_canciones_analizadas.append({
                                'nombre': nombre_cancion,
                                'id': id_cancion,
                                'polaridad': polaridad
                            })
                            pbar.update(1)
                    
                    with open(archivo_cache, 'w') as f:
                        json.dump(todas_las_canciones_analizadas, f, indent=4)
                    print(f"\nAnálisis guardado en caché.")

                print(f"Análisis completo. Se procesaron {len(todas_las_canciones_analizadas)} canciones.")
                time.sleep(1)

                canciones_filtradas = []
                mood_texto = ""
                if seleccion_mood == 1:
                    mood_texto = "Positivas"
                    canciones_filtradas = [c for c in todas_las_canciones_analizadas if c['polaridad'] > 0.1]
                elif seleccion_mood == 2:
                    mood_texto = "Negativas"
                    canciones_filtradas = [c for c in todas_las_canciones_analizadas if c['polaridad'] < -0.1]

                print(f"\n--- CANCIONES {mood_texto.upper()} DE {nombre_real_artista.upper()} ---")
                if not canciones_filtradas:
                    print("\nNo se encontraron canciones que coincidan con tu criterio.")
                else:
                    for i, cancion in enumerate(canciones_filtradas):
                        print(f"  [{i+1}] {cancion['nombre']} (Polaridad: {cancion['polaridad']:.2f})")
                    
                    crear_playlist = input("\n¿Quieres crear una playlist en Spotify con estas canciones? (s/n): ").lower()
                    if crear_playlist == 's':
                        nombre_playlist = f"{nombre_real_artista} - Canciones {mood_texto}"
                        descripcion_playlist = f"Una selección de las canciones más {mood_texto.lower()} de {nombre_real_artista}, generada por Mood Selector."
                        
                        print(f"\nCreando playlist '{nombre_playlist}'...")
                        
                        playlist = sp.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion_playlist)
                        playlist_id = playlist['id']
                        
                        ids_para_playlist = [c['id'] for c in canciones_filtradas if c['id']]
                        for i in range(0, len(ids_para_playlist), 100):
                            lote = ids_para_playlist[i:i+100]
                            sp.playlist_add_items(playlist_id, lote)
                        
                        print("¡Playlist creada con éxito! Revisa tu cuenta de Spotify.")
                        print(f"Enlace: {playlist['external_urls']['spotify']}")

            else:
                print("Opción no válida.")
        else:
            print("Número de artista fuera de rango.")
    except (ValueError, KeyError) as e:
        print(f"Ocurrió un error: {e}")

