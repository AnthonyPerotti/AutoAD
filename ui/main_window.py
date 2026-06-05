import os
# pyrefly: ignore [missing-import]
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
        pasta = filedialog.askdirectory()
        if not pasta: return
        self.app_state.hooks_path = pasta
        self.hooks_panel.set_path(pasta)
        self.add_log(f"Hooks carregados: {pasta}")
        self.atualizar_total()

    def selecionar_cta(self):
        pasta = filedialog.askdirectory()
        if not pasta: return
        self.app_state.cta_path = pasta
        self.cta_panel.set_path(pasta)
        self.add_log(f"CTA carregado: {pasta}")
        self.atualizar_total()

    def selecionar_output(self):
        pasta = filedialog.askdirectory()
        if not pasta: return
        self.app_state.output_path = pasta
        
        self.output_path_entry.configure(state="normal")
        self.output_path_entry.delete(0, "end")
        self.output_path_entry.insert(0, pasta)
        self.output_path_entry.configure(state="readonly")
        
        self.add_log(f"Saída definida: {pasta}")
        self.atualizar_total()

    def clear_output(self):
        self.app_state.output_path = ""
        self.output_path_entry.configure(state="normal")
        self.output_path_entry.delete(0, "end")
        self.output_path_entry.insert(0, "No folder selected")
        self.output_path_entry.configure(state="readonly")
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

    def iniciar_geracao(self):
        # self.controls_panel.status_label.configure(text="Gerando vídeos...", text_color="#f59e0b")
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
        for card in self.corpos_panel.cards:
            if card.path:
                corpos_paths.append(card.path)
                
        if not corpos_paths:
            self.add_log(self.lang["select_body_alert"] if hasattr(self, 'lang') else "Select at least one body folder.")
            self.app_state.renderizando = False
            return

        # self.queue_panel.clear()
        # if not self.queue_visible: self.toggle_queue()

        self.renderer.generate(
            self.app_state.hooks_path,
            corpos_paths,
            self.app_state.cta_path,
            self.app_state.output_path,
            self.encoder_var.get(),
            self.on_render_log,
            self.on_render_progress,
            self.on_job_update,
            self.on_render_finish,
        )

    def on_job_update(self, job):
        pass # Optional: restore render queue if needed

    def on_render_log(self, text):
        self.after(0, lambda: self.add_log(text))

    def on_render_progress(self, progress, current, total):
        def update():
            self.controls_panel.progressbar.set(progress)
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

    def abrir_configuracoes(self):
        SettingsWindow(
            self,
            self.encoder_var,
            self.language_var,
            self.salvar_configuracoes,
            self.aplicar_idioma,
        )

    def aplicar_idioma(self):
        lang = translations.get(self.language_var.get(), translations["English"]) if self.language_var.get() in translations else None
        if not lang:
            lang = translations["English"]
            
        self.lang = lang
        self.title(lang["title"])
        self.title_label.configure(text=lang["title"])
        
        self.output_title.configure(text=lang["output"])
        self.btn_output.configure(text=lang["select_folder"])
        if not self.app_state.output_path:
            self.output_path_entry.configure(state="normal")
            self.output_path_entry.delete(0, "end")
            self.output_path_entry.insert(0, lang["no_folder"])
            self.output_path_entry.configure(state="readonly")
        self.cloud_cb.configure(text=lang["auto_open"])
        
        self.hooks_panel.update_language(lang)
        self.corpos_panel.update_language(lang)
        self.cta_panel.update_language(lang)
        self.controls_panel.update_language(lang)
        if hasattr(self.logs_panel, "update_language"):
            self.logs_panel.update_language(lang)
            
        salvar_config(
            {
                "encoder": self.encoder_var.get(),
                "auto_open": self.auto_open_var.get(),
                "language": self.language_var.get(),
            }
        )

    def abrir_output(self):
        if not self.app_state.output_path: return
        os.startfile(self.app_state.output_path)

    def __init__(self):
        super().__init__()
        self.renderer = RenderManager()
        self.language_var = ctk.StringVar(value="English")
        
        self.title("AutoAD Content Assembler v1.5")
        self.geometry("600x950") # Make it vertical
        self.minsize(550, 800)
        self.configure(fg_color="#18181b")

        self.encoder_var = ctk.StringVar(value="CPU (libx264)")
        self.auto_open_var = ctk.BooleanVar(value=False)
        self.app_state = AppState()
        
        self.total_var = ctk.StringVar(value="0")
        self.progress_text_var = ctk.StringVar(value="")

        # TOP BAR
        self.topbar = ctk.CTkFrame(self, fg_color="#27272a", height=40, corner_radius=0)
        self.topbar.pack(fill="x", side="top")
        
        self.title_label = ctk.CTkLabel(
            self.topbar, text="AutoAD Content Assembler v1.5", font=("Segoe UI", 14, "bold"), text_color="#d1d5db"
        )
        self.title_label.pack(side="left", padx=20, pady=5)
        
        self.btn_settings = ctk.CTkButton(
            self.topbar, text="⚙", width=30, height=30, fg_color="transparent", hover_color="#3f3f46", 
            font=("Segoe UI", 16), command=self.abrir_configuracoes
        )
        self.btn_settings.pack(side="right", padx=10)

        # MAIN CONTAINER SCROLLABLE
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # PANELS
        self.hooks_panel = HooksPanel(self.main_container, self.selecionar_hooks, self.limpar_hooks)
        self.hooks_panel.pack(fill="x", padx=20, pady=(15, 10))

        self.corpos_panel = CorposPanel(
            self.main_container,
            lambda: filedialog.askdirectory(),
            self.atualizar_total,
            self.add_log,
        )
        self.corpos_panel.pack(fill="x", padx=20, pady=10)

        self.cta_panel = CTAPanel(self.main_container, self.selecionar_cta, self.limpar_cta)
        self.cta_panel.pack(fill="x", padx=20, pady=10)

        # OUTPUT PANEL (Custom built here to match mockup)
        self.output_frame = ctk.CTkFrame(
            self.main_container, corner_radius=10, fg_color="#1e1e24", border_width=2, border_color="#c2410c"
        )
        self.output_frame.pack(fill="x", padx=20, pady=10)
        
        # Header
        self.output_header = ctk.CTkFrame(self.output_frame, fg_color="#c2410c", corner_radius=6, height=30)
        self.output_header.pack(fill="x", padx=10, pady=(10, 5))
        self.output_header.pack_propagate(False)

        self.output_title = ctk.CTkLabel(self.output_header, text="OUTPUT", font=("Segoe UI", 14, "bold"), text_color="#ffffff")
        self.output_title.place(relx=0.5, rely=0.5, anchor="center")

        # Content
        self.output_content = ctk.CTkFrame(self.output_frame, fg_color="transparent")
        self.output_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        self.out_row1 = ctk.CTkFrame(self.output_content, fg_color="transparent")
        self.out_row1.pack(fill="x")

        self.btn_output = ctk.CTkButton(
            self.out_row1, text="📁 SELECT FOLDER", width=160, height=36, corner_radius=6,
            fg_color="#c2410c", hover_color="#ea580c", font=("Segoe UI", 13, "bold"), command=self.selecionar_output
        )
        self.btn_output.pack(side="left", padx=(0, 10))

        self.output_path_entry = ctk.CTkEntry(
            self.out_row1, height=36, fg_color="#27272a", border_width=1, border_color="#3f3f46", text_color="#d1d5db"
        )
        self.output_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.output_path_entry.insert(0, "No folder selected")
        self.output_path_entry.configure(state="readonly")

        self.btn_clear_output = ctk.CTkButton(
            self.out_row1, text="🗑", width=36, height=36, corner_radius=6, fg_color="#3f3f46",
            hover_color="#52525b", font=("Segoe UI", 16), command=self.clear_output
        )
        self.btn_clear_output.pack(side="left")
        
        # Checkbox
        self.cloud_cb = ctk.CTkCheckBox(
            self.output_content, text="Upload to cloud after export", variable=self.auto_open_var, 
            font=("Segoe UI", 12), text_color="#9ca3af", command=self.salvar_configuracoes
        )
        self.cloud_cb.pack(anchor="e", pady=(10, 0))

        # CONTROLS
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
        self.controls_panel.pack(fill="x", padx=20, pady=10)

        # LOGS
        self.logs_panel = LogsPanel(self.main_container)
        self.logs_panel.pack(fill="x", padx=20, pady=(10, 20))

        # Config Load
        config = carregar_config()
        self.app_state.encoder = config.get("encoder", "CPU (libx264)")
        self.app_state.auto_open = config.get("auto_open", False)
        self.app_state.language = config.get("language", "English")
        self.encoder_var.set(self.app_state.encoder)
        self.auto_open_var.set(self.app_state.auto_open)
        self.language_var.set(self.app_state.language)
        self.aplicar_idioma()
