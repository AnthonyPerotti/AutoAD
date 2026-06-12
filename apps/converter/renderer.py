import os
import subprocess
import threading
import sys
from core.ffmpeg import FFMPEG_PATH

class ConverterManager:
    def __init__(self):
        self.is_running = False
        self.stop_requested = False

    def stop(self):
        self.stop_requested = True

    def _generate_watermark_image(self, data):
        from PIL import Image, ImageDraw, ImageFont, ImageColor
        
        t = data["type"]
        padding = 40
        
        txt_img = None
        tw, th = 0, 0
        font_size = 250
        
        if t in ("val_text", "val_both"):
            font_path = data["font_path"]
            
            logo_img = None
            lw, lh = 0, 0
            if t in ("val_img", "val_both"):
                logo_img = Image.open(data["image_path"]).convert("RGBA")
                lw, lh = logo_img.size
                
            if t == "val_both":
                font_size = max(int(lh * 0.3), 30)
            else:
                font_size = 150
                
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
                
            text = data["text"]
            color = data["text_color"]
            
            dummy_img = Image.new("RGBA", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            
            txt_align = "center"
            layout_align = data.get("layout_align", "val_center")
            if layout_align == "val_left": txt_align = "left"
            if layout_align == "val_right": txt_align = "right"
            
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align=txt_align)
            tw = int(bbox[2] - bbox[0])
            th = int(bbox[3] - bbox[1])
            
            if tw == 0: tw = 1
            if th == 0: th = 1
            
            txt_img = Image.new("RGBA", (tw, th), (0,0,0,0))
            draw = ImageDraw.Draw(txt_img)
            
            try:
                r, g, b = ImageColor.getrgb(color)
            except:
                r, g, b = 255, 255, 255
                
            draw.multiline_text((-bbox[0], -bbox[1]), text, font=font, fill=(r, g, b, 255), align=txt_align)
            
        elif t == "val_img":
            logo_img = Image.open(data["image_path"]).convert("RGBA")
            lw, lh = logo_img.size

        fw, fh = 0, 0
        if t == "val_text":
            final_img = txt_img
            fw, fh = tw, th
        elif t == "val_img":
            final_img = logo_img
            fw, fh = lw, lh
        else: # Both
            layout = data["layout_hybrid"]
            align = data.get("layout_align", "val_center")
            
            if layout in ("val_tb", "val_ta"):
                fw = max(tw, lw)
                fh = lh + padding + txt_img.height
                final_img = Image.new("RGBA", (fw, fh), (0,0,0,0))
                
                if align == "val_left":
                    lx, tx = 0, 0
                elif align == "val_right":
                    lx, tx = fw - lw, fw - tw
                else: # Center
                    lx, tx = (fw - lw)//2, (fw - tw)//2
                    
                if layout == "val_tb":
                    final_img.paste(logo_img, (lx, 0), logo_img)
                    final_img.paste(txt_img, (tx, lh + padding), txt_img)
                else:
                    final_img.paste(txt_img, (tx, 0), txt_img)
                    final_img.paste(logo_img, (lx, txt_img.height + padding), logo_img)
                    
            else: # Text on Right / Text on Left
                fw = lw + padding + tw
                fh = max(lh, txt_img.height)
                final_img = Image.new("RGBA", (fw, fh), (0,0,0,0))
                
                if align == "val_top":
                    ly, ty = 0, 0
                elif align == "val_bottom":
                    ly, ty = fh - lh, fh - txt_img.height
                else: # Center
                    ly, ty = (fh - lh)//2, (fh - txt_img.height)//2
                    
                if layout == "val_tr":
                    final_img.paste(logo_img, (0, ly), logo_img)
                    final_img.paste(txt_img, (lw + padding, ty), txt_img)
                else:
                    final_img.paste(txt_img, (0, ty), txt_img)
                    final_img.paste(logo_img, (tw + padding, ly), logo_img)
                
        out_path = os.path.abspath("temp_wm.png")
        final_img.save(out_path, "PNG")
        
        ratio_w = 1.0
        if t == "val_both" and lw > 0:
            ratio_w = fw / lw
            
        return out_path, ratio_w

    def process_batch(self, videos, output_dir, selected_presets, custom_settings, encoder, watermark_data, log_callback, progress_callback, finish_callback):
        self.is_running = True
        self.stop_requested = False

        codec = {
            "CPU (libx264)": "libx264",
            "NVIDIA (NVENC)": "h264_nvenc",
            "AMD (AMF)": "h264_amf",
            "Intel (QSV)": "h264_qsv",
        }.get(encoder, "libx264")

        def run():
            errored = []
            total = len(videos) * len(selected_presets)
            current_idx = 0

            has_watermark = watermark_data["enabled"]
            wm_path = None
            ratio_w = 1.0

            if has_watermark:
                log_callback("Pré-renderizando marca d'água...")
                try:
                    wm_path, ratio_w = self._generate_watermark_image(watermark_data)
                except Exception as e:
                    log_callback(f"Erro ao gerar a marca d'água: {str(e)}")
                    self.is_running = False
                    finish_callback(False, videos)
                    return

                pos = watermark_data["position"]
                try: m = int(watermark_data["margin"])
                except: m = 20
                try: scale_perc = int(watermark_data["scale"]) / 100.0
                except: scale_perc = 0.2
                try: opac_val = int(watermark_data["opacity"]) / 100.0
                except: opac_val = 1.0

                if pos == "val_pos_tl": ox, oy = f"{m}", f"{m}"
                elif pos == "val_pos_tr": ox, oy = f"W-w-{m}", f"{m}"
                elif pos == "val_pos_bl": ox, oy = f"{m}", f"H-h-{m}"
                elif pos == "val_pos_br": ox, oy = f"W-w-{m}", f"H-h-{m}"
                elif pos == "val_center": ox, oy = "(W-w)/2", "(H-h)/2"
                elif pos == "val_dvd": ox, oy = "abs(mod(t*100,2*(W-w))-(W-w))", "abs(mod(t*100,2*(H-h))-(H-h))"
                else: ox, oy = f"{m}", f"{m}"

            for vid in videos:
                if self.stop_requested:
                    break
                    
                basename = os.path.basename(vid)
                name, ext = os.path.splitext(basename)
                
                for preset in selected_presets:
                    if self.stop_requested:
                        break
                        
                    current_idx += 1
                    preset_folder = os.path.join(output_dir, preset.capitalize())
                    os.makedirs(preset_folder, exist_ok=True)
                    out_path = os.path.join(preset_folder, f"{name}{ext}")
                    
                    log_callback(f"Processing ({current_idx}/{total}): {basename} -> {preset.upper()}...")

                    cmd = [FFMPEG_PATH, "-y", "-i", vid]
                    if has_watermark:
                        cmd.extend(["-i", wm_path])

                    v_codec = "x264"
                    if "nvenc" in codec: v_codec = "nvenc"
                    elif "amf" in codec: v_codec = "amf"
                    elif "qsv" in codec: v_codec = "qsv"

                    scale_filter = ""
                    if preset in ["tiktok", "shorts", "reels"]:
                        scale_filter = "scale=-2:1920,crop=1080:1920:exact=1"
                    elif preset == "youtube":
                        pass # keep original resolution or add 1080p scale if needed
                    elif preset == "custom":
                        w, h = custom_settings["res"].split("x")
                        scale_filter = f"scale={w}:{h}"

                    filter_complex = ""
                    if has_watermark:
                        if scale_filter:
                            filter_complex = f"[0:v]{scale_filter}[vid_scaled];"
                            filter_complex += f"[1:v][vid_scaled]scale2ref=w=rw*({scale_perc}*{ratio_w}):h=ow/a[wm][vid];"
                        else:
                            filter_complex = f"[1:v][0:v]scale2ref=w=rw*({scale_perc}*{ratio_w}):h=ow/a[wm][vid];"
                            
                        filter_complex += f"[wm]format=rgba,colorchannelmixer=aa={opac_val}[wm_alpha];[vid][wm_alpha]overlay=x='{ox}':y='{oy}'"
                        cmd.extend(["-filter_complex", filter_complex])
                    else:
                        if scale_filter:
                            cmd.extend(["-vf", scale_filter])

                    cmd.extend(["-c:v", codec])
                    cmd.extend(["-c:a", "aac"])

                    if preset == "tiktok":
                        cmd.extend(["-b:v", "8M", "-maxrate", "8M", "-bufsize", "16M", "-b:a", "256k", "-ar", "44100"])
                    elif preset == "shorts":
                        if v_codec == "x264": cmd.extend(["-crf", "18", "-preset", "slow"])
                        else: cmd.extend(["-b:v", "15M"])
                        cmd.extend(["-b:a", "256k", "-ar", "48000"])
                    elif preset == "reels":
                        cmd.extend(["-r", "30", "-b:v", "8M", "-maxrate", "8M", "-bufsize", "16M", "-b:a", "128k", "-ar", "44100"])
                    elif preset == "youtube":
                        if v_codec == "x264": cmd.extend(["-crf", "18", "-preset", "slow"])
                        else: cmd.extend(["-b:v", "15M"])
                        cmd.extend(["-b:a", "320k", "-ar", "48000"])
                    elif preset == "custom":
                        fps = custom_settings.get("fps", "")
                        if fps: cmd.extend(["-r", fps])
                        bitrate = custom_settings.get("bitrate", "10M")
                        if v_codec == "x264": cmd.extend(["-crf", "18", "-preset", "medium"])
                        else: cmd.extend(["-b:v", bitrate])
                        cmd.extend(["-b:a", "256k", "-ar", "48000"])

                    cmd.extend(["-movflags", "+faststart", out_path])

                    try:
                        startupinfo = None
                        if sys.platform == "win32":
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                        process = subprocess.Popen(
                            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
                            startupinfo=startupinfo, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        )
                        
                        _, stderr = process.communicate()
                        
                        if process.returncode != 0 and not self.stop_requested:
                            errored.append(f"{vid} ({preset})")
                            log_callback(f"Error processing {basename} for {preset}.")
                            print(f"FFmpeg Error: {stderr}")
                    except Exception as e:
                        errored.append(f"{vid} ({preset})")
                        log_callback(f"Error starting FFmpeg for {basename}: {e}")
                        
                    progress_callback(float(current_idx)/total, current_idx, total)

            if wm_path and os.path.exists(wm_path):
                try: os.remove(wm_path)
                except: pass

            self.is_running = False
            finish_callback(self.stop_requested, errored)

        threading.Thread(target=run, daemon=True).start()
