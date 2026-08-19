import glob
import os
import shutil

import yt_dlp
OUTPUT_DIR = os.path.join(os.getcwd(), "descargas")

def get_best_video_format(info_dict):
    formats = info_dict.get("formats") or []
    video_formats = [
        fmt for fmt in formats
        if fmt.get("vcodec") != "none" and fmt.get("height") is not None
    ]

    return None if not video_formats else max(
        video_formats, key=lambda fmt: (
            fmt.get("height", 0), fmt.get("fps", 0), fmt.get("tbr", 0),
            1 if fmt.get("vcodec") == "avc1" else 0,
        ),
    )

def format_size(fmt):
    size = fmt.get("filesize") or fmt.get("filesize_approx")
    if not size:
        return "N/A"
    return f"{size / 1024 / 1024:.1f} MiB"


def is_mp4_compatible(fmt):
    return fmt.get("ext") == "mp4" or (
        fmt.get("ext") == "m4a"
        and fmt.get("vcodec") in (None, "none")
    )


def list_available_formats(info_dict):
    formats = info_dict.get("formats") or []
    if not formats:
        print("No se encontraron formatos descargables.")
        return []

    sorted_formats = sorted(
        (
            fmt for fmt in formats
            if (
                fmt.get("vcodec") not in (None, "none")
                or fmt.get("acodec") not in (None, "none")
            )
        ),
        key=lambda fmt: (
            fmt.get("height") or 0,
            fmt.get("fps") or 0,
            fmt.get("tbr") or 0,
            fmt.get("acodec") != "none",
            fmt.get("format_id", ""),
        ),
        reverse=True,
    )

    print("\nTodos los formatos disponibles:")
    print("  ID | Tipo | Resolucion | FPS | Extension | Video | Audio | Bitrate | Tamano")
    for fmt in sorted_formats:
        has_video = fmt.get("vcodec") not in (None, "none")
        has_audio = fmt.get("acodec") not in (None, "none")
        if has_video and has_audio:
            format_type = "video+audio"
        elif has_video:
            format_type = "video"
        elif has_audio:
            format_type = "audio"
        else:
            format_type = "otro"

        resolution = f"{fmt.get('width') or 'N/A'}x{fmt.get('height') or 'N/A'}"
        fps = fmt.get("fps") or "N/A"
        extension = fmt.get("ext") or "N/A"
        video_codec = fmt.get("vcodec") or "N/A"
        audio_codec = fmt.get("acodec") or "N/A"
        bitrate = fmt.get("tbr") or "N/A"
        print(
            f"  {fmt.get('format_id', 'N/A')} | {format_type:11} | "
            f"{resolution:11} | {str(fps):>3} | "
            f"{extension:9} | {video_codec:18} | "
            f"{audio_codec:15} | {str(bitrate):>7} | "
            f"{format_size(fmt)}"
        )

    return sorted_formats


def select_video_and_audio(formats):
    formats_by_id = {
        str(fmt.get("format_id")): fmt
        for fmt in formats
    }
    video_formats = {
        format_id: fmt
        for format_id, fmt in formats_by_id.items()
        if fmt.get("vcodec") not in (None, "none")
        and fmt.get("height") is not None
    }
    audio_formats = {
        str(fmt.get("format_id")): fmt
        for fmt in formats
        if fmt.get("acodec") not in (None, "none")
        and fmt.get("vcodec") in (None, "none")
    }

    if not video_formats:
        raise ValueError("No hay formatos de video disponibles.")

    print("\nSelecciona un formato de video.")
    video_id = input("ID de video (o 'q' para cancelar): ").strip()
    if video_id.lower() == "q":
        raise SystemExit("Descarga cancelada.")
    if video_id not in formats_by_id or video_id not in video_formats:
        raise ValueError(f"El ID de video '{video_id}' no existe o no es un formato de video.")

    if formats_by_id[video_id].get("acodec") not in (None, "none"):
        return video_id, None

    if not audio_formats:
        raise ValueError("El formato elegido no tiene audio y no hay audios disponibles.")

    audio_id = input("ID de audio (o 'q' para cancelar): ").strip()
    if audio_id.lower() == "q":
        raise SystemExit("Descarga cancelada.")
    if audio_id not in audio_formats:
        raise ValueError(f"El ID de audio '{audio_id}' no existe o no es un formato de audio.")

    return video_id, audio_id

url = input("Introduce la URL del video de YT: ").strip()

if not url:
    print("No se introdujo ninguna URL.")
    raise SystemExit(0)

try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    chrome_data_dir = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome"
    )
    chrome_cookie_databases = glob.glob(
        os.path.join(chrome_data_dir, "*", "Cookies")
    )
    browser = None
    if (shutil.which("google-chrome") or shutil.which("chrome")) and chrome_cookie_databases:
        browser = "chrome"
    elif chrome_cookie_databases:
        browser = "chrome"

    ydl_opts = {
        "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "js_runtimes": {"node": {}},
        "retries": 10,
        "fragment_retries": 10,
        "http_chunk_size": 10 * 1024 * 1024,
    }

    if browser:
        ydl_opts["cookiesfrombrowser"] = (browser,)

    print("\nSelecciona la calidad que quieres descargar...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = list_available_formats(info_dict)

    video_id, audio_id = select_video_and_audio(formats)
    selected_format = video_id if audio_id is None else f"{video_id}+{audio_id}"
    print(f"\nDescargando los formatos seleccionados: {selected_format}")

    ydl_opts.update({
        "format": selected_format,
        "merge_output_format": "mp4",
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("Descarga completada!")

except Exception as e:
    print(f"Ha ocurrido un error durante la descarga: {e}")