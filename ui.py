import os
import customtkinter as ctk
import itertools
import subprocess
import threading
import json

from translations import translations
from tkinter import messagebox
from PIL import Image
from logic import FFMPEG_PATH
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AutoAddApp(ctk.CTk):

    # ============================================
    # LOG
    # ============================================

    def add_log(self, text):

        self.log_box.insert("end", f"{text}\n")

        self.log_box.see("end")

    # ============================================
    # LIMPAR HOOKS
    # ============================================

    def limpar_hooks(self):

        self.hooks_path = ""

        for widget in self.hooks_preview.winfo_children():
            widget.destroy()

        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.atualizar_total()

        self.add_log("Hooks removidos.")

    # ============================================
    # LIMPAR CORPOS
    # ============================================

    def limpar_corpos(self):

        for card in self.corpos_widgets:

            card.destroy()

        self.corpos_widgets.clear()

        self.adicionar_corpo()

        self.atualizar_total()

        self.add_log("Corpos removidos.")

    # ============================================
    # LIMPAR CTA
    # ============================================

    def limpar_cta(self):

        self.cta_path = ""

        for widget in self.cta_preview.winfo_children():

            widget.destroy()

        self.cta_label.place(relx=0.5, rely=0.5, anchor="center")

        self.atualizar_total()

        self.add_log("CTAs removidos.")

    # ============================================
    # SELECIONAR HOOKS
    # ============================================

    def selecionar_hooks(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.hooks_path = pasta

        self.drop_label.configure(text=os.path.basename(pasta))

        self.add_log(f"Hooks carregados: {pasta}")

        self.atualizar_total()

        self.drop_label.configure(text="Carregando previews...")

        threading.Thread(target=self.mostrar_hooks, daemon=True).start()

    # ============================================
    # MOSTRAR HOOKS
    # ============================================

    def mostrar_hooks(self):

        self.after(0, self.limpar_hooks_preview)

        videos = [f for f in os.listdir(self.hooks_path) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(self.hooks_path, video)

            thumb = self.gerar_thumbnail(full_path)

            row = index // 3
            col = index % 3

            self.after(
                0,
                lambda v=video, t=thumb, r=row, c=col: self.criar_hook_card(v, t, r, c),
            )

        self.after(0, self.finalizar_hooks_preview)

    def limpar_hooks_preview(self):

        self.drop_label.place_forget()

        for widget in self.hooks_preview.winfo_children():

            widget.destroy()

    def finalizar_hooks_preview(self):

        self.add_log("Hooks carregados.")

    def criar_hook_card(self, video, thumb, row, col):

        item = ctk.CTkFrame(
            self.hooks_preview,
            corner_radius=10,
            fg_color="#111827",
            width=180,
            height=150,
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

    # ============================================
    # GERAR THUMB
    # ============================================

    def gerar_thumbnail(self, video_path):
        try:
            os.makedirs("thumbs", exist_ok=True)
            nome = os.path.splitext(os.path.basename(video_path))[0]
            thumb_path = os.path.join("thumbs", f"{nome}.jpg")
            if os.path.exists(thumb_path):
                return thumb_path
            cmd = [
                FFMPEG_PATH,
                "-y",
                "-ss",
                "00:00:05",
                "-i",
                video_path,
                "-vf",
                "scale=320:-1",
                "-vframes",
                "1",
                thumb_path,
            ]

            startupinfo = subprocess.STARTUPINFO()

            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            return thumb_path
        except:
            return None

    # ============================================
    # ADICIONAR CORPO
    # ============================================

    def adicionar_corpo(self):

        if len(self.corpos_widgets) >= 6:

            self.add_log("Limite máximo de corpos atingido.")

            return

        index = len(self.corpos_widgets) + 1

        card = ctk.CTkFrame(self.corpos_area, corner_radius=12, fg_color="#241737")

        card.pack(fill="x", pady=8, padx=5)

        card.path = ""

        # ============================================
        # LABEL
        # ============================================

        label = ctk.CTkLabel(card, text=f"Corpo {index}", font=("Segoe UI", 14, "bold"))

        label.pack(side="left", padx=15, pady=12)

        # ============================================
        # BOTÃO SELECIONAR
        # ============================================

        btn_select = ctk.CTkButton(
            card,
            text="Selecionar Pasta",
            width=160,
            height=32,
            corner_radius=10,
            command=lambda c=card: self.selecionar_corpo(c, path_label, preview),
        )

        btn_select.pack(side="right", padx=10, pady=10)

        # ============================================
        # BOTÃO REMOVER
        # ============================================

        btn_remove = ctk.CTkButton(
            card,
            text="-",
            width=32,
            height=32,
            corner_radius=10,
            fg_color="#991b1b",
            hover_color="#dc2626",
            command=lambda: self.remover_corpo(card),
        )

        btn_remove.pack(side="right", padx=(0, 5))

        # ============================================
        # PATH
        # ============================================

        path_label = ctk.CTkLabel(
            card, text="Nenhuma pasta selecionada", text_color="#9ca3af"
        )

        path_label.pack(anchor="w", padx=15, pady=(0, 10))

        preview = ctk.CTkScrollableFrame(card, height=180, fg_color="#1a1325")

        preview.pack(fill="x", padx=10, pady=(0, 10))

        self.corpos_widgets.append(card)

    # ============================================
    # REINDEXAR CORPOS
    # ============================================

    def atualizar_indices_corpos(self):

        for i, card in enumerate(self.corpos_widgets):

            card.index = i

            for widget in card.winfo_children():

                if isinstance(widget, ctk.CTkLabel):

                    texto = widget.cget("text")

                    if texto.startswith("Corpo"):

                        widget.configure(text=f"Corpo {i+1}")

    # ============================================
    # REMOVER CORPO
    # ============================================

    def remover_corpo(self, card):

        if len(self.corpos_widgets) <= 1:
            return

        self.corpos_widgets.remove(card)

        card.destroy()

        self.atualizar_indices_corpos()

        self.atualizar_total()

        self.add_log("Corpo removido.")

    # ============================================
    # SELECIONAR CORPO
    # ============================================

    def selecionar_corpo(self, card, label, preview):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        card.path = pasta

        label.configure(text=os.path.basename(pasta))

        self.add_log(f"Corpo carregado: {pasta}")

        self.mostrar_preview_corpo(pasta, preview)

        self.atualizar_total()

    # ============================================
    # MOSTRAR PREVIEW CORPO
    # ============================================

    def mostrar_preview_corpo(self, pasta, preview):

        for widget in preview.winfo_children():

            widget.destroy()

        videos = [f for f in os.listdir(pasta) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(pasta, video)

            thumb = self.gerar_thumbnail(full_path)

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

            label = ctk.CTkLabel(
                item, text=video, wraplength=120, font=("Segoe UI", 11)
            )

            label.pack(padx=5, pady=(0, 5))

    # ============================================
    # SELECIONAR CTA
    # ============================================

    def selecionar_cta(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.cta_path = pasta

        self.cta_label.configure(text=os.path.basename(pasta))

        self.add_log(f"CTA carregado: {pasta}")

        self.atualizar_total()
        self.mostrar_ctas()

    # ============================================
    # MOSTRAR CTAs
    # ============================================

    def mostrar_ctas(self):

        self.cta_label.place_forget()

        for widget in self.cta_preview.winfo_children():

            widget.destroy()

        videos = [f for f in os.listdir(self.cta_path) if f.lower().endswith(".mp4")]

        for index, video in enumerate(videos):

            full_path = os.path.join(self.cta_path, video)

            thumb = self.gerar_thumbnail(full_path)

            item = ctk.CTkFrame(
                self.cta_preview,
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

    # ============================================
    # SELECIONAR OUTPUT
    # ============================================

    def selecionar_output(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.output_path = pasta

        self.output_label.configure(text=pasta)

        self.add_log(f"Saída definida: {pasta}")

        self.atualizar_total()

    # ============================================
    # TOTAL PREVISTO
    # ============================================

    def atualizar_total(self):

        self.total_label.configure(text="Total previsto: 0 vídeos")

        try:

            if not self.hooks_path:
                return

            if not self.cta_path:
                return

            total = 1

            hooks = len(
                [f for f in os.listdir(self.hooks_path) if f.lower().endswith(".mp4")]
            )

            total *= hooks

            for card in self.corpos_widgets:

                pasta = card.path

                if not pasta:
                    return

                qtd = len([f for f in os.listdir(pasta) if f.lower().endswith(".mp4")])

                total *= qtd

            ctas = len(
                [f for f in os.listdir(self.cta_path) if f.lower().endswith(".mp4")]
            )

            total *= ctas

            self.total_label.configure(text=f"Total previsto: {total} vídeos")

        except:

            pass

    # ============================================
    # INICIAR GERAÇÃO
    # ============================================

    def iniciar_geracao(self):

        self.status_label.configure(text="Gerando vídeos...", text_color="#f59e0b")

        if self.renderizando:
            return

        self.renderizando = True

        self.progressbar.set(0)

        self.progress_label.configure(text="0 / 0")

        total_text = self.total_label.cget("text")

        try:

            total = int(total_text.split(":")[1].replace("vídeos", "").strip())

        except:

            total = 0

        if total > 100:

            continuar = messagebox.askyesno(
                "Confirmação", f"Serão gerados {total} vídeos.\n\nDeseja continuar?"
            )

            if not continuar:

                self.renderizando = False

                return

        thread = threading.Thread(target=self.gerar_videos, daemon=True)

        thread.start()

    # ============================================
    # GERAR VÍDEOS
    # ============================================

    def gerar_videos(self):

        self.stop_requested = False

        # ============================================
        # VALIDAR
        # ============================================

        if not self.hooks_path:

            self.add_log("Selecione os hooks.")

            self.renderizando = False

            return

        if not self.cta_path:

            self.add_log("Selecione os CTAs.")

            self.renderizando = False

            return

        if not self.output_path:

            self.add_log("Selecione a saída.")

            self.renderizando = False

            return

        # ============================================
        # LISTAS
        # ============================================

        hooks = [f for f in os.listdir(self.hooks_path) if f.lower().endswith(".mp4")]

        ctas = [f for f in os.listdir(self.cta_path) if f.lower().endswith(".mp4")]

        corpos_listas = []

        for card in self.corpos_widgets:

            pasta = card.path

            if not pasta:

                self.add_log("Selecione todas as pastas de corpos.")

                self.renderizando = False

                return

            if not os.path.exists(pasta):

                self.add_log(f"Pasta inexistente: {pasta}")

                self.renderizando = False

                return

            videos = [f for f in os.listdir(pasta) if f.lower().endswith(".mp4")]

            corpos_listas.append((pasta, videos))

        # ============================================
        # COMBINAÇÕES
        # ============================================

        lista_final = []

        for hook in hooks:

            for cta in ctas:

                corpos_videos = []

                for pasta, videos in corpos_listas:

                    corpos_videos.append([os.path.join(pasta, v) for v in videos])

                for combinacao in itertools.product(*corpos_videos):

                    lista = []

                    lista.append(os.path.join(self.hooks_path, hook))

                    lista.extend(combinacao)

                    lista.append(os.path.join(self.cta_path, cta))

                    lista_final.append(lista)

        # ============================================
        # TOTAL
        # ============================================

        total = len(lista_final)

        self.add_log(f"{total} vídeos serão gerados.")

        # ============================================
        # LOOP
        # ============================================

        for index, videos in enumerate(lista_final):

            if self.stop_requested:

                self.status_label.configure(text="Interrompido", text_color="#ef4444")

                self.add_log("Geração interrompida.")

                break

            self.add_log(f"Gerando {index+1}/{total}")

            temp_txt = os.path.join(os.getcwd(), f"temp_{index}.txt")

            with open(temp_txt, "w", encoding="utf-8") as f:

                for video in videos:

                    video = video.replace("\\", "/")

                    f.write(f"file '{video}'\n")

            hook_nome = os.path.splitext(os.path.basename(videos[0]))[0]

            cta_nome = os.path.splitext(os.path.basename(videos[-1]))[0]

            corpos_nome = []

            for corpo in videos[1:-1]:

                corpos_nome.append(os.path.splitext(os.path.basename(corpo))[0])

            nome_corpos = "_".join(corpos_nome)

            nome_final = f"{hook_nome}" f"_{nome_corpos}" f"_{cta_nome}.mp4"

            nome_final = nome_final[:180]

            output_file = os.path.join(self.output_path, nome_final)

            cmd = [
                FFMPEG_PATH,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                temp_txt,
                "-c:v",
                self.get_encoder(),
                "-c:a",
                "aac",
                "-preset",
                "fast",
                output_file,
            ]

            startupinfo = subprocess.STARTUPINFO()

            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            stdout, stderr = self.current_process.communicate()

            returncode = self.current_process.returncode

            self.current_process = None

            if returncode != 0 and not self.stop_requested:

                self.add_log(f"ERRO FFmpeg:\n{stderr}")

                self.current_process = None

            if os.path.exists(temp_txt):

                os.remove(temp_txt)

            progresso = (index + 1) / total

            self.progressbar.set(progresso)

            self.progress_label.configure(text=f"{index+1} / {total}")

            self.after(0, lambda: None)

        if self.stop_requested:

            self.add_log("Render interrompido.")

            self.status_label.configure(text="Interrompido", text_color="#ef4444")

        else:

            self.add_log("Finalizado.")

            self.status_label.configure(text="Finalizado", text_color="#22c55e")

        self.renderizando = False

        if self.auto_open_var.get():

            os.startfile(self.output_path)

    # ============================================
    # GET ENCODER
    # ============================================

    def get_encoder(self):

        encoder = self.encoder_var.get()

        if "NVIDIA" in encoder:

            return "h264_nvenc"

        if "AMD" in encoder:

            return "h264_amf"

        if "Intel" in encoder:

            return "h264_qsv"

        return "libx264"

    # ============================================
    # STOP
    # ============================================

    def parar(self):

        self.stop_requested = True

        if self.current_process:

            try:

                self.current_process.kill()

                self.add_log("FFmpeg interrompido.")

            except:

                pass

    def abrir_configuracoes(self):

        config_window = ctk.CTkToplevel(self)

        config_window.title("Settings")

        config_window.geometry("420x420")

        config_window.resizable(False, False)

        config_window.grab_set()

        # ============================================
        # TITLE
        # ============================================

        title = ctk.CTkLabel(
            config_window, text="⚙ Settings", font=("Segoe UI Semibold", 24)
        )

        title.pack(pady=(20, 25))

        # ============================================
        # ENCODER
        # ============================================

        encoder_label = ctk.CTkLabel(
            config_window, text="Render Encoder", font=("Segoe UI", 14)
        )

        encoder_label.pack(anchor="w", padx=25)

        encoder_menu = ctk.CTkOptionMenu(
            config_window,
            values=["CPU (libx264)", "NVIDIA (NVENC)", "AMD (AMF)", "Intel (QSV)"],
            variable=self.encoder_var,
            width=250,
            command=lambda _: self.salvar_config(),
        )

        encoder_menu.pack(pady=(5, 20))

        # ============================================
        # LANGUAGE
        # ============================================

        language_label = ctk.CTkLabel(
            config_window, text="Language", font=("Segoe UI", 14)
        )

        language_label.pack(anchor="w", padx=25)

        language_label.pack(anchor="w", padx=25)

        language_menu = ctk.CTkOptionMenu(
            config_window,
            values=["Português", "English"],
            variable=self.language_var,
            width=250,
            command=lambda _: self.aplicar_idioma(),
        )

        language_menu.pack(pady=(5, 20))

    def aplicar_idioma(self):

        lang = translations[self.language_var.get()]

        self.title(lang["title"])

        self.title_label.configure(text=lang["title"])

        self.hooks_title.configure(text=lang["hooks"])

        self.corpos_title.configure(text=lang["bodies"])

        self.cta_title.configure(text=lang["ctas"])

        self.output_title.configure(text=lang["output"])

        self.control_title.configure(text=lang["controls"])

        self.logs_title.configure(text=lang["logs"])

        self.btn_generate.configure(text=lang["generate"])

        self.btn_stop.configure(text=lang["stop"])

        self.progress_title.configure(text=lang["progress"])

        self.auto_open_checkbox.configure(text=lang["auto_open"])

        self.btn_open_output.configure(text=lang["open_output"])

        self.status_label.configure(text=lang["ready"])

        self.salvar_config()

    def abrir_output(self):

        if not self.output_path:
            return

        os.startfile(self.output_path)

    def salvar_config(self):

        config = {
            "encoder": self.encoder_var.get(),
            "auto_open": self.auto_open_var.get(),
            "language": self.language_var.get(),
        }

        with open("settings.json", "w", encoding="utf-8") as f:

            json.dump(config, f, indent=4)

    def carregar_config(self):

        if not os.path.exists("settings.json"):
            return

        try:

            with open("settings.json", "r", encoding="utf-8") as f:

                config = json.load(f)

            self.encoder_var.set(config.get("encoder", "CPU (libx264)"))

            self.auto_open_var.set(config.get("auto_open", False))

            self.language_var.set(config.get("language", "Português"))

        except:

            pass
        
        self.aplicar_idioma()

    def __init__(self):

        super().__init__()

        self.language_var = ctk.StringVar(value="Português")

        # ============================================
        # CONTAINER PRINCIPAL
        # ============================================

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")

        self.main_container.pack(fill="both", expand=True)

        self.encoder_var = ctk.StringVar(value="CPU (libx264)")

        # ============================================
        # ESTADOS
        # ============================================

        self.hooks_path = ""
        self.cta_path = ""
        self.output_path = ""
        self.corpos_widgets = []
        self.stop_requested = False
        self.renderizando = False
        self.current_process = None

        # ============================================
        # JANELA
        # ============================================

        self.title("AutoAD")

        self.geometry("1180x760")

        self.minsize(980, 650)

        # ============================================
        # GRID PRINCIPAL
        # ============================================

        self.main_container.grid_columnconfigure(0, weight=1)

        self.main_container.grid_columnconfigure(1, weight=1)

        self.main_container.grid_rowconfigure(1, weight=1)

        self.main_container.grid_rowconfigure(2, weight=1)

        self.main_container.grid_rowconfigure(4, weight=1)

        # ============================================
        # TÍTULO
        # ============================================

        self.title_label = ctk.CTkLabel(
            self.main_container, text="AutoAD", font=("Segoe UI", 28, "bold")
        )

        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        settings_button = ctk.CTkButton(
            self.main_container,
            text="⚙",
            width=40,
            height=40,
            corner_radius=12,
            font=("Segoe UI", 18),
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.abrir_configuracoes,
        )

        settings_button.place(relx=0.97, y=35, anchor="ne")

        # ============================================
        # CARD HOOKS
        # ============================================

        hooks_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=18,
            fg_color="#111827",
            border_width=1,
            border_color="#2563eb",
        )

        hooks_card.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="nsew")

        # ============================================
        # TÍTULO HOOKS
        # ============================================

        self.hooks_title = ctk.CTkLabel(
            hooks_card,
            text="🎣 HOOKS",
            font=("Segoe UI", 20, "bold"),
            text_color="#60a5fa",
        )

        self.hooks_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BOTÕES
        # ============================================

        hooks_buttons_frame = ctk.CTkFrame(hooks_card, fg_color="transparent")

        hooks_buttons_frame.pack(fill="x", padx=20)

        btn_hooks_add = ctk.CTkButton(
            hooks_buttons_frame,
            text="Adicionar",
            width=140,
            height=38,
            corner_radius=12,
            command=self.selecionar_hooks,
        )

        btn_hooks_add.pack(side="left", padx=(0, 10))

        btn_hooks_clear = ctk.CTkButton(
            hooks_buttons_frame,
            text="Limpar",
            width=120,
            height=38,
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=12,
            command=self.limpar_hooks,
        )

        btn_hooks_clear.pack(side="left")

        # ============================================
        # DROP AREA
        # ============================================

        hooks_drop = ctk.CTkFrame(
            hooks_card,
            corner_radius=16,
            fg_color="#0b1220",
            border_width=1,
            border_color="#1e3a8a",
            height=260,
        )

        self.hooks_preview = ctk.CTkScrollableFrame(hooks_drop, fg_color="transparent")

        self.hooks_preview.pack(fill="both", expand=True, padx=10, pady=10)

        hooks_drop.pack(fill="both", expand=True, padx=20, pady=20)

        hooks_drop.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            hooks_drop,
            text="Arraste e solte os hooks aqui\n\nou clique em Adicionar",
            font=("Segoe UI", 18),
            text_color="#9ca3af",
            justify="center",
        )

        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # ============================================
        # CARD CORPOS
        # ============================================

        corpos_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=18,
            fg_color="#1a1325",
            border_width=1,
            border_color="#7c3aed",
        )

        corpos_card.grid(row=1, column=1, padx=(10, 20), pady=(10, 10), sticky="nsew")

        # ============================================
        # TÍTULO
        # ============================================

        self.corpos_title = ctk.CTkLabel(
            corpos_card,
            text="🎬 CORPOS",
            font=("Segoe UI", 20, "bold"),
            text_color="#c084fc",
        )

        self.corpos_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BOTÕES
        # ============================================

        corpos_buttons = ctk.CTkFrame(corpos_card, fg_color="transparent")

        corpos_buttons.pack(fill="x", padx=20)

        btn_add_corpo = ctk.CTkButton(
            corpos_buttons,
            text="+ Adicionar Corpo",
            width=180,
            height=38,
            corner_radius=12,
            fg_color="#7c3aed",
            hover_color="#8b5cf6",
            command=self.adicionar_corpo,
        )

        btn_add_corpo.pack(side="left", padx=(0, 10))

        btn_clear_corpos = ctk.CTkButton(
            corpos_buttons,
            text="Limpar",
            width=120,
            height=38,
            corner_radius=12,
            fg_color="#3b2a50",
            hover_color="#4c3570",
            command=self.limpar_corpos,
        )

        btn_clear_corpos.pack(side="left")

        # ============================================
        # ÁREA DOS CORPOS
        # ============================================

        self.corpos_area = ctk.CTkScrollableFrame(
            corpos_card,
            corner_radius=16,
            fg_color="#120d1c",
            border_width=1,
            border_color="#5b21b6",
            height=260,
        )

        self.corpos_area.pack(fill="both", expand=True, padx=20, pady=20)

        self.adicionar_corpo()

        # ============================================
        # CARD CTA
        # ============================================

        cta_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=18,
            fg_color="#102016",
            border_width=1,
            border_color="#22c55e",
        )

        cta_card.grid(row=2, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")

        # ============================================
        # TÍTULO
        # ============================================

        self.cta_title = ctk.CTkLabel(
            cta_card,
            text="📢 CTAs",
            font=("Segoe UI", 20, "bold"),
            text_color="#4ade80",
        )

        self.cta_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # BOTÕES
        # ============================================

        cta_buttons = ctk.CTkFrame(cta_card, fg_color="transparent")

        cta_buttons.pack(fill="x", padx=20)

        btn_cta_add = ctk.CTkButton(
            cta_buttons,
            text="Adicionar",
            width=140,
            height=38,
            corner_radius=12,
            fg_color="#16a34a",
            hover_color="#22c55e",
            command=self.selecionar_cta,
        )

        btn_cta_add.pack(side="left", padx=(0, 10))

        btn_cta_clear = ctk.CTkButton(
            cta_buttons,
            text="Limpar",
            width=120,
            height=38,
            corner_radius=12,
            fg_color="#1f3b2b",
            hover_color="#2b513b",
            command=self.limpar_cta,
        )

        btn_cta_clear.pack(side="left")

        # ============================================
        # DROP AREA
        # ============================================

        cta_drop = ctk.CTkFrame(
            cta_card,
            corner_radius=16,
            fg_color="#0b1a11",
            border_width=1,
            border_color="#166534",
            height=180,
        )

        cta_drop.pack(fill="both", expand=True, padx=20, pady=20)

        cta_drop.pack_propagate(False)

        self.cta_preview = ctk.CTkScrollableFrame(cta_drop, fg_color="transparent")

        self.cta_preview.pack(fill="both", expand=True, padx=10, pady=10)

        self.cta_label = ctk.CTkLabel(
            cta_drop,
            text="Adicione os vídeos CTA",
            font=("Segoe UI", 18),
            text_color="#9ca3af",
        )

        self.cta_label.place(relx=0.5, rely=0.5, anchor="center")

        # ============================================
        # CARD SAÍDA
        # ============================================

        output_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=18,
            fg_color="#2a1a0f",
            border_width=1,
            border_color="#f59e0b",
        )

        output_card.grid(row=2, column=1, padx=(10, 20), pady=(0, 10), sticky="nsew")

        # ============================================
        # TÍTULO
        # ============================================

        self.output_title = ctk.CTkLabel(
            output_card,
            text="📁 SAÍDA",
            font=("Segoe UI", 20, "bold"),
            text_color="#fbbf24",
        )

        self.output_title.pack(anchor="w", padx=20, pady=(15, 10))

        # ============================================
        # DESCRIÇÃO
        # ============================================

        output_desc = ctk.CTkLabel(
            output_card,
            text="Escolha onde os vídeos serão exportados",
            font=("Segoe UI", 14),
            text_color="#9ca3af",
        )

        output_desc.pack(anchor="w", padx=20)

        # ============================================
        # BOTÃO
        # ============================================

        btn_output = ctk.CTkButton(
            output_card,
            text="Selecionar Pasta de Saída",
            width=260,
            height=42,
            corner_radius=14,
            fg_color="#d97706",
            hover_color="#f59e0b",
            font=("Segoe UI", 14, "bold"),
            command=self.selecionar_output,
        )

        btn_output.pack(padx=20, pady=(20, 10), anchor="w")

        # ============================================
        # LABEL
        # ============================================

        self.output_label = ctk.CTkLabel(
            output_card,
            text="Nenhuma pasta selecionada",
            wraplength=420,
            justify="left",
            text_color="#d1d5db",
        )

        self.output_label.pack(anchor="w", padx=20, pady=(0, 20))

        # ============================================
        # CARD CONTROLES
        # ============================================

        control_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color="#161616",
            border_width=1,
            border_color="#3f3f46",
        )

        control_card.grid(
            row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew"
        )

        # ============================================
        # HEADER
        # ============================================

        self.control_title = ctk.CTkLabel(
            control_card,
            text="⚡ CONTROLES",
            font=("Segoe UI", 22, "bold"),
            text_color="#f3f4f6",
        )

        self.control_title.pack(anchor="w", padx=20, pady=(15, 5))

        # ============================================
        # TOTAL
        # ============================================

        self.total_label = ctk.CTkLabel(
            control_card,
            text="Total previsto: 0 vídeos",
            font=("Segoe UI", 15, "bold"),
            text_color="#9ca3af",
        )

        self.total_label.pack(anchor="w", padx=20, pady=(0, 15))

        # ============================================
        # CONTROLS CONTENT
        # ============================================

        controls_content = ctk.CTkFrame(control_card, fg_color="transparent")

        controls_content.pack(fill="x", padx=20, pady=(0, 20))

        # ============================================
        # LEFT SIDE
        # ============================================

        left_controls = ctk.CTkFrame(controls_content, fg_color="transparent")

        left_controls.pack(side="left", anchor="n")

        # ============================================
        # RIGHT SIDE
        # ============================================

        right_controls = ctk.CTkFrame(controls_content, fg_color="transparent")

        right_controls.pack(side="right", anchor="ne")

        # ============================================
        # BUTTONS FRAME
        # ============================================

        buttons_frame = ctk.CTkFrame(left_controls, fg_color="transparent")

        buttons_frame.pack(anchor="w")

        # ============================================
        # BOTÃO GERAR
        # ============================================

        self.btn_generate = ctk.CTkButton(
            buttons_frame,
            text="GERAR VÍDEOS",
            width=260,
            height=52,
            corner_radius=16,
            fg_color="#2563eb",
            hover_color="#3b82f6",
            font=("Segoe UI", 16, "bold"),
            command=self.iniciar_geracao,
        )

        self.btn_generate.pack(side="left", padx=(0, 15), pady=(0, 20))

        # ============================================
        # BOTÃO STOP
        # ============================================

        self.btn_stop = ctk.CTkButton(
            buttons_frame,
            text="STOP",
            width=140,
            height=52,
            corner_radius=16,
            fg_color="#991b1b",
            hover_color="#dc2626",
            font=("Segoe UI", 16, "bold"),
            command=self.parar,
        )

        self.btn_stop.pack(side="left", pady=(0, 20))

        # ============================================
        # OUTPUT OPTIONS
        # ============================================

        output_options = ctk.CTkFrame(right_controls, fg_color="transparent")

        output_options.pack(anchor="e")

        self.auto_open_var = ctk.BooleanVar(value=False)

        self.auto_open_checkbox = ctk.CTkCheckBox(
            output_options,
            text="Open destination at end",
            variable=self.auto_open_var,
            font=("Segoe UI", 14),
            command=self.salvar_config,
        )

        self.auto_open_checkbox.pack(anchor="w", pady=(0, 10))

        self.btn_open_output = ctk.CTkButton(
            output_options,
            text="Open Output Folder",
            height=42,
            corner_radius=12,
            fg_color="#374151",
            hover_color="#4b5563",
            command=self.abrir_output,
        )

        self.btn_open_output.pack(anchor="w")

        # ============================================
        # PROGRESSO
        # ============================================

        self.progress_title = ctk.CTkLabel(
            control_card,
            text="PROGRESSO",
            font=("Segoe UI", 14, "bold"),
            text_color="#d1d5db",
        )

        self.progress_title.pack(anchor="w", padx=20)

        self.progressbar = ctk.CTkProgressBar(
            control_card,
            width=700,
            height=18,
            corner_radius=10,
            progress_color="#2563eb",
        )

        self.progressbar.pack(fill="x", padx=20, pady=(10, 5))

        self.progressbar.set(0)

        # ============================================
        # LABEL PROGRESSO
        # ============================================

        self.progress_label = ctk.CTkLabel(
            control_card, text="0 / 0", font=("Segoe UI", 13), text_color="#9ca3af"
        )

        self.progress_label.pack(anchor="w", padx=20, pady=(0, 20))

        # ============================================
        # CARD LOGS
        # ============================================

        logs_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=20,
            fg_color="#101010",
            border_width=1,
            border_color="#27272a",
        )

        logs_card.grid(
            row=4, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew"
        )

        # ============================================
        # HEADER
        # ============================================

        logs_header = ctk.CTkFrame(logs_card, fg_color="transparent")

        logs_header.pack(fill="x", padx=20, pady=(15, 10))

        # ============================================
        # TÍTULO
        # ============================================

        self.logs_title = ctk.CTkLabel(
            logs_header,
            text="📜 LOGS",
            font=("Segoe UI", 20, "bold"),
            text_color="#f4f4f5",
        )

        self.logs_title.pack(side="left")

        # ============================================
        # STATUS
        # ============================================

        self.status_label = ctk.CTkLabel(
            logs_header,
            text="Sistema pronto",
            font=("Segoe UI", 13),
            text_color="#22c55e",
        )

        self.status_label.pack(side="right")

        # ============================================
        # LOG BOX
        # ============================================

        self.log_box = ctk.CTkTextbox(
            logs_card,
            corner_radius=14,
            fg_color="#09090b",
            border_width=1,
            border_color="#18181b",
            font=("Consolas", 13),
            activate_scrollbars=True,
        )

        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ============================================
        # LOG INICIAL
        # ============================================

        self.log_box.insert("end", "AutoAdd iniciado com sucesso.\n")

        self.log_box.insert("end", "FFmpeg carregado.\n")

        self.log_box.insert("end", "Sistema pronto para uso.\n")

        self.carregar_config()
