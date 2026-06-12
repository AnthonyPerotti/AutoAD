import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.translations import translations
from tkinter import messagebox
from core.config import salvar_config, carregar_config
from core.theme import COLORS, FONTS, SIZES
from core.utils import get_resource_path

from apps.assembler.ui.view import AssemblerView
from apps.resizer.ui.view import ResizerView
from apps.renamer.ui.view import RenamerView
from apps.converter.ui.view import ConverterView
from apps.audio_tools.ui.view import AudioToolsView
from apps.subtitles.ui.view import SubtitlesView
from ui.placeholder import PlaceholderModuleView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Module registry: key, icon, label_pt, label_en, is_placeholder
MODULES = [
    ("assembler", "📦", "Content Assembler", "Content Assembler", False),
    ("resizer", "🖼", "Video Resizer", "Video Resizer", False),
    ("subtitles", "📝", "Subtitle Studio", "Subtitle Studio", False),
    ("converter", "🔄", "Video Converter", "Video Converter", False),
    ("audio_tools", "🎵", "Audio Toolkit", "Audio Toolkit", False),
    ("renamer", "🏷", "Bulk Renamer", "Bulk Renamer", False),
]

# Placeholder module config: key -> (icon, title, description, features)
PLACEHOLDER_CONFIG = {
    "resizer": (
        "🖼", "Video Resizer",
        "Redimensione vídeos entre formatos verticais e horizontais com inteligência.",
        [
            "Vertical → Horizontal / Horizontal → Vertical",
            "Presets: TikTok, YouTube, Shorts, Reels",
            "Blur Background",
            "Smart Crop & Auto Center",
            "Aspect Ratio Presets",
            "Upscale Canvas",
            "Batch Resize",
        ]
    ),
    "subtitles": (
        "📝", "Subtitle Studio",
        "Adicione legendas automaticamente aos seus vídeos.",
        [
            "Legendas automáticas",
            "Suporte a .SRT",
            "Suporte a .ASS",
            "Estilos personalizáveis",
        ]
    ),
    "exporter": (
        "📤", "Social Export Manager",
        "Exporte vídeos com presets otimizados para cada plataforma.",
        [
            "Preset TikTok",
            "Preset YouTube Shorts",
            "Preset Instagram Reels",
            "Preset Kwai",
            "Preset YouTube",
            "Export em batch",
        ]
    ),
    "watermark": (
        "💧", "Video Watermarker",
        "Aplique logos, textos e marcas d'água nos seus vídeos.",
        [
            "Logo overlay",
            "Texto personalizado",
            "Marca d'água transparente",
            "Batch Watermark",
            "Posicionamento flexível",
        ]
    ),
    "audio_tools": (
        "🎵", "Audio Toolkit",
        "Ferramentas de áudio para otimizar seus vídeos.",
        [
            "Normalize volume",
            "Remover silêncio",
            "Volume boost",
            "Batch audio convert",
        ]
    ),
}


class AutoADSuiteApp(ctk.CTk):

    def salvar_configuracoes(self):
        config = {
            "encoder": self.encoder_var.get(),
            "language": self.language_var.get(),
            "auto_open": self.auto_open_var.get(),
            "theme": self.theme_var.get(),
            "ui_scale": self.ui_scale_var.get(),
            "overwrite_behavior": self.overwrite_var.get(),
        }
        salvar_config(config)

    def __init__(self):
        super().__init__()
        self.language_var = ctk.StringVar(value="English")
        self.encoder_var = ctk.StringVar(value="CPU (libx264)")
        self.auto_open_var = ctk.BooleanVar(value=False)
        self.theme_var = ctk.StringVar(value="Dark")
        self.ui_scale_var = ctk.StringVar(value="100%")
        self.overwrite_var = ctk.StringVar(value="Ask")

        self.title("AutoAD Suite v2.1")
        self.geometry("980x950")
        self.minsize(900, 800)

        try:
            icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
            self.iconbitmap(icon_path)
        except Exception:
            pass

        self.configure(fg_color=COLORS["bg_main"])

        self.language_sidebar_var = ctk.StringVar(value="🌐 English")
        self.current_view = "assembler"

        # ==========================================
        # LEFT SIDEBAR PANEL
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLORS["bg_sidebar"], border_width=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Logo Header
        self.sidebar_logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_logo_frame.pack(fill="x", padx=20, pady=(25, 20))

        try:
            from PIL import Image
            icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
            logo_img = ctk.CTkImage(light_image=Image.open(icon_path), dark_image=Image.open(icon_path), size=(38, 38))
            self.logo_icon_label = ctk.CTkLabel(
                self.sidebar_logo_frame,
                text="",
                image=logo_img,
                width=38,
                height=38
            )
        except Exception:
            self.logo_icon_label = ctk.CTkLabel(
                self.sidebar_logo_frame,
                text="A",
                font=("Segoe UI", 22, "bold"),
                text_color=COLORS["text_main"],
                fg_color=COLORS["hook"],
                width=38,
                height=38,
                corner_radius=8
            )
        self.logo_icon_label.pack(side="left", padx=(0, 12))

        self.logo_text_container = ctk.CTkFrame(self.sidebar_logo_frame, fg_color="transparent")
        self.logo_text_container.pack(side="left")

        self.logo_title = ctk.CTkLabel(self.logo_text_container, text="AutoAD Suite", font=("Segoe UI", 14, "bold"), text_color=COLORS["text_main"], anchor="w")
        self.logo_title.pack(anchor="w")

        self.logo_version = ctk.CTkLabel(self.logo_text_container, text="v2.0", font=("Segoe UI", 11), text_color=COLORS["text_muted"], anchor="w")
        self.logo_version.pack(anchor="w")

        # Category: Dashboard Link
        self.nav_buttons = {}

        self.btn_db = ctk.CTkButton(
            self.sidebar_frame,
            text="  🏠  Dashboard",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 12),
            command=lambda: self.on_sidebar_click("dashboard")
        )
        self.btn_db.pack(fill="x", padx=15, pady=(5, 10))
        self.nav_buttons["dashboard"] = self.btn_db

        # Category: APPLICATIONS
        self.sidebar_header_app = ctk.CTkLabel(self.sidebar_frame, text="APLICAÇÕES", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_muted"], anchor="w")
        self.sidebar_header_app.pack(fill="x", padx=20, pady=(10, 5))

        # Build module buttons from MODULES registry
        for key, icon, label_pt, label_en, is_placeholder in MODULES:
            # Use fixed spacing for icons
            btn_text = f"  {icon}   {label_pt}"
            fg = COLORS["hook"] if key == "assembler" else "transparent"
            font_style = ("Segoe UI", 12, "bold") if key == "assembler" else ("Segoe UI", 12)
            
            if is_placeholder:
                text_color = COLORS.get("text_muted", "#6c757d")
            else:
                text_color = COLORS["text_main"] if key == "assembler" else COLORS["text_light"]

            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=btn_text,
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color=fg,
                hover_color=COLORS["bg_hover"],
                text_color=text_color,
                font=font_style,
                command=lambda k=key: self.on_sidebar_click(k)
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[key] = btn


        # Category: SETTINGS
        self.sidebar_header_config = ctk.CTkLabel(self.sidebar_frame, text="CONFIGURAÇÕES", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_muted"], anchor="w")
        self.sidebar_header_config.pack(fill="x", padx=20, pady=(18, 5))

        self.config_buttons = {}
        btn_config = ctk.CTkButton(
            self.sidebar_frame,
            text="  ⚙️  Configurações",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 12),
            command=self.abrir_configuracoes
        )
        btn_config.pack(fill="x", padx=15, pady=3)
        self.config_buttons["configuracoes"] = btn_config

        # Bottom Frame inside Sidebar
        self.sidebar_bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_bottom_frame.pack(side="bottom", fill="x", padx=15, pady=25)

        # Language dropdown
        self.language_menu = ctk.CTkOptionMenu(
            self.sidebar_bottom_frame,
            values=["🌐 Português (BR)", "🌐 English"],
            variable=self.language_sidebar_var,
            fg_color=COLORS["bg_panel"],
            button_color=COLORS["bg_panel"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_panel"],
            dropdown_hover_color=COLORS["border"],
            dropdown_text_color=COLORS["text_main"],
            text_color=COLORS["text_main"],
            font=("Segoe UI", 12),
            command=self.on_sidebar_language_change
        )
        self.language_menu.pack(fill="x", pady=(0, 15))

        # Theme toggle slider sun/moon
        self.theme_frame = ctk.CTkFrame(self.sidebar_bottom_frame, fg_color=COLORS["bg_panel"], height=32, corner_radius=16)
        self.theme_frame.pack(fill="x")

        self.theme_lbl_sun = ctk.CTkLabel(self.theme_frame, text="☀️", font=("Segoe UI", 11))
        self.theme_lbl_sun.pack(side="left", padx=(15, 5), pady=3)

        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame,
            text="",
            width=40,
            progress_color=COLORS["hook"],
            command=self.toggle_theme
        )
        self.theme_switch.pack(side="left", padx=5)
        self.theme_switch.select()  # default to dark

        self.theme_lbl_moon = ctk.CTkLabel(self.theme_frame, text="🌙", font=("Segoe UI", 11))
        self.theme_lbl_moon.pack(side="left", padx=(5, 15), pady=3)

        # ==========================================
        # RIGHT CONTENT AREA
        # ==========================================
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.main_content_frame.pack(side="right", fill="both", expand=True)

        # Header Row
        self.header_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent", height=70)
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.header_title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_title_container.pack(side="left")

        self.title_row = ctk.CTkFrame(self.header_title_container, fg_color="transparent")
        self.title_row.pack(anchor="w")

        self.title_label = ctk.CTkLabel(
            self.title_row, text="Content Assembler", font=("Segoe UI", 20, "bold"), text_color=COLORS["text_main"]
        )
        self.title_label.pack(side="left")

        # v2.0 badge
        self.badge_frame = ctk.CTkFrame(self.title_row, fg_color=COLORS["hook"], corner_radius=6, height=20, width=40)
        self.badge_frame.pack(side="left", padx=(8, 0))
        self.badge_frame.pack_propagate(False)
        self.badge_lbl = ctk.CTkLabel(self.badge_frame, text="v2.1", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_main"])
        self.badge_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.subtitle_label = ctk.CTkLabel(
            self.header_title_container,
            text="Monte, organize e exporte seus conteúdos de forma rápida e eficiente.",
            font=FONTS["text_normal"],
            text_color=COLORS["text_muted"]
        )
        self.subtitle_label.pack(anchor="w", pady=(3, 0))

        # Header right container
        self.header_right_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_right_container.pack(side="right", fill="y", padx=(0, 5))

        # Github link top right
        import webbrowser
        self.dev_link = ctk.CTkLabel(
            self.header_right_container, text="developed by Anthony Perotti", font=("Segoe UI", 11, "italic"), text_color=COLORS["text_muted"], cursor="hand2"
        )
        self.dev_link.pack(side="top", anchor="e", pady=(0, 2))
        self.dev_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/AnthonyPerotti"))

        # Status badge on right side of header
        self.status_pill_frame = ctk.CTkFrame(
            self.header_right_container,
            fg_color=COLORS["bg_panel"],
            border_width=SIZES["border_thin"],
            border_color=COLORS["border"],
            height=30,
            corner_radius=15
        )
        self.status_pill_frame.pack(side="top", anchor="e")
        self.status_pill_frame.pack_propagate(False)

        self.status_dot_lbl = ctk.CTkLabel(self.status_pill_frame, text="●", text_color=COLORS["success"], font=("Segoe UI", 12))
        self.status_dot_lbl.pack(side="left", padx=(12, 5))

        self.status_pill_label = ctk.CTkLabel(
            self.status_pill_frame,
            text="Sistema Online",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["text_light"]
        )
        self.status_pill_label.pack(side="left", padx=(0, 12))

        # View container
        self.view_container = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        # ==========================================
        # INSTANTIATE MODULE VIEWS
        # ==========================================
        from apps.assembler.ui.view import AssemblerView
        from apps.renamer.ui.view import RenamerView
        from apps.resizer.ui.view import ResizerView
        from apps.subtitles.ui.view import SubtitlesView
        from apps.audio_tools.ui.view import AudioToolsView
        from apps.converter.ui.view import ConverterView

        self.assembler_view = AssemblerView(self.view_container, self)
        self.assembler_view.pack(fill="both", expand=True)
        self.current_view = "assembler"
        
        self.module_views = {}
        for key, icon, title_pt, title_en, is_placeholder in MODULES:
            if is_placeholder:
                config = PLACEHOLDER_CONFIG.get(key, ("❓", "Em breve", "Este módulo está em desenvolvimento.", []))
                view = PlaceholderModuleView(self.view_container, *config)
                self.module_views[key] = view
            elif key == "renamer":
                self.module_views[key] = RenamerView(self.view_container, self)
            elif key == "resizer":
                self.module_views[key] = ResizerView(self.view_container, self)
            elif key == "subtitles":
                self.module_views[key] = SubtitlesView(self.view_container, self)
            elif key == "audio_tools":
                self.module_views[key] = AudioToolsView(self.view_container, self)
            elif key == "converter":
                self.module_views[key] = ConverterView(self.view_container, self)

        # Dashboard
        self.dashboard_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self._build_dashboard()

        # Footer Frame
        self.footer_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent", height=30)
        self.footer_frame.pack(side="bottom", fill="x", padx=25, pady=5)

        self.footer_status_label = ctk.CTkLabel(
            self.footer_frame,
            text="● Sistema operacional normal",
            font=("Segoe UI", 10),
            text_color=COLORS["success"]
        )
        self.footer_status_label.pack(side="left")

        self.footer_version_label = ctk.CTkLabel(
            self.footer_frame,
            text="AutoAD Suite v2.1",
            font=("Segoe UI", 10),
            text_color=COLORS["text_muted"]
        )
        self.footer_version_label.pack(side="right")

        # Config Load
        config = carregar_config()
        if "encoder" not in config:
            from core.utils import detect_best_encoder
            config["encoder"] = detect_best_encoder()
            salvar_config(config)

        self.encoder_var.set(config.get("encoder", "CPU (libx264)"))
        self.auto_open_var.set(config.get("auto_open", False))
        self.language_var.set(config.get("language", "English"))
        self.theme_var.set(config.get("theme", "Dark"))
        self.ui_scale_var.set(config.get("ui_scale", "100%"))
        self.overwrite_var.set(config.get("overwrite_behavior", "Ask"))
        
        self.aplicar_escala_ui()
        self.aplicar_tema_inicial()
        self.aplicar_idioma()

    def aplicar_escala_ui(self):
        scale_str = self.ui_scale_var.get().replace("%", "")
        try:
            scale_float = int(scale_str) / 100.0
            ctk.set_widget_scaling(scale_float)
            ctk.set_window_scaling(scale_float)
        except:
            pass
            
    def aplicar_tema_inicial(self):
        theme = self.theme_var.get()
        if theme == "Dark":
            ctk.set_appearance_mode("dark")
            self.theme_switch.select()
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.deselect()

    # ==========================================
    # DASHBOARD
    # ==========================================

    def _build_dashboard(self):
        self.db_title = ctk.CTkLabel(self.dashboard_view, text="Visão Geral do AutoAD Suite", font=("Segoe UI", 16, "bold"), text_color=COLORS["text_main"])
        self.db_title.pack(anchor="w", pady=(10, 20))

        self.db_grid = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        self.db_grid.pack(fill="x", pady=10)
        self.db_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self.card1 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card1.grid(row=0, column=0, padx=10, sticky="ew")
        self.card1.pack_propagate(False)
        lbl1 = ctk.CTkLabel(self.card1, text="Módulos Disponíveis", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl1.pack(pady=(15, 5))
        active_modules = sum(1 for m in MODULES if not m[4])
        self.db_stat_modules = ctk.CTkLabel(self.card1, text=str(active_modules), font=("Segoe UI", 24, "bold"), text_color=COLORS["hook"])
        self.db_stat_modules.pack()

        self.card2 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card2.grid(row=0, column=1, padx=10, sticky="ew")
        self.card2.pack_propagate(False)
        lbl2 = ctk.CTkLabel(self.card2, text="Renderizador", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl2.pack(pady=(15, 5))
        self.db_stat_renderer = ctk.CTkLabel(self.card2, text=self.encoder_var.get(), font=("Segoe UI", 12, "bold"), text_color=COLORS["cta"])
        self.db_stat_renderer.pack()
        self.encoder_var.trace_add("write", lambda *args: self.db_stat_renderer.configure(text=self.encoder_var.get()))

        self.card3 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card3.grid(row=0, column=2, padx=10, sticky="ew")
        self.card3.pack_propagate(False)
        lbl3 = ctk.CTkLabel(self.card3, text="Status do Sistema", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl3.pack(pady=(15, 5))
        self.db_stat_status = ctk.CTkLabel(self.card3, text="Online", font=("Segoe UI", 16, "bold"), text_color=COLORS["success"])
        self.db_stat_status.pack()

    # ==========================================
    # NAVIGATION
    # ==========================================

    def on_sidebar_click(self, module_key):
        # Reset navigation buttons styling
        for key, btn in self.nav_buttons.items():
            is_placeholder = any(m[0] == key and m[4] for m in MODULES)
            if key == module_key:
                btn.configure(fg_color=COLORS["hook"], text_color=COLORS["text_main"], font=("Segoe UI", 12, "bold"))
            else:
                if is_placeholder:
                    btn.configure(fg_color="transparent", text_color=COLORS.get("text_muted", "#6c757d"), font=("Segoe UI", 12, "normal"))
                else:
                    btn.configure(fg_color="transparent", text_color=COLORS["text_light"], font=("Segoe UI", 12, "normal"))

        # Hide all views
        self.assembler_view.pack_forget()
        self.dashboard_view.pack_forget()
        for view in self.module_views.values():
            view.pack_forget()

        # Show target view
        if module_key == "assembler":
            self.assembler_view.pack(fill="both", expand=True)
            self.current_view = "assembler"
        elif module_key == "dashboard":
            self.dashboard_view.pack(fill="both", expand=True, padx=20, pady=10)
            self.current_view = "dashboard"
        elif module_key in self.module_views:
            self.module_views[module_key].pack(fill="both", expand=True)
            self.current_view = module_key
        
        self.aplicar_idioma()

    # ==========================================
    # LANGUAGE
    # ==========================================

    def on_sidebar_language_change(self, val):
        if "Português" in val:
            self.language_var.set("Português")
        else:
            self.language_var.set("English")
        self.aplicar_idioma()

    def aplicar_idioma(self):
        lang = translations.get(self.language_var.get(), translations["English"]) if self.language_var.get() in translations else None
        if not lang:
            lang = translations["English"]

        self.lang = lang
        self.title(lang["title"])

        # Sync sidebar language menu
        sidebar_lang_val = "🌐 Português (BR)" if self.language_var.get() == "Português" else "🌐 English"
        if self.language_sidebar_var.get() != sidebar_lang_val:
            self.language_sidebar_var.set(sidebar_lang_val)

        # Update header based on current view
        if self.current_view == "assembler":
            self.title_label.configure(text=lang["content_assembler"])
            self.subtitle_label.configure(text=lang["subtitle"])
        elif self.current_view == "dashboard":
            self.title_label.configure(text=lang["dashboard"])
            self.subtitle_label.configure(text=lang.get("dashboard_subtitle", "Visualize as estatísticas e informações do sistema."))
        elif self.current_view in self.module_views:
            # Get module display name
            for key, icon, label_pt, label_en, is_placeholder in MODULES:
                if key == self.current_view:
                    label = label_pt if self.language_var.get() == "Português" else label_en
                    self.title_label.configure(text=label)
                    break
            self.subtitle_label.configure(text=lang.get("module_subtitle", "Explore esta ferramenta do AutoAD Suite."))

        self.status_pill_label.configure(text=lang["sistema_online"])
        self.footer_status_label.configure(text="● " + lang["sistema_normal"])

        # Sidebar configurations and bottom buttons
        self.sidebar_header_config.configure(text=lang["configuracoes_header"])
        self.config_buttons["configuracoes"].configure(text=f"  ⚙️  {lang['configuracoes']}")

        # Translate sidebar items
        self.nav_buttons["dashboard"].configure(text=f"  🏠  {lang['dashboard']}")
        
        # Update module buttons
        for key, icon, label_pt, label_en, is_placeholder in MODULES:
            if key in self.nav_buttons:
                label = label_pt if self.language_var.get() == "Português" else label_en
                self.nav_buttons[key].configure(text=f"  {icon}  {label}")

        self.config_buttons["configuracoes"].configure(text=f"  ⚙️  {lang['configuracoes']}")

        # Update assembler view language
        self.assembler_view.update_language(lang)

        # Update placeholder module views
        for view in self.module_views.values():
            if hasattr(view, "update_language"):
                view.update_language(lang)

        salvar_config(
            {
                "encoder": self.encoder_var.get(),
                "auto_open": self.auto_open_var.get(),
                "language": self.language_var.get(),
                "theme": self.theme_var.get(),
                "ui_scale": self.ui_scale_var.get(),
                "overwrite_behavior": self.overwrite_var.get(),
            }
        )

    # ==========================================
    # SETTINGS
    # ==========================================

    def abrir_configuracoes(self):
        from apps.assembler.ui.popups.settings_popup import SettingsWindow
        SettingsWindow(self)

    # ==========================================
    # THEME
    # ==========================================

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.theme_var.set("Dark")
        else:
            ctk.set_appearance_mode("light")
            self.theme_var.set("Light")
        self.salvar_configuracoes()
