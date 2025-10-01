# El Álbum Esencial 🎵

**Aplicación en vivo:** [http://saulbracamonte.pythonanywhere.com/](http://saulbracamonte.pythonanywhere.com/)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Spotify API](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)

---

## 🚀 Resumen del Proyecto

"El Álbum Esencial" es una aplicación web full-stack que resuelve una pregunta común para cualquier fan de la música: **¿Por dónde empiezo con un artista nuevo?** La aplicación busca un artista en Spotify, identifica su álbum de estudio más representativo y permite al usuario guardar ese álbum como una nueva playlist en su propia cuenta de Spotify con un solo clic.

Este proyecto demuestra la creación de una aplicación web completa, desde la concepción y el diseño de la interfaz hasta la integración con APIs externas y el despliegue en un servidor de producción.

---

## 💡 El Viaje del Desarrollo: Un Pivote Estratégico

Este proyecto es un caso de estudio sobre la **adaptación y la resolución de problemas** en el desarrollo de software.

La idea original, "Positive Finder", buscaba analizar el sentimiento de **toda** la discografía de un artista para encontrar sus canciones más positivas. Aunque la aplicación era **100% funcional en mi entorno local**, durante el despliegue me enfrenté a dos muros técnicos infranqueables en las plataformas de hosting gratuito:

1.  **Timeouts de Servidor:** El análisis de cientos de canciones era un proceso demasiado largo para el límite de 30 segundos de los servidores, causando que la aplicación fallara.
2.  **Bloqueo de APIs:** Los servicios de scraping de letras como Genius.com identificaban las peticiones desde los servidores en la nube como bots y las bloqueaban.

> En lugar de abandonar el proyecto, tomé una **decisión de ingeniería y de producto**: pivoté hacia una idea que mantuviera el espíritu del proyecto original pero que fuera **técnicamente robusta, eficiente y desplegable.**

Así nació **"El Álbum Esencial"**. Esta nueva versión se enfoca en entregar un resultado de alto valor ("el mejor álbum para empezar") de forma casi instantánea, garantizando una experiencia de usuario fluida y demostrando mi capacidad para adaptar una solución a las limitaciones del entorno de producción del mundo real.

---

## ✨ Características Principales

*   **Búsqueda de Artistas en Tiempo Real:** Se conecta a la API de Spotify para encontrar cualquier artista.
*   **Identificación de Álbum Esencial:** Implementa una lógica para determinar el álbum más representativo de un artista (actualmente, el más reciente o popular).
*   **Creación de Playlists con Un Clic:** Se integra de forma segura con la autenticación de usuario de Spotify (`OAuth 2.0`) para crear playlists en la cuenta del usuario.
*   **Diseño Moderno y Responsivo:** Interfaz de usuario limpia y atractiva desarrollada con Bootstrap y CSS personalizado para una experiencia óptima en cualquier dispositivo.
*   **Desplegada y Siempre Activa:** Alojada en PythonAnywhere y mantenida "despierta" por un monitor de UptimeRobot.

---

## 🛠️ Stack Tecnológico

| Área | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Lógica del servidor, enrutamiento y manejo de peticiones. |
| **API Externa** | Spotify API | Búsqueda de artistas, obtención de álbumes y creación de playlists. |
| **Autenticación** | OAuth 2.0 | Autenticación segura para que los usuarios puedan crear playlists. |
| **Frontend** | HTML5, CSS3, Bootstrap 5 | Estructura, estilo y diseño responsivo de la interfaz de usuario. |
| **Servidor** | Gunicorn | Servidor WSGI para producción. |
| **Despliegue** | PythonAnywhere | Plataforma de hosting para la aplicación en vivo. |
| **Control de Versiones** | Git, GitHub | Gestión del código fuente y colaboración. |

> **Nota:** El `requirements.txt` puede contener librerías como `lyricsgenius`, `nltk` y `textblob`, que fueron parte de la idea original del proyecto ("Positive Finder") y no se utilizan en la versión actual. Se han conservado para documentar el pivote técnico del proyecto.

---

## 📂 Estructura del Proyecto

```
/
├─── main.py                # Punto de entrada de la aplicación Flask y definición de rutas.
├─── spotify_logic.py       # Lógica de negocio para interactuar con la API de Spotify.
├─── requirements.txt       # Dependencias del proyecto.
├─── Procfile               # Configuración para el servidor Gunicorn (usado por Heroku/similares).
├─── templates/             # Archivos HTML con la estructura de las páginas.
│    ├─── index.html        # Página principal de búsqueda.
│    ├─── resultados.html   # Página para mostrar los resultados de búsqueda de artistas.
│    └─── playlist.html     # Página para mostrar el álbum esencial y sus canciones.
└─── static/                # Archivos estáticos.
     └─── style.css         # Estilos CSS personalizados.
```

---

## 🚀 Cómo Ejecutar el Proyecto Localmente

Para ejecutar este proyecto en tu propia máquina, sigue estos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/saul-enrique/spotify-mood-app.git
    cd spotify-mood-app
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *En Windows, usa `venv\Scripts\activate`*

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tus credenciales de Spotify:**
    *   Ve al [Dashboard de Desarrolladores de Spotify](https://developer.spotify.com/dashboard/) y crea una nueva aplicación.
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Añade tus credenciales con el siguiente formato:
        ```
        SPOTIPY_CLIENT_ID='TU_ID_DE_CLIENTE_DE_SPOTIFY'
        SPOTIPY_CLIENT_SECRET='TU_SECRETO_DE_CLIENTE_DE_SPOTIFY'
        ```

5.  **Configura el Redirect URI en Spotify:**
    *   En la configuración de tu aplicación en el Dashboard de Spotify, añade la siguiente URL a la lista de "Redirect URIs":
        ```
        http://127.0.0.1:5000/callback
        ```
        *Nota: Usaremos el puerto 5000, que es el puerto por defecto de Flask.*

6.  **Ejecuta la aplicación:**
    ```bash
    flask run
    ```
    *Opcionalmente, puedes usar `python3 main.py` si prefieres ejecutarlo en modo de depuración.*

7.  **Abre tu navegador** y ve a `http://127.0.0.1:5000`.

---
