import os
import subprocess
import threading
from core.ffmpeg import FFMPEG_PATH

class WatermarkManager:
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
        font_size = 250 # Render text in high resolution
        
        if t in ("val_text", "val_both"):
            font_path = data["font_path"]
            
            logo_img = None
            lw, lh = 0, 0
            if t in ("val_img", "val_both"):
                logo_img = Image.open(data["image_path"]).convert("RGBA")
                lw, lh = logo_img.size
                
            # Set font size relative to logo if Both
            if t == "val_both":
                font_size = max(int(lh * 0.3), 30)
            else:
                font_size = 150 # Large for text-only
                
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
                
            text = data["text"]
            color = data["text_color"]
            
            dummy_img = Image.new("RGBA", (1, 1))
            draw = ImageDraw.Draw(dummy_img)
            
            # Align text within its own bounding box for multiline
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
        
        # Calculate ratio to keep logo visually stable when scaling width
        ratio_w = 1.0
        if t == "val_both" and lw > 0:
            ratio_w = fw / lw
            
        return out_path, ratio_w

    def process_batch(self, input_videos, output_dir, data, on_log, on_progress, on_finish):
        self.is_running = True
        self.stop_requested = False

        codec = {
            "CPU (libx264)": "libx264",
            "NVIDIA (NVENC)": "h264_nvenc",
            "AMD (AMF)": "h264_amf",
            "Intel (QSV)": "h264_qsv",
        }.get(data["encoder"], "libx264")

        pos = data["position"]
        try:
            m = int(data["margin"])
        except:
            m = 20
        
        try:
            scale_perc = int(data["scale"]) / 100.0
        except:
            scale_perc = 0.2
            
        try:
            opac_val = int(data["opacity"]) / 100.0
        except:
            opac_val = 1.0

        # FFmpeg overlay coordinates
        if pos == "val_pos_tl":
            ox, oy = f"{m}", f"{m}"
        elif pos == "val_pos_tr":
            ox, oy = f"W-w-{m}", f"{m}"
        elif pos == "val_pos_bl":
            ox, oy = f"{m}", f"H-h-{m}"
        elif pos == "val_pos_br":
            ox, oy = f"W-w-{m}", f"H-h-{m}"
        elif pos == "val_center":
            ox, oy = "(W-w)/2", "(H-h)/2"
        elif pos == "val_dvd":
            ox = "abs(mod(t*100,2*(W-w))-(W-w))"
            oy = "abs(mod(t*100,2*(H-h))-(H-h))"
        else:
            ox, oy = f"{m}", f"{m}"

        def worker():
            errored = []
            total = len(input_videos)
            
            # PRE-RENDER WATERMARK IMAGE
            on_log("Pré-renderizando marca d'água...")
            try:
                wm_path, ratio_w = self._generate_watermark_image(data)
            except Exception as e:
                on_log(f"Erro ao gerar a marca d'água: {str(e)}")
                self.is_running = False
                on_finish(False, input_videos)
                return

            try:
                for idx, video_path in enumerate(input_videos):
                    if self.stop_requested:
                        break

                    filename = os.path.basename(video_path)
                    name, ext = os.path.splitext(filename)
                    out_filename = f"{name}_watermarked{ext}"
                    output_path = os.path.join(output_dir, out_filename)

                    # Now it's always an image overlay. ratio_w guarantees logo preserves width across text changes.
                    vf = f"[1:v][0:v]scale2ref=w=rw*({scale_perc}*{ratio_w}):h=ow/a[wm][vid];[wm]format=rgba,colorchannelmixer=aa={opac_val}[wm_alpha];[vid][wm_alpha]overlay=x='{ox}':y='{oy}'"
                    
                    cmd = [
                        FFMPEG_PATH, "-y", "-i", video_path, "-i", wm_path,
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
                        print(f"FFmpeg Error on {filename} (Watermark): {stderr}")
                        
                        if os.path.exists(output_path):
                            try:
                                os.remove(output_path)
                            except:
                                pass

                    percent = (idx + 1) / total
                    on_progress(percent, idx + 1, total)

            finally:
                # Cleanup temp watermark
                if os.path.exists(wm_path):
                    try:
                        os.remove(wm_path)
                    except:
                        pass
                
                self.is_running = False
                on_finish(self.stop_requested, errored)

        threading.Thread(target=worker, daemon=True).start()
