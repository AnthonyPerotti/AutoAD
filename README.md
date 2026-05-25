# AutoAdd

Modern desktop application for automated batch video generation using FFmpeg.

AutoAdd allows you to combine Hooks, Bodies and CTAs dynamically, generating hundreds of video variations automatically through a modern desktop interface.

---

# Features

* Modern desktop UI
* Automatic thumbnail previews
* Dynamic body management
* Batch video rendering
* GPU encoder support

  * NVIDIA NVENC
  * AMD AMF
  * Intel QSV
  * CPU x264
* Real-time progress tracking
* Instant render stop
* Scrollable responsive interface
* FFmpeg integration
* Multiple hooks, bodies and CTAs
* Automatic combination calculation
* Render logging system

---

# Requirements

* Python 3.14+
* FFmpeg
* CustomTkinter
* Pillow

---

# Installation

```bash
git clone https://github.com/yourusername/AutoAdd.git
cd AutoAdd
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running

```bash
python app.py
```

---

# Build Executable

```bash
pyinstaller --onedir --windowed --name AutoAdd --icon=icon.ico --add-data "ffmpeg.exe;." app.py
```

---

# AutoAdd v2.0

Major update including:

* Complete UI redesign
* Thumbnail preview system
* GPU encoder support
* Instant stop rendering
* Dynamic body system
* Better FFmpeg integration
* Scrollable modern interface
* Improved render pipeline
* Professional workflow improvements

---

# Project Structure

```text
AutoAdd/
├── app.py
├── ui.py
├── ffmpeg.exe
├── icon.ico
├── thumbs/
├── dist/
└── README.md
```

---

# Supported Encoders

| Encoder    | Hardware   |
| ---------- | ---------- |
| libx264    | CPU        |
| h264_nvenc | NVIDIA GPU |
| h264_amf   | AMD GPU    |
| h264_qsv   | Intel GPU  |

---

# Notes

* FFmpeg must be available in the project folder.
* GPU encoding depends on compatible hardware/drivers.
* `--onedir` builds are recommended for stability.

---

# License

MIT License

---

# Author

Developed by Anthony Perotti
