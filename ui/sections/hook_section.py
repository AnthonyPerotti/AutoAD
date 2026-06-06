# pyrefly: ignore [missing-import]
import customtkinter as ctk
from ui.components.section_card import SectionCard
from core.theme import COLORS, FONTS, SIZES
from core.utils import count_videos

class HooksPanel(SectionCard):
    def __init__(self, parent, on_select_folder, on_clear_folder=None):
        super().__init__(
            parent, 
            title="HOOK", 
            color_key="hook", 
            icon="🪝", 
            subtitle="Selecione a pasta com os vídeos de Hook"
        )
        self.hooks_path = ""
        self.on_select_folder = on_select_folder
        self.on_clear_folder = on_clear_folder

        # Row 1: Button, Path Box Container
        self.row1 = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.row1.pack(fill="x", pady=(5, 5))

        self.select_button = ctk.CTkButton(
            self.row1,
            text="Selecionar Pasta",
            width=150,
            height=36,
            corner_radius=SIZES["corner_button"],
            fg_color=COLORS["hook"],
            text_color=COLORS["text_main"],
            hover_color="#2563eb",
            font=FONTS["button_normal"],
            command=self.select_folder,
        )
        self.select_button.pack(side="left", padx=(0, 12))

        # Path display container (mimics the input field in mockup)
        self.path_container = ctk.CTkFrame(
            self.row1, 
            height=36, 
            fg_color=COLORS["bg_main"], 
            border_width=SIZES["border_thin"], 
            border_color=COLORS["border"]
        )
        self.path_container.pack(side="left", fill="x", expand=True)
        self.path_container.pack_propagate(False)

        self.path_label = ctk.CTkLabel(
            self.path_container,
            text="Nenhuma pasta selecionada",
            font=FONTS["text_normal"],
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.path_label.pack(side="left", fill="x", expand=True, padx=12)

        # Folder icon button on the right side of path entry
        self.btn_folder_action = ctk.CTkButton(
            self.path_container,
            text="📁",
            width=30,
            height=30,
            fg_color=COLORS["transparent"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 13),
            command=self.open_folder_explorer
        )
        self.btn_folder_action.pack(side="right", padx=3)

        # Trash/Clear button next to container
        self.btn_clear = ctk.CTkButton(
            self.row1,
            text="🗑",
            width=36,
            height=36,
            corner_radius=SIZES["corner_button"],
            fg_color=COLORS["border"],
            hover_color="#27272a",
            font=("Segoe UI", 14),
            command=self.on_clear_folder if self.on_clear_folder else self.clear_folder,
        )
        self.btn_clear.pack(side="left", padx=(10, 0))

        # Row 2: Videos Found Text with colored status dot
        self.status_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.status_container.pack(fill="x", pady=(5, 0))

        self.status_dot = ctk.CTkLabel(
            self.status_container,
            text="◌",
            font=("Segoe UI", 14),
            text_color=COLORS["hook"]
        )
        self.status_dot.pack(side="left", padx=(5, 5))

        self.count_label = ctk.CTkLabel(
            self.status_container,
            text="0 vídeos encontrados",
            font=FONTS["text_small"],
            text_color=COLORS["text_muted"],
        )
        self.count_label.pack(side="left")

    def select_folder(self):
        self.on_select_folder()

    def open_folder_explorer(self):
        if self.hooks_path and os.path.exists(self.hooks_path):
            try: os.startfile(self.hooks_path)
            except: pass
        else:
            self.select_folder()

    def set_path(self, path):
        self.hooks_path = path
        if path:
            self.path_label.configure(text=path, text_color=COLORS["text_main"])
            self.status_dot.configure(text="●", text_color=COLORS["hook"])
        else:
            no_folder_text = self.lang["no_folder"] if hasattr(self, 'lang') else "Nenhuma pasta selecionada"
            self.path_label.configure(text=no_folder_text, text_color=COLORS["text_muted"])
            self.status_dot.configure(text="◌", text_color=COLORS["text_muted"])
        
        count = count_videos(path)
        videos_found_text = self.lang["videos_found"] if hasattr(self, 'lang') else "{} vídeos encontrados"
        self.count_label.configure(text=videos_found_text.format(count))

    def update_language(self, lang):
        self.lang = lang
        self.set_title(lang["hooks"])
        self.set_subtitle(lang["hook_subtitle"])
        self.select_button.configure(text=lang["select_folder"])
        self.btn_clear.configure(text=lang["clear"])
        self.set_path(self.hooks_path)

    def clear_folder(self):
        self.hooks_path = ""
        self.set_path("")

    def clear_preview(self):
        self.clear_folder()

