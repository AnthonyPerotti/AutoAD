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

        self.btn_select_dir = ctk.CTkButton(
            self.input_panel, text="Select Folder", font=FONTS["button_normal"],
            fg_color=COLORS["hook"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.select_input_dir
        )
        self.btn_select_dir.pack(padx=20, pady=(0, 10), fill="x")

        self.lbl_dir = ctk.CTkLabel(self.input_panel, text="No folder selected", font=FONTS["text_small"], text_color=COLORS["text_muted"], wraplength=270, anchor="w")
        self.lbl_dir.pack(anchor="w", padx=20, pady=(0, 15))

        # Settings Panel
        self.settings_panel = ctk.CTkFrame(self.left_col, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.settings_panel.pack(fill="x", pady=(0, 10))

        self.lbl_settings_title = ctk.CTkLabel(self.settings_panel, text="⚙ Settings", font=FONTS["title_section"], text_color=COLORS["text_main"])
        self.lbl_settings_title.pack(anchor="w", padx=20, pady=(15, 10))

        self.lbl_model, self.opt_model = self._add_option_row(self.settings_panel, "Model:", WHISPER_MODELS, "large-v3")
        self.lbl_lang,  self.opt_lang  = self._add_option_row(self.settings_panel, "Language:", ["Portuguese", "English", "Spanish", "Auto-detect"], "Portuguese")
        self.lbl_device, self.opt_device = self._add_option_row(self.settings_panel, "Device:", DEVICE_OPTIONS, "Auto", callback=self._on_device_change)
        self.lbl_compute, self.opt_compute = self._add_option_row(self.settings_panel, "Compute Type:", COMPUTE_OPTIONS, "Auto")

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
        if "cuda_fallback" in desc:
            name = desc.replace("cuda_fallback:", "")
            return f"✔ CUDA (float32) — {name} [Maxwell]", COLORS["body"]
        elif "cuda" in desc:
            name = desc.replace("cuda:", "")
            return f"✔ CUDA (int8_float16) — {name}", COLORS["success"]
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
        folder = filedialog.askdirectory(title=self.lang.get("transcriber_select_folder", "Select Input Folder"))
        if folder:
            self.input_dir = folder
            self.lbl_dir.configure(text=folder)

    def toggle_run(self):
        if self.transcriber.is_running:
            self.transcriber.stop()
            self.btn_run.configure(state="disabled")
            return

        if not self.input_dir:
            messagebox.showwarning("Warning", self.lang.get("transcriber_warn_no_folder", "Please select an input folder first."))
            return

        lang_display = self.opt_lang._variable.get()
        language = _LANG_CODE_MAP.get(lang_display, "pt")
        model_size = self.opt_model._variable.get()
        device_pref = self.opt_device._variable.get().lower()
        compute_pref = self.opt_compute._variable.get().lower()

        self.btn_run.configure(text=self.lang.get("transcriber_cancel", "⏹ Cancel"), fg_color=COLORS["stop_btn"], hover_color=COLORS["stop_btn_hover"])
        self.progress_bar.set(0)
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.log(self.lang.get("transcriber_log_starting", "Starting batch transcription..."))
        self.log(f"  Model: {model_size}  |  Language: {lang_display}  |  Device: {device_pref}\n")

        self.transcriber.process_batch(
            input_dir=self.input_dir,
            model_size=model_size,
            language=language,
            device_pref=device_pref,
            compute_pref=compute_pref,
            log_callback=self._safe_log,
            progress_callback=self._safe_progress,
            finish_callback=self._on_finish,
        )

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
        self.lbl_settings_title.configure(text=lang.get("transcriber_settings_title", "⚙ Settings"))
        self.lbl_model.configure(text=lang.get("transcriber_model_label", "Model:"))
        self.lbl_lang.configure(text=lang.get("transcriber_lang_label", "Language:"))
        self.lbl_device.configure(text=lang.get("transcriber_device_label", "Device:"))
        self.lbl_compute.configure(text=lang.get("transcriber_compute_label", "Compute Type:"))
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
