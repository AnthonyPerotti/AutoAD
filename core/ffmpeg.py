import os
import sys


def get_ffmpeg_path():

    if getattr(sys, "frozen", False):

        base_path = sys._MEIPASS

    else:

        base_path = os.path.dirname(os.path.dirname(__file__))

    return os.path.join(base_path, "ffmpeg.exe")


FFMPEG_PATH = get_ffmpeg_path()
