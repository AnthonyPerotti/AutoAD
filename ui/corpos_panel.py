import os

import customtkinter as ctk

from PIL import Image

from core.thumbnails import gerar_thumbnail


class CorposPanel(ctk.CTkFrame):

    def __init__(self, parent, on_select, on_update_total, on_log):

        super().__init__(
            parent,
            corner_radius=18,
            fg_color="#1a1325",
            border_width=1,
            border_color="#7c3aed",
        )

        self.on_select = on_select

        self.on_update_total = on_update_total

        self.on_log = on_log

        self.cards = []

        # ============================================
        # TITLE
        # ============================================

        self.corpos_title = ctk.CTkLabel(
            self, text="🎬 CORPOS", font=("Segoe UI", 20, "bold"), text_color="#c084fc"
        )

        self.corpos_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BUTTONS
        # ============================================

        buttons = ctk.CTkFrame(self, fg_color="transparent")

        buttons.pack(fill="x", padx=20)

        self.btn_add = ctk.CTkButton(
            buttons,
            text="+ Adicionar Corpo",
            width=180,
            height=38,
            corner_radius=12,
            fg_color="#7c3aed",
            hover_color="#8b5cf6",
            command=self.add_body,
        )

        self.btn_add.pack(side="left", padx=(0, 10))

        self.btn_clear = ctk.CTkButton(
            buttons,
            text="Limpar",
            width=120,
            height=38,
            corner_radius=12,
            fg_color="#3b2a50",
            hover_color="#4c3570",
            command=self.clear,
        )

        self.btn_clear.pack(side="left")

        # ============================================
        # AREA
        # ============================================

        self.area = ctk.CTkScrollableFrame(
            self,
            corner_radius=16,
            fg_color="#120d1c",
            border_width=1,
            border_color="#5b21b6",
            height=260,
        )

        self.area.pack(fill="both", expand=True, padx=20, pady=20)

        self.add_body()

    def add_body(self):

        if len(self.cards) >= 6:

            self.on_log("Limite máximo de corpos atingido.")

            return

        index = len(self.cards) + 1

        card = ctk.CTkFrame(self.area, corner_radius=12, fg_color="#241737")

        card.pack(fill="x", pady=8, padx=5)

        card.path = ""

        # ============================================
        # LABEL
        # ============================================

        title = ctk.CTkLabel(card, text=f"Corpo {index}", font=("Segoe UI", 14, "bold"))

        title.pack(side="left", padx=15, pady=12)

        # ============================================
        # SELECT BUTTON
        # ============================================

        preview = ctk.CTkScrollableFrame(card, height=180, fg_color="#1a1325")

        preview.pack(fill="x", padx=10, pady=(0, 10))

        path_label = ctk.CTkLabel(
            card, text="Nenhuma pasta selecionada", text_color="#9ca3af"
        )

        path_label.pack(anchor="w", padx=15, pady=(0, 10))

        btn_select = ctk.CTkButton(
            card,
            text="Selecionar Pasta",
            width=160,
            height=32,
            corner_radius=10,
            command=lambda: self.select_body(card, path_label, preview),
        )

        btn_select.pack(side="right", padx=10, pady=10)

        # ============================================
        # REMOVE BUTTON
        # ============================================

        btn_remove = ctk.CTkButton(
            card,
            text="-",
            width=32,
            height=32,
            corner_radius=10,
            fg_color="#991b1b",
            hover_color="#dc2626",
            command=lambda: self.remove_body(card),
        )

        btn_remove.pack(side="right", padx=(0, 5))

        self.cards.append(card)

    def update_indexes(self):

        for i, card in enumerate(self.cards):

            for widget in card.winfo_children():

                if isinstance(widget, ctk.CTkLabel):

                    text = widget.cget("text")

                    if text.startswith("Corpo"):

                        widget.configure(text=f"Corpo {i+1}")

    def remove_body(self, card):

        if len(self.cards) <= 1:
            return

        self.cards.remove(card)

        card.destroy()

        self.update_indexes()

        self.on_update_total()

        self.on_log("Corpo removido.")

    def select_body(self, card, label, preview):

        path = self.on_select()

        if not path:
            return

        card.path = path

        label.configure(text=os.path.basename(path))

        self.show_preview(path, preview)

        self.on_update_total()

        self.on_log(f"Corpo carregado: {path}")

    def show_preview(self, path, preview):

        for widget in preview.winfo_children():

            widget.destroy()

        videos = [f for f in os.listdir(path) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(path, video)

            thumb = gerar_thumbnail(full_path)

            item = ctk.CTkFrame(
                preview, corner_radius=10, fg_color="#241737", width=180, height=150
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

                img_label.pack(padx=5, pady=5)

            text = ctk.CTkLabel(item, text=video, wraplength=120, font=("Segoe UI", 11))

            text.pack(padx=5, pady=(0, 5))

    def clear(self):

        for card in self.cards:

            card.destroy()

        self.cards.clear()

        self.add_body()

        self.on_update_total()

        self.on_log("Corpos removidos.")
