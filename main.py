from flask import Flask, render_template, request
from spotify_logic import encontrar_album_esencial, buscar_artistas_en_spotify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    nombre_artista = request.form['artist_name']
    
    # Primero buscamos para obtener la lista de artistas
    lista_artistas = buscar_artistas_en_spotify(nombre_artista)
    
    if not lista_artistas:
        return f"<h1>No se encontró al artista '{nombre_artista}'</h1><a href='/'>Volver</a>"
        
    return render_template('resultados.html', artistas=lista_artistas, busqueda=nombre_artista)

@app.route('/album_esencial/<artist_id>/<artist_name>')
def mostrar_album(artist_id, artist_name):
    # Ahora que tenemos el ID, encontramos su álbum esencial
    album, canciones = encontrar_album_esencial(artist_id)
    
    if not album:
        return f"<h1>No se pudo encontrar un álbum esencial para {artist_name}</h1><a href='/'>Volver</a>"
    
    return render_template('playlist.html', album=album, canciones=canciones, artista_name=artist_name)

if __name__ == '__main__':
    app.run(debug=True)
