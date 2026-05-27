import os
import threading

import customtkinter as ctk

from PIL import Image

from core.thumbnails import gerar_thumbnail


class HooksPanel(ctk.CTkFrame):

    def __init__(self, parent, on_select_folder):

        super().__init__(
            parent,
            corner_radius=20,
            fg_color="#161616",
            border_width=1,
            border_color="#3f3f46",
        )

        self.hooks_path = ""

        self.on_select_folder = on_select_folder

        # ============================================
        # TITLE
        # ============================================

        self.hooks_title = ctk.CTkLabel(
            self, text="🎣 HOOKS", font=("Segoe UI", 22, "bold"), text_color="#f3f4f6"
        )

        self.hooks_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BUTTON
        # ============================================

        self.select_button = ctk.CTkButton(
            self,
            text="Selecionar Pasta",
            width=180,
            height=40,
            corner_radius=12,
            command=self.select_folder,
        )

        self.select_button.pack(anchor="w", padx=20, pady=(0, 15))

        # ============================================
        # SCROLL
        # ============================================

        self.preview = ctk.CTkScrollableFrame(self, height=260, fg_color="#0f172a")

        self.preview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ============================================
        # LOADING LABEL
        # ============================================

        self.loading_label = ctk.CTkLabel(
            self.preview,
            text="Nenhum hook carregado",
            font=("Segoe UI", 14),
            text_color="#9ca3af",
        )

        self.loading_label.pack(pady=40)

    def select_folder(self):

        self.on_select_folder()

    def set_path(self, path):

        self.hooks_path = path

        self.loading_label.configure(text="Carregando previews...")

        threading.Thread(target=self.load_hooks, daemon=True).start()

    def clear_preview(self):

        for widget in self.preview.winfo_children():

            widget.destroy()

    def load_hooks(self):

        self.after(0, self.clear_preview)

        videos = [f for f in os.listdir(self.hooks_path) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(self.hooks_path, video)

            thumb = gerar_thumbnail(full_path)

            row = index // 3
            col = index % 3

            self.after(
                0,
                lambda v=video, t=thumb, r=row, c=col: self.create_hook_card(
                    v, t, r, c
                ),
            )

    def create_hook_card(self, video, thumb, row, col):

        item = ctk.CTkFrame(
            self.preview, corner_radius=10, fg_color="#111827", width=180, height=150
        )

        item.grid(row=row, column=col, padx=8, pady=8, sticky="n")

        item.grid_propagate(False)

        if thumb and os.path.exists(thumb):

            try:

                image = Image.open(thumb)

                img = ctk.CTkImage(light_image=image, dark_image=image, size=(160, 90))

                img_label = ctk.CTkLabel(item, image=img, text="")

                img_label.image = img

                img_label.pack(pady=(10, 5))

            except:

                pass

        text = ctk.CTkLabel(item, text=video, font=("Segoe UI", 13))

        text.pack(padx=8, pady=(0, 8))
