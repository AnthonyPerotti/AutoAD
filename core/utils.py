import os
import sys
from tkinter import filedialog

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def open_folder(path):
    if not path: return
    try:
        os.startfile(path)
    except Exception as e:
        print(f"Error opening folder: {e}")

def select_directory():
    return filedialog.askdirectory()

def count_videos(path):
    if not path or not os.path.exists(path):
        return 0
    return len([f for f in os.listdir(path) if f.lower().endswith(".mp4")])

def format_name(text):
    return text.strip() if text else ""
