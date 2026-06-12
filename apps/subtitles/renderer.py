import os
import subprocess
import threading
import sys
from core.ffmpeg import FFMPEG_PATH

class SubtitlesManager:
    def __init__(self):
        self.is_running = False
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def _get_ffmpeg_cmd(self, input_path, output_path, sub_path, font_name, font_size, font_color, encoder):
        # Format the subtitle path for FFmpeg filter. Windows paths need escaping for filters.
        # e.g. C:\path\to\sub.srt -> C\\:/path/to/sub.srt
        safe_sub_path = sub_path.replace('\\', '/').replace(':', '\\:')
        
        # Style formatting for Subtitles filter (.srt only uses force_style)
        # FontName, FontSize, PrimaryColour (&HBBGGRR)
        style = f"FontName={font_name},FontSize={font_size}"
        if font_color and font_color.startswith("#") and len(font_color) == 7:
            # Convert #RRGGBB to &HBBGGRR for ASS styling
            r, g, b = font_color[1:3], font_color[3:5], font_color[5:7]
            ass_color = f"&H{b}{g}{r}"
            style += f",PrimaryColour={ass_color}"
            
        if sub_path.lower().endswith(".ass"):
            # If it's .ass, we just pass the file, force_style is optional or ignored depending on the file
            filter_str = f"ass='{safe_sub_path}'"
        else:
            filter_str = f"subtitles='{safe_sub_path}':force_style='{style}'"

        cmd = [
            FFMPEG_PATH, "-y",
            "-i", input_path,
            "-vf", filter_str,
            "-c:a", "copy"  # Copy audio to be fast
        ]

        if "NVENC" in encoder:
            cmd.extend(["-c:v", "h264_nvenc", "-preset", "p4"])
        elif "AMF" in encoder:
            cmd.extend(["-c:v", "h264_amf", "-quality", "balanced"])
        elif "QSV" in encoder:
            cmd.extend(["-c:v", "h264_qsv", "-preset", "medium"])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "fast"])

        cmd.append(output_path)
        return cmd

    def process_batch(self, videos, output_dir, sub_path, font_name, font_size, font_color, encoder, log_callback, progress_callback, finish_callback):
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
                out_path = os.path.join(output_dir, f"{name}_sub{ext}")
                
                log_callback(f"Processing ({i+1}/{total}): {basename}...")
                
                cmd = self._get_ffmpeg_cmd(vid, out_path, sub_path, font_name, font_size, font_color, encoder)
                
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
                        errored.append(vid)
                        log_callback(f"Error processing {basename}.")
                        # You could log process.stderr.read() here if debugging is needed
                except Exception as e:
                    errored.append(vid)
                    log_callback(f"Error starting FFmpeg for {basename}: {e}")
                    
                progress_callback(float(i+1)/total, i+1, total)

            self.is_running = False
            finish_callback(self.stop_requested, errored)

        threading.Thread(target=run, daemon=True).start()
