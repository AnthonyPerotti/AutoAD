# pyrefly: ignore [missing-import]
import customtkinter as ctk
import os
from ui.components.section_card import SectionCard
from core.theme import COLORS, FONTS, SIZES
from core.utils import count_videos

class BodyData:
    def __init__(self):
        self.path = ""

class CorposPanel(SectionCard):
    def __init__(self, parent, on_select, on_update_total, on_log):
        super().__init__(
            parent, 
            title="BODY", 
            color_key="body", 
            icon="🥞", 
            subtitle="Selecione as pastas com os vídeos de Body"
        )
        self.on_select = on_select
        self.on_update_total = on_update_total
        self.on_log = on_log
        
        self.cards = [BodyData(), BodyData(), BodyData()]
        self.current_tab = 0

        # Custom Tabs Container
        self.tab_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.tab_container.pack(fill="x", pady=(5, 12))
        self.tab_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.tab_frames = []
        self.tab_labels_on = []
        self.tab_labels_name = []
        
        tab_names = ["Body A", "Body B", "Body C"]
        for i, name in enumerate(tab_names):
            # Tab Frame acts as button
            t_frame = ctk.CTkFrame(self.tab_container, height=36, corner_radius=SIZES["corner_pill"], cursor="hand2")
            t_frame.grid(row=0, column=i, sticky="ew", padx=3)
            t_frame.pack_propagate(False)
            
            # Use inner frame to center contents
            inner = ctk.CTkFrame(t_frame, fg_color="transparent")
            inner.place(relx=0.5, rely=0.5, anchor="center")
            
            lbl_name = ctk.CTkLabel(inner, text=name, font=FONTS["button_normal"], text_color=COLORS["text_main"])
            lbl_name.pack(side="left")
            
            lbl_on = ctk.CTkLabel(inner, text="", font=("Segoe UI", 11, "bold"), text_color="#22c55e") # Neon Green
            lbl_on.pack(side="left", padx=(6, 0))
            
            # Bind clicks
            for w in [t_frame, inner, lbl_name, lbl_on]:
                w.bind("<Button-1>", lambda e, idx=i: self.on_tab_click(idx))
                
            self.tab_frames.append(t_frame)
            self.tab_labels_on.append(lbl_on)
            self.tab_labels_name.append(lbl_name)

        # Row 1: Button, Path Box Container
        self.row1 = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.row1.pack(fill="x", pady=(5, 5))

        self.select_button = ctk.CTkButton(
            self.row1,
            text="Selecionar Pasta",
            width=150,
            height=36,
            corner_radius=SIZES["corner_button"],
            fg_color=COLORS["body"],
            text_color=COLORS["text_main"],
            hover_color="#8b5cf6",
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
            command=self.clear_current_folder,
        )
        self.btn_clear.pack(side="left", padx=(10, 0))

        # Row 2: Scenes Found Text with colored status dot
        self.status_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["transparent"])
        self.status_container.pack(fill="x", pady=(5, 0))

        self.status_dot = ctk.CTkLabel(
            self.status_container,
            text="◌",
            font=("Segoe UI", 14),
            text_color=COLORS["body"]
        )
        self.status_dot.pack(side="left", padx=(5, 5))

        self.count_label = ctk.CTkLabel(
            self.status_container,
            text="0 cenas encontradas",
            font=FONTS["text_small"],
            text_color=COLORS["text_muted"],
        )
        self.count_label.pack(side="left")

        self.update_ui_for_tab()

    def on_tab_click(self, index):
        self.current_tab = index
        self.update_ui_for_tab()

    def open_folder_explorer(self):
        path = self.cards[self.current_tab].path
        if path and os.path.exists(path):
            try: os.startfile(path)
            except: pass
        else:
            self.select_folder()

    def update_ui_for_tab(self):
        # Update Tab Styling
        for i, t_frame in enumerate(self.tab_frames):
            if i == self.current_tab:
                t_frame.configure(fg_color=COLORS["body"])
            else:
                t_frame.configure(fg_color="#182030") # Darker tab background for inactive tabs
                
        # Update "On" text for all tabs
        for i, lbl_on in enumerate(self.tab_labels_on):
            if self.cards[i].path:
                lbl_on.configure(text="On")
            else:
                lbl_on.configure(text="")
                
        path = self.cards[self.current_tab].path
        
        if path:
            self.path_label.configure(text=path, text_color=COLORS["text_main"])
            self.status_dot.configure(text="●", text_color=COLORS["body"])
        else:
            no_folder_text = self.lang["no_folder"] if hasattr(self, 'lang') else "Nenhuma pasta selecionada"
            self.path_label.configure(text=no_folder_text, text_color=COLORS["text_muted"])
            self.status_dot.configure(text="◌", text_color=COLORS["text_muted"])
        
        count = count_videos(path)
        scenes_found_text = self.lang["scenes_found"] if hasattr(self, 'lang') else "{} cenas encontradas"
        self.count_label.configure(text=scenes_found_text.format(count))

    def update_language(self, lang):
        self.lang = lang
        self.set_title(lang["bodies"])
        self.set_subtitle(lang["body_subtitle"])
        self.select_button.configure(text=lang["select_folder"])
        self.btn_clear.configure(text=lang["clear"])
        
        body_tab_format = lang.get("body_tab", "Body {}")
        for i, lbl_name in enumerate(self.tab_labels_name):
            lbl_name.configure(text=body_tab_format.format(["A", "B", "C"][i]))
            
        self.update_ui_for_tab()

    def select_folder(self):
        path = self.on_select()
        if not path:
            return
        
        self.cards[self.current_tab].path = path
        self.update_ui_for_tab()
        self.on_update_total()
        self.on_log(f"Body {self.current_tab + 1} loaded: {path}")

    def clear_current_folder(self):
        self.cards[self.current_tab].path = ""
        self.update_ui_for_tab()
        self.on_update_total()
        self.on_log(f"Body {self.current_tab + 1} cleared.")

    def clear(self):
        for card in self.cards:
            card.path = ""
        self.update_ui_for_tab()
        self.on_update_total()
        self.on_log("Bodies cleared.")

