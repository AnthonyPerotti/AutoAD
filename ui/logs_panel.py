# pyrefly: ignore [missing-import]
import customtkinter as ctk


class LogsPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            corner_radius=10,
            fg_color="#1e1e24",
            border_width=1,
            border_color="#3f3f46",
        )

        # Header Row
        self.header_row = ctk.CTkFrame(self, fg_color="transparent")
        self.header_row.pack(fill="x", padx=20, pady=(15, 10))

        self.logs_title = ctk.CTkLabel(
            self.header_row, 
            text="ACTIVITY LOGS 📋", 
            font=("Segoe UI", 14, "bold"), 
            text_color="#d1d5db"
        )
        self.logs_title.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.header_row, 
            text="System Status: Online 🟢", 
            font=("Segoe UI", 12), 
            text_color="#9ca3af"
        )
        self.status_label.pack(side="right")

        # Container for logs and logo
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.logs_box = ctk.CTkTextbox(
            self.content_frame,
            height=120,
            font=("Consolas", 12),
            fg_color="#18181b", # Darker background
            text_color="#a1a1aa",
            border_width=0,
            wrap="word",
        )
        self.logs_box.pack(fill="both", expand=True)

        self.logs_box.insert("end", "Sistema iniciado.\n")
        self.logs_box.configure(state="disabled")

        # Bottom right logo text overlaid using place, or we can add it below logs box
        # Since logs box fills, we'll put it in a bottom row
        self.bottom_row = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=20)
        self.bottom_row.pack(fill="x", pady=(5, 0))
        
        self.logo_label = ctk.CTkLabel(
            self.bottom_row,
            text="AutoAD v1.5",
            font=("Segoe UI", 14, "bold"),
            text_color="#d1d5db"
        )
        self.logo_label.pack(side="right")


    def add_log(self, text):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        formatted = f"{now}    {text}"

        self.logs_box.configure(state="normal")
        self.logs_box.insert("end", f"{formatted}\n")
        self.logs_box.see("end")
        self.logs_box.configure(state="disabled")

    def update_language(self, lang):
        self.logs_title.configure(text=lang["logs"] + " 📋")
