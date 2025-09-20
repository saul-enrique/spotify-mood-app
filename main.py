from flask import Flask, render_template, request, redirect, url_for
from spotify_logic import buscar_artistas, analizar_discografia
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24) 

# --- AUTENTICACIÓN CON PERMISOS DE USUARIO ---
scope = "playlist-modify-public"
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:5000/callback", # Ruta que Spotify usará para devolvernos el control
    scope=scope,
    cache_path=".cache" # Guardamos el token en un archivo .cache
)

@app.route('/')
def index():
    # Verificamos si ya tenemos un token, si no, vamos a autorizar
    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return f'<h2>Necesitamos tu permiso para crear playlists</h2><a href="{auth_url}">Autorizar con Spotify</a>'
    
    return render_template('index.html')

@app.route('/callback')
def callback():
    # Esta ruta la llama Spotify después de la autorización
    auth_manager.get_access_token(request.args.get("code"))
    return redirect('/')

# --- El resto de las rutas ---
@app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    
    sp = spotipy.Spotify(auth_manager=auth_manager)
    lista_artistas = sp.search(q='artist:' + nombre_artista, type='artist', limit=10)['artists']['items']

    return render_template('resultados.html', artistas=lista_artistas, busqueda=nombre_artista)

@app.route('/artista/<artist_id>/<artist_name>')
def mostrar_positivas(artist_id, artist_name):
    # La función de lógica ahora nos devuelve dos listas
    todas_las_canciones, canciones_positivas = analizar_discografia(artist_id, artist_name)
    
    return render_template('playlist.html', 
                            todas_las_canciones=todas_las_canciones, # <-- NUEVO
                            canciones_filtradas=canciones_positivas, # <-- Cambiado de nombre
                            artist_name=artist_name,
                            artist_id=artist_id)

@app.route('/crear_playlist', methods=['POST'])
def crear_playlist_route():
    artist_name = request.form['artist_name']
    track_ids_str = request.form.get('track_ids', '') # Usamos .get para evitar errores si no llega

    if not track_ids_str:
        return "No se seleccionaron canciones para la playlist."

    track_ids = track_ids_str.split(',')

    # Obtenemos el cliente de spotify con la autenticación del usuario
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp.current_user()['id']

    # Creamos la playlist
    nombre_playlist = f"{artist_name} - Canciones Positivas"
    descripcion_playlist = f"Una selección de las canciones más positivas de {artist_name}, generada por Mood Selector."
    playlist = sp.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion_playlist)
    
    # Añadimos las canciones
    sp.playlist_add_items(playlist['id'], track_ids)
    
    return f"""
        <h1>¡Playlist creada con éxito!</h1>
        <p>Puedes verla aquí: <a href="{playlist['external_urls']['spotify']}" target="_blank">{nombre_playlist}</a></p>
        <a href="/">Crear otra</a>
    """

if __name__ == '__main__':
    app.run(debug=True)