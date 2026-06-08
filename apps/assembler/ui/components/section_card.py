# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.theme import COLORS, FONTS, SIZES

class SectionCard(ctk.CTkFrame):
    def __init__(self, parent, title, color_key, icon="📂", subtitle=""):
        self.accent_color = COLORS.get(color_key, COLORS["border"])
        super().__init__(
            parent,
            corner_radius=SIZES["corner_panel"],
            fg_color=COLORS["bg_panel"],
            border_width=SIZES["border_width"],
            border_color=self.accent_color,
        )
        self.is_collapsed = False

        # Header Row Container
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS["transparent"], height=48, cursor="hand2")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 5))
        self.header_frame.pack_propagate(False)

        # Icon Frame
        self.icon_frame = ctk.CTkFrame(
            self.header_frame, 
            fg_color=self.accent_color, 
            width=36, 
            height=36, 
            corner_radius=8
        )
        self.icon_frame.pack(side="left", padx=(0, 12))
        self.icon_frame.pack_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_frame, 
            text=icon, 
            font=("Segoe UI", 16), 
            text_color=COLORS["text_main"]
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Text container (Title and Subtitle)
        self.text_container = ctk.CTkFrame(self.header_frame, fg_color=COLORS["transparent"])
        self.text_container.pack(side="left", fill="both", expand=True)

        self.title_label = ctk.CTkLabel(
            self.text_container, 
            text=title, 
            font=FONTS["title_main"], 
            text_color=COLORS["text_main"],
            anchor="w"
        )
        self.title_label.pack(anchor="w", pady=(0, 0))

        self.subtitle_label = ctk.CTkLabel(
            self.text_container, 
            text=subtitle, 
            font=FONTS["text_small"], 
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.subtitle_label.pack(anchor="w")

        # Chevron Arrow on Far Right
        self.chevron_label = ctk.CTkLabel(
            self.header_frame, 
            text="∧", 
            font=("Segoe UI", 14, "bold"), 
            text_color=COLORS["text_muted"]
        )
        self.chevron_label.pack(side="right", padx=(10, 5))

        # Content Container for subclasses to inject widgets
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["transparent"])
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        # Bind click to header area to toggle collapse
        for w in [self.header_frame, self.icon_frame, self.icon_label, self.text_container, self.title_label, self.subtitle_label, self.chevron_label]:
            w.bind("<Button-1>", lambda e: self.toggle_collapse())

    def toggle_collapse(self):
        if self.is_collapsed:
            self.content_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))
            self.chevron_label.configure(text="∧")
            self.is_collapsed = False
        else:
            self.content_frame.pack_forget()
            self.chevron_label.configure(text="∨")
            self.is_collapsed = True

    def set_title(self, title):
        self.title_label.configure(text=title)

    def set_subtitle(self, subtitle):
        self.subtitle_label.configure(text=subtitle)
