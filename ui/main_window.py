import os
import customtkinter as ctk

from core.translations import translations
from tkinter import messagebox
from tkinter import filedialog
from core.config import salvar_config, carregar_config
from core.renderer import RenderManager
from ui.settings_window import SettingsWindow
from ui.controls_panel import ControlsPanel
from ui.logs_panel import LogsPanel
from ui.hooks_panel import HooksPanel
from ui.cta_panel import CTAPanel
from ui.corpos_panel import CorposPanel
from core.state import AppState
from ui.render_queue_panel import RenderQueuePanel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AutoAddApp(ctk.CTk):

    def salvar_configuracoes(self):

        config = {
            "encoder": self.encoder_var.get(),
            "language": self.language_var.get(),
            "auto_open": self.auto_open_var.get(),
        }

        salvar_config(config)

    # ============================================
    # LOG
    # ============================================

    def add_log(self, text):

        self.logs_panel.add_log(text)

        current = self.logs_panel.logs_box.get("1.0", "end")

        lines = current.splitlines()

        if len(lines) > 300:

            trimmed = "\n".join(lines[-300:])

            self.logs_panel.logs_box.delete("1.0", "end")

            self.logs_panel.logs_box.insert("end", trimmed)

    # ============================================
    # LIMPAR HOOKS
    # ============================================

    def limpar_hooks(self):

        self.app_state.hooks_path = ""

        self.hooks_panel.clear_preview()

        self.hooks_panel.loading_label.configure(text="Nenhum hook carregado")

        self.atualizar_total()

        self.add_log("Hooks removidos.")

    # ============================================
    # LIMPAR CTA
    # ============================================

    def limpar_cta(self):

        self.app_state.cta_path = ""

        self.cta_panel.clear()

        self.atualizar_total()

        self.add_log("CTAs removidos.")

    # ============================================
    # SELECIONAR HOOKS
    # ============================================

    def selecionar_hooks(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.app_state.hooks_path = pasta

        self.hooks_panel.set_path(pasta)

        self.add_log(f"Hooks carregados: {pasta}")

        self.atualizar_total()

    # ============================================
    # SELECIONAR CTA
    # ============================================

    def selecionar_cta(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.app_state.cta_path = pasta

        self.cta_panel.set_path(pasta)

        self.add_log(f"CTA carregado: {pasta}")

        self.atualizar_total()

    # ============================================
    # SELECIONAR OUTPUT
    # ============================================

    def selecionar_output(self):

        pasta = filedialog.askdirectory()

        if not pasta:
            return

        self.app_state.output_path = pasta

        self.output_label.configure(text=pasta)

        self.add_log(f"Saída definida: {pasta}")

        self.atualizar_total()

    # ============================================
    # TOTAL PREVISTO
    # ============================================

    def atualizar_total(self):

        self.total_var.set("Total previsto: 0 vídeos")

        try:

            if not self.app_state.hooks_path:
                return

            if not self.app_state.cta_path:
                return

            total = 1

            hooks = len(
                [
                    f
                    for f in os.listdir(self.app_state.hooks_path)
                    if f.lower().endswith(".mp4")
                ]
            )

            total *= hooks

            for card in self.corpos_panel.cards:

                pasta = card.path

                if not pasta:
                    return

                qtd = len([f for f in os.listdir(pasta) if f.lower().endswith(".mp4")])

                total *= qtd

            ctas = len(
                [
                    f
                    for f in os.listdir(self.app_state.cta_path)
                    if f.lower().endswith(".mp4")
                ]
            )

            total *= ctas

            self.total_var.set(f"Total previsto: {total} vídeos")

        except:

            pass

    # ============================================
    # INICIAR GERAÇÃO
    # ============================================

    def iniciar_geracao(self):

        self.controls_panel.status_label.configure(
            text="Gerando vídeos...", text_color="#f59e0b"
        )

        if self.app_state.renderizando:
            return

        self.app_state.renderizando = True

        self.controls_panel.progressbar.set(0)

        self.progress_text_var.set("0 / 0")

        total_text = self.total_var.get()

        try:

            total = int(total_text.split(":")[1].replace("vídeos", "").strip())

        except:

            total = 0

        if total > 100:

            continuar = messagebox.askyesno(
                "Confirmação", f"Serão gerados {total} vídeos.\n\nDeseja continuar?"
            )

            if not continuar:

                self.app_state.renderizando = False

                return

        corpos_paths = []

        for card in self.corpos_panel.cards:

            if not card.path:

                self.add_log("Selecione todas as pastas de corpos.")

                self.app_state.renderizando = False

                return

            corpos_paths.append(card.path)

        self.queue_panel.clear()

        if not self.queue_visible:

            self.toggle_queue()

        self.renderer.generate(
            self.app_state.hooks_path,
            corpos_paths,
            self.app_state.cta_path,
            self.app_state.output_path,
            self.encoder_var.get(),
            self.on_render_log,
            self.on_render_progress,
            self.on_job_update,
        )

    def on_job_update(self, job):

        def update():

            if job not in self.queue_panel.job_widgets:

                self.queue_panel.add_job(job)

            self.queue_panel.update_job(job)

        self.after(0, update)

    def on_render_log(self, text):

        self.after(0, lambda: self.add_log(text))

    def on_render_progress(self, progress, current, total):

        def update():

            self.controls_panel.progressbar.set(progress)

            self.progress_text_var.set(f"{current} / {total}")

        self.after(0, update)

    def on_render_finish(self, interrupted, jobs):

        def finish():

            if interrupted:

                self.controls_panel.status_label.configure(
                    text="Interrompido", text_color="#ef4444"
                )

                self.add_log("Render interrompido.")

            else:

                self.controls_panel.status_label.configure(
                    text="Finalizado", text_color="#22c55e"
                )

                self.add_log("Finalizado.")

            self.app_state.renderizando = False

            if self.auto_open_var.get():

                os.startfile(self.app_state.output_path)

            done = len([j for j in jobs if j.status == "done"])

            errors = len([j for j in jobs if j.status == "error"])

            self.add_log(f"Renderizados: {done}")

            if errors > 0:

                self.add_log(f"Falhas: {errors}")

        self.after(0, finish)

    # ============================================
    # STOP
    # ============================================

    def parar(self):

        self.renderer.stop()

        self.add_log("Parando renderização...")

    def abrir_configuracoes(self):

        SettingsWindow(
            self,
            self.encoder_var,
            self.language_var,
            self.salvar_configuracoes,
            self.aplicar_idioma,
        )

    def aplicar_idioma(self):

        lang = translations[self.language_var.get()]

        self.title(lang["title"])

        self.title_label.configure(text=lang["title"])

        self.hooks_panel.hooks_title.configure(text=lang["hooks"])

        self.corpos_panel.corpos_title.configure(text=lang["bodies"])

        self.cta_panel.cta_title.configure(text=lang["ctas"])

        self.output_title.configure(text=lang["output"])

        self.controls_panel.control_title.configure(text=lang["controls"])

        self.logs_panel.logs_title.configure(text=lang["logs"])

        self.controls_panel.btn_generate.configure(text=lang["generate"])

        self.controls_panel.btn_stop.configure(text=lang["stop"])

        self.controls_panel.progress_title.configure(text=lang["progress"])

        self.controls_panel.auto_open_checkbox.configure(text=lang["auto_open"])

        self.controls_panel.btn_open_output.configure(text=lang["open_output"])

        self.controls_panel.status_label.configure(text=lang["ready"])

        salvar_config(
            {
                "encoder": self.encoder_var.get(),
                "auto_open": self.auto_open_var.get(),
                "language": self.language_var.get(),
            }
        )

    def abrir_output(self):

        if not self.app_state.output_path:
            return

        os.startfile(self.app_state.output_path)

    def toggle_logs(self):

        self.logs_visible = not self.logs_visible

        if self.logs_visible:

            self.logs_panel.grid()

            self.toggle_logs_btn.configure(text="▼ Logs")

        else:

            self.logs_panel.grid_remove()

            self.toggle_logs_btn.configure(text="▶ Logs")

    def toggle_queue(self):

        self.queue_visible = not self.queue_visible

        if self.queue_visible:

            self.queue_panel.grid()

            self.toggle_queue_btn.configure(text="▼ Render Queue")

        else:

            self.queue_panel.grid_remove()

            self.toggle_queue_btn.configure(text="▶ Render Queue")

    def __init__(self):

        super().__init__()

        self.renderer = RenderManager()
        self.logs_visible = False
        self.queue_visible = False
        self.language_var = ctk.StringVar(value="Português")

        # ============================================
        # CONTAINER PRINCIPAL
        # ============================================

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")

        self.main_container.pack(fill="both", expand=True)

        self.encoder_var = ctk.StringVar(value="CPU (libx264)")

        self.auto_open_var = ctk.BooleanVar(value=False)

        self.app_state = AppState()

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

        self.hooks_panel = HooksPanel(self.main_container, self.selecionar_hooks)

        self.hooks_panel.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.corpos_panel = CorposPanel(
            self.main_container,
            lambda: filedialog.askdirectory(),
            self.atualizar_total,
            self.add_log,
        )

        self.corpos_panel.grid(
            row=1, column=1, padx=(10, 20), pady=(10, 10), sticky="nsew"
        )

        self.cta_panel = CTAPanel(self.main_container, self.selecionar_cta)

        self.cta_panel.grid(row=2, column=0, padx=(20, 10), pady=(0, 10), sticky="nsew")

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

        self.total_var = ctk.StringVar(value="Total previsto: 0 vídeos")

        self.progress_text_var = ctk.StringVar(value="0 / 0")

        self.controls_panel = ControlsPanel(
            self.main_container,
            self.total_var,
            None,
            self.progress_text_var,
            self.auto_open_var,
            self.iniciar_geracao,
            self.parar,
            self.abrir_output,
            self.salvar_configuracoes,
        )

        self.controls_panel.grid(
            row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew"
        )

        self.logs_panel = LogsPanel(self.main_container)

        self.toggle_logs_btn = ctk.CTkButton(
            self.main_container, text="▶ Logs", height=36, command=self.toggle_logs
        )

        self.toggle_logs_btn.grid(
            row=4,
            column=0,
            padx=(20, 10),
            pady=(0, 10),
            sticky="w"
        )

        self.logs_panel.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=20,
            pady=(0, 10),
            sticky="nsew"
        )

        self.logs_panel.grid_remove()

        self.queue_panel = RenderQueuePanel(self.main_container)

        self.toggle_queue_btn = ctk.CTkButton(
            self.main_container,
            text="▶ Render Queue",
            height=36,
            command=self.toggle_queue,
        )

        self.toggle_queue_btn.grid(
            row=4,
            column=1,
            padx=(10, 20),
            pady=(0, 10),
            sticky="e"
        )

        self.queue_panel.grid(
            row=6,
            column=0,
            columnspan=2,
            padx=20,
            pady=(0, 20),
            sticky="nsew"
        )

        self.queue_panel.grid_remove()

        self.main_container.grid_rowconfigure(5, weight=1)
        self.main_container.grid_rowconfigure(6, weight=1)

        config = carregar_config()

        self.app_state.encoder = config.get("encoder", "CPU (libx264)")

        self.app_state.auto_open = config.get("auto_open", False)

        self.app_state.language = config.get("language", "Português")

        self.encoder_var.set(self.app_state.encoder)

        self.auto_open_var.set(self.app_state.auto_open)

        self.language_var.set(self.app_state.language)

        self.aplicar_idioma()
