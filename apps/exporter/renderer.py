import os
import subprocess
import threading
import sys
from core.ffmpeg import FFMPEG_PATH

class ExporterManager:
    def __init__(self):
        self.is_running = False
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def _get_ffmpeg_cmd(self, input_path, output_path, preset, encoder):
        cmd = [FFMPEG_PATH, "-y", "-i", input_path]
        
        # Base codec selection
        if "NVENC" in encoder:
            cmd.extend(["-c:v", "h264_nvenc"])
            v_codec = "nvenc"
        elif "AMF" in encoder:
            cmd.extend(["-c:v", "h264_amf"])
            v_codec = "amf"
        elif "QSV" in encoder:
            cmd.extend(["-c:v", "h264_qsv"])
            v_codec = "qsv"
        else:
            cmd.extend(["-c:v", "libx264"])
            v_codec = "x264"
            
        cmd.extend(["-c:a", "aac"])

        if preset == "tiktok":
            # 1080x1920 max, max bitrate 8M, audio 256k
            cmd.extend(["-vf", "scale='min(1080,iw)':-2"])
            cmd.extend(["-b:v", "8M", "-maxrate", "8M", "-bufsize", "16M"])
            cmd.extend(["-b:a", "256k", "-ar", "44100"])
            cmd.extend(["-movflags", "+faststart"])
        elif preset == "shorts":
            # YouTube Shorts: 1080x1920, high quality, no strict limit but 10-15M is good
            cmd.extend(["-vf", "scale='min(1080,iw)':-2"])
            if v_codec == "x264":
                cmd.extend(["-crf", "18", "-preset", "slow"])
            else:
                cmd.extend(["-b:v", "15M"])
            cmd.extend(["-b:a", "256k", "-ar", "48000"])
            cmd.extend(["-movflags", "+faststart"])
        elif preset == "reels":
            # Instagram Reels: 1080x1920, 30fps max ideally, 5-8M bitrate
            cmd.extend(["-vf", "scale='min(1080,iw)':-2"])
            cmd.extend(["-r", "30"])
            cmd.extend(["-b:v", "8M", "-maxrate", "8M", "-bufsize", "16M"])
            cmd.extend(["-b:a", "128k", "-ar", "44100"])
            cmd.extend(["-movflags", "+faststart"])
        elif preset == "youtube":
            # YouTube 1080p Landscape: High bitrate
            if v_codec == "x264":
                cmd.extend(["-crf", "18", "-preset", "slow"])
            else:
                cmd.extend(["-b:v", "15M"])
            cmd.extend(["-b:a", "320k", "-ar", "48000"])
            cmd.extend(["-movflags", "+faststart"])

        cmd.append(output_path)
        return cmd

    def process_batch(self, videos, output_dir, selected_presets, encoder, log_callback, progress_callback, finish_callback):
        self.is_running = True
        self.stop_requested = False
        
        def run():
            errored = []
            total = len(videos) * len(selected_presets)
            current_idx = 0
            
            for vid in videos:
                if self.stop_requested:
                    break
                    
                basename = os.path.basename(vid)
                name, ext = os.path.splitext(basename)
                
                for preset in selected_presets:
                    if self.stop_requested:
                        break
                        
                    current_idx += 1
                    
                    # Create preset folder
                    preset_folder = os.path.join(output_dir, preset.capitalize())
                    os.makedirs(preset_folder, exist_ok=True)
                    
                    out_path = os.path.join(preset_folder, f"{name}{ext}")
                    
                    log_callback(f"Processing ({current_idx}/{total}): {basename} -> {preset.upper()}...")
                    
                    cmd = self._get_ffmpeg_cmd(vid, out_path, preset, encoder)
                    
                    try:
                        startupinfo = None
                        if sys.platform == "win32":
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        )
                        
                        while process.poll() is None:
                            if self.stop_requested:
                                process.terminate()
                                break
                        
                        if process.returncode != 0 and not self.stop_requested:
                            errored.append(f"{vid} ({preset})")
                            log_callback(f"Error processing {basename} for {preset}.")
                    except Exception as e:
                        errored.append(f"{vid} ({preset})")
                        log_callback(f"Error starting FFmpeg for {basename}: {e}")
                        
                    progress_callback(float(current_idx)/total, current_idx, total)

            self.is_running = False
            finish_callback(self.stop_requested, errored)

        threading.Thread(target=run, daemon=True).start()
