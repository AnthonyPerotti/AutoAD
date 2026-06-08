# AutoAD Suite v2.0

Modern desktop application suite for automated batch video generation and file management.

AutoAD allows you to dynamically combine Hooks, Bodies and CTAs, generating large-scale video variations automatically through a modern desktop interface optimized for speed, usability and workflow automation. It also includes utility tools like a Bulk File Renamer.

---

## Features

### Content Assembler
* Dynamic body management (multiple folders)
* Batch video rendering combining Hooks, Bodies, and CTAs
* Fixed native naming pattern: `[AD_{num}] {hook}{body_a}{body_b}...{cta}`
* Smart overwrite behavior handling (Ask, Skip, Rename, Overwrite)
* Automatic thumbnail previews
* Real-time render queue and logs
* FFmpeg integration with CPU and GPU encoding support

### Bulk Renamer
* Bulk rename files in any directory
* Live preview of new filenames before applying
* Prefix and Suffix configuration
* Sequential numbering
* Search and Replace functionality

### General
* Modern Sidebar Navigation
* Multilingual support (English, Português)
* Dynamic UI Scaling
* Light and Dark Theme

---

## Supported Encoders (Assembler)

| Encoder | Hardware |
|---|---|
| libx264 | CPU |
| h264_nvenc | NVIDIA GPU |
| h264_amf | AMD GPU |
| h264_qsv | Intel GPU |

---

## Requirements

* Python 3.10+
* FFmpeg (in `tools/` folder)
* CustomTkinter
* Pillow

---

## Installation

Clone repository:

```bash
git clone https://github.com/AnthonyPerotti/AutoAD.git
cd AutoAD
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

## Running

```bash
python app.py
```

---

## Build Executable

Run the following command to generate the standalone executable using PyInstaller:

```bash
pyinstaller --onedir --windowed --name "AutoAD Suite" --icon="assets/icon.ico" --add-data "tools;tools" --add-data "assets;assets" app.py
```

---

## Project Structure

```text
AutoAD/
│
├── app.py
├── requirements.txt
├── README.md
│
├── assets/
│   └── icon.ico
│
├── core/
│   ├── config.py
│   ├── theme.py
│   ├── translations.py
│   └── utils.py
│
├── apps/
│   ├── assembler/     # Content Assembler App
│   ├── renamer/       # Bulk Renamer App
│   └── resizer/       # (Placeholder) Video Resizer App
│
├── ui/
│   └── hub_window.py  # Main navigation and router
│
└── tools/
    └── ffmpeg.exe
```

---

## License

MIT License

---

## Author

Developed by Anthony Perotti