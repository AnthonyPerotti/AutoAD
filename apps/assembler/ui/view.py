import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
from core.config import salvar_config, carregar_config
from apps.assembler.renderer import RenderManager
from apps.assembler.ui.popups.settings_popup import SettingsWindow
from apps.assembler.ui.sections.process_section import ControlsPanel
from apps.assembler.ui.sections.logs_section import LogsPanel
from apps.assembler.ui.sections.hook_section import HooksPanel
from apps.assembler.ui.sections.cta_section import CTAPanel
from apps.assembler.ui.sections.body_section import CorposPanel
from apps.assembler.ui.sections.output_section import OutputPanel
from apps.assembler.state import AppState
from apps.assembler.ui.popups.queue_popup import RenderQueuePanel
from core.theme import COLORS, FONTS, SIZES


class AssemblerView(ctk.CTkFrame):
    """Content Assembler module view — extracted from main_window.py"""

    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.renderer = RenderManager()
        self.app_state = AppState()

        self.encoder_var = hub.encoder_var
        self.auto_open_var = hub.auto_open_var
        self.language_var = hub.language_var

        self.total_var = ctk.StringVar(value="0")
        self.progress_text_var = ctk.StringVar(value="")

        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)

        # PANELS
        self.hooks_panel = HooksPanel(self.scroll_frame, self.selecionar_hooks, self.limpar_hooks)
        self.hooks_panel.pack(fill="x", padx=20, pady=(15, 10))

        from core.utils import select_directory
        self.corpos_panel = CorposPanel(
            self.scroll_frame,
            select_directory,
            self.atualizar_total,
            self.add_log,
        )
        self.corpos_panel.pack(fill="x", padx=20, pady=10)

        self.cta_panel = CTAPanel(self.scroll_frame, self.selecionar_cta, self.limpar_cta)
        self.cta_panel.pack(fill="x", padx=20, pady=10)

        # OUTPUT PANEL
        self.output_panel = OutputPanel(
            self.scroll_frame,
            self.auto_open_var,
            self.hub.overwrite_var,
            self.selecionar_output,
            self.clear_output,
            lambda *_: self.hub.salvar_configuracoes(),
            lambda *_: self.hub.salvar_configuracoes()
        )
        self.output_panel.pack(fill="x", padx=20, pady=10)

        # CONTROLS
        self.controls_panel = ControlsPanel(
            self.scroll_frame,
            self.total_var,
            None,
            self.progress_text_var,
            self.auto_open_var,
            self.iniciar_geracao,
            self.parar,
            self.abrir_output,
            self.hub.salvar_configuracoes,
        )
        self.controls_panel.pack(fill="x", padx=20, pady=10)

        # LOGS
        self.logs_panel = LogsPanel(self.scroll_frame)
        self.logs_panel.pack(fill="x", padx=20, pady=(10, 20))

    # ==========================================
    # FOLDER SELECTION
    # ==========================================

    def add_log(self, text):
        self.logs_panel.add_log(text)

    def limpar_hooks(self):
        self.app_state.hooks_path = ""
        self.hooks_panel.hooks_path = ""
        self.hooks_panel.set_path("")
        self.atualizar_total()
        self.add_log("Hooks cleared.")

    def limpar_cta(self):
        self.app_state.cta_path = ""
        self.cta_panel.cta_path = ""
        self.cta_panel.set_path("")
        self.atualizar_total()
        self.add_log("CTAs cleared.")

    def selecionar_hooks(self):
        from core.utils import select_directory
        pasta = select_directory()
        if not pasta: return
        self.app_state.hooks_path = pasta
        self.hooks_panel.set_path(pasta)
        self.add_log(f"Hooks carregados: {pasta}")
        self.atualizar_total()

    def selecionar_cta(self):
        from core.utils import select_directory
        pasta = select_directory()
        if not pasta: return
        self.app_state.cta_path = pasta
        self.cta_panel.set_path(pasta)
        self.add_log(f"CTA carregado: {pasta}")
        self.atualizar_total()

    def selecionar_output(self):
        from core.utils import select_directory
        pasta = select_directory()
        if not pasta: return
        self.app_state.output_path = pasta
        self.output_panel.set_path(pasta)
        self.add_log(f"Saída definida: {pasta}")
        self.atualizar_total()

    def clear_output(self):
        self.app_state.output_path = ""
        self.output_panel.set_path("")
        self.add_log("Output cleared.")
        self.atualizar_total()

    def atualizar_total(self):
        self.total_var.set("0")
        try:
            if not self.app_state.hooks_path: return
            if not self.app_state.cta_path: return

            total = 1
            hooks = len([f for f in os.listdir(self.app_state.hooks_path) if f.lower().endswith(".mp4")])
            total *= hooks

            corpos_validos = False
            for card in self.corpos_panel.cards:
                pasta = card.path
                if not pasta: continue
                qtd = len([f for f in os.listdir(pasta) if f.lower().endswith(".mp4")])
                if qtd > 0:
                    total *= qtd
                    corpos_validos = True
            
            if not corpos_validos:
                return

            ctas = len([f for f in os.listdir(self.app_state.cta_path) if f.lower().endswith(".mp4")])
            total *= ctas
            
            self.total_var.set(f"{total}")
        except:
            pass

    # ==========================================
    # RENDER
    # ==========================================

    def iniciar_geracao(self):
        if self.app_state.renderizando: return
        self.app_state.renderizando = True
        self.controls_panel.progressbar.set(0)
        self.progress_text_var.set("0 / 0")
        self.controls_panel.set_generating_state(True)

        total_text = self.total_var.get()
        try: total = int(total_text)
        except: total = 0

        if total > 100:
            continuar = messagebox.askyesno("Confirmação", f"Serão gerados {total} vídeos.\n\nDeseja continuar?")
            if not continuar:
                self.app_state.renderizando = False
                return

        corpos_paths = []
        if not self.app_state.hooks_path or not self.app_state.cta_path or not self.app_state.output_path:
            messagebox.showwarning("Aviso", "Selecione todas as pastas (Hook, CTA e Output).")
            return

        for card in self.corpos_panel.cards:
            if card.path:
                corpos_paths.append(card.path)
        if not corpos_paths:
            messagebox.showwarning("Aviso", self.lang["select_body_alert"] if hasattr(self, 'lang') else "Selecione pelo menos uma pasta de corpo.")
            return

        self.renderer.generate(
            self.app_state.hooks_path,
            corpos_paths,
            self.app_state.cta_path,
            self.app_state.output_path,
            self.encoder_var.get(),
            self.hub.overwrite_var.get(),
            self.on_render_log,
            self.on_render_progress,
            self.on_job_update,
            self.on_render_finish,
            self.on_ask_overwrite
        )

    def on_ask_overwrite(self, count, callback):
        def ask():
            lang = self.hub.lang if hasattr(self.hub, 'lang') else {}
            title = lang.get("overwrite_title", "Arquivos Existentes")
            msg = lang.get("overwrite_msg", f"Existem {count} arquivo(s) com o mesmo nome na pasta de destino.\n\nDeseja sobrescrevê-los?")
            resp = messagebox.askyesno(title, msg)
            callback(resp)
        self.after(0, ask)

    def on_job_update(self, job):
        pass

    def on_render_log(self, text):
        self.after(0, lambda: self.add_log(text))

    def on_render_progress(self, progress, current, total):
        def update():
            self.controls_panel.progressbar.set(progress)
            self.controls_panel.progress_percent.configure(text=f"{int(progress*100)}%")
            self.progress_text_var.set(f"Assembling Project: {int(progress*100)}% complete (Processing segment {current} of {total})")
        self.after(0, update)

    def on_render_finish(self, interrupted, jobs):
        def finish():
            if interrupted:
                self.add_log("Render interrompido.")
            else:
                self.add_log("Finalizado.")

            self.app_state.renderizando = False
            self.controls_panel.set_generating_state(False)
            
            if self.auto_open_var.get() and self.app_state.output_path:
                try: os.startfile(self.app_state.output_path)
                except: pass

            done = len([j for j in jobs if j.status == "done"])
            errors = len([j for j in jobs if j.status == "error"])
            
            self.add_log(f"Renderizados: {done}")
            if errors > 0: self.add_log(f"Falhas: {errors}")
        self.after(0, finish)

    def parar(self):
        self.renderer.stop()
        self.add_log("Parando renderização...")

    def abrir_output(self):
        if not self.app_state.output_path: return
        os.startfile(self.app_state.output_path)

    # ==========================================
    # LANGUAGE
    # ==========================================

    def update_language(self, lang):
        self.hooks_panel.update_language(lang)
        self.corpos_panel.update_language(lang)
        self.cta_panel.update_language(lang)
        self.output_panel.update_language(lang)
        
        if not self.app_state.output_path:
            self.output_panel.set_path("")
        
        self.controls_panel.update_language(lang)
        if hasattr(self.logs_panel, "update_language"):
            self.logs_panel.update_language(lang)
