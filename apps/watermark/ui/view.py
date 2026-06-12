import os
import glob
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES
from core.ui_utils import AutoScrollableFrame
from apps.watermark.renderer import WatermarkManager

class WatermarkView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.input_videos = []
        self.output_dir = ""
        self.watermark_image_path = ""
        self.custom_font_path = ""
        self.watermark_manager = WatermarkManager()

        # Add Scrollable wrapper
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
        self.lbl_out_dir.pack(pady=(0, 15), padx=15)

        # ============================================
        # RIGHT COLUMN: Options & Log
        # ============================================
        self.right_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.right_col.grid_rowconfigure(2, weight=1)

        # Options panel
        self.options_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.options_panel.pack(fill="x", pady=(0, 10))

        # Type Selection (Imagem / Texto)
        self.row_type = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        self.row_type.pack(fill="x", padx=15, pady=(15, 5))
        
        self.var_type = ctk.StringVar(value="val_img")
        self.rb_img = ctk.CTkRadioButton(self.row_type, text="🖼 Image", variable=self.var_type, value="val_img", command=self.on_type_change, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_main"])
        self.rb_img.pack(side="left", padx=(0, 15))
        self.rb_text = ctk.CTkRadioButton(self.row_type, text="🔤 Text", variable=self.var_type, value="val_text", command=self.on_type_change, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_main"])
        self.rb_text.pack(side="left", padx=(0, 15))
        self.rb_both = ctk.CTkRadioButton(self.row_type, text="🖼 + 🔤 Both", variable=self.var_type, value="val_both", command=self.on_type_change, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_main"])
        self.rb_both.pack(side="left")

        # --- HYBRID LAYOUT OPTIONS ---
        self.hybrid_frame = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        
        row_h1 = ctk.CTkFrame(self.hybrid_frame, fg_color="transparent")
        row_h1.pack(fill="x", pady=0)
        self.lbl_wm_pos_txt = ctk.CTkLabel(row_h1, text="Text Position:", width=100, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_pos_txt.pack(side="left", padx=(0, 10))
        self.var_hybrid_layout = ctk.StringVar(value="Text Below Image")
        self.menu_hybrid = ctk.CTkOptionMenu(
            row_h1, variable=self.var_hybrid_layout,
            values=["Text Below Image", "Text Above Image", "Text on Right", "Text on Left"],
            command=self.update_align_options
        )
        self.menu_hybrid.pack(side="left", fill="x", expand=True)

        # --- IMAGE OPTIONS ---
        self.img_frame = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        
        self.btn_sel_image = ctk.CTkButton(self.img_frame, text="Select Logo", fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], command=self.select_image)
        self.btn_sel_image.pack(pady=(5, 5), anchor="w")
        
        self.lbl_image = ctk.CTkLabel(self.img_frame, text="No image selected", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        self.lbl_image.pack(pady=(0, 5), anchor="w")

        # --- TEXT OPTIONS ---
        self.txt_frame = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        
        row_txt1 = ctk.CTkFrame(self.txt_frame, fg_color="transparent")
        row_txt1.pack(fill="x", pady=5)
        self.entry_text = ctk.CTkTextbox(row_txt1, height=60, fg_color=COLORS["bg_main"], text_color=COLORS["text_main"])
        self.entry_text.insert("0.0", "Type your watermark...")
        self.entry_text.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_color = ctk.CTkEntry(row_txt1, width=80, placeholder_text="HEX Color")
        self.entry_color.insert(0, "#FFFFFF")
        self.entry_color.pack(side="left")

        row_txt_align = ctk.CTkFrame(self.txt_frame, fg_color="transparent")
        row_txt_align.pack(fill="x", pady=5)
        self.lbl_wm_align = ctk.CTkLabel(row_txt_align, text="Alignment:", width=100, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_align.pack(side="left")
        self.var_hybrid_align = ctk.StringVar(value="Center")
        self.menu_align = ctk.CTkOptionMenu(
            row_txt_align, variable=self.var_hybrid_align,
            values=["Left", "Center", "Right"]
        )
        self.menu_align.pack(side="left", fill="x", expand=True)

        row_txt2 = ctk.CTkFrame(self.txt_frame, fg_color="transparent")
        row_txt2.pack(fill="x", pady=5)
        self.lbl_wm_font = ctk.CTkLabel(row_txt2, text="Font:", width=100, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_font.pack(side="left")
        
        # Load fonts
        self.fonts_list = self.load_system_fonts()
        self.var_font = ctk.StringVar(value="Arial" if "Arial" in self.fonts_list else self.fonts_list[0] if self.fonts_list else "None")
        self.menu_font = ctk.CTkOptionMenu(row_txt2, variable=self.var_font, values=self.fonts_list + ["Browse Custom..."], command=self.on_font_change)
        self.menu_font.pack(side="left", fill="x", expand=True)

        # --- COMMON OPTIONS (Scale, Opacity) ---
        row_common = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        row_common.pack(fill="x", padx=15, pady=5)
        
        self.lbl_wm_size = ctk.CTkLabel(row_common, text="Size (%):", width=80, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_size.pack(side="left")
        self.entry_scale = ctk.CTkEntry(row_common, width=60)
        self.entry_scale.insert(0, "20")
        self.entry_scale.pack(side="left", padx=(0, 15))
        
        self.lbl_wm_opacity = ctk.CTkLabel(row_common, text="Opacity (%):", width=90, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_opacity.pack(side="left")
        self.entry_opacity = ctk.CTkEntry(row_common, width=60)
        self.entry_opacity.insert(0, "100")
        self.entry_opacity.pack(side="left")

        # --- POSITION ---
        row_pos = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        row_pos.pack(fill="x", padx=15, pady=(5, 15))
        
        self.lbl_wm_position = ctk.CTkLabel(row_pos, text="Position:", width=60, anchor="w", font=("Segoe UI", 11))
        self.lbl_wm_position.pack(side="left")
        self.var_pos = ctk.StringVar(value="Bottom Right")
        self.menu_pos = ctk.CTkOptionMenu(
            row_pos, variable=self.var_pos,
            values=[
                "Top Left", "Top Right", 
                "Bottom Left", "Bottom Right", 
                "Center", "DVD Bouncing"
            ],
            command=self.on_pos_change
        )
        self.menu_pos.pack(side="left", padx=(5, 15))
        
        self.lbl_margin = ctk.CTkLabel(row_pos, text="Margin (px):", width=70, anchor="w", font=("Segoe UI", 11))
        self.lbl_margin.pack(side="left")
        self.entry_margin = ctk.CTkEntry(row_pos, width=60)
        self.entry_margin.insert(0, "20")
        self.entry_margin.pack(side="left")

        # Status & Run panel
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
            row_bottom, text="▶ Start Watermark", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"], text_color=COLORS["text_main"],
            width=200,
            command=self.toggle_run
        )
        self.btn_run.pack(side="right")
        
        self.update_encoder_label()
        self.hub.encoder_var.trace_add("write", lambda *args: self.update_encoder_label())
        
        self.lang = {}
        self.on_type_change() # Init layout

    def get_key_for_val(self, val, prefix):
        for k, v in self.lang.items():
            if v == val and k.startswith(prefix): return k
        if prefix == "val_t": return "val_tb"
        if prefix == "val_pos_": return "val_pos_br"
        if prefix == "val_": return "val_center"
        return val

    def load_system_fonts(self):
        self.system_fonts_paths = {}
        try:
            # Load basic TTF fonts from Windows
            for f in glob.glob("C:/Windows/Fonts/*.ttf"):
                basename = os.path.basename(f).replace(".ttf", "")
                if basename.isalpha() or " " in basename:
                    self.system_fonts_paths[basename] = f
        except:
            pass
        return sorted(list(self.system_fonts_paths.keys()))[:50] # Top 50 to avoid lag

    def on_font_change(self, val):
        if val == self.lang.get("wm_browse_font", "Browse Custom..."):
            f = filedialog.askopenfilename(title="Select Font", filetypes=[("Font Files", "*.ttf *.otf")])
            if f:
                self.custom_font_path = f
                # Add it to the menu temporarily
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

    def update_align_options(self, val):
        key = self.get_key_for_val(val, "val_t")
        if key in ("val_tr", "val_tl"):
            self.menu_align.configure(values=[self.lang.get("val_top", "Top"), self.lang.get("val_center", "Center"), self.lang.get("val_bottom", "Bottom")])
            current_align_key = self.get_key_for_val(self.var_hybrid_align.get(), "val_")
            if current_align_key not in ["val_top", "val_center", "val_bottom"]:
                self.var_hybrid_align.set(self.lang.get("val_center", "Center"))
        else:
            self.menu_align.configure(values=[self.lang.get("val_left", "Left"), self.lang.get("val_center", "Center"), self.lang.get("val_right", "Right")])
            current_align_key = self.get_key_for_val(self.var_hybrid_align.get(), "val_")
            if current_align_key not in ["val_left", "val_center", "val_right"]:
                self.var_hybrid_align.set(self.lang.get("val_center", "Center"))

    def on_type_change(self):
        t = self.var_type.get()
        self.txt_frame.pack_forget()
        self.img_frame.pack_forget()
        self.hybrid_frame.pack_forget()
        
        last_frame = self.row_type
        if t in ("val_img", "val_both"):
            self.img_frame.pack(fill="x", padx=15, pady=5, after=last_frame)
            last_frame = self.img_frame
            
        if t in ("val_text", "val_both"):
            self.txt_frame.pack(fill="x", padx=15, pady=5, after=last_frame)
            last_frame = self.txt_frame
            
        if t == "val_both":
            self.hybrid_frame.pack(fill="x", padx=15, pady=5, after=last_frame)

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
            text=self.lang.get("start_watermark", "▶ Start Watermark"),
            fg_color=COLORS["btn_action"],
            hover_color=COLORS["btn_action_hover"]
        )
        if stopped:
            self.log(self.lang.get("operation_cancelled", "Operation cancelled."))
        else:
            success = len(self.input_videos) - len(errored)
            self.log(self.lang.get("done", "Done! {} videos processed.").format(success))
            if errored:
                self.log(self.lang.get("errors_found", "Errors in {} videos.").format(len(errored)))
        
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def toggle_run(self):
        if self.watermark_manager.is_running:
            self.watermark_manager.stop()
            self.btn_run.configure(state="disabled")
            return

        if not self.input_videos:
            messagebox.showwarning("Warning", self.lang.get("add_videos_first", "Add videos first."))
            return
        if not self.output_dir:
            messagebox.showwarning("Warning", self.lang.get("select_output_first", "Select an output folder."))
            return

        t = self.var_type.get()
        text_val = self.entry_text.get("0.0", "end").strip()
        default_txt = self.lang.get("wm_type_here", "Type your watermark...")
        if text_val == default_txt:
            text_val = ""

        if t in ("val_img", "val_both") and not self.watermark_image_path:
            messagebox.showwarning("Warning", self.lang.get("wm_no_image", "No image"))
            return
        if t in ("val_text", "val_both") and not text_val:
            messagebox.showwarning("Warning", "Type the watermark text.")
            return

        font_name = self.var_font.get()
        if font_name == self.lang.get("wm_browse_font", "Browse Custom...") or font_name == os.path.basename(self.custom_font_path):
            actual_font_path = self.custom_font_path
        else:
            actual_font_path = self.system_fonts_paths.get(font_name, "")

        data = {
            "type": t,
            "layout_hybrid": self.get_key_for_val(self.var_hybrid_layout.get(), "val_t"),
            "layout_align": self.get_key_for_val(self.var_hybrid_align.get(), "val_"),
            "image_path": self.watermark_image_path,
            "text": text_val,
            "text_color": self.entry_color.get() or "#FFFFFF",
            "font_path": actual_font_path,
            "scale": self.entry_scale.get() or "20",
            "opacity": self.entry_opacity.get() or "100",
            "position": self.get_key_for_val(self.var_pos.get(), "val_pos_"),
            "margin": self.entry_margin.get() or "20",
            "encoder": self.hub.encoder_var.get()
        }

        self.btn_run.configure(
            text=self.lang.get("cancel", "⏹ Cancel"),
            fg_color=COLORS["stop_btn"],
            hover_color=COLORS["stop_btn_hover"]
        )
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.watermark_manager.process_batch(
            self.input_videos, self.output_dir, data,
            self.log, self.update_progress, self.on_finish
        )

    def update_language(self, lang):
        old_lang = self.lang if self.lang else lang
        self.lang = lang
        
        # Save keys for dropdowns
        hybrid_layout_key = self.get_key_for_val(self.var_hybrid_layout.get(), "val_t")
        align_key = self.get_key_for_val(self.var_hybrid_align.get(), "val_")
        pos_key = self.get_key_for_val(self.var_pos.get(), "val_pos_")
        
        # Buttons / Labels
        self.btn_add_videos.configure(text=lang.get("add_videos", "➕ Add Videos"))
        self.btn_clear_videos.configure(text=lang.get("clear_list", "Clear List"))
        self.btn_out_dir.configure(text=lang.get("output_folder", "📂 Output Folder"))
        self.btn_open_out_dir.configure(text=lang.get("open", "Open"))
        if not self.output_dir:
            self.lbl_out_dir.configure(text=lang.get("no_folder_selected", "No folder selected"))
            
        if not self.watermark_manager.is_running:
            self.btn_run.configure(text=lang.get("start_watermark", "▶ Start Watermark"))
        else:
            self.btn_run.configure(text=lang.get("cancel", "⏹ Cancel"))
            
        self.rb_img.configure(text=lang.get("wm_type_img", "🖼 Image"))
        self.rb_text.configure(text=lang.get("wm_type_text", "🔤 Text"))
        self.rb_both.configure(text=lang.get("wm_type_both", "🖼 + 🔤 Both"))
        
        self.lbl_wm_pos_txt.configure(text=lang.get("wm_pos_txt", "Text Position:"))
        self.lbl_wm_align.configure(text=lang.get("wm_align", "Alignment:"))
        self.btn_sel_image.configure(text=lang.get("wm_select_logo", "Select Logo"))
        if not self.watermark_image_path:
            self.lbl_image.configure(text=lang.get("wm_no_image", "No image"))
        
        if self.entry_text.get("0.0", "end").strip() == old_lang.get("wm_type_here", "Type your watermark..."):
            self.entry_text.delete("0.0", "end")
            self.entry_text.insert("0.0", lang.get("wm_type_here", "Type your watermark..."))
            
        self.entry_color.configure(placeholder_text=lang.get("wm_hex", "HEX Color"))
        self.lbl_wm_font.configure(text=lang.get("wm_font", "Font:"))
        self.lbl_wm_size.configure(text=lang.get("wm_size", "Size (%):"))
        self.lbl_wm_opacity.configure(text=lang.get("wm_opacity", "Opacity (%):"))
        self.lbl_wm_position.configure(text=lang.get("wm_position", "Position:"))
        self.lbl_margin.configure(text=lang.get("wm_margin", "Margin (px):"))
        
        # Dropdowns
        self.menu_hybrid.configure(values=[
            lang.get("val_tb"), lang.get("val_ta"), lang.get("val_tr"), lang.get("val_tl")
        ])
        self.menu_pos.configure(values=[
            lang.get("val_pos_tl"), lang.get("val_pos_tr"), 
            lang.get("val_pos_bl"), lang.get("val_pos_br"), 
            lang.get("val_center"), lang.get("val_dvd")
        ])
        
        # Update align options properly based on current hybrid layout
        self.update_align_options(lang.get(hybrid_layout_key))
        
        self.menu_font.configure(values=self.fonts_list + [lang.get("wm_browse_font", "Browse Custom...")])
        
        # Restore selections
        self.var_hybrid_layout.set(lang.get(hybrid_layout_key, lang.get("val_tb")))
        self.var_hybrid_align.set(lang.get(align_key, lang.get("val_center")))
        self.var_pos.set(lang.get(pos_key, lang.get("val_pos_br")))
