import os, shutil, yt_dlp
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


def list_available_formats(info_dict):
    formats = info_dict.get("formats") or []
    if not formats:
        print("No se encontraron formatos descargables.")
        return

    sorted_formats = sorted(
        (
            fmt for fmt in formats
            if fmt.get("vcodec") not in (None, "none")
            or fmt.get("acodec") not in (None, "none")
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

url = input("Introduce la URL del video de YT: ").strip()

if not url:
    print("No se introdujo ninguna URL.")
    raise SystemExit(0)

try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    browser = None
    if shutil.which("google-chrome") or shutil.which("chrome"):
        browser = "chrome"

    ydl_opts = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "js_runtimes": {"node": {}},
        "extractor_args": {"youtube": {"player_client": ["web", "android"]}},
    }

    if browser:
        ydl_opts["cookiesfrombrowser"] = (browser,)

    print("\nSeleccionando la mejor calidad disponible...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        list_available_formats(info_dict)
        best_video = get_best_video_format(info_dict)
        if best_video:
            print(
                f"\nDescargando en calidad: "
                f"{best_video.get('height', 'unknown')}p @ {best_video.get('fps', 'unknown')}fps"
            )
        else:
            print("\nNo se encontraron formatos de video con resolución disponible.")
        ydl.download([url])

    print("Descarga completada!")

except Exception as e:
    print(f"Ha ocurrido un error durante la descarga: {e}")