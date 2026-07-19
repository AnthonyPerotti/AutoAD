import customtkinter as ctk
import sys
import subprocess
import webbrowser
from core.theme import COLORS, FONTS, SIZES

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, hub):
        super().__init__(hub)
        self.hub = hub
        self.title("Settings")
        self.geometry("700x500")
        self.minsize(700, 500)
        self.grab_set()

        try:
            import os
            from core.utils import get_resource_path
            icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
            self.after(200, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

        # Main Layout: 2 Columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ============================================
        # SIDEBAR
        # ============================================
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=COLORS["bg_panel"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame, text="⚙ Settings", font=("Segoe UI Semibold", 20), text_color=COLORS["text_main"]
        )
        self.sidebar_title.pack(pady=(25, 20), padx=20, anchor="w")

        self.nav_buttons = {}
        nav_items = [
            ("general", "General"),
            ("rendering", "Rendering"),
            ("about", "About")
        ]

        for key, text in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_light"],
                font=("Segoe UI", 13),
                command=lambda k=key: self.show_frame(k)
            )
            btn.pack(fill="x", padx=15, pady=2)
            self.nav_buttons[key] = btn

        # ============================================
        # CONTENT AREA
        # ============================================
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}
        
        # --- GENERAL ---
        self.frames["general"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.frames["general"], text="General Settings", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Language
        ctk.CTkLabel(self.frames["general"], text="Language", font=("Segoe UI", 14)).pack(anchor="w")
        self.lang_menu = ctk.CTkOptionMenu(
            self.frames["general"],
            values=["English", "Português"],
            variable=self.hub.language_var,
            width=250,
            command=self.on_language_change
        )
        self.lang_menu.pack(anchor="w", pady=(5, 20))

        # Theme
        ctk.CTkLabel(self.frames["general"], text="Theme", font=("Segoe UI", 14)).pack(anchor="w")
        self.theme_menu = ctk.CTkOptionMenu(
            self.frames["general"],
            values=["Dark", "Light"],
            variable=self.hub.theme_var,
            width=250,
            command=self.on_theme_change
        )
        self.theme_menu.pack(anchor="w", pady=(5, 20))

        # UI Scale
        ctk.CTkLabel(self.frames["general"], text="UI Scale", font=("Segoe UI", 14)).pack(anchor="w")
        self.scale_menu = ctk.CTkOptionMenu(
            self.frames["general"],
            values=["90%", "100%", "110%", "125%"],
            variable=self.hub.ui_scale_var,
            width=250,
            command=self.on_scale_change
        )
        self.scale_menu.pack(anchor="w", pady=(5, 20))


        # --- RENDERING ---
        self.frames["rendering"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(self.frames["rendering"], text="Rendering Settings", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(self.frames["rendering"], text="Render Encoder", font=("Segoe UI", 14)).pack(anchor="w")
        enc_row = ctk.CTkFrame(self.frames["rendering"], fg_color="transparent")
        enc_row.pack(anchor="w", pady=(5, 10))
        self.enc_menu = ctk.CTkOptionMenu(
            enc_row,
            values=["CPU (libx264)", "NVIDIA (NVENC)", "AMD (AMF)", "Intel (QSV)"],
            variable=self.hub.encoder_var,
            width=220,
            command=self.save_all
        )
        self.enc_menu.pack(side="left")
        ctk.CTkButton(
            enc_row, text="⚡ Auto-detect", width=110,
            fg_color="transparent", border_width=1, border_color=COLORS["border"],
            hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            font=("Segoe UI", 12),
            command=self.auto_detect_encoder
        ).pack(side="left", padx=(10, 0))

        self.lbl_enc_hint = ctk.CTkLabel(
            self.frames["rendering"],
            text="Auto-detect scans your system for the best available GPU encoder.",
            font=("Segoe UI", 11), text_color=COLORS["text_muted"], wraplength=400, justify="left"
        )
        self.lbl_enc_hint.pack(anchor="w", pady=(0, 20))




        # --- ABOUT ---
        self.frames["about"] = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        ctk.CTkLabel(self.frames["about"], text="About AutoAD Suite", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 20))

        info_card = ctk.CTkFrame(self.frames["about"], fg_color=COLORS["bg_panel"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        info_card.pack(fill="x", pady=(0, 20))

        def add_info_row(parent, label, value):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12, "bold"), text_color=COLORS["text_muted"]).pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Segoe UI", 12), text_color=COLORS["text_main"]).pack(side="right")

        def get_pkg_version(pkg):
            try:
                import importlib
                mod = importlib.import_module(pkg)
                return getattr(mod, "__version__", "n/a")
            except Exception:
                return "n/a"

        from core.version import APP_FULL_NAME
        add_info_row(info_card, "Version", APP_FULL_NAME)
        add_info_row(info_card, "Python Version", sys.version.split()[0])
        add_info_row(info_card, "FFmpeg", self.get_ffmpeg_version())
        add_info_row(info_card, "faster-whisper", get_pkg_version("faster_whisper"))
        add_info_row(info_card, "customtkinter", get_pkg_version("customtkinter"))
        add_info_row(info_card, "ctranslate2", get_pkg_version("ctranslate2"))

        ctk.CTkLabel(self.frames["about"], text="Links & Contact", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 10))

        links_frame = ctk.CTkFrame(self.frames["about"], fg_color="transparent")
        links_frame.pack(fill="x")

        ctk.CTkButton(
            links_frame, text="GitHub", width=100, fg_color="transparent", border_width=1, border_color=COLORS["border"],
            hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            command=lambda: webbrowser.open("https://github.com/AnthonyPerotti/AutoAD")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            links_frame, text="Documentation", width=120, fg_color="transparent", border_width=1, border_color=COLORS["border"],
            hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
            command=lambda: webbrowser.open("https://github.com/AnthonyPerotti/AutoAD")
        ).pack(side="left", padx=(0, 10))

        discord_row = ctk.CTkFrame(self.frames["about"], fg_color="transparent")
        discord_row.pack(anchor="w", pady=(15, 0))
        ctk.CTkLabel(discord_row, text="Discord:", font=("Segoe UI", 12, "bold"), text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkLabel(discord_row, text="@spisham", font=("Segoe UI", 12), text_color=COLORS["text_main"]).pack(side="left", padx=(8, 0))


        # Set initial frame
        self.show_frame("general")

    def show_frame(self, key):
        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color=COLORS["hook"] if k == key else "transparent",
                          text_color=COLORS["text_main"] if k == key else COLORS["text_light"])
        for k, frame in self.frames.items():
            frame.pack_forget()
        self.frames[key].pack(fill="both", expand=True)

    def on_language_change(self, _=None):
        self.hub.aplicar_idioma()
        self.save_all()

    def on_theme_change(self, _=None):
        self.hub.aplicar_tema_inicial()
        self.save_all()

    def on_scale_change(self, _=None):
        self.hub.aplicar_escala_ui()
        self.save_all()

    def save_all(self, _=None):
        self.hub.salvar_configuracoes()

    def auto_detect_encoder(self):
        from core.utils import detect_best_encoder
        best = detect_best_encoder()
        self.hub.encoder_var.set(best)
        self.lbl_enc_hint.configure(
            text=f"Detected: {best}  —  Auto-detect scans your system for the best available GPU encoder.",
            text_color=COLORS["success"]
        )
        self.save_all()

    def get_ffmpeg_version(self):
        try:
            from core.ffmpeg import FFMPEG_PATH
            result = subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            first_line = result.stdout.split('\n')[0]
            return first_line.replace("ffmpeg version ", "").split(" ")[0]
        except Exception:
            return "Not found"

