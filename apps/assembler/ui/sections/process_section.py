# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.theme import COLORS, FONTS, SIZES


class ControlsPanel(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        total_var,
        progress_var,
        progress_text_var,
        auto_open_var,
        on_generate,
        on_stop,
        on_open_output,
        on_auto_open_change,
    ):
        super().__init__(
            parent,
            corner_radius=SIZES["corner_panel"],
            fg_color=COLORS["bg_panel"],
            border_width=SIZES["border_thin"],
            border_color=COLORS["border"],
        )

        # Container with padding
        self.container = ctk.CTkFrame(self, fg_color=COLORS["transparent"])
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Title
        self.control_title = ctk.CTkLabel(
            self.container,
            text="CONTROLES",
            font=FONTS["title_main"],
            text_color=COLORS["text_light"],
        )
        self.control_title.pack(anchor="w", pady=(0, 15))

        # Row 1: Total Box and EXPORT Button
        self.row1 = ctk.CTkFrame(self.container, fg_color=COLORS["transparent"])
        self.row1.pack(fill="x", pady=(0, 20))

        # Left: Total Box
        self.total_box = ctk.CTkFrame(
            self.row1,
            corner_radius=8,
            fg_color=COLORS["bg_main"],
            border_width=SIZES["border_thin"],
            border_color=COLORS["border"],
            width=120,
            height=60
        )
        self.total_box.pack(side="left", fill="y")
        self.total_box.pack_propagate(False)
        
        self.total_lbl_top = ctk.CTkLabel(
            self.total_box,
            text="TOTAL DE ITENS",
            font=("Segoe UI", 9, "bold"),
            text_color=COLORS["text_muted"]
        )
        self.total_lbl_top.pack(pady=(8, 0))

        self.total_label = ctk.CTkLabel(
            self.total_box,
            textvariable=total_var,
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_main"],
        )
        self.total_label.pack(pady=(0, 5))

        self.is_generating = False
        self.on_generate = on_generate
        self.on_stop = on_stop

        # Right: EXPORT button with icon
        self.btn_generate = ctk.CTkButton(
            self.row1,
            text="📤 EXPORTAR CONTEÚDO",
            height=60,
            corner_radius=SIZES["corner_button"],
            fg_color=COLORS["export_btn"],
            text_color=COLORS["text_main"],
            hover_color=COLORS["export_btn_hover"],
            font=("Segoe UI", 14, "bold"),
            command=self.toggle_action,
        )
        self.btn_generate.pack(side="left", fill="both", expand=True, padx=(15, 0))

        # Row 2: Progress Bar and percentage
        self.progress_row = ctk.CTkFrame(self.container, fg_color=COLORS["transparent"])
        self.progress_row.pack(fill="x", pady=(0, 10))

        self.progressbar = ctk.CTkProgressBar(
            self.progress_row, 
            height=8, 
            corner_radius=SIZES["corner_pill"], 
            progress_color=COLORS["export_btn_hover"], 
            fg_color=COLORS["border"]
        )
        self.progressbar.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.progressbar.set(0)

        self.progress_percent = ctk.CTkLabel(
            self.progress_row,
            text="0%",
            font=FONTS["text_small"],
            text_color=COLORS["text_light"]
        )
        self.progress_percent.pack(side="right")

        # Row 3: Progress text
        self.progress_label = ctk.CTkLabel(
            self.container,
            textvariable=progress_text_var,
            font=FONTS["text_small"],
            text_color=COLORS["text_muted"],
        )
        self.progress_label.pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            self.container, text="", font=FONTS["text_small"], text_color="#22c55e"
        )

    def toggle_action(self):
        if self.is_generating:
            if self.on_stop: self.on_stop()
        else:
            if self.on_generate: self.on_generate()

    def set_generating_state(self, is_generating):
        self.is_generating = is_generating
        self.update_button_text()

    def update_button_text(self):
        if self.is_generating:
            txt = "⏹ " + (self.lang["stop"] if hasattr(self, 'lang') else "STOP EXPORT")
            self.btn_generate.configure(text=txt, fg_color=COLORS["stop_btn"], hover_color=COLORS["stop_btn_hover"])
        else:
            txt = "📤 " + (self.lang["generate"] if hasattr(self, 'lang') else "EXPORT CONTENT")
            self.btn_generate.configure(text=txt, fg_color=COLORS["export_btn"], hover_color=COLORS["export_btn_hover"])

    def update_language(self, lang):
        self.lang = lang
        self.control_title.configure(text=lang["controls"])
        self.total_lbl_top.configure(text=lang["total"])
        self.update_button_text()
