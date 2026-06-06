# pyrefly: ignore [missing-import]
import customtkinter as ctk
import os
from ui.components.section_card import SectionCard
from core.theme import COLORS, FONTS, SIZES

class OutputPanel(SectionCard):
    def __init__(self, parent, auto_open_var, on_select_output, on_clear_output, on_auto_open_change):
        super().__init__(
            parent, 
            title="OUTPUT", 
            color_key="output", 
            icon="📥", 
            subtitle="Selecione a pasta de destino para exportação"
        )
        
        self.on_select_output = on_select_output
        self.on_clear_output = on_clear_output
        self.output_path = ""
        
        self.out_row1 = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.out_row1.pack(fill="x", pady=(5, 5))

        self.btn_output = ctk.CTkButton(
            self.out_row1, 
            text="Selecionar Pasta", 
            width=150, 
            height=36, 
            corner_radius=SIZES["corner_button"],
            fg_color=COLORS["output"], 
            text_color=COLORS["text_main"], 
            hover_color="#ea580c", 
            font=FONTS["button_normal"], 
            command=self.on_select_output
        )
        self.btn_output.pack(side="left", padx=(0, 12))

        # Path display container (mimics the input field in mockup)
        self.path_container = ctk.CTkFrame(
            self.out_row1, 
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
        self.btn_clear_output = ctk.CTkButton(
            self.out_row1, 
            text="🗑", 
            width=36, 
            height=36, 
            corner_radius=SIZES["corner_button"], 
            fg_color=COLORS["border"],
            hover_color="#27272a", 
            font=("Segoe UI", 14), 
            command=self.on_clear_output
        )
        self.btn_clear_output.pack(side="left", padx=(10, 0))
        
        # Left-aligned checkbox with blue checkmark
        self.cloud_cb = ctk.CTkCheckBox(
            self.content_frame, 
            text="Abrir pasta de saída após exportar", 
            variable=auto_open_var, 
            font=FONTS["text_small"], 
            text_color=COLORS["text_muted"], 
            fg_color="#1d4ed8",          # Blue background for checkmark
            hover_color="#2563eb",
            command=on_auto_open_change
        )
        self.cloud_cb.pack(anchor="w", pady=(10, 5), padx=(5, 0))

    def open_folder_explorer(self):
        if self.output_path and os.path.exists(self.output_path):
            try: os.startfile(self.output_path)
            except: pass
        else:
            self.on_select_output()

    def update_language(self, lang):
        self.lang = lang
        self.set_title(lang["output"])
        self.set_subtitle(lang["output_subtitle"])
        self.btn_output.configure(text=lang["select_folder"])
        self.cloud_cb.configure(text=lang["auto_open"])
        self.set_path(self.output_path)
        
    def set_path(self, path):
        self.output_path = path
        if path:
            self.path_label.configure(text=path, text_color=COLORS["text_main"])
        else:
            no_folder_text = self.lang["no_folder"] if hasattr(self, 'lang') else "Nenhuma pasta selecionada"
            self.path_label.configure(text=no_folder_text, text_color=COLORS["text_muted"])
