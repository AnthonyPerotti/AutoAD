import os
import glob
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES
from core.ui_utils import AutoScrollableFrame
from apps.subtitles.renderer import SubtitlesManager

class SubtitlesView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.input_videos = []
        self.output_dir = ""
        self.subtitle_path = ""
        self.subtitles_manager = SubtitlesManager()

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

        # Mode Selection
        self.row_mode = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        self.row_mode.pack(fill="x", padx=15, pady=(15, 5))
        
        self.var_mode = ctk.StringVar(value="manual")
        self.rb_manual = ctk.CTkRadioButton(self.row_mode, text="Manual (.srt/.ass)", variable=self.var_mode, value="manual", command=self.on_mode_change, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_main"])
        self.rb_manual.pack(side="left", padx=(0, 15))
        
        self.rb_auto = ctk.CTkRadioButton(self.row_mode, text="Auto AI (Whisper)", variable=self.var_mode, value="auto", command=self.on_mode_change, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_muted"])
        self.rb_auto.pack(side="left")

        # --- AUTO MODE FRAME ---
        self.auto_frame = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        self.lbl_auto_dev = ctk.CTkLabel(self.auto_frame, text="Feature in development.\nPlease use Manual mode for now.", text_color=COLORS["hook"], font=("Segoe UI", 12, "bold"))
        self.lbl_auto_dev.pack(pady=20)

        # --- MANUAL MODE FRAME ---
        self.manual_frame = ctk.CTkFrame(self.options_panel, fg_color="transparent")
        
        self.btn_sel_sub = ctk.CTkButton(self.manual_frame, text="Select Subtitle File", fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], command=self.select_subtitle)
        self.btn_sel_sub.pack(pady=(5, 5), anchor="w")
        
        self.lbl_sub_path = ctk.CTkLabel(self.manual_frame, text="No subtitle selected", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        self.lbl_sub_path.pack(pady=(0, 10), anchor="w")

        # Style Options (only useful for SRT, ASS defines its own)
        self.style_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        self.style_frame.pack(fill="x")
        
        row_s1 = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        row_s1.pack(fill="x", pady=5)
        
        self.lbl_font = ctk.CTkLabel(row_s1, text="Font:", width=80, anchor="w", font=("Segoe UI", 11))
        self.lbl_font.pack(side="left")
        self.entry_font = ctk.CTkEntry(row_s1, placeholder_text="Arial")
        self.entry_font.insert(0, "Arial")
        self.entry_font.pack(side="left", fill="x", expand=True, padx=(0, 10))

        row_s2 = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        row_s2.pack(fill="x", pady=5)

        self.lbl_size = ctk.CTkLabel(row_s2, text="Size:", width=80, anchor="w", font=("Segoe UI", 11))
        self.lbl_size.pack(side="left")
        self.entry_size = ctk.CTkEntry(row_s2, width=60)
        self.entry_size.insert(0, "24")
        self.entry_size.pack(side="left", padx=(0, 15))
        
        self.lbl_color = ctk.CTkLabel(row_s2, text="Color:", width=60, anchor="w", font=("Segoe UI", 11))
        self.lbl_color.pack(side="left")
        self.entry_color = ctk.CTkEntry(row_s2, width=80, placeholder_text="#FFFFFF")
        self.entry_color.insert(0, "#FFFFFF")
        self.entry_color.pack(side="left")

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
            row_bottom, text="▶ Burn Subtitles", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"], text_color=COLORS["text_main"],
            width=200,
            command=self.toggle_run
        )
        self.btn_run.pack(side="right")
        
        self.update_encoder_label()
        self.hub.encoder_var.trace_add("write", lambda *args: self.update_encoder_label())
        
        self.lang = {}
        self.on_mode_change() # Init layout

    def on_mode_change(self):
        mode = self.var_mode.get()
        self.manual_frame.pack_forget()
        self.auto_frame.pack_forget()
        
        if mode == "manual":
            self.manual_frame.pack(fill="x", padx=15, pady=5)
        else:
            self.auto_frame.pack(fill="x", padx=15, pady=5)

    def select_subtitle(self):
        f = filedialog.askopenfilename(title=self.lang.get("sub_select", "Select Subtitle"), filetypes=[("Subtitles", "*.srt *.ass")])
        if f:
            self.subtitle_path = f
            self.lbl_sub_path.configure(text=os.path.basename(f))

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
            messagebox.showwarning("Warning", self.lang.get("no_folder_selected", "No folder selected."))

    def update_progress(self, percent, current, total):
        pass

    def on_finish(self, stopped, errored):
        self.btn_run.configure(
            text=self.lang.get("start_subtitles", "▶ Burn Subtitles"),
            fg_color=COLORS["btn_action"],
            hover_color=COLORS["btn_action_hover"],
            state="normal"
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
        
        if not stopped and self.var_open_folder.get():
            self.open_output_dir()

    def toggle_run(self):
        if self.subtitles_manager.is_running:
            self.subtitles_manager.stop()
            self.btn_run.configure(state="disabled")
            return

        if self.var_mode.get() == "auto":
            messagebox.showinfo("In Development", "Auto-Subtitle using AI is currently in development.\nPlease use Manual mode.")
            return

        if not self.input_videos:
            messagebox.showwarning("Warning", self.lang.get("add_videos_first", "Add videos first."))
            return
        if not self.output_dir:
            messagebox.showwarning("Warning", self.lang.get("select_output_first", "Select an output folder."))
            return

        if not self.subtitle_path:
            messagebox.showwarning("Warning", self.lang.get("sub_no_file", "No subtitle file selected."))
            return

        self.btn_run.configure(
            text=self.lang.get("cancel", "⏹ Cancel"),
            fg_color=COLORS["stop_btn"],
            hover_color=COLORS["stop_btn_hover"]
        )
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.subtitles_manager.process_batch(
            self.input_videos, self.output_dir, self.subtitle_path,
            self.entry_font.get(), self.entry_size.get(), self.entry_color.get(),
            self.hub.encoder_var.get(),
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
            
        if not self.subtitles_manager.is_running:
            self.btn_run.configure(text=lang.get("start_subtitles", "▶ Burn Subtitles"))
        else:
            self.btn_run.configure(text=lang.get("cancel", "⏹ Cancel"))
            
        self.rb_manual.configure(text=lang.get("sub_manual", "Manual (.srt/.ass)"))
        self.rb_auto.configure(text=lang.get("sub_auto", "Auto AI (Whisper)"))
        self.btn_sel_sub.configure(text=lang.get("sub_select", "Select Subtitle File"))
        
        if not self.subtitle_path:
            self.lbl_sub_path.configure(text=lang.get("sub_no_file", "No subtitle selected"))
            
        self.lbl_font.configure(text=lang.get("sub_font", "Font:"))
        self.lbl_size.configure(text=lang.get("sub_size", "Size:"))
        self.lbl_color.configure(text=lang.get("sub_color", "Color:"))
        self.lbl_auto_dev.configure(text=lang.get("sub_auto_dev", "Feature in development.\nPlease use Manual mode for now."))
        self.chk_open_folder.configure(text=lang.get("open_folder_done", "Abrir pasta ao finalizar"))
