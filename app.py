import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
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
sp_auth_manager = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp = spotipy.Spotify(auth_manager=sp_auth_manager)
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
            print("  [1] Positivas / Alegres")
            print("  [2] Negativas / Tristes")
            print("  [3] Neutrales")
            
            try:
                seleccion_mood = int(input("Elige una opción (1, 2 o 3): ")) # <-- Mensaje más claro
            except ValueError:
                seleccion_mood = 0

            if seleccion_mood in [1, 2, 3]:
                os.makedirs('cache', exist_ok=True)
                archivo_cache = f"cache/{id_artista}.json"
                
                todas_las_canciones_analizadas = []

                if os.path.exists(archivo_cache):
                    print("\n¡Buenas noticias! Este artista ya ha sido analizado. Cargando desde caché...")
                    with open(archivo_cache, 'r') as f:
                        todas_las_canciones_analizadas = json.load(f)
                    time.sleep(1)
                else:
                    print("\nPrimera vez que se analiza este artista. Esto puede tardar varios minutos...")
                    resultados_albums = sp.artist_albums(id_artista, album_type='album', limit=50)
                    albums = resultados_albums['items']
                    
                    lista_completa_de_canciones_spotify = []
                    for album in albums:
                        lista_completa_de_canciones_spotify.extend(sp.album_tracks(album['id'])['items'])

                    with tqdm(total=len(lista_completa_de_canciones_spotify), desc="Procesando Canciones") as pbar:
                        for cancion in lista_completa_de_canciones_spotify:
                            nombre_cancion = cancion['name']
                            
                            letra = "Letra no encontrada."
                            try:
                                api_url = f"https://api.genius.com/search?q={requests.utils.quote(nombre_cancion + ' ' + nombre_real_artista)}"
                                headers = {'Authorization': f'Bearer {genius_token}'}
                                respuesta_genius = requests.get(api_url, headers=headers).json()
                                url_cancion_genius = None
                                for hit in respuesta_genius['response']['hits']:
                                    if hit['result']['primary_artist']['name'].lower() == nombre_real_artista.lower():
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
                            
                            todas_las_canciones_analizadas.append({'nombre': nombre_cancion, 'polaridad': polaridad})
                            pbar.update(1)
                    
                    with open(archivo_cache, 'w') as f:
                        json.dump(todas_las_canciones_analizadas, f, indent=4)
                    print(f"\nAnálisis guardado en caché para futuras búsquedas.")

                print(f"Análisis completo. Se procesaron {len(todas_las_canciones_analizadas)} canciones.")
                time.sleep(1)

                canciones_filtradas = []
                if seleccion_mood == 1:
                    canciones_filtradas = [c for c in todas_las_canciones_analizadas if c['polaridad'] > 0.1]
                    print(f"\n--- CANCIONES POSITIVAS DE {nombre_real_artista.upper()} ---")
                elif seleccion_mood == 2:
                    canciones_filtradas = [c for c in todas_las_canciones_analizadas if c['polaridad'] < -0.1]
                    print(f"\n--- CANCIONES NEGATIVAS DE {nombre_real_artista.upper()} ---")
                elif seleccion_mood == 3:
                    canciones_filtradas = [c for c in todas_las_canciones_analizadas if -0.1 <= c['polaridad'] <= 0.1]
                    print(f"\n--- CANCIONES NEUTRALES DE {nombre_real_artista.upper()} ---")

                if not canciones_filtradas:
                    print("\nNo se encontraron canciones que coincidan con tu criterio.")
                else:
                    for i, cancion in enumerate(canciones_filtradas):
                        print(f"  [{i+1}] {cancion['nombre']} (Polaridad: {cancion['polaridad']:.2f})")
            
            else:
                print("Opción de sentimiento no válida. Debes elegir 1, 2 o 3.")
        else:
            print("Número de artista fuera de rango.")
    except (ValueError, KeyError):
        print("Entrada inválida o error en los datos recibidos.")
