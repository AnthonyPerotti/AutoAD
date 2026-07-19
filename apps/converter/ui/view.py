import os
import glob
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES
from core.ui_utils import AutoScrollableFrame, show_completion_popup
from apps.converter.renderer import ConverterManager

class ConverterView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.input_videos = []
        self.output_dir = ""
        self.watermark_image_path = ""
        self.custom_font_path = ""
        self.converter_manager = ConverterManager()

        self.scroll_frame = AutoScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.scroll_frame.grid_columnconfigure(0, weight=1, minsize=350)
        self.scroll_frame.grid_columnconfigure(1, weight=1, minsize=400)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        # ============================================
        # LEFT COLUMN: Inputs
        # ============================================
        self.left_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=10)
        self.left_col.grid_rowconfigure(2, weight=1)

        # Input videos panel
        self.input_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.input_panel.pack(fill="both", expand=True, pady=(0, 10))

        self.btn_add_videos = ctk.CTkButton(
            self.input_panel, text="➕ Add Videos", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.add_videos
        )
        self.btn_add_videos.pack(pady=15, padx=15, fill="x")

        self.videos_list = ctk.CTkScrollableFrame(self.input_panel, fg_color="transparent")
        self.videos_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.btn_clear_videos = ctk.CTkButton(
            self.input_panel, text="Clear List", font=("Segoe UI", 11),
            fg_color="transparent", hover_color=COLORS["bg_hover"], text_color=COLORS["text_light"],
            command=self.clear_videos
        )
        self.btn_clear_videos.pack(pady=(0, 15))

        # Output dir panel
        self.output_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.output_panel.pack(fill="x")

        btn_row = ctk.CTkFrame(self.output_panel, fg_color="transparent")
        btn_row.pack(pady=15, padx=15, fill="x")

        self.btn_out_dir = ctk.CTkButton(
            btn_row, text="📂 Output Folder", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["export_btn"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.select_output_dir
        )
        self.btn_out_dir.pack(side="left", fill="x", expand=True)

        self.btn_open_out_dir = ctk.CTkButton(
            btn_row, text="Open", font=("Segoe UI", 13, "bold"), width=60,
            fg_color="transparent", hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            border_width=1, border_color=COLORS["border"],
            command=self.open_output_dir
        )
        self.btn_open_out_dir.pack(side="left", padx=(10, 0))

        self.lbl_out_dir = ctk.CTkLabel(self.output_panel, text="No folder selected", font=("Segoe UI", 11), text_color=COLORS["text_muted"], wraplength=300)
        self.lbl_out_dir.pack(pady=(0, 15), padx=15, anchor="w")

        # ============================================
        # RIGHT COLUMN: Options
        # ============================================
        self.right_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        # EXPORT OPTIONS
        self.export_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.export_panel.pack(fill="x", pady=(0, 10))
        
        self.lbl_presets = ctk.CTkLabel(self.export_panel, text="Output Formats:", font=("Segoe UI", 14, "bold"), text_color=COLORS["text_main"])
        self.lbl_presets.pack(anchor="w", padx=20, pady=(15, 5))

        # Checkboxes for formats
        formats_row = ctk.CTkFrame(self.export_panel, fg_color="transparent")
        formats_row.pack(fill="x", padx=15)
        
        self.var_tiktok = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(formats_row, text="TikTok", variable=self.var_tiktok).pack(side="left", padx=5, pady=5)
        self.var_shorts = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(formats_row, text="Shorts", variable=self.var_shorts).pack(side="left", padx=5, pady=5)
        self.var_reels = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(formats_row, text="Reels", variable=self.var_reels).pack(side="left", padx=5, pady=5)
        self.var_youtube = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(formats_row, text="YouTube", variable=self.var_youtube).pack(side="left", padx=5, pady=5)

        self.var_custom = ctk.BooleanVar(value=False)
        self.chk_custom = ctk.CTkCheckBox(self.export_panel, text="Custom Resolution", variable=self.var_custom, command=self.on_custom_toggle)
        self.chk_custom.pack(anchor="w", padx=20, pady=10)

        self.custom_frame = ctk.CTkFrame(self.export_panel, fg_color="transparent")
        
        c_row1 = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        c_row1.pack(fill="x", pady=2)
        ctk.CTkLabel(c_row1, text="Resolução (LxA):").pack(side="left")
        self.entry_custom_res = ctk.CTkEntry(c_row1, width=100)
        self.entry_custom_res.insert(0, "1080x1920")
        self.entry_custom_res.pack(side="left", padx=10)

        c_row2 = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        c_row2.pack(fill="x", pady=2)
        ctk.CTkLabel(c_row2, text="FPS:").pack(side="left")
        self.entry_custom_fps = ctk.CTkEntry(c_row2, width=60)
        self.entry_custom_fps.insert(0, "60")
        self.entry_custom_fps.pack(side="left", padx=10)
        
        ctk.CTkLabel(c_row2, text="Bitrate:").pack(side="left")
        self.entry_custom_bitrate = ctk.CTkEntry(c_row2, width=80)
        self.entry_custom_bitrate.insert(0, "10M")
        self.entry_custom_bitrate.pack(side="left", padx=10)

        # WATERMARK OPTIONS
        self.wm_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.wm_panel.pack(fill="x", pady=(0, 10))

        self.var_wm_enabled = ctk.BooleanVar(value=False)
        self.chk_wm_enabled = ctk.CTkCheckBox(self.wm_panel, text="Add Watermark", font=("Segoe UI", 14, "bold"), variable=self.var_wm_enabled, command=self.on_wm_toggle)
        self.chk_wm_enabled.pack(anchor="w", padx=20, pady=(15, 10))

        self.wm_options_frame = ctk.CTkFrame(self.wm_panel, fg_color="transparent")
        
        self.row_type = ctk.CTkFrame(self.wm_options_frame, fg_color="transparent")
        self.row_type.pack(fill="x", padx=15, pady=(5, 5))
        self.var_type = ctk.StringVar(value="val_img")
        self.rb_img = ctk.CTkRadioButton(self.row_type, text="🖼 Image", variable=self.var_type, value="val_img", command=self.on_type_change)
        self.rb_img.pack(side="left", padx=(0, 15))
        self.rb_text = ctk.CTkRadioButton(self.row_type, text="🔤 Text", variable=self.var_type, value="val_text", command=self.on_type_change)
        self.rb_text.pack(side="left", padx=(0, 15))

        self.img_frame = ctk.CTkFrame(self.wm_options_frame, fg_color="transparent")
        self.btn_sel_image = ctk.CTkButton(self.img_frame, text="Select Logo", fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], command=self.select_image)
        self.btn_sel_image.pack(pady=5, anchor="w")
        self.lbl_image = ctk.CTkLabel(self.img_frame, text="No image selected", text_color=COLORS["text_muted"])
        self.lbl_image.pack(anchor="w")

        self.txt_frame = ctk.CTkFrame(self.wm_options_frame, fg_color="transparent")
        self.entry_text = ctk.CTkTextbox(self.txt_frame, height=60, fg_color=COLORS["bg_main"], text_color=COLORS["text_main"])
        self.entry_text.insert("0.0", "Watermark text...")
        self.entry_text.pack(fill="x", pady=5)
        
        t_row = ctk.CTkFrame(self.txt_frame, fg_color="transparent")
        t_row.pack(fill="x")
        self.entry_color = ctk.CTkEntry(t_row, width=80, placeholder_text="HEX (#FFFFFF)")
        self.entry_color.insert(0, "#FFFFFF")
        self.entry_color.pack(side="left", padx=(0, 10))

        self.fonts_list = self.load_system_fonts()
        self.var_font = ctk.StringVar(value="Arial" if "Arial" in self.fonts_list else self.fonts_list[0] if self.fonts_list else "None")
        self.menu_font = ctk.CTkOptionMenu(t_row, variable=self.var_font, values=self.fonts_list + ["Browse Custom..."], command=self.on_font_change)
        self.menu_font.pack(side="left", fill="x", expand=True)

        row_common = ctk.CTkFrame(self.wm_options_frame, fg_color="transparent")
        row_common.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row_common, text="Size (%):", width=60, anchor="w").pack(side="left")
        self.entry_scale = ctk.CTkEntry(row_common, width=50)
        self.entry_scale.insert(0, "20")
        self.entry_scale.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(row_common, text="Opacity (%):", width=70, anchor="w").pack(side="left")
        self.entry_opacity = ctk.CTkEntry(row_common, width=50)
        self.entry_opacity.insert(0, "100")
        self.entry_opacity.pack(side="left")

        row_pos = ctk.CTkFrame(self.wm_options_frame, fg_color="transparent")
        row_pos.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(row_pos, text="Position:", width=60, anchor="w").pack(side="left")
        self.var_pos = ctk.StringVar(value="Bottom Right")
        self.menu_pos = ctk.CTkOptionMenu(
            row_pos, variable=self.var_pos,
            values=["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center", "DVD Bouncing"],
            command=self.on_pos_change
        )
        self.menu_pos.pack(side="left", padx=(0, 15))
        self.lbl_margin = ctk.CTkLabel(row_pos, text="Margin:", width=50, anchor="w")
        self.lbl_margin.pack(side="left")
        self.entry_margin = ctk.CTkEntry(row_pos, width=50)
        self.entry_margin.insert(0, "20")
        self.entry_margin.pack(side="left")

        # RUN PANEL
        self.run_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.run_panel.pack(fill="both", expand=True)

        self.log_textbox = ctk.CTkTextbox(self.run_panel, fg_color=COLORS["bg_main"], text_color=COLORS["text_main"], font=("Consolas", 11))
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.log_textbox.insert("end", "Waiting for videos...\n")

        self.progress_bar = ctk.CTkProgressBar(self.run_panel, progress_color=COLORS["hook"])
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        row_bottom = ctk.CTkFrame(self.run_panel, fg_color="transparent")
        row_bottom.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_encoder = ctk.CTkLabel(row_bottom, text="Encoder: Auto", font=("Segoe UI", 10), text_color=COLORS["text_muted"])
        self.lbl_encoder.pack(side="left")

        self.btn_run = ctk.CTkButton(
            row_bottom, text="▶ Converter / Exportar", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"], text_color=COLORS["text_main"],
            width=200,
            command=self.toggle_run
        )
        self.btn_run.pack(side="right")
        
        self.update_encoder_label()
        self.hub.encoder_var.trace_add("write", lambda *args: self.update_encoder_label())
        
        self.lang = {}
        self.on_type_change()
        self.on_custom_toggle()
        self.on_wm_toggle()

    def get_key_for_val(self, val, prefix):
        if val == "Top Left": return "val_pos_tl"
        if val == "Top Right": return "val_pos_tr"
        if val == "Bottom Left": return "val_pos_bl"
        if val == "Bottom Right": return "val_pos_br"
        if val == "Center": return "val_center"
        if val == "DVD Bouncing": return "val_dvd"
        if prefix == "val_pos_": return "val_pos_br"
        if prefix == "val_": return "val_center"
        return val

    def load_system_fonts(self):
        self.system_fonts_paths = {}
        try:
            for f in glob.glob("C:/Windows/Fonts/*.ttf"):
                basename = os.path.basename(f).replace(".ttf", "")
                if basename.isalpha() or " " in basename:
                    self.system_fonts_paths[basename] = f
        except:
            pass
        return sorted(list(self.system_fonts_paths.keys()))[:50]

    def on_font_change(self, val):
        if val == self.lang.get("wm_browse_font", "Browse Custom..."):
            f = filedialog.askopenfilename(title="Select Font", filetypes=[("Font Files", "*.ttf *.otf")])
            if f:
                self.custom_font_path = f
                name = os.path.basename(f)
                self.var_font.set(name)
            else:
                self.var_font.set("Arial" if "Arial" in self.fonts_list else self.fonts_list[0])

    def on_pos_change(self, val):
        key = self.get_key_for_val(val, "val_pos_")
        if key == "val_center" or key == "val_dvd":
            self.lbl_margin.pack_forget()
            self.entry_margin.pack_forget()
        else:
            self.lbl_margin.pack(side="left")
            self.entry_margin.pack(side="left")

    def on_type_change(self):
        t = self.var_type.get()
        self.txt_frame.pack_forget()
        self.img_frame.pack_forget()
        
        if t == "val_img":
            self.img_frame.pack(fill="x", padx=15, pady=5, after=self.row_type)
        if t == "val_text":
            self.txt_frame.pack(fill="x", padx=15, pady=5, after=self.row_type)

    def on_custom_toggle(self):
        if self.var_custom.get():
            self.custom_frame.pack(fill="x", padx=40, pady=5)
        else:
            self.custom_frame.pack_forget()

    def on_wm_toggle(self):
        if self.var_wm_enabled.get():
            self.wm_options_frame.pack(fill="x")
        else:
            self.wm_options_frame.pack_forget()

    def select_image(self):
        f = filedialog.askopenfilename(title=self.lang.get("wm_select_logo", "Select Logo"), filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if f:
            self.watermark_image_path = f
            self.lbl_image.configure(text=os.path.basename(f))

    def update_encoder_label(self):
        enc = self.hub.encoder_var.get()
        self.lbl_encoder.configure(text=f"Encoder: {enc}")

    def log(self, msg):
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")

    def add_videos(self):
        files = filedialog.askopenfilenames(
            title=self.lang.get("add_videos", "Select Videos"),
            filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
        )
        if files:
            for f in files:
                if f not in self.input_videos:
                    self.input_videos.append(f)
                    
                    frame = ctk.CTkFrame(self.videos_list, fg_color=COLORS["bg_main"], corner_radius=4)
                    frame.pack(fill="x", pady=2)
                    lbl = ctk.CTkLabel(frame, text=os.path.basename(f), font=("Segoe UI", 11), text_color=COLORS["text_main"], anchor="w")
                    lbl.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            self.log(self.lang.get("videos_added", "{} videos added.").format(len(files)))

    def clear_videos(self):
        self.input_videos.clear()
        for widget in self.videos_list.winfo_children():
            widget.destroy()
        self.log(self.lang.get("list_cleared", "List cleared."))

    def select_output_dir(self):
        d = filedialog.askdirectory(title=self.lang.get("output_folder", "Output Folder"))
        if d:
            self.output_dir = d
            self.lbl_out_dir.configure(text=d)
            self.log(f"Output: {d}")

    def open_output_dir(self):
        from core.utils import open_folder
        if self.output_dir:
            open_folder(self.output_dir)
        else:
            messagebox.showwarning("Aviso", self.lang.get("no_folder_selected", "Nenhuma pasta selecionada."))

    def update_progress(self, percent, current, total):
        pass

    def on_finish(self, stopped, errored):
        self.btn_run.configure(
            text=self.lang.get("start_converter", "▶ Converter / Exportar"),
            fg_color=COLORS["btn_action"],
            hover_color=COLORS["btn_action_hover"],
            state="normal"
        )
        if not stopped:
            self.log(self.lang.get("done", "Done!"))
            if errored:
                self.log(self.lang.get("errors_found", "Errors in some tasks."))
            show_completion_popup(self, self.lang, "Video Converter", self.output_dir)
        else:
            self.log(self.lang.get("operation_cancelled", "Operation cancelled."))
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def toggle_run(self):
        if self.converter_manager.is_running:
            self.converter_manager.stop()
            self.btn_run.configure(state="disabled")
            return

        if not self.input_videos:
            messagebox.showwarning("Warning", self.lang.get("add_videos_first", "Add videos first."))
            return
        if not self.output_dir:
            messagebox.showwarning("Warning", self.lang.get("select_output_first", "Select an output folder."))
            return

        selected_presets = []
        if self.var_tiktok.get(): selected_presets.append("tiktok")
        if self.var_shorts.get(): selected_presets.append("shorts")
        if self.var_reels.get(): selected_presets.append("reels")
        if self.var_youtube.get(): selected_presets.append("youtube")

        custom_settings = {}
        if self.var_custom.get():
            res = self.entry_custom_res.get()
            if "x" not in res:
                messagebox.showwarning("Warning", "Invalid custom resolution format (e.g., 1080x1920).")
                return
            selected_presets.append("custom")
            custom_settings = {
                "res": res,
                "fps": self.entry_custom_fps.get(),
                "bitrate": self.entry_custom_bitrate.get()
            }

        if not selected_presets:
            messagebox.showwarning("Warning", "Select at least one format to export.")
            return

        font_name = self.var_font.get()
        actual_font_path = self.custom_font_path if font_name == self.lang.get("wm_browse_font", "Browse Custom...") else self.system_fonts_paths.get(font_name, "")
        
        watermark_data = {
            "enabled": self.var_wm_enabled.get(),
            "type": self.var_type.get(),
            "image_path": self.watermark_image_path,
            "text": self.entry_text.get("0.0", "end").strip(),
            "text_color": self.entry_color.get() or "#FFFFFF",
            "font_path": actual_font_path,
            "scale": self.entry_scale.get() or "20",
            "opacity": self.entry_opacity.get() or "100",
            "position": self.get_key_for_val(self.var_pos.get(), "val_pos_"),
            "margin": self.entry_margin.get() or "20",
        }

        if watermark_data["enabled"]:
            if watermark_data["type"] == "val_img" and not watermark_data["image_path"]:
                messagebox.showwarning("Warning", self.lang.get("wm_no_image", "No image selected."))
                return
            if watermark_data["type"] == "val_text" and not watermark_data["text"]:
                messagebox.showwarning("Warning", "Type the watermark text.")
                return

        self.btn_run.configure(
            text=self.lang.get("cancel", "⏹ Cancel"),
            fg_color=COLORS["stop_btn"],
            hover_color=COLORS["stop_btn_hover"]
        )
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.converter_manager.process_batch(
            self.input_videos, self.output_dir,
            selected_presets, custom_settings,
            self.hub.encoder_var.get(), watermark_data,
            self.log, self.update_progress, self.on_finish
        )

    def update_language(self, lang):
        self.lang = lang
        self.btn_add_videos.configure(text=lang.get("add_videos", "➕ Add Videos"))
        self.btn_clear_videos.configure(text=lang.get("clear_list", "Clear List"))
        self.btn_out_dir.configure(text=lang.get("output_folder", "📂 Output Folder"))
        self.btn_open_out_dir.configure(text=lang.get("open", "Open"))
        if not self.output_dir:
            self.lbl_out_dir.configure(text=lang.get("no_folder_selected", "No folder selected"))
        if not self.converter_manager.is_running:
            self.btn_run.configure(text=lang.get("start_converter", "▶ Convert / Export"))
        else:
            self.btn_run.configure(text=lang.get("cancel", "⏹ Cancel"))
        self.lbl_presets.configure(text=lang.get("exp_select", "Output Formats:"))
        self.chk_custom.configure(text=lang.get("exp_custom", "Custom Resolution"))
        self.chk_wm_enabled.configure(text=lang.get("wm_enable", "Add Watermark"))
