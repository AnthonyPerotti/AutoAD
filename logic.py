import os
import sys

# ============================================
# BASE DIR
# ============================================

if getattr(sys, "frozen", False):

    BASE_DIR = os.path.dirname(
        sys.executable
    )

else:

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

# ============================================
# FFMPEG
# ============================================

FFMPEG_PATH = os.path.join(
    BASE_DIR,
    "ffmpeg.exe"
)