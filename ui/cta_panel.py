import os

import customtkinter as ctk

from PIL import Image

from core.thumbnails import gerar_thumbnail


class CTAPanel(ctk.CTkFrame):

    def __init__(self, parent, on_select):

        super().__init__(
            parent,
            corner_radius=18,
            fg_color="#102016",
            border_width=1,
            border_color="#22c55e",
        )

        self.cta_path = ""

        self.on_select = on_select

        # ============================================
        # TITLE
        # ============================================

        self.cta_title = ctk.CTkLabel(
            self, text="📢 CTAs", font=("Segoe UI", 20, "bold"), text_color="#4ade80"
        )

        self.cta_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BUTTONS
        # ============================================

        buttons = ctk.CTkFrame(self, fg_color="transparent")

        buttons.pack(fill="x", padx=20)

        self.btn_add = ctk.CTkButton(
            buttons,
            text="Adicionar",
            width=140,
            height=38,
            corner_radius=12,
            fg_color="#16a34a",
            hover_color="#22c55e",
            command=self.select_folder,
        )

        self.btn_add.pack(side="left", padx=(0, 10))

        # ============================================
        # DROP AREA
        # ============================================

        drop = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#0b1a11",
            border_width=1,
            border_color="#166534",
            height=180,
        )

        drop.pack(fill="both", expand=True, padx=20, pady=20)

        drop.pack_propagate(False)

        self.preview = ctk.CTkScrollableFrame(drop, fg_color="transparent")

        self.preview.pack(fill="both", expand=True, padx=10, pady=10)

        self.label = ctk.CTkLabel(
            drop,
            text="Adicione os vídeos CTA",
            font=("Segoe UI", 18),
            text_color="#9ca3af",
        )

        self.label.place(relx=0.5, rely=0.5, anchor="center")

    def select_folder(self):

        self.on_select()

    def set_path(self, path):

        self.cta_path = path

        self.show_ctas()

    def clear(self):

        self.cta_path = ""

        for widget in self.preview.winfo_children():

            widget.destroy()

        self.label.place(relx=0.5, rely=0.5, anchor="center")

    def show_ctas(self):

        self.label.place_forget()

        for widget in self.preview.winfo_children():

            widget.destroy()

        videos = [f for f in os.listdir(self.cta_path) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(self.cta_path, video)

            thumb = gerar_thumbnail(full_path)

            item = ctk.CTkFrame(
                self.preview,
                corner_radius=10,
                fg_color="#102016",
                width=180,
                height=150,
            )

            row = index // 3
            col = index % 3

            item.grid(row=row, column=col, padx=8, pady=8, sticky="n")

            item.grid_propagate(False)

            if thumb and os.path.exists(thumb):

                image = Image.open(thumb)

                img = ctk.CTkImage(light_image=image, dark_image=image, size=(160, 90))

                img_label = ctk.CTkLabel(item, image=img, text="")

                img_label.image = img

                img_label.pack(pady=(10, 5))

            text = ctk.CTkLabel(item, text=video, font=("Segoe UI", 13))

            text.pack(padx=8, pady=(0, 8))
