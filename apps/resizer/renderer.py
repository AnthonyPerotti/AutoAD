import os
import subprocess
import threading
from core.ffmpeg import FFMPEG_PATH

class ResizerManager:
    def __init__(self):
        self.is_running = False
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def process_batch(self, input_videos, output_dir, preset, custom_w, custom_h, mode, submode_val, encoder, on_log, on_progress, on_finish):
        self.is_running = True
        self.stop_requested = False

        # Determine target resolution based on keys
        w, h = 1080, 1920
        if preset == "val_preset_916":
            w, h = 1080, 1920
        elif preset == "val_preset_169":
            w, h = 1920, 1080
        elif preset == "val_preset_11":
            w, h = 1080, 1080
        elif preset == "val_preset_45":
            w, h = 1080, 1350
        elif preset == "val_preset_custom":
            try:
                w = int(custom_w)
                h = int(custom_h)
            except (ValueError, TypeError):
                on_log("Erro: Resolução customizada inválida, usando 1080x1920.")
                w, h = 1080, 1920

        # Enforce even dimensions (required by some encoders)
        if w % 2 != 0: w += 1
        if h % 2 != 0: h += 1

        # Determine encoder
        codec = {
            "CPU (libx264)": "libx264",
            "NVIDIA (NVENC)": "h264_nvenc",
            "AMD (AMF)": "h264_amf",
            "Intel (QSV)": "h264_qsv",
        }.get(encoder, "libx264")

        def worker():
            errored = []
            total = len(input_videos)
            try:
                for idx, video_path in enumerate(input_videos):
                    if self.stop_requested:
                        break

                    filename = os.path.basename(video_path)
                    name, ext = os.path.splitext(filename)
                    out_filename = f"{name}_resized{ext}"
                    output_path = os.path.join(output_dir, out_filename)

                    # Build filtergraph
                    vf = ""
                    if mode == "val_mode_blur":
                        blur = submode_val if str(submode_val).isdigit() else "20"
                        vf = f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur={blur}:5[bg];[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
                    elif mode == "val_mode_color":
                        color = submode_val if str(submode_val).startswith("#") else "#000000"
                        vf = f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color='{color}'"
                    elif mode == "val_mode_crop":
                        vf = f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
                    elif mode == "val_mode_stretch":
                        vf = f"[0:v]scale={w}:{h}"

                    cmd = [
                        FFMPEG_PATH, "-y", "-i", video_path,
                        "-filter_complex", vf,
                        "-c:v", codec, "-c:a", "copy",
                        output_path
                    ]

                    on_log(f"Processando {idx+1}/{total}: {filename} ...")
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    process = subprocess.Popen(
                        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                        text=True, startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    _, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        errored.append(filename)
                        on_log(f"Erro em {filename}:")
                        if "nvenc" in codec and "Driver does not support" in stderr:
                            on_log(" ↳ SEU DRIVER NVIDIA ESTÁ DESATUALIZADO.")
                            on_log(" ↳ Solução: Atualize-o pelo GeForce Experience ou mude o Encoder para 'CPU' em Settings > Rendering.")
                        elif "nvenc" in codec and "No NVENC capable devices found" in stderr:
                            on_log(" ↳ Sua placa NVIDIA não suporta o encoder acelerado.")
                            on_log(" ↳ Solução: Mude o Encoder para 'CPU' em Settings > Rendering.")
                        else:
                            on_log(" ↳ Erro desconhecido do FFmpeg. Verifique o console para os detalhes técnicos.")
                        print(f"FFmpeg Error on {filename}: {stderr}")
                        if os.path.exists(output_path):
                            try:
                                os.remove(output_path)
                            except:
                                pass

                    percent = (idx + 1) / total
                    on_progress(percent, idx + 1, total)

            finally:
                self.is_running = False
                on_finish(self.stop_requested, errored)

        threading.Thread(target=worker, daemon=True).start()
