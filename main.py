from flask import Flask, render_template, request, redirect
from spotify_logic import analizar_discografia
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

scope = "playlist-modify-public"
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope,
    cache_path=".cache"
)
sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=20)

@app.route('/')
def index():
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)
    return render_template('index.html')

@app.route('/callback')
def callback():
    auth_manager.get_access_token(request.args.get("code"))
    return redirect('/')

@app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    lista_artistas = sp.search(q='artist:' + nombre_artista, type='artist', limit=10)['artists']['items']
    return render_template('resultados.html', artistas=lista_artistas, busqueda=nombre_artista)

@app.route('/artista/<artist_id>/<artist_name>')
def mostrar_positivas(artist_id, artist_name):
    canciones_positivas = analizar_discografia(artist_id, artist_name)
    return render_template('playlist.html', 
                            canciones=canciones_positivas, 
                            artist_name=artist_name)

@app.route('/crear_playlist', methods=['POST'])
def crear_playlist_route():
    artist_name = request.form['artist_name']
    track_ids_str = request.form.get('track_ids', '')
    
    if not track_ids_str:
        return "No se seleccionaron canciones."

    track_ids = track_ids_str.split(',')
    user_id = sp.current_user()['id']
    
    nombre_playlist = f"{artist_name} - Canciones Positivas"
    descripcion = f"Canciones positivas de {artist_name} encontradas por Mood Selector."
    playlist = sp.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion)
    
    sp.playlist_add_items(playlist['id'], track_ids)
    
    return f'<h1>¡Playlist creada!</h1><p><a href="{playlist["external_urls"]["spotify"]}" target="_blank">Ver en Spotify</a></p><a href="/">Crear otra</a>'

if __name__ == '__main__':
    app.run(debug=True)
