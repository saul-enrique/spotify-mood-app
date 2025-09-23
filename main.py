from flask import Flask, render_template, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from spotify_logic import analizar_discografia

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

scope = "playlist-modify-public"
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    cache_handler=spotipy.cache_handler.FlaskSessionCacheHandler(session)
)
sp_public = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

 @app.route('/')
def index():
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)
    return render_template('index.html')

 @app.route('/callback')
def callback():
    auth_manager.get_access_token(request.args.get("code"), as_dict=False)
    return redirect('/')

 @app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    return redirect(f"/artista/{nombre_artista}")

 @app.route('/artista/<artist_name>')
def mostrar_resultados(artist_name):
    resultados = sp_public.search(q='artist:' + artist_name, type='artist', limit=10)['artists']['items']
    if not resultados:
        return f"<h1>No se encontró al artista '{artist_name}'</h1><a href='/'>Volver</a>"
    
    artista_elegido = resultados[0]
    artist_id = artista_elegido['id']
    nombre_real_artista = artista_elegido['name']

    canciones_positivas = analizar_discografia(artist_id, nombre_real_artista)
    
    session['track_ids_para_playlist'] = [c['id'] for c in canciones_positivas if c.get('id')]
    session['artist_name_para_playlist'] = nombre_real_artista
    
    return render_template('playlist.html', 
                            canciones=canciones_positivas, 
                            artist_name=nombre_real_artista)

 @app.route('/crear_playlist_login')
def crear_playlist_login():
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

 @app.route('/crear_playlist_final')
def crear_playlist_final():
    sp_user = spotipy.Spotify(auth_manager=auth_manager)
    
    track_ids = session.get('track_ids_para_playlist', [])
    artist_name = session.get('artist_name_para_playlist', 'Artista Desconocido')
    
    if not track_ids:
        return "Error: No se encontraron canciones en la sesión."

    user_id = sp_user.current_user()['id']
    nombre_playlist = f"{artist_name} - Canciones Positivas"
    descripcion = f"Canciones positivas de {artist_name} encontradas por Positive Finder."
    playlist = sp_user.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion)
    
    if track_ids:
        for i in range(0, len(track_ids), 100):
            lote = track_ids[i:i+100]
            sp_user.playlist_add_items(playlist['id'], lote)
    
    playlist_url = playlist["external_urls"]["spotify"]
    return f'<h1>¡Playlist creada!</h1><p><a href="{playlist_url}" target="_blank">Ver en Spotify</a></p><a href="/">Crear otra</a>'

if __name__ == '__main__':
    app.run(debug=True, port=8888)