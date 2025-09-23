from flask import Flask, render_template, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from spotify_logic import analizar_discografia

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24) # Necesario para guardar datos en la sesión

# --- CONFIGURACIÓN PARA LA FASE 2 (Crear Playlist) ---
# Este objeto solo se usará cuando el usuario quiera iniciar sesión.
# Lee el redirect_uri desde las variables de entorno, lo que lo hace flexible.
scope = "playlist-modify-public"
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
)

# --- RUTAS DE LA APLICACIÓN ---

 @app.route('/')
def index():
    return render_template('index.html')

 @app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    # La lógica de búsqueda y análisis está en spotify_logic.py
    # y usa su propia autenticación simple para ser rápida y pública.
    return redirect(f"/artista/{nombre_artista}")

 @app.route('/artista/<artist_name>')
def mostrar_resultados(artist_name):
    # Primero buscamos al artista para obtener su ID y nombre correctos
    sp_public = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
    ))
    resultados = sp_public.search(q='artist:' + artist_name, type='artist', limit=10)['artists']['items']
    
    if not resultados:
        return f"<h1>No se encontró al artista '{artist_name}'</h1><a href='/'>Volver</a>"

    # En una app más compleja, mostraríamos la lista para elegir.
    # Aquí, tomamos el primer resultado, el más relevante.
    artista_elegido = resultados[0]
    artist_id = artista_elegido['id']
    nombre_real_artista = artista_elegido['name']

    # Hacemos el análisis, que es rápido porque no hace scraping
    canciones_positivas = analizar_discografia(artist_id, nombre_real_artista)
    
    # Guardamos los datos necesarios en la sesión para después de la autenticación
    session['track_ids_para_playlist'] = [c['id'] for c in canciones_positivas if c.get('id')]
    session['artist_name_para_playlist'] = nombre_real_artista
    
    return render_template('playlist.html', 
                            canciones=canciones_positivas, 
                            artist_name=nombre_real_artista)

 @app.route('/crear_playlist_login')
def crear_playlist_login():
    # Paso 1 para crear la playlist: redirigir al usuario a Spotify para que dé permiso
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

 @app.route('/callback')
def callback():
    # Paso 2: Spotify nos devuelve aquí después de que el usuario acepta
    auth_manager.get_access_token(request.args.get("code"), as_dict=False)
    # Paso 3: Ahora que tenemos el permiso, redirigimos a la creación final
    return redirect('/crear_playlist_final')

 @app.route('/crear_playlist_final')
def crear_playlist_final():
    # Paso 4: Usamos el token que acabamos de obtener para actuar en nombre del usuario
    sp_user = spotipy.Spotify(auth_manager=auth_manager)
    
    track_ids = session.get('track_ids_para_playlist', [])
    artist_name = session.get('artist_name_para_playlist', 'Artista Desconocido')
    
    if not track_ids:
        return "Error: No se encontraron canciones en la sesión. Por favor, empieza de nuevo."

    user_id = sp_user.current_user()['id']
    nombre_playlist = f"{artist_name} - Canciones Positivas"
    descripcion = f"Canciones positivas de {artist_name} encontradas por Positive Finder."
    playlist = sp_user.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion)
    
    # Añadimos las canciones en lotes de 100
    for i in range(0, len(track_ids), 100):
        lote = track_ids[i:i+100]
        sp_user.playlist_add_items(playlist['id'], lote)
    
    playlist_url = playlist["external_urls"]["spotify"]
    return f'<h1>¡Playlist creada!</h1><p><a href="{playlist_url}" target="_blank">Ver en Spotify</a></p><a href="/">Crear otra</a>'

if __name__ == '__main__':
    app.run(debug=True)