from flask import Flask, render_template, request, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from spotify_logic import encontrar_album_esencial

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de autenticación para cuando el usuario quiera crear una playlist
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
    # Si no tenemos un token de sesión, mostramos la página de login
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return render_template('login.html', auth_url=auth_url)
    # Si ya estamos logueados, mostramos la página principal
    return render_template('index.html')

@app.route('/callback')
def callback():
    # Spotify nos envía aquí después del login para guardar el token
    auth_manager.get_access_token(request.args.get("code"), as_dict=False)
    return redirect('/')

@app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista_buscado = request.form['artist_name']
    album, canciones, artista_encontrado = encontrar_album_esencial(nombre_artista_buscado)
    
    if not artista_encontrado:
        return f"<h1>No se encontró al artista '{nombre_artista_buscado}'</h1><a href='/'>Volver</a>"

    # Guardamos los datos que necesitaremos para crear la playlist
    session['track_ids_para_playlist'] = [c['id'] for c in canciones if c and c.get('id')]
    session['playlist_name'] = f"Álbum Esencial: {album['name']} de {artista_encontrado['name']}"
    
    return render_template('resultados.html', resultado=album, canciones=canciones, artista=artista_encontrado)

@app.route('/crear_playlist')
def crear_playlist_route():
    # Verificamos que el usuario esté logueado antes de crear
    if not auth_manager.get_cached_token():
        return redirect('/')

    sp_user = spotipy.Spotify(auth_manager=auth_manager)
    
    track_ids = session.get('track_ids_para_playlist', [])
    playlist_name = session.get('playlist_name', 'Mi Álbum Esencial')
    
    if not track_ids:
        return "<h1>Error: No hay canciones para agregar.</h1><a href='/'>Volver</a>"

    user_id = sp_user.current_user()['id']
    playlist = sp_user.user_playlist_create(user=user_id, name=playlist_name, public=True, description="Generada por El Álbum Esencial.")
    
    # Añadimos las canciones en lotes de 100
    for i in range(0, len(track_ids), 100):
        lote = track_ids[i:i+100]
        sp_user.playlist_add_items(playlist['id'], lote)
    
    playlist_url = playlist["external_urls"]["spotify"]
    return render_template('exito.html', playlist_url=playlist_url, nombre_playlist=playlist_name)

if __name__ == '__main__':
    # Usamos el puerto 8888 para que coincida con la redirect_uri local
    os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:8888/callback'
    app.run(debug=True, port=8888)