import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob # <--- NUEVA IMPORTACIÓN

# (La función obtener_letra sigue igual, no la hemos cambiado)
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

# --- El resto del programa ---
load_dotenv()
# (La configuración de Spotify y Genius sigue igual)
sp_auth_manager = SpotifyClientCredentials(client_id=os.getenv("SPOTIPY_CLIENT_ID"), client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"))
sp = spotipy.Spotify(auth_manager=sp_auth_manager)
genius_token = os.getenv("GENIUS_ACCESS_TOKEN")

nombre_artista = input("Escribe el nombre de un artista o banda: ")
# (El código de búsqueda y selección de artista sigue igual)
# ...

# --- HEMOS MODIFICADO EL BUCLE PRINCIPAL ---
# (Voy a omitir el código repetido de la selección de artista para ser más breve)

# --- INICIO DEL CÓDIGO COMPLETO (para que copies y pegues sin problemas) ---
resultados = sp.search(q='artist:' + nombre_artista, type='artist', limit=10)
items = resultados['artists']['items']

if not items:
    print(f"No se encontraron artistas con el nombre '{nombre_artista}'.")
else:
    print("Se encontraron los siguientes artistas:")
    for i, artista_item in enumerate(items):
        print(f"  [{i + 1}] {artista_item['name']}")

    try:
        seleccion = int(input("nEscribe el número del artista correcto: "))
        if 1 <= seleccion <= len(items):
            artista_elegido = items[seleccion - 1]
            id_artista = artista_elegido['id']
            nombre_real_artista = artista_elegido['name']

            print(f"nHas elegido a: {nombre_real_artista}")
            print("Obteniendo discografía completa...")
            resultados_albums = sp.artist_albums(id_artista, album_type='album', limit=50)
            albums = resultados_albums['items']

            if not albums:
                print(f"No se encontraron álbumes para {nombre_real_artista}.")
            else:
                todas_las_canciones = []
                print("Recopilando, buscando letras y analizando sentimientos (esto puede tardar)...")

                for album in albums:
                    resultados_canciones = sp.album_tracks(album['id'])
                    canciones_album = resultados_canciones['items']

                    for cancion in canciones_album:
                        nombre_cancion = cancion['name']
                        print(f"n-> Procesando: '{nombre_cancion}'")
                        
                        # (La búsqueda de letra sigue igual)
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
                        except Exception as e:
                            letra = f"Error al buscar en la API de Genius: {e}"

                        # --- NUEVO BLOQUE DE ANÁLISIS DE SENTIMIENTO ---
                        polaridad = 0.0 # Valor por defecto si no hay letra
                        if "Letra no encontrada" not in letra and "Error" not in letra:
                            analisis = TextBlob(letra)
                            polaridad = analisis.sentiment.polarity
                        
                        print(f"   ...Análisis de sentimiento (Polaridad): {polaridad:.2f}")

                        todas_las_canciones.append({
                            'nombre': nombre_cancion,
                            'letra': letra,
                            'polaridad': polaridad # <-- GUARDAMOS EL PUNTAJE
                        })
                        
                        if len(todas_las_canciones) >= 5:
                            break
                    if len(todas_las_canciones) >= 5:
                        break

                print("n" + "=" * 40)
                print("¡Análisis de prueba finalizado!")
                print("=" * 40)
                
                for cancion_encontrada in todas_las_canciones:
                    # Mostramos el resultado con su puntaje
                    print(f"nCanción: {cancion_encontrada['nombre']} (Polaridad: {cancion_encontrada['polaridad']:.2f})")
                    print(f"Letra: {cancion_encontrada['letra'][:100]}...")

        else:
            print("Número fuera de rango.")
    except (ValueError, KeyError):
        print("Entrada inválida o error en los datos recibidos.")