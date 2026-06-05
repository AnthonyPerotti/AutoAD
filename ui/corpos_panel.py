import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk

class BodyData:
    def __init__(self):
        self.path = ""

class CorposPanel(ctk.CTkFrame):
    def __init__(self, parent, on_select, on_update_total, on_log):
        super().__init__(
            parent,
            corner_radius=10,
            fg_color="#1e1e24",
            border_width=2,
            border_color="#7e22ce",  # Purple accent
        )
        self.on_select = on_select
        self.on_update_total = on_update_total
        self.on_log = on_log
        
        self.cards = [BodyData(), BodyData(), BodyData()]
        self.current_tab = 0

        # Title Header
        self.header_frame = ctk.CTkFrame(self, fg_color="#7e22ce", corner_radius=6, height=30)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)

        self.corpos_title = ctk.CTkLabel(
            self.header_frame, text="BODY", font=("Segoe UI", 14, "bold"), text_color="#ffffff"
        )
        self.corpos_title.place(relx=0.5, rely=0.5, anchor="center")

        # Custom Tabs Container
        self.tab_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_container.pack(fill="x", padx=20, pady=(15, 0))
        self.tab_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.tab_frames = []
        self.tab_labels_on = []
        self.tab_labels_name = []
        
        tab_names = ["Body A", "Body B", "Body C"]
        for i, name in enumerate(tab_names):
            # Tab Frame acts as button
            t_frame = ctk.CTkFrame(self.tab_container, height=30, corner_radius=6, cursor="hand2")
            t_frame.grid(row=0, column=i, sticky="ew", padx=2)
            t_frame.pack_propagate(False)
            
            # Use inner frame to center contents
            inner = ctk.CTkFrame(t_frame, fg_color="transparent")
            inner.place(relx=0.5, rely=0.5, anchor="center")
            
            lbl_name = ctk.CTkLabel(inner, text=name, font=("Segoe UI", 13), text_color="#ffffff")
            lbl_name.pack(side="left")
            
            lbl_on = ctk.CTkLabel(inner, text="", font=("Segoe UI", 13, "bold"), text_color="#00ff00") # Neon Green
            lbl_on.pack(side="left", padx=(5, 0))
            
            # Bind clicks
            for w in [t_frame, inner, lbl_name, lbl_on]:
                w.bind("<Button-1>", lambda e, idx=i: self.on_tab_click(idx))
                
            self.tab_frames.append(t_frame)
            self.tab_labels_on.append(lbl_on)
            self.tab_labels_name.append(lbl_name)

        # Content Container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(15, 15))

        # Row 1: Button, Path, Trash
        self.row1 = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.row1.pack(fill="x")

        self.select_button = ctk.CTkButton(
            self.row1,
            text="📁 SELECT FOLDER",
            width=160,
            height=36,
            corner_radius=6,
            fg_color="#7e22ce",
            text_color="#ffffff",
            hover_color="#9333ea",
            font=("Segoe UI", 13, "bold"),
            command=self.select_folder,
        )
        self.select_button.pack(side="left", padx=(0, 10))

        self.path_entry = ctk.CTkEntry(
            self.row1,
            height=36,
            fg_color="#27272a",
            border_width=1,
            border_color="#3f3f46",
            text_color="#d1d5db"
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.path_entry.insert(0, "No folder selected")
        self.path_entry.configure(state="readonly")

        self.btn_clear = ctk.CTkButton(
            self.row1,
            text="🗑",
            width=36,
            height=36,
            corner_radius=6,
            fg_color="#3f3f46",
            hover_color="#52525b",
            font=("Segoe UI", 16),
            command=self.clear_current_folder,
        )
        self.btn_clear.pack(side="left")

        # Row 2: Scenes Found Text
        self.count_label = ctk.CTkLabel(
            self.content_frame,
            text="0 scenes found",
            font=("Segoe UI", 12),
            text_color="#9ca3af",
        )
        self.count_label.pack(anchor="e", pady=(5, 0))

        self.update_ui_for_tab()

    def on_tab_click(self, index):
        self.current_tab = index
        self.update_ui_for_tab()

    def update_ui_for_tab(self):
        # Update Tab Styling
        for i, t_frame in enumerate(self.tab_frames):
            if i == self.current_tab:
                t_frame.configure(fg_color="#7e22ce")
            else:
                t_frame.configure(fg_color="#27272a")
                
        # Update "On" text for all tabs
        for i, lbl_on in enumerate(self.tab_labels_on):
            if self.cards[i].path:
                lbl_on.configure(text="On")
            else:
                lbl_on.configure(text="")
                
        path = self.cards[self.current_tab].path
        
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        if path:
            self.path_entry.insert(0, path)
        else:
            no_folder_text = self.lang["no_folder"] if hasattr(self, 'lang') else "No folder selected"
            self.path_entry.insert(0, no_folder_text)
        self.path_entry.configure(state="readonly")
        
        if path and os.path.exists(path):
            videos = [f for f in os.listdir(path) if f.lower().endswith(".mp4")]
            scenes_found_text = self.lang["scenes_found"] if hasattr(self, 'lang') else "{} scenes found"
            self.count_label.configure(text=scenes_found_text.format(len(videos)))
        else:
            scenes_found_text = self.lang["scenes_found"] if hasattr(self, 'lang') else "{} scenes found"
            self.count_label.configure(text=scenes_found_text.format(0))

    def update_language(self, lang):
        self.lang = lang
        self.corpos_title.configure(text=lang["bodies"])
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
