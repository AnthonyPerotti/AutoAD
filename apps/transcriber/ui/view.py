import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES
from core.ui_utils import AutoScrollableFrame, show_completion_popup
from apps.transcriber.transcriber import WhisperTranscriber, detect_device_and_compute

WHISPER_MODELS = ["large-v3", "large-v2", "medium", "small", "base", "tiny"]
DEVICE_OPTIONS  = ["Auto", "CUDA", "CPU"]
COMPUTE_OPTIONS = ["Auto", "int8_float16", "float32", "int8"]

_LANG_CODE_MAP = {
    "Português": "pt", "Portuguese": "pt",
    "English": "en",
    "Español": "es", "Spanish": "es",
    "Auto-detect": None,
}


class TranscriberView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.input_dir = ""
        self.output_dir = ""
        self.transcriber = WhisperTranscriber()
        self.lang = {}

        self.scroll_frame = AutoScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        self.scroll_frame.grid_columnconfigure(0, weight=1, minsize=320)
        self.scroll_frame.grid_columnconfigure(1, weight=2, minsize=420)
        self.scroll_frame.grid_rowconfigure(0, weight=1)

        self.left_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=10)

        # Input Folder Panel
        self.input_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.input_panel.pack(fill="x", pady=(0, 10))

        self.lbl_input_title = ctk.CTkLabel(self.input_panel, text="📂 Input Folder", font=FONTS["title_section"], text_color=COLORS["text_main"])
        self.lbl_input_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.lbl_input_desc = ctk.CTkLabel(self.input_panel, text="Select the folder containing video or audio files.", font=FONTS["text_small"], text_color=COLORS["text_muted"], wraplength=260)
        self.lbl_input_desc.pack(anchor="w", padx=20, pady=(0, 10))

        self.lbl_input_scope, self.opt_input_scope = self._add_option_row(self.input_panel, "Input Scope:", ["Single File", "Folder (No subfolders)", "Folder (With subfolders)"], "Folder (No subfolders)")

        self.btn_select_dir = ctk.CTkButton(
            self.input_panel, text="Select Folder", font=FONTS["button_normal"],
            fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.select_input_dir
        )
        self.btn_select_dir.pack(padx=20, pady=(10, 5), fill="x")

        self.lbl_dir = ctk.CTkLabel(self.input_panel, text="No folder selected", font=FONTS["text_small"], text_color=COLORS["text_muted"], wraplength=270, anchor="w")
        self.lbl_dir.pack(anchor="w", padx=20, pady=(0, 15))

        self.lbl_output_folder = ctk.CTkLabel(self.input_panel, text="Destination:", font=FONTS["text_normal"])
        self.lbl_output_folder.pack(anchor="w", padx=20, pady=(0, 5))

        self.btn_select_out_dir = ctk.CTkButton(
            self.input_panel, text="Same as input file(s)", font=FONTS["button_normal"],
            fg_color="transparent", border_width=1, border_color=COLORS["border"], hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            command=self.select_output_dir
        )
        self.btn_select_out_dir.pack(padx=20, pady=(0, 15), fill="x")

        # Settings Panel
        self.settings_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.settings_panel.pack(fill="x", pady=(0, 10))

        self.lbl_settings_title = ctk.CTkLabel(self.settings_panel, text="⚙ Settings", font=FONTS["title_section"], text_color=COLORS["text_main"])
        self.lbl_settings_title.pack(anchor="w", padx=20, pady=(15, 10))

        self.lbl_model, self.opt_model = self._add_option_row(self.settings_panel, "Model:", WHISPER_MODELS, "large-v3")
        self.lbl_lang,  self.opt_lang  = self._add_option_row(self.settings_panel, "Language:", ["Portuguese", "English", "Spanish", "Auto-detect"], "Portuguese")
        self.lbl_device, self.opt_device = self._add_option_row(self.settings_panel, "Device:", DEVICE_OPTIONS, "Auto", callback=self._on_device_change)
        self.lbl_compute, self.opt_compute = self._add_option_row(self.settings_panel, "Compute Type:", COMPUTE_OPTIONS, "Auto")
        self.lbl_output_mode, self.opt_output_mode = self._add_option_row(self.settings_panel, "Output Mode:", ["Grouped Single File", "Separate TXT Files"], "Grouped Single File")

        self.lbl_model_hint = ctk.CTkLabel(self.settings_panel, text="'large-v3' gives the highest accuracy.\nSmaller models are faster but less precise.", font=(FONTS["text_small"][0], 10), text_color=COLORS["text_muted"], justify="left", wraplength=260)
        self.lbl_model_hint.pack(anchor="w", padx=20, pady=(0, 15))

        # Hardware Info Panel
        self.hw_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.hw_panel.pack(fill="x")

        self.lbl_hw_title = ctk.CTkLabel(self.hw_panel, text="🖥 Detected Hardware", font=FONTS["title_section"], text_color=COLORS["text_main"])
        self.lbl_hw_title.pack(anchor="w", padx=20, pady=(15, 5))

        hw_text, hw_color = self._get_hw_display()
        self.lbl_hw = ctk.CTkLabel(self.hw_panel, text=hw_text, font=FONTS["text_normal"], text_color=hw_color)
        self.lbl_hw.pack(anchor="w", padx=20, pady=(0, 15))

        # Right Column
        self.right_col = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.right_col.grid_rowconfigure(0, weight=1)

        self.log_panel = ctk.CTkFrame(self.right_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.log_panel.pack(fill="both", expand=True)

        self.lbl_log_title = ctk.CTkLabel(self.log_panel, text="📋 Activity Log", font=FONTS["title_section"], text_color=COLORS["text_main"])
        self.lbl_log_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.log_textbox = ctk.CTkTextbox(self.log_panel, fg_color=COLORS["bg_main"], text_color=COLORS["text_main"], font=("Consolas", 11))
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.log_textbox.insert("end", "Waiting for input folder...\n")
        self.log_textbox.configure(state="disabled")

        self.progress_bar = ctk.CTkProgressBar(self.log_panel, progress_color=COLORS["hook"])
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        self.lbl_progress = ctk.CTkLabel(self.log_panel, text="", font=FONTS["text_small"], text_color=COLORS["text_muted"])
        self.lbl_progress.pack(anchor="e", padx=15, pady=(0, 10))

        row_run = ctk.CTkFrame(self.log_panel, fg_color="transparent")
        row_run.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_output_hint = ctk.CTkLabel(row_run, text="Output: transcricoes_agrupadas.txt in the input folder", font=(FONTS["text_small"][0], 10), text_color=COLORS["text_muted"])
        self.lbl_output_hint.pack(side="left")

        self.btn_run = ctk.CTkButton(
            row_run, text="▶ Start Transcription", font=FONTS["button_large"],
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"],
            text_color=COLORS["text_main"], width=200,
            command=self.toggle_run
        )
        self.btn_run.pack(side="right")

    def _add_option_row(self, parent, label_text: str, values: list, default: str, callback=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 8))
        lbl = ctk.CTkLabel(row, text=label_text, font=FONTS["text_normal"], width=100, anchor="w")
        lbl.pack(side="left")
        var = ctk.StringVar(value=default)
        opt = ctk.CTkOptionMenu(row, variable=var, values=values, font=FONTS["text_normal"], width=140, command=callback)
        opt.pack(side="left", padx=(10, 0))
        return lbl, opt

    def _get_hw_display(self):
        device, compute, desc = detect_device_and_compute("auto", "auto")
        if "cuda" in desc.lower():
            return f"✔ {desc.capitalize()}", COLORS["success"]
        return "⚡ CPU — int8", COLORS["text_muted"]

    def _on_device_change(self, value):
        if value == "CPU":
            self.opt_compute.configure(values=["int8"])
            self.opt_compute._variable.set("int8")
        else:
            self.opt_compute.configure(values=COMPUTE_OPTIONS)

    def log(self, msg):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def update_progress(self, value: float):
        self.progress_bar.set(value)
        self.lbl_progress.configure(text=f"{int(value * 100)}%")

    def select_input_dir(self):
        scope_str = self.opt_input_scope.get()
        if "Single" in scope_str or "Arquivo" in scope_str:
            path = filedialog.askopenfilename(title="Select File", filetypes=[("Media", "*.mp4 *.mp3 *.wav *.flac *.m4a")])
        else:
            path = filedialog.askdirectory(title=self.lang.get("transcriber_select_folder", "Select Folder"))
        
        if path:
            self.input_dir = path
            self.lbl_dir.configure(text=path)

    def select_output_dir(self):
        folder = filedialog.askdirectory(title=self.lang.get("transcriber_output_folder_label", "Select Output Folder"))
        if folder:
            self.output_dir = folder
            self.btn_select_out_dir.configure(text=folder)

    def toggle_run(self):
        if self.transcriber.is_running:
            self.transcriber.stop()
            self.btn_run.configure(state="disabled")
            return

        if not self.input_dir:
            messagebox.showwarning("Warning", self.lang.get("transcriber_warn_no_folder", "Please select an input first."))
            return

        lang_display = self.opt_lang.get()
        language = _LANG_CODE_MAP.get(lang_display, "pt")
        model_size = self.opt_model.get()
        device_pref = self.opt_device.get().lower()
        compute_pref = self.opt_compute.get().lower()
        
        scope_str = self.opt_input_scope.get()
        if "Single" in scope_str or "Arquivo" in scope_str:
            input_scope = "single"
        elif "Recursive" in scope_str or "subpastas" in scope_str.lower():
            input_scope = "recursive"
        else:
            input_scope = "folder"
            
        mode_str = self.opt_output_mode.get()
        if "Separate" in mode_str or "Separados" in mode_str:
            output_mode = "individual"
        else:
            output_mode = "grouped"

        def _start_batch(override_device=None):
            final_device = override_device if override_device else device_pref
            self.btn_run.configure(text=self.lang.get("transcriber_cancel", "⏹ Cancel"), fg_color=COLORS["stop_btn"], hover_color=COLORS["stop_btn_hover"])
            self.progress_bar.set(0)
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")
            self.log(self.lang.get("transcriber_log_starting", "Starting transcription..."))
            self.log(f"  Model: {model_size}  |  Language: {lang_display}  |  Device: {final_device}\n")

            self.transcriber.process_batch(
                input_path=self.input_dir,
                model_size=model_size,
                language=language,
                device_pref=final_device,
                compute_pref=compute_pref,
                input_scope=input_scope,
                output_mode=output_mode,
                output_dir=self.output_dir,
                log_callback=self._safe_log,
                progress_callback=self._safe_progress,
                finish_callback=self._on_finish,
            )

        import ctranslate2
        from core.downloader import check_cuda_dlls_exist, download_cuda_dependencies, inject_cuda_paths
        
        needs_cuda = device_pref == "cuda" or (device_pref == "auto" and ctranslate2.get_cuda_device_count() > 0)
        
        if needs_cuda and not check_cuda_dlls_exist():
            ans = messagebox.askyesno("NVIDIA CUDA", 
                self.lang.get("transcriber_dl_prompt", "Os pacotes da NVIDIA CUDA não foram encontrados.\n\nDeseja baixar as bibliotecas (~500MB) para habilitar a Placa de Vídeo?\n(Se clicar em Não, a CPU será usada)."))
            if ans:
                self.btn_run.configure(state="disabled")
                self.progress_bar.set(0)
                self.log_textbox.configure(state="normal")
                self.log_textbox.delete("1.0", "end")
                self.log(self.lang.get("transcriber_log_starting", "Starting download of CUDA libraries (this may take a while)...\n"))
                self.log_textbox.configure(state="disabled")

                def _dl_prog(pct, msg):
                    self._safe_progress(pct)
                    # We don't log every chunk to avoid freezing, only if it's a new file
                    # Or we just let downloader.py call log_callback
                    
                def _run_dl():
                    success = download_cuda_dependencies(_dl_prog, self._safe_log)
                    if success:
                        self._safe_log("\nDownload complete! Starting transcription...\n")
                        inject_cuda_paths()
                        self.after(0, lambda: _start_batch())
                    else:
                        self._safe_log("\nDownload failed! Falling back to CPU...\n")
                        self.after(0, lambda: self.opt_device.set("CPU"))
                        self.after(0, lambda: _start_batch("cpu"))

                import threading
                threading.Thread(target=_run_dl, daemon=True).start()
                return
            else:
                self.opt_device.set("CPU")
                _start_batch("cpu")
                return

        # If already exists or not using CUDA
        inject_cuda_paths()
        _start_batch()

    def _safe_log(self, msg):
        self.after(0, lambda: self.log(msg))

    def _safe_progress(self, value):
        self.after(0, lambda: self.update_progress(value))

    def _on_finish(self, success, output_path, errored=None):
        def _ui():
            self.btn_run.configure(
                text=self.lang.get("transcriber_start", "▶ Start Transcription"),
                fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"],
                state="normal"
            )
            self.progress_bar.set(1.0 if success else self.progress_bar.get())

            if success:
                self.log("\n✅ Transcription complete!")
                self.log(f"📄 Saved to:\n   {output_path}")
                show_completion_popup(self, self.lang, "Batch Transcriber", output_path)
            elif output_path is None:
                self.log("\n✖ Process ended with a critical error.")
            else:
                self.log(f"\n⚠ Completed with {len(errored or [])} error(s).")
                if errored:
                    self.log("Files with errors:")
                    for f in errored:
                        self.log(f"  • {f}")
        self.after(0, _ui)

    def update_language(self, lang):
        self.lang = lang
        self.lbl_input_title.configure(text=lang.get("transcriber_input_title", "📂 Input Folder"))
        self.lbl_input_desc.configure(text=lang.get("transcriber_input_desc", "Select the folder containing video or audio files."))
        self.btn_select_dir.configure(text=lang.get("transcriber_select_folder", "Select Folder"))
        
        if not self.input_dir:
            self.lbl_dir.configure(text=lang.get("transcriber_no_folder", "No folder selected"))
            
        self.lbl_output_folder.configure(text=lang.get("transcriber_output_folder_label", "Destination:"))
        if not self.output_dir:
            self.btn_select_out_dir.configure(text=lang.get("transcriber_output_same_as_input", "Same as input file(s)"))
            
        self.lbl_settings_title.configure(text=lang.get("transcriber_settings_title", "⚙ Settings"))
        self.lbl_model.configure(text=lang.get("transcriber_model_label", "Model:"))
        self.lbl_lang.configure(text=lang.get("transcriber_lang_label", "Language:"))
        self.lbl_device.configure(text=lang.get("transcriber_device_label", "Device:"))
        self.lbl_compute.configure(text=lang.get("transcriber_compute_label", "Compute Type:"))
        
        self.lbl_input_scope.configure(text=lang.get("transcriber_input_scope_label", "Input Scope:"))
        opts_scope = [
            lang.get("transcriber_scope_single", "Single File"),
            lang.get("transcriber_scope_folder", "Folder (No subfolders)"),
            lang.get("transcriber_scope_recursive", "Folder (With subfolders)")
        ]
        self.opt_input_scope.configure(values=opts_scope)
        if self.opt_input_scope.get() not in opts_scope:
            self.opt_input_scope.set(opts_scope[1])
            
        self.lbl_output_mode.configure(text=lang.get("transcriber_output_mode_label", "Output Mode:"))
        opts_mode = [
            lang.get("transcriber_mode_grouped", "Grouped Single File"),
            lang.get("transcriber_mode_individual", "Separate TXT Files")
        ]
        self.opt_output_mode.configure(values=opts_mode)
        if self.opt_output_mode.get() not in opts_mode:
            self.opt_output_mode.set(opts_mode[0])

        self.lbl_model_hint.configure(text=lang.get("transcriber_model_hint", "'large-v3' gives the highest accuracy.\nSmaller models are faster but less precise."))
        self.lbl_hw_title.configure(text=lang.get("transcriber_hw_title", "🖥 Detected Hardware"))
        self.lbl_log_title.configure(text=lang.get("transcriber_log_title", "📋 Activity Log"))
        self.lbl_output_hint.configure(text=lang.get("transcriber_output_hint", "Output: transcricoes_agrupadas.txt in the input folder"))
        if not self.transcriber.is_running:
            self.btn_run.configure(text=lang.get("transcriber_start", "▶ Start Transcription"))
        else:
            self.btn_run.configure(text=lang.get("transcriber_cancel", "⏹ Cancel"))

        # Update language dropdown options
        lang_opts_str = lang.get("transcriber_lang_options", "Portuguese,English,Spanish,Auto-detect")
        lang_opts = [o.strip() for o in lang_opts_str.split(",")]
        self.opt_lang.configure(values=lang_opts)
