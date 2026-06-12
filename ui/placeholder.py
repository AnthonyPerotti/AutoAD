# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.theme import COLORS, FONTS, SIZES

class PlaceholderModuleView(ctk.CTkFrame):
    """Generic placeholder view for modules that are not yet implemented."""

    def __init__(self, parent, icon, title, description, features):
        super().__init__(parent, fg_color="transparent")

        # Center container
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.place(relx=0.5, rely=0.45, anchor="center")

        # Icon
        self.icon_lbl = ctk.CTkLabel(
            self.center, text=icon, font=("Segoe UI", 48)
        )
        self.icon_lbl.pack(pady=(0, 15))

        # Title
        self.title_lbl = ctk.CTkLabel(
            self.center, text=title,
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["text_main"]
        )
        self.title_lbl.pack(pady=(0, 8))

        # "Coming soon" badge
        self.badge_frame = ctk.CTkFrame(
            self.center, fg_color=COLORS["hook"],
            corner_radius=12, height=28
        )
        self.badge_frame.pack(pady=(0, 20))
        self.badge_lbl = ctk.CTkLabel(
            self.badge_frame, text="  EM BREVE  ",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["text_main"]
        )
        self.badge_lbl.pack(padx=12, pady=4)

        # Description
        self.desc_lbl = ctk.CTkLabel(
            self.center, text=description,
            font=FONTS["text_normal"],
            text_color=COLORS["text_muted"],
            wraplength=400, justify="center"
        )
        self.desc_lbl.pack(pady=(0, 25))

        # Features list inside a card
        self.features_card = ctk.CTkFrame(
            self.center,
            fg_color=COLORS["bg_panel"],
            border_width=SIZES["border_width"],
            border_color=COLORS["border"],
            corner_radius=SIZES["corner_panel"]
        )
        self.features_card.pack(fill="x", padx=20)

        self.features_title = ctk.CTkLabel(
            self.features_card, text="Funcionalidades planejadas:",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_light"],
            anchor="w"
        )
        self.features_title.pack(fill="x", padx=20, pady=(15, 10))

        for feat in features:
            feat_lbl = ctk.CTkLabel(
                self.features_card, text=f"  •  {feat}",
                font=FONTS["text_small"],
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            feat_lbl.pack(fill="x", padx=20, pady=2)

        # Bottom spacer
        spacer = ctk.CTkLabel(self.features_card, text="")
        spacer.pack(pady=(5, 15))

    def update_language(self, lang):
        # Placeholder — will be expanded when modules are implemented
        badge_text = "  EM BREVE  " if lang.get("title", "").find("v") != -1 and "AutoAD" in lang.get("title", "") else "  COMING SOON  "
        if lang.get("configuracoes_header", "") == "CONFIGURAÇÕES":
            badge_text = "  EM BREVE  "
            self.features_title.configure(text="Funcionalidades planejadas:")
        else:
            badge_text = "  COMING SOON  "
            self.features_title.configure(text="Planned features:")
        self.badge_lbl.configure(text=badge_text)
