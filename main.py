from flask import Flask, render_template, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from spotify_logic import analizar_discografia, buscar_artistas_en_spotify

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

 @app.route('/')
def index():
    # La página de inicio ahora maneja la autorización
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return render_template('login.html', auth_url=auth_url)
    return render_template('index.html')

 @app.route('/callback')
def callback():
    auth_manager.get_access_token(request.args.get("code"), as_dict=False)
    return redirect('/')

 @app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    lista_artistas = buscar_artistas_en_spotify(nombre_artista)
    return render_template('resultados.html', artistas=lista_artistas, busqueda=nombre_artista)

 @app.route('/artista/<artist_id>/<artist_name>')
def mostrar_positivas(artist_id, artist_name):
    canciones_positivas = analizar_discografia(artist_id, artist_name)
    session['track_ids_para_playlist'] = [c['id'] for c in canciones_positivas if c.get('id')]
    session['artist_name_para_playlist'] = artist_name
    return render_template('playlist.html', 
                            canciones=canciones_positivas, 
                            artist_name=artist_name)

 @app.route('/crear_playlist')
def crear_playlist_route():
    sp_user = spotipy.Spotify(auth_manager=auth_manager)
    
    track_ids = session.get('track_ids_para_playlist', [])
    artist_name = session.get('artist_name_para_playlist', 'Artista Desconocido')
    
    if not track_ids:
        return "Error: No se encontraron canciones en la sesión para crear la playlist."

    user_id = sp_user.current_user()['id']
    nombre_playlist = f"{artist_name} - Canciones Positivas"
    descripcion = f"Canciones positivas de {artist_name} encontradas por Positive Finder."
    playlist = sp_user.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion)
    
    if track_ids:
        for i in range(0, len(track_ids), 100):
            lote = track_ids[i:i+100]
            sp_user.playlist_add_items(playlist['id'], lote)
    
    playlist_url = playlist["external_urls"]["spotify"]
    return render_template('exito.html', playlist_url=playlist_url, nombre_playlist=nombre_playlist)

if __name__ == '__main__':
    # Usamos el puerto 8888 para que coincida con la redirect_uri local
    os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:8888/callback'
    app.run(debug=True, port=8888)