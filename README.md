# AutoAD Suite v2.2

Modern desktop application suite for automated batch video generation, conversions, transcriptions, and file management.

AutoAD is a modular ecosystem containing powerful applications like the **Content Assembler** (dynamic video combinations of Hooks, Bodies and CTAs), **Video Converter** (batch resizer and watermarker), **Audio Toolkit** (peak normalization, extraction, silence cutting), **Batch Transcriber** (faster-whisper local audio/video transcribing), and a **Bulk Renamer**, all managed within a single beautiful interface optimized for speed and workflow automation.

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

### Video Converter
* Batch resize and crop videos (e.g. 9:16 TikTok/Reels, 16:9 YouTube, 1:1, 4:5)
* Configure custom Bitrate, FPS, and Resolutions
* Apply image or text Watermarks on the same export
* Smart background modes (Blur Background, Solid Color, Stretch)

### Audio Toolkit
* Peak Normalization (dB) using FFmpeg true peak `loudnorm`
* Cut silence automatically
* Batch extract videos to MP3

### Batch Transcriber
* Local speech-to-text batch transcription using `faster-whisper`
* Dynamic 3-layer hardware detection (CUDA int8_float16, CUDA float32 fallback for older Maxwell GPUs, or CPU int8)
* Manual device and compute type settings override
* Aggregate outputs into a single `.txt` file to prevent token limit issues (e.g. NotebookLM)

### Bulk Renamer
* Bulk rename files in any directory
* Live preview of new filenames before applying
* Prefix and Suffix configuration (including Hybrid Sequential numbering)
* Search and Replace functionality

### General
* Modern Sidebar Navigation & unified Dashboard
* Multilingual support (English, Português)
* Dynamic UI Scaling
* Light and Dark Theme
* Unified completion popup notification (with Quick Open folder access)

---

## Supported Encoders (Global)

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
* torch (for CUDA capability detection)
* faster-whisper (local transcription engine)

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

**One-file Portable Executable:**
```bash
pyinstaller --noconfirm --windowed --onefile --icon "assets/icon.ico" --add-data "tools/ffmpeg.exe;tools" --add-data "assets;assets" --name "AutoAD Suite" app.py
```

**Directory Build (Faster Startup):**
```bash
pyinstaller "AutoAD Suite.spec" --noconfirm
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
│   ├── ui_utils.py
│   ├── version.py
│   └── utils.py
│
├── apps/
│   ├── assembler/     # Content Assembler App
│   ├── renamer/       # Bulk Renamer App
│   ├── converter/     # Video Converter App
│   ├── audio_tools/   # Audio Toolkit App
│   ├── subtitles/     # Subtitles Tools App
│   └── transcriber/   # Batch Transcriber App
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

