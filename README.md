# Positive Finder ✨

**Aplicación en vivo:** [https://saulbracamonte.pythonanywhere.com/](http://saulbracamonte.pythonanywhere.com/)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Spotify API](https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white)
![Genius API](https://img.shields.io/badge/Genius-yellow?style=for-the-badge&logo=genius&logoColor=black)

Positive Finder es una aplicación web full-stack que descubre el lado más positivo de tus artistas favoritos. La aplicación analiza la discografía completa de cualquier artista y genera una lista de sus canciones más alegres, permitiendo al usuario crear una playlist con ellas directamente en su cuenta de Spotify.

---

## El Viaje del Desarrollo: Un Caso de Estudio Real

Este proyecto fue más que un ejercicio de programación; fue una simulación completa de los desafíos del desarrollo en el mundo real.

La idea inicial era simple: analizar el sentimiento de las letras de todas las canciones de un artista. El desarrollo local fue un éxito, logrando una aplicación funcional que cumplía con todos los requisitos. Sin embargo, el verdadero desafío comenzó durante el despliegue en plataformas gratuitas como Render y PythonAnywhere.

1.  **El Muro del Rendimiento:** El análisis inicial, que requería cientos de peticiones de web scraping a Genius.com para obtener las letras completas, era demasiado lento. Esto provocaba **timeouts** en los servidores de producción (Gunicorn), que están diseñados para peticiones rápidas, no para procesos de análisis de datos de varios minutos.

2.  **El Bloqueo de APIs:** Las peticiones de web scraping que funcionaban desde mi máquina local eran bloqueadas activamente por Genius cuando se originaban desde los centros de datos de los servicios de despliegue. Este es un mecanismo anti-bot común contra el que tuve que ingeniar una solución.

3.  **El Pivote Estratégico:** Enfrentado a estas limitaciones, tomé una decisión de ingeniería clave: sacrifiqué la profundidad del análisis (letras completas) por la **fiabilidad, velocidad y éxito del despliegue**. Refactoricé toda la lógica de análisis para dejar de depender del web scraping y utilizar únicamente la API de Genius. Esta nueva versión analiza el sentimiento basándose en los títulos completos de las canciones, un proceso **10 veces más rápido** y que no es bloqueado por las APIs.

El resultado es una aplicación robusta, rápida y desplegada con éxito, que demuestra mi capacidad para adaptarme a las restricciones técnicas y tomar decisiones de producto para entregar un proyecto funcional.

## Características Principales

*   **Búsqueda de Artistas en Tiempo Real:** Se conecta a la API de Spotify para encontrar cualquier artista.
*   **Análisis de Sentimiento:** Utiliza `TextBlob` para analizar la "positividad" de los títulos de las canciones de toda la discografía de un artista.
*   **Sistema de Caché Inteligente:** La primera vez que se analiza un artista, los resultados se guardan. Las búsquedas posteriores para el mismo artista son **instantáneas**.
*   **Creación de Playlists con Un Clic:** Se integra con la autenticación de usuario de Spotify (`OAuth`) para crear playlists públicas en la cuenta del usuario con las canciones encontradas.
*   **Diseño Moderno y Responsivo:** Interfaz de usuario limpia y atractiva desarrollada con Bootstrap y CSS personalizado.
*   **Desplegada y Siempre Activa:** Alojada en PythonAnywhere y mantenida "despierta" por un monitor de UptimeRobot.

## Stack Tecnológico

*   **Backend:** Python, Flask
*   **APIs Externas:**
    *   Spotify API (autenticación de cliente y de usuario con `OAuth`)
    *   Genius API (para metadatos de canciones)
*   **Análisis de Datos:** TextBlob (para Procesamiento de Lenguaje Natural y análisis de sentimiento)
*   **Frontend:** HTML5, CSS3, Bootstrap 5
*   **Base de Datos / Caché:** Sistema de archivos con JSON.
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
        GENIUS_ACCESS_TOKEN='TU_TOKEN_DE_ACCESO_DE_GENIUS'
        SPOTIPY_REDIRECT_URI='http://127.0.0.1:8888/callback'
        ```
5.  **Actualiza tu Dashboard de Spotify:**
    *   Asegúrate de añadir `http://127.0.0.1:8888/callback` a la lista de Redirect URIs en la configuración de tu aplicación de Spotify.

6.  **Ejecuta la aplicación:**
    ```bash
    python3 main.py
    ```
7.  Abre tu navegador y ve a `http://127.0.0.1:8888`.
