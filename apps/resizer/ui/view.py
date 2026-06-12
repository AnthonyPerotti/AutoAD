import os
import threading
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES
from core.ui_utils import AutoScrollableFrame
from apps.resizer.renderer import ResizerManager

class ResizerView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.input_videos = []
        self.output_dir = ""
        self.resizer_manager = ResizerManager()

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
            self.input_panel, text="➕ Adicionar Vídeos", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.add_videos
        )
        self.btn_add_videos.pack(pady=15, padx=15, fill="x")

        self.videos_list = ctk.CTkScrollableFrame(self.input_panel, fg_color="transparent")
        self.videos_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.btn_clear_videos = ctk.CTkButton(
            self.input_panel, text="Limpar Lista", font=("Segoe UI", 11),
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
            btn_row, text="📂 Pasta de Saída", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["export_btn"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.select_output_dir
        )
        self.btn_out_dir.pack(side="left", fill="x", expand=True)

        self.btn_open_out_dir = ctk.CTkButton(
            btn_row, text="Abrir", font=("Segoe UI", 13, "bold"), width=60,
            fg_color="transparent", hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            border_width=1, border_color=COLORS["border"],
            command=self.open_output_dir
        )
        self.btn_open_out_dir.pack(side="left", padx=(10, 0))

        self.lbl_out_dir = ctk.CTkLabel(self.output_panel, text="Nenhuma pasta selecionada", font=("Segoe UI", 11), text_color=COLORS["text_muted"], wraplength=300)
        self.lbl_out_dir.pack(pady=(0, 10), padx=15, anchor="w")

        self.var_open_folder = ctk.BooleanVar(value=True)
        self.chk_open_folder = ctk.CTkCheckBox(self.output_panel, text="Abrir pasta ao finalizar", variable=self.var_open_folder, font=("Segoe UI", 11))
        self.chk_open_folder.pack(anchor="w", padx=15, pady=(0, 15))


        # ============================================
        # RIGHT COLUMN: Options & Log
        # ============================================
        self.right_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.right_col.grid_rowconfigure(2, weight=1)

        # Options panel
        self.options_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.options_panel.pack(fill="x", pady=(0, 10))

        # Preset
        row_preset = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        row_preset.pack(fill="x", padx=15, pady=(15, 5))
        self.lbl_preset = ctk.CTkLabel(row_preset, text="Proporção:", width=80, anchor="w", font=("Segoe UI", 12))
        self.lbl_preset.pack(side="left")
        
        self.var_preset = ctk.StringVar(value="9:16 (TikTok/Reels)")
        self.menu_preset = ctk.CTkOptionMenu(
            row_preset, variable=self.var_preset,
            values=["9:16 (TikTok/Reels)", "16:9 (YouTube)", "1:1 (Feed)", "4:5 (Portrait)", "Customizado"],
            command=self.on_preset_change
        )
        self.menu_preset.pack(side="left", padx=10, fill="x", expand=True)

        # Custom Res (Hidden by default)
        self.row_custom = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        
        self.lbl_res = ctk.CTkLabel(self.row_custom, text="Resolução:", width=80, anchor="w", font=("Segoe UI", 12))
        self.lbl_res.pack(side="left")
        self.entry_width = ctk.CTkEntry(self.row_custom, width=60, placeholder_text="Width")
        self.entry_width.pack(side="left", padx=(10, 5))
        ctk.CTkLabel(self.row_custom, text="x", font=("Segoe UI", 12)).pack(side="left")
        self.entry_height = ctk.CTkEntry(self.row_custom, width=60, placeholder_text="Height")
        self.entry_height.pack(side="left", padx=(5, 10))

        # Mode
        row_mode = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        row_mode.pack(fill="x", padx=15, pady=5)
        self.lbl_mode = ctk.CTkLabel(row_mode, text="Modo:", width=80, anchor="w", font=("Segoe UI", 12))
        self.lbl_mode.pack(side="left")
        
        self.var_mode = ctk.StringVar(value="Blur Background")
        self.menu_mode = ctk.CTkOptionMenu(
            row_mode, variable=self.var_mode,
            values=["Blur Background", "Cor Sólida", "Crop & Center", "Stretch"],
            command=self.on_mode_change
        )
        self.menu_mode.pack(side="left", padx=10, fill="x", expand=True)

        # Blur Strength / Color Hex
        self.row_submode = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        self.row_submode.pack(fill="x", padx=15, pady=(5, 15))
        
        self.lbl_submode = ctk.CTkLabel(self.row_submode, text="Blur (0-100):", width=80, anchor="w", font=("Segoe UI", 12))
        self.lbl_submode.pack(side="left")
        
        self.entry_submode = ctk.CTkEntry(self.row_submode, width=100)
        self.entry_submode.insert(0, "20")
        self.entry_submode.pack(side="left", padx=10)

        # Status & Run panel
        self.run_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.run_panel.pack(fill="both", expand=True)

        self.log_textbox = ctk.CTkTextbox(self.run_panel, fg_color=COLORS["bg_main"], text_color=COLORS["text_main"], font=("Consolas", 11))
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=15)
        self.log_textbox.insert("end", "Aguardando vídeos...\n")

        self.progress_bar = ctk.CTkProgressBar(self.run_panel, progress_color=COLORS["hook"])
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        row_bottom = ctk.CTkFrame(self.run_panel, fg_color="transparent")
        row_bottom.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_encoder = ctk.CTkLabel(row_bottom, text="Encoder: Auto", font=("Segoe UI", 10), text_color=COLORS["text_muted"])
        self.lbl_encoder.pack(side="left")

        self.btn_run = ctk.CTkButton(
            row_bottom, text="▶ Iniciar Redimensionamento", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"], text_color=COLORS["text_main"],
            width=240,
            command=self.toggle_run
        )
        self.btn_run.pack(side="right")
        
        self.update_encoder_label()
        
        # Monitor changes in encoder variable to update the label in real time
        self.hub.encoder_var.trace_add("write", lambda *args: self.update_encoder_label())
        self.lang = {}

    def get_preset_key(self, display_val):
        for k, v in self.lang.items():
            if v == display_val and k.startswith("val_preset_"):
                return k
        return "val_preset_916"

    def get_mode_key(self, display_val):
        for k, v in self.lang.items():
            if v == display_val and k.startswith("val_mode_"):
                return k
        return "val_mode_blur"

    def on_preset_change(self, val):
        key = self.get_preset_key(val)
        if key == "val_preset_custom":
            self.row_custom.pack(fill="x", padx=15, pady=5, after=self.menu_preset.master)
        else:
            self.row_custom.pack_forget()

    def on_mode_change(self, val):
        key = self.get_mode_key(val)
        if key == "val_mode_blur":
            self.row_submode.pack(fill="x", padx=15, pady=(5, 15))
            self.lbl_submode.configure(text=self.lang.get("resizer_blur", "Blur (0-100):"))
            self.entry_submode.delete(0, "end")
            self.entry_submode.insert(0, "20")
        elif key == "val_mode_color":
            self.row_submode.pack(fill="x", padx=15, pady=(5, 15))
            self.lbl_submode.configure(text=self.lang.get("resizer_color", "Cor HEX:"))
            self.entry_submode.delete(0, "end")
            self.entry_submode.insert(0, "#000000")
        else:
            self.row_submode.pack_forget()

    def update_encoder_label(self):
        enc = self.hub.encoder_var.get()
        self.lbl_encoder.configure(text=f"Encoder: {enc}")

    def log(self, msg):
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")

    def add_videos(self):
        files = filedialog.askopenfilenames(
            title=self.lang.get("add_videos", "Selecionar Vídeos"),
            filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
        )
        if files:
            for f in files:
                if f not in self.input_videos:
                    self.input_videos.append(f)
                    
                    # Add to UI
                    frame = ctk.CTkFrame(self.videos_list, fg_color=COLORS["bg_main"], corner_radius=4)
                    frame.pack(fill="x", pady=2)
                    lbl = ctk.CTkLabel(frame, text=os.path.basename(f), font=("Segoe UI", 11), text_color=COLORS["text_main"], anchor="w")
                    lbl.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            msg = self.lang.get("videos_added", "{} vídeos adicionados.").format(len(files))
            self.log(msg)

    def clear_videos(self):
        self.input_videos.clear()
        for widget in self.videos_list.winfo_children():
            widget.destroy()
        self.log(self.lang.get("list_cleared", "Lista limpa."))

    def select_output_dir(self):
        d = filedialog.askdirectory(title=self.lang.get("output_folder", "Pasta de Saída"))
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
        self.progress_bar.set(percent)

    def on_finish(self, stopped, errored):
        self.btn_run.configure(
            text=self.lang.get("start_resizer", "▶ Iniciar"),
            fg_color=COLORS["btn_action"],
            hover_color=COLORS["btn_action_hover"],
            state="normal"
        )
        if stopped:
            self.log(self.lang.get("operation_cancelled", "Operação cancelada."))
        else:
            success = len(self.input_videos) - len(errored)
            self.log(self.lang.get("done", "Concluído! {} vídeos processados.").format(success))
            if errored:
                self.log(self.lang.get("errors_found", "Erros em {} vídeos.").format(len(errored)))
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        
        if not stopped and self.var_open_folder.get():
            self.open_output_dir()

    def toggle_run(self):
        if self.resizer_manager.is_running:
            self.resizer_manager.stop()
            self.btn_run.configure(state="disabled")
            return

        if not self.input_videos:
            messagebox.showwarning("Aviso", self.lang.get("add_videos_first", "Adicione vídeos primeiro."))
            return
        if not self.output_dir:
            messagebox.showwarning("Aviso", self.lang.get("select_output_first", "Selecione uma pasta de saída."))
            return

        preset = self.get_preset_key(self.var_preset.get())
        mode = self.get_mode_key(self.var_mode.get())
        submode_val = self.entry_submode.get()
        custom_w = self.entry_width.get() if preset == "val_preset_custom" else None
        custom_h = self.entry_height.get() if preset == "val_preset_custom" else None
        encoder = self.hub.encoder_var.get()

        self.btn_run.configure(
            text=self.lang.get("cancel", "⏹ Cancelar"),
            fg_color=COLORS["stop_btn"],
            hover_color=COLORS["stop_btn_hover"]
        )
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.resizer_manager.process_batch(
            self.input_videos, self.output_dir, preset, custom_w, custom_h,
            mode, submode_val, encoder, self.log, self.update_progress, self.on_finish
        )

    def update_language(self, lang):
        old_lang = self.lang if self.lang else lang
        self.lang = lang
        
        # Save keys of current selection
        preset_key = "val_preset_916"
        mode_key = "val_mode_blur"
        for k, v in old_lang.items():
            if v == self.var_preset.get() and k.startswith("val_preset_"): preset_key = k
            if v == self.var_mode.get() and k.startswith("val_mode_"): mode_key = k
            
        self.btn_add_videos.configure(text=lang.get("add_videos", "➕ Adicionar Vídeos"))
        self.btn_clear_videos.configure(text=lang.get("clear_list", "Limpar Lista"))
        self.btn_out_dir.configure(text=lang.get("output_folder", "📂 Pasta de Saída"))
        self.btn_open_out_dir.configure(text=lang.get("open", "Abrir"))
        if not self.output_dir:
            self.lbl_out_dir.configure(text=lang.get("no_folder_selected", "Nenhuma pasta selecionada"))
            
        if not self.resizer_manager.is_running:
            self.btn_run.configure(text=lang.get("start_resizer", "▶ Iniciar"))
        else:
            self.btn_run.configure(text=lang.get("cancel", "⏹ Cancelar"))
            
        self.lbl_preset.configure(text=lang.get("resizer_preset", "Proporção:"))
        self.lbl_res.configure(text=lang.get("resizer_res", "Resolução:"))
        self.lbl_mode.configure(text=lang.get("resizer_mode", "Modo:"))
        
        if mode_key == "val_mode_blur":
            self.lbl_submode.configure(text=lang.get("resizer_blur", "Blur (0-100):"))
        elif mode_key == "val_mode_color":
            self.lbl_submode.configure(text=lang.get("resizer_color", "Cor HEX:"))
            
        self.menu_preset.configure(values=[
            lang.get("val_preset_916"), lang.get("val_preset_169"), 
            lang.get("val_preset_11"), lang.get("val_preset_45"), lang.get("val_preset_custom")
        ])
        
        self.menu_mode.configure(values=[
            lang.get("val_mode_blur"), lang.get("val_mode_color"),
            lang.get("val_mode_crop"), lang.get("val_mode_stretch")
        ])
        
        # Restore selections to new language strings
        self.var_preset.set(lang.get(preset_key, lang.get("val_preset_916")))
        self.var_mode.set(lang.get(mode_key, lang.get("val_mode_blur")))
        self.chk_open_folder.configure(text=lang.get("open_folder_done", "Abrir pasta ao finalizar"))
