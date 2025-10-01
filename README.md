# El Álbum Esencial 🎵

**Aplicación en vivo:** [http://saulbracamonte.pythonanywhere.com/](http://saulbracamonte.pythonanywhere.com/)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Spotify API](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)

"El Álbum Esencial" es una aplicación web full-stack que resuelve una pregunta para cualquier fan de la música: ¿Por dónde empiezo con un artista nuevo? La aplicación busca un artista en Spotify, identifica su álbum de estudio más representativo (basado en la API de Spotify) y permite al usuario crear una playlist con ese álbum completo en su propia cuenta con un solo clic.

---

## El Viaje del Desarrollo: Un Pivote Estratégico

Este proyecto es un caso de estudio sobre la adaptación y la resolución de problemas en el desarrollo web del mundo real.

La idea original, "Positive Finder", buscaba analizar el sentimiento de **toda** la discografía de un artista. Aunque la aplicación era **100% funcional en mi entorno local**, durante el despliegue en plataformas gratuitas (Render, PythonAnywhere) me enfrenté a dos muros técnicos infranqueables:

1.  **Timeouts de Servidor:** El análisis de cientos de canciones era un proceso demasiado largo para el límite de 30 segundos de los servidores web gratuitos, causando que la aplicación fallara.
2.  **Bloqueo de APIs:** Los servicios de scraping de letras como Genius.com identificaban las peticiones desde los servidores de la nube como bots y las bloqueaban, haciendo imposible obtener los datos necesarios de forma fiable.

En lugar de abandonar el proyecto, tomé una **decisión de ingeniería y de producto**: pivoté hacia una idea que mantuviera el espíritu del proyecto original pero que fuera **técnicamente robusta, eficiente y desplegable.**

Así nació **"El Álbum Esencial"**. Esta nueva versión se enfoca en entregar un resultado de alto valor ("el mejor álbum para empezar") de forma casi instantánea, garantizando una experiencia de usuario perfecta y demostrando mi capacidad para adaptar una solución a las limitaciones del entorno de producción.

## Características Principales

*   **Búsqueda de Artistas en Tiempo Real:** Se conecta a la API de Spotify para encontrar cualquier artista.
*   **Identificación de Álbum Esencial:** Implementa una lógica para determinar el álbum más representativo de un artista.
*   **Creación de Playlists con Un Clic:** Se integra de forma segura con la autenticación de usuario de Spotify (`OAuth`) para crear playlists públicas en la cuenta del usuario.
*   **Diseño Moderno y Responsivo:** Interfaz de usuario limpia y atractiva desarrollada con Bootstrap y CSS personalizado.
*   **Desplegada y Siempre Activa:** Alojada en PythonAnywhere y mantenida "despierta" por un monitor de UptimeRobot.

## Stack Tecnológico

*   **Backend:** Python, Flask
*   **API Externa:** Spotify API (utilizando `Client Credentials` para búsquedas públicas y `OAuth` para acciones de usuario)
*   **Frontend:** HTML5, CSS3, Bootstrap 5
*   **Servidor de Producción:** Gunicorn
*   **Plataforma de Despliegue:** PythonAnywhere
*   **Control de Versiones:** Git y GitHub

## Ejecución Local

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
3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configura tus credenciales:**
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Añade tus credenciales con el siguiente formato:
        ```        SPOTIPY_CLIENT_ID='TU_ID_DE_CLIENTE_DE_SPOTIFY'
        SPOTIPY_CLIENT_SECRET='TU_SECRETO_DE_CLIENTE_DE_SPOTIFY'
        ```
5.  **Actualiza tu Dashboard de Spotify:**
    *   Asegúrate de añadir `http://127.0.0.1:8888/callback` a la lista de Redirect URIs en la configuración de tu aplicación de Spotify.

6.  **Ejecuta la aplicación:**
    ```bash
    python3 main.py
    ```
7.  Abre tu navegador y ve a `http://127.0.0.1:8888`.