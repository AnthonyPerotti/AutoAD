# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.theme import COLORS, FONTS, SIZES


class LogsPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(
            parent,
            corner_radius=SIZES["corner_panel"],
            fg_color=COLORS["bg_panel"],
            border_width=SIZES["border_thin"],
            border_color=COLORS["border"],
        )

        # Header Row
        self.header_row = ctk.CTkFrame(self, fg_color=COLORS["transparent"])
        self.header_row.pack(fill="x", padx=20, pady=(12, 8))

        self.logs_title = ctk.CTkLabel(
            self.header_row, 
            text="LOGS DE ATIVIDADE", 
            font=FONTS["title_main"], 
            text_color=COLORS["text_light"]
        )
        self.logs_title.pack(side="left")

        # Clear Logs button on the right
        self.btn_clear = ctk.CTkButton(
            self.header_row,
            text="🗑 Limpar Logs",
            width=110,
            height=28,
            corner_radius=6,
            fg_color=COLORS["transparent"],
            hover_color=COLORS["border"],
            border_width=SIZES["border_thin"],
            border_color=COLORS["border"],
            text_color=COLORS["text_light"],
            font=FONTS["text_small"],
            command=self.limpar_logs
        )
        self.btn_clear.pack(side="right")

        # Container for logs
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["transparent"])
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.logs_box = ctk.CTkTextbox(
            self.content_frame,
            height=100,
            font=("Consolas", 11),
            fg_color=COLORS["bg_main"],
            text_color="#4ade80", # Sleek terminal green
            border_width=0,
            wrap="word",
        )
        self.logs_box.pack(fill="both", expand=True)

        self.logs_box.insert("end", "● [00:00:00] Sistema iniciado com sucesso.\n")
        self.logs_box.configure(state="disabled")

    def add_log(self, text):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        formatted = f"● [{now}] {text}"

        self.logs_box.configure(state="normal")
        self.logs_box.insert("end", f"{formatted}\n")
        self.logs_box.see("end")
        self.logs_box.configure(state="disabled")

    def limpar_logs(self):
        self.logs_box.configure(state="normal")
        self.logs_box.delete("1.0", "end")
        self.logs_box.configure(state="disabled")

    def update_language(self, lang):
        self.logs_title.configure(text=lang["logs"])
        clear_text = "🗑 Limpar Logs" if lang["title"].lower().find("v1.6") != -1 and lang["logs"].startswith("LOGS") else "🗑 Clear Logs"
        if "limpar" in clear_text.lower() and lang["title"].lower().find("v1.6") != -1:
            self.btn_clear.configure(text="🗑 Limpar Logs")
        else:
            self.btn_clear.configure(text="🗑 Clear Logs")

