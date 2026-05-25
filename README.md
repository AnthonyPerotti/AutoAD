# AutoAdd

Sistema desktop para automação de variações de anúncios em vídeo utilizando FFmpeg.

O AutoAdd combina automaticamente:

* Hooks
* Corpos de vídeo
* CTAs

Gerando centenas ou milhares de combinações em lote de forma automática.

---

# Preview

```text
Hook + Corpo(s) + CTA
```

Resultado:

```text
64
256
1024
ou milhares de variações automaticamente
```

---

# Funcionalidades

* Geração automática de combinações de vídeos
* Suporte para múltiplos corpos de vídeo
* Até 6 corpos simultâneos
* Integração com FFmpeg
* Interface desktop moderna
* Sistema de logs
* Barra de progresso
* Botão STOP
* Previsão automática de quantidade de vídeos
* Confirmação para grandes lotes
* Nome automático dos arquivos
* Exportação em lote
* Compatível com Windows

---

# Estrutura de funcionamento

O sistema sempre respeita a ordem:

```text
HOOK → CORPOS → CTA
```

Exemplo:

```text
Hook_01.mp4
↓
Corpo_03.mp4
↓
CTA_02.mp4
```

---

# Como funciona

O AutoAdd utiliza:

```python
itertools.product()
```

Para gerar todas as combinações possíveis entre:

* Hooks
* Corpos
* CTAs

Exemplo:

```text
4 Hooks
4 Corpos
4 CTAs
```

Resultado:

```text
64 vídeos
```

---

# Interface

Inspirado em ferramentas profissionais como:

* Shutter Encoder
* Adobe Media Encoder
* HandBrake

---

# Tecnologias utilizadas

* Python
* CustomTkinter
* FFmpeg
* PyInstaller

---

# Instalação

## 1. Clone o projeto

```bash
git clone https://github.com/SEU-USUARIO/AutoAdd.git
```

---

## 2. Instale as dependências

```bash
pip install customtkinter
pip install pyinstaller
```

---

## 3. Adicione o FFmpeg

Baixe o FFmpeg:

[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Estrutura necessária:

```text
ffmpeg/
└── bin/
    ├── ffmpeg.exe
    └── ffprobe.exe
```

---

# Executar

```bash
python app.py
```

---

# Gerar executável

```bash
pyinstaller --onedir --windowed --name AutoAdd --icon=icon.ico app.py
```

---

# Executável final

O executável será criado em:

```text
dist/AutoAdd/
```

---

# Importante

A pasta `ffmpeg` deve estar junto do executável:

```text
dist/
└── AutoAdd/
    ├── AutoAdd.exe
    └── ffmpeg/
```

---

# Roadmap

* Drag & Drop
* Preview de vídeos
* Miniaturas automáticas
* GPU Encoding
* Watermark automática
* Templates de render
* Randomização avançada
* Presets de exportação

---

# Autor

Anthony Perotti

---

# Licença

Projeto open-source para estudos e automação de workflows de edição de vídeo.
