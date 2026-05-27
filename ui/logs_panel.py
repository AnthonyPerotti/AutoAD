import customtkinter as ctk


class LogsPanel(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            corner_radius=20,
            fg_color="#161616",
            border_width=1,
            border_color="#3f3f46",
        )

        # ============================================
        # TITLE
        # ============================================

        self.logs_title = ctk.CTkLabel(
            self, text="📜 LOGS", font=("Segoe UI", 22, "bold"), text_color="#f3f4f6"
        )

        self.logs_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # TEXTBOX
        # ============================================

        self.logs_box = ctk.CTkTextbox(
            self,
            height=220,
            font=("Consolas", 13),
            fg_color="#0f172a",
            border_width=1,
            border_color="#374151",
        )

        self.logs_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.logs_box.insert("end", "Sistema iniciado.\n")

        self.logs_box.configure(state="disabled")

    def add_log(self, text):

        self.logs_box.configure(state="normal")

        self.logs_box.insert("end", f"{text}\n")

        self.logs_box.see("end")

        self.logs_box.configure(state="disabled")
