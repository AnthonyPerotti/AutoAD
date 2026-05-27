import customtkinter as ctk


class SettingsWindow(ctk.CTkToplevel):

    def __init__(self, parent, encoder_var, language_var, on_save, on_language_change):

        super().__init__(parent)

        self.title("Settings")

        self.geometry("420x420")

        self.resizable(False, False)

        self.grab_set()

        # ============================================
        # TITLE
        # ============================================

        title = ctk.CTkLabel(self, text="⚙ Settings", font=("Segoe UI Semibold", 24))

        title.pack(pady=(20, 25))

        # ============================================
        # ENCODER
        # ============================================

        encoder_label = ctk.CTkLabel(self, text="Render Encoder", font=("Segoe UI", 14))

        encoder_label.pack(anchor="w", padx=25)

        encoder_menu = ctk.CTkOptionMenu(
            self,
            values=["CPU (libx264)", "NVIDIA (NVENC)", "AMD (AMF)", "Intel (QSV)"],
            variable=encoder_var,
            width=250,
            command=lambda _: on_save(),
        )

        encoder_menu.pack(pady=(5, 20))

        # ============================================
        # LANGUAGE
        # ============================================

        language_label = ctk.CTkLabel(self, text="Language", font=("Segoe UI", 14))

        language_label.pack(anchor="w", padx=25)

        language_menu = ctk.CTkOptionMenu(
            self,
            values=["Português", "English"],
            variable=language_var,
            width=250,
            command=lambda _: (on_language_change(), on_save()),
        )

        language_menu.pack(pady=(5, 20))
