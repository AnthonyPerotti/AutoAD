import os
import subprocess
import threading
import sys
from core.ffmpeg import FFMPEG_PATH

class AudioToolsManager:
    def __init__(self):
        self.is_running = False
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def _get_ffmpeg_cmd(self, input_path, output_path, extract_mp3, normalize, peak_db, remove_silence, encoder):
        cmd = [FFMPEG_PATH, "-y", "-i", input_path]
        
        audio_filters = []
        if normalize:
            try:
                pdb = float(peak_db)
            except:
                pdb = -1.0
            audio_filters.append(f"loudnorm=I=-14:LRA=11:tp={pdb}")
            
        if remove_silence:
            audio_filters.append("silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-40dB")

        if audio_filters:
            cmd.extend(["-af", ",".join(audio_filters)])
            
        if extract_mp3:
            cmd.extend(["-vn", "-c:a", "libmp3lame", "-q:a", "2"])
        else:
            # We are modifying audio, keep video intact
            if "NVENC" in encoder:
                cmd.extend(["-c:v", "h264_nvenc", "-preset", "p4"])
            elif "AMF" in encoder:
                cmd.extend(["-c:v", "h264_amf", "-quality", "balanced"])
            elif "QSV" in encoder:
                cmd.extend(["-c:v", "h264_qsv", "-preset", "medium"])
            else:
                cmd.extend(["-c:v", "libx264", "-preset", "fast"])
            cmd.extend(["-c:v", "copy"])
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            
        cmd.append(output_path)
        return cmd

    def process_batch(self, videos, output_dir, extract_mp3, normalize, peak_db, remove_silence, encoder, log_callback, progress_callback, finish_callback):
        self.is_running = True
        self.stop_requested = False
        
        def run():
            errored = []
            total = len(videos)
            
            for i, vid in enumerate(videos):
                if self.stop_requested:
                    break
                    
                basename = os.path.basename(vid)
                name, ext = os.path.splitext(basename)
                
                if extract_mp3:
                    out_path = os.path.join(output_dir, f"{name}.mp3")
                else:
                    out_path = os.path.join(output_dir, f"{name}_audio{ext}")
                
                log_callback(f"Processing ({i+1}/{total}): {basename}...")
                
                cmd = self._get_ffmpeg_cmd(vid, out_path, extract_mp3, normalize, peak_db, remove_silence, encoder)
                
                try:
                    startupinfo = None
                    if sys.platform == "win32":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )
                    
                    import time
                    while process.poll() is None:
                        if self.stop_requested:
                            process.terminate()
                            break
                        time.sleep(0.5)
                    
                    if process.returncode != 0 and not self.stop_requested:
                        errored.append(vid)
                        log_callback(f"Error processing {basename}.")
                except Exception as e:
                    errored.append(vid)
                    log_callback(f"Error starting FFmpeg for {basename}: {e}")
                    
                progress_callback(float(i+1)/total, i+1, total)

            self.is_running = False
            finish_callback(self.stop_requested, errored)

        threading.Thread(target=run, daemon=True).start()
