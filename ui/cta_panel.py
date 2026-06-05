import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk

class CTAPanel(ctk.CTkFrame):
    def __init__(self, parent, on_select_folder, on_clear_folder=None):
        super().__init__(
            parent,
            corner_radius=10,
            fg_color="#1e1e24",
            border_width=2,
            border_color="#15803d",  # Green accent
        )
        self.cta_path = ""
        self.on_select_folder = on_select_folder
        self.on_clear_folder = on_clear_folder

        # Title Header
        self.header_frame = ctk.CTkFrame(self, fg_color="#10b981", corner_radius=6, height=30)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)

        self.cta_title = ctk.CTkLabel(
            self.header_frame, text="CTA", font=("Segoe UI", 14, "bold"), text_color="#ffffff"
        )
        self.cta_title.place(relx=0.5, rely=0.5, anchor="center")

        # Content Container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Row 1: Button, Path, Trash
        self.row1 = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.row1.pack(fill="x")

        self.select_button = ctk.CTkButton(
            self.row1,
            text="📁 SELECT FOLDER",
            width=160,
            height=36,
            corner_radius=6,
            fg_color="#15803d",
            text_color="#ffffff",
            hover_color="#16a34a",
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
            command=self.on_clear_folder if self.on_clear_folder else self.clear_folder,
        )
        self.btn_clear.pack(side="left")

        # Row 2: Videos Found Text
        self.count_label = ctk.CTkLabel(
            self.content_frame,
            text="0 videos found",
            font=("Segoe UI", 12),
            text_color="#9ca3af",
        )
        self.count_label.pack(anchor="e", pady=(5, 0))

    def select_folder(self):
        self.on_select_folder()

    def set_path(self, path):
        self.cta_path = path
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
            videos_found_text = self.lang["videos_found"] if hasattr(self, 'lang') else "{} videos found"
            self.count_label.configure(text=videos_found_text.format(len(videos)))
        else:
            videos_found_text = self.lang["videos_found"] if hasattr(self, 'lang') else "{} videos found"
            self.count_label.configure(text=videos_found_text.format(0))

    def update_language(self, lang):
        self.lang = lang
        self.cta_title.configure(text=lang["ctas"])
        self.select_button.configure(text=lang["select_folder"])
        self.btn_clear.configure(text=lang["clear"])
        self.set_path(self.cta_path)

    def clear_folder(self):
        self.cta_path = ""
        self.set_path("")

    def clear(self):
        # Kept for compatibility with main_window.py
        self.clear_folder()
