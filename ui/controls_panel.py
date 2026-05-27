import customtkinter as ctk


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
            corner_radius=20,
            fg_color="#161616",
            border_width=1,
            border_color="#3f3f46",
        )

        # ============================================
        # HEADER
        # ============================================

        self.control_title = ctk.CTkLabel(
            self,
            text="⚡ CONTROLES",
            font=("Segoe UI", 22, "bold"),
            text_color="#f3f4f6",
        )

        self.control_title.pack(anchor="w", padx=20, pady=(15, 5))

        # ============================================
        # TOTAL
        # ============================================

        self.total_label = ctk.CTkLabel(
            self,
            textvariable=total_var,
            font=("Segoe UI", 15, "bold"),
            text_color="#9ca3af",
        )

        self.total_label.pack(anchor="w", padx=20, pady=(0, 15))

        # ============================================
        # CONTENT
        # ============================================

        controls_content = ctk.CTkFrame(self, fg_color="transparent")

        controls_content.pack(fill="x", padx=20, pady=(0, 20))

        # ============================================
        # LEFT
        # ============================================

        left_controls = ctk.CTkFrame(controls_content, fg_color="transparent")

        left_controls.pack(side="left", anchor="n")

        # ============================================
        # RIGHT
        # ============================================

        right_controls = ctk.CTkFrame(controls_content, fg_color="transparent")

        right_controls.pack(side="right", anchor="ne")

        # ============================================
        # BUTTONS
        # ============================================

        buttons_frame = ctk.CTkFrame(left_controls, fg_color="transparent")

        buttons_frame.pack(anchor="w")

        self.btn_generate = ctk.CTkButton(
            buttons_frame,
            text="GERAR VÍDEOS",
            width=260,
            height=52,
            corner_radius=16,
            fg_color="#2563eb",
            hover_color="#3b82f6",
            font=("Segoe UI", 16, "bold"),
            command=on_generate,
        )

        self.btn_generate.pack(side="left", padx=(0, 15), pady=(0, 20))

        self.btn_stop = ctk.CTkButton(
            buttons_frame,
            text="STOP",
            width=140,
            height=52,
            corner_radius=16,
            fg_color="#991b1b",
            hover_color="#dc2626",
            font=("Segoe UI", 16, "bold"),
            command=on_stop,
        )

        self.btn_stop.pack(side="left", pady=(0, 20))

        # ============================================
        # OUTPUT OPTIONS
        # ============================================

        output_options = ctk.CTkFrame(right_controls, fg_color="transparent")

        output_options.pack(anchor="e")

        self.auto_open_checkbox = ctk.CTkCheckBox(
            output_options,
            text="Open destination at end",
            variable=auto_open_var,
            font=("Segoe UI", 14),
            command=on_auto_open_change,
        )

        self.auto_open_checkbox.pack(anchor="w", pady=(0, 10))

        self.btn_open_output = ctk.CTkButton(
            output_options,
            text="Open Output Folder",
            height=42,
            corner_radius=12,
            fg_color="#374151",
            hover_color="#4b5563",
            command=on_open_output,
        )

        self.btn_open_output.pack(anchor="w")

        # ============================================
        # PROGRESS TITLE
        # ============================================

        self.progress_title = ctk.CTkLabel(
            self, text="PROGRESSO", font=("Segoe UI", 14, "bold"), text_color="#d1d5db"
        )

        self.progress_title.pack(anchor="w", padx=20)

        # ============================================
        # PROGRESS BAR
        # ============================================

        self.progressbar = ctk.CTkProgressBar(
            self, width=700, height=18, corner_radius=10, progress_color="#2563eb"
        )

        self.progressbar.pack(fill="x", padx=20, pady=(10, 5))

        self.progressbar.set(0)

        # ============================================
        # PROGRESS LABEL
        # ============================================

        self.progress_label = ctk.CTkLabel(
            self,
            textvariable=progress_text_var,
            font=("Segoe UI", 13),
            text_color="#9ca3af",
        )

        self.progress_label.pack(anchor="w", padx=20, pady=(0, 20))

        # ============================================
        # STATUS
        # ============================================

        self.status_label = ctk.CTkLabel(
            self, text="Pronto", font=("Segoe UI", 14, "bold"), text_color="#22c55e"
        )

        self.status_label.pack(anchor="w", padx=20, pady=(0, 20))
