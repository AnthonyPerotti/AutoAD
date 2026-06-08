import os
import subprocess

from core.ffmpeg import FFMPEG_PATH

THUMBS_DIR = "assets/thumbs"

os.makedirs(THUMBS_DIR, exist_ok=True)


def gerar_thumbnail(video_path):

    try:

        nome = os.path.splitext(os.path.basename(video_path))[0]

        thumb_path = os.path.join(THUMBS_DIR, f"{nome}.jpg")

        if os.path.exists(thumb_path):

            return thumb_path

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-ss",
            "00:00:00.5",
            "-i",
            video_path,
            "-vf",
            "scale=320:-1",
            "-vframes",
            "1",
            thumb_path,
        ]

        startupinfo = subprocess.STARTUPINFO()

        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        return thumb_path

    except:

        return None
