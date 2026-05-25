import os
import itertools
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FFMPEG_PATH = os.path.join(
    BASE_DIR,
    "ffmpeg",
    "bin",
    "ffmpeg.exe"
)