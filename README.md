# Descargador de YouTube

Script de consola para consultar los formatos disponibles de un video de YouTube y descargar la combinacion elegida en la carpeta `descargas/`.

## Requisitos

- macOS, Linux o Windows con Python 3.
- `ffmpeg` instalado y disponible en el `PATH`.
- Node.js, recomendado por `yt-dlp` para resolver los desafios JavaScript actuales de YouTube.
- Una conexion a Internet.

En macOS, instala las dependencias del sistema con Homebrew:

```bash
brew install python ffmpeg node
```

## Instalacion

Desde la carpeta del proyecto:

```bash
make install
```

Comprueba que `ffmpeg` esta disponible:

```bash
make check-ffmpeg
```

## Uso

La forma recomendada es:

```bash
make run
```

Tambien puedes ejecutar el script directamente:

```bash
.venv/bin/python Import-YT.py
```

El programa solicitara la URL del video y mostrara los formatos de video ordenados por:

1. Mayor resolucion.
2. Mayor FPS.
3. Mayor bitrate.

A continuacion, selecciona el `ID de video` que quieras descargar.

- Si el formato elegido es `video+audio`, por ejemplo `95` o `18`, se descargara directamente.
- Si el formato elegido es solo `video`, el programa mostrara una segunda tabla con los formatos de audio disponibles y solicitara un `ID de audio`, por ejemplo `140`.
- La descarga de formatos separados se realiza con una expresion como `136+140` y `ffmpeg` los combina en un archivo MP4.
- Escribe `q` en cualquier pregunta para cancelar.

Ejemplo de seleccion:

```text
ID de video (o 'q' para cancelar): 136

Formatos de audio disponibles:
  ID | Tipo | Resolucion | FPS | Extension | Video | Audio | Bitrate | Tamano
  140 | audio | N/AxN/A | N/A | m4a | none | mp4a.40.2 | 129.474 | 4.8 MiB

ID de audio (o 'q' para cancelar): 140
```

Los archivos descargados se guardan en:

```text
descargas/
```

## Cookies del navegador

Para videos publicos no son necesarias las cookies. El script solo intenta leer cookies de Chrome si encuentra una base de cookies existente en macOS.

Si un video requiere iniciar sesion, revisa que Chrome tenga un perfil con la sesion activa. No compartas ni subas la base de cookies, porque contiene informacion sensible.

## Errores frecuentes

### `ffmpeg no esta instalado`

Instala `ffmpeg` y vuelve a ejecutar:

```bash
brew install ffmpeg
make check-ffmpeg
```

### `HTTP Error 403: Forbidden`

Actualiza `yt-dlp` y comprueba que Node.js este instalado:

```bash
.venv/bin/pip install --upgrade yt-dlp
node --version
```

El script vuelve a extraer la informacion antes de descargar, usa reintentos y divide las descargas grandes en bloques. Aun asi, YouTube puede rechazar temporalmente una URL, limitar una cuenta o exigir autenticacion.

Si el primer intento recibe un `403`, el programa vuelve a extraer las URLs y reintenta el formato elegido. Si vuelve a fallar, prueba un fallback MP4/M4A de hasta 1080p. Los errores se guardan en `descargas.log` para poder revisar el formato y el tipo de excepcion sin guardar cookies ni URLs firmadas.

Los archivos `.part` se conservan cuando una descarga falla. Esto permite que `yt-dlp` intente reanudarla en una ejecucion posterior.

### `El ID no existe o no es un formato de video/audio`

Copia el ID exactamente como aparece en la tabla correspondiente. Un ID de audio no puede usarse como video, y viceversa.

## Estructura del proyecto

```text
.
├── Import-YT.py       # Programa principal
├── Makefile           # Comandos de instalacion y ejecucion
├── requirements.txt   # Dependencia de Python
└── descargas/         # Destino de los archivos descargados
```

## Limpieza del entorno virtual

Para borrar el entorno virtual creado por el proyecto:

```bash
make clean
```
