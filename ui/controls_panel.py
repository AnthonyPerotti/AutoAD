# pyrefly: ignore [missing-import]
import customtkinter as ctk


class ControlsPanel(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        total_var,
        progress_var,
        progress_text_var,
        auto_open_var,  # Not used visually here anymore, moved to OUTPUT logically in main window
        on_generate,
        on_stop,
        on_open_output, # Also moved to OUTPUT conceptually, but kept in signature if needed
        on_auto_open_change,
    ):
        super().__init__(
            parent,
            corner_radius=10,
            fg_color="#1e1e24",
            border_width=1,
            border_color="#52525b", # Grey border
        )

        # Container with padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header Title
        self.control_title = ctk.CTkLabel(
            self.container,
            text="PROCESS CONTROLES",
            font=("Segoe UI", 16),
            text_color="#d1d5db",
        )
        self.control_title.pack(anchor="w", pady=(0, 15))

        # Row 1: Total Box and EXPORT Button
        self.row1 = ctk.CTkFrame(self.container, fg_color="transparent")
        self.row1.pack(fill="x", pady=(0, 20))

        # Left: Total Box
        self.total_box = ctk.CTkFrame(
            self.row1,
            corner_radius=8,
            fg_color="#18181b",
            border_width=1,
            border_color="#3f3f46"
        )
        self.total_box.pack(side="left", fill="y", ipadx=20)
        
        self.total_lbl_top = ctk.CTkLabel(
            self.total_box,
            text="TOTAL",
            font=("Segoe UI", 10),
            text_color="#9ca3af"
        )
        self.total_lbl_top.pack(pady=(10, 0))

        self.total_label = ctk.CTkLabel(
            self.total_box,
            textvariable=total_var,
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff",
        )
        self.total_label.pack(pady=(0, 10))

        self.is_generating = False
        self.on_generate = on_generate
        self.on_stop = on_stop

        # Right: EXPORT button
        self.btn_generate = ctk.CTkButton(
            self.row1,
            text="EXPORT",
            height=60,
            corner_radius=10,
            fg_color="#0d9488",
            hover_color="#14b8a6",
            font=("Segoe UI", 22, "bold"),
            command=self.toggle_action,
        )
        self.btn_generate.pack(side="left", fill="both", expand=True, padx=(15, 0))

        # Row 2: Progress Bar
        self.progressbar = ctk.CTkProgressBar(
            self.container, height=12, corner_radius=6, progress_color="#14b8a6", fg_color="#3f3f46"
        )
        self.progressbar.pack(fill="x", pady=(0, 10))
        self.progressbar.set(0)

        # Row 3: Progress text
        self.progress_label = ctk.CTkLabel(
            self.container,
            textvariable=progress_text_var,
            font=("Segoe UI", 12),
            text_color="#d1d5db",
        )
        self.progress_label.pack(anchor="w")

        # Status Label (Hidden or used for something else, since mock doesn't have it here)
        self.status_label = ctk.CTkLabel(
            self.container, text="", font=("Segoe UI", 12), text_color="#22c55e"
        )
        # self.status_label.pack(anchor="w") # Not packing, let's keep it accessible

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
            txt = self.lang["stop"] if hasattr(self, 'lang') else "STOP"
            self.btn_generate.configure(text=txt, fg_color="#991b1b", hover_color="#dc2626")
        else:
            txt = self.lang["generate"] if hasattr(self, 'lang') else "EXPORT"
            self.btn_generate.configure(text=txt, fg_color="#0d9488", hover_color="#14b8a6")

    def update_language(self, lang):
        self.lang = lang
        self.control_title.configure(text=lang["controls"])
        self.total_lbl_top.configure(text=lang["total"])
        self.update_button_text()
