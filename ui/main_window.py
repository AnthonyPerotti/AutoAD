import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from core.translations import translations
from tkinter import messagebox
from tkinter import filedialog
from core.config import salvar_config, carregar_config
from core.renderer import RenderManager
from ui.popups.settings_popup import SettingsWindow
from ui.sections.process_section import ControlsPanel
from ui.sections.logs_section import LogsPanel
from ui.sections.hook_section import HooksPanel
from ui.sections.cta_section import CTAPanel
from ui.sections.body_section import CorposPanel
from ui.sections.output_section import OutputPanel
from core.state import AppState
from ui.popups.queue_popup import RenderQueuePanel
from core.theme import COLORS, FONTS, SIZES

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

    def iniciar_geracao(self):
        # self.controls_panel.status_label.configure(text="Gerando vídeos...", text_color=COLORS["warning"])
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
        
        # Sync sidebar language menu
        sidebar_lang_val = "🌐 Português (BR)" if self.language_var.get() == "Português" else "🌐 English"
        if self.language_sidebar_var.get() != sidebar_lang_val:
            self.language_sidebar_var.set(sidebar_lang_val)
        
        # Update dynamic labels
        if self.current_view == "assembler":
            self.title_label.configure(text=lang["content_assembler"])
            self.subtitle_label.configure(text=lang["subtitle"])
        elif self.current_view == "dashboard":
            self.title_label.configure(text=lang["dashboard"])
            self.subtitle_label.configure(text="Visualize as estatísticas e informações do sistema.")
        elif self.current_view == "tools":
            self.title_label.configure(text=lang["outras_ferramentas"])
            self.subtitle_label.configure(text="Explore outras funções compiladas no AutoAD Suite.")

        self.status_pill_label.configure(text=lang["sistema_online"])
        self.footer_status_label.configure(text="● " + lang["sistema_normal"])
        
        # Translate sidebar headers
        self.sidebar_header_app.configure(text=lang["aplicacoes"])
        self.sidebar_header_support.configure(text=lang["suporte_header"])
        self.sidebar_header_config.configure(text=lang["configuracoes_header"])
        
        # Translate sidebar items
        self.nav_buttons["dashboard"].configure(text=f"  🏠  {lang['dashboard']}")
        self.nav_buttons["assembler"].configure(text=f"  📦  {lang['content_assembler']}")
        self.nav_buttons["tools"].configure(text=f"  🎛️  {lang['outras_ferramentas']}")
        self.support_buttons["suporte"].configure(text=f"  🎧  {lang['suporte']}")
        self.support_buttons["documentacao"].configure(text=f"  📖  {lang['documentacao']}")
        self.support_buttons["sobre"].configure(text=f"  ℹ️  {lang['sobre']}")
        self.config_buttons["configuracoes"].configure(text=f"  ⚙️  {lang['configuracoes']}")
        
        self.hooks_panel.update_language(lang)
        self.corpos_panel.update_language(lang)
        self.cta_panel.update_language(lang)
        self.output_panel.update_language(lang)
        
        # update paths to reflect no_folder text changes
        if not self.app_state.output_path: self.output_panel.set_path("")
        
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

    def on_sidebar_click(self, target):
        self.current_view = target
        
        # Reset navigation buttons styling
        for key, btn in self.nav_buttons.items():
            if key == target:
                btn.configure(fg_color=COLORS["hook"], text_color=COLORS["text_main"], font=("Segoe UI", 12, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_light"], font=("Segoe UI", 12, "normal"))
                
        # Switch views
        self.main_container.pack_forget()
        self.dashboard_view.pack_forget()
        self.tools_view.pack_forget()
        
        if target == "assembler":
            self.main_container.pack(fill="both", expand=True)
        elif target == "dashboard":
            self.dashboard_view.pack(fill="both", expand=True, padx=20, pady=10)
        elif target == "tools":
            self.tools_view.pack(fill="both", expand=True, padx=20, pady=10)
            
        self.aplicar_idioma()

    def on_sidebar_language_change(self, val):
        if "Português" in val:
            self.language_var.set("Português")
        else:
            self.language_var.set("English")
        self.aplicar_idioma()

    def toggle_theme_mode(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.add_log("Aparência: Modo Escuro ativado.")
        else:
            ctk.set_appearance_mode("light")
            self.add_log("Aparência: Modo Claro ativado.")

    def __init__(self):
        super().__init__()
        self.renderer = RenderManager()
        self.language_var = ctk.StringVar(value="English")
        

        self.title("AutoAD Suite v1.6")
        self.geometry("980x950") 
        self.minsize(900, 800)
        
        try:
            from core.utils import get_resource_path
            icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
            self.iconbitmap(icon_path)
        except Exception:
            pass

        
        self.configure(fg_color=COLORS["bg_main"])

        self.encoder_var = ctk.StringVar(value="CPU (libx264)")
        self.auto_open_var = ctk.BooleanVar(value=False)
        self.app_state = AppState()
        
        self.total_var = ctk.StringVar(value="0")
        self.progress_text_var = ctk.StringVar(value="")
        self.language_sidebar_var = ctk.StringVar(value="🌐 English")
        self.current_view = "assembler"

        # ==========================================
        # LEFT SIDEBAR PANEL
        # ==========================================
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COLORS["bg_sidebar"], border_width=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Logo Header
        self.sidebar_logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_logo_frame.pack(fill="x", padx=20, pady=(25, 20))
        
        try:
            from PIL import Image
            from core.utils import get_resource_path
            icon_path = get_resource_path(os.path.join("assets", "icon.ico"))
            logo_img = ctk.CTkImage(light_image=Image.open(icon_path), dark_image=Image.open(icon_path), size=(38, 38))
            self.logo_icon_label = ctk.CTkLabel(
                self.sidebar_logo_frame, 
                text="", 
                image=logo_img,
                width=38,
                height=38
            )
        except Exception:
            self.logo_icon_label = ctk.CTkLabel(
                self.sidebar_logo_frame, 
                text="A", 
                font=("Segoe UI", 22, "bold"), 
                text_color=COLORS["text_main"],
                fg_color=COLORS["hook"],
                width=38,
                height=38,
                corner_radius=8
            )
        self.logo_icon_label.pack(side="left", padx=(0, 12))
        
        self.logo_text_container = ctk.CTkFrame(self.sidebar_logo_frame, fg_color="transparent")
        self.logo_text_container.pack(side="left")
        
        self.logo_title = ctk.CTkLabel(self.logo_text_container, text="AutoAD Suite", font=("Segoe UI", 14, "bold"), text_color=COLORS["text_main"], anchor="w")
        self.logo_title.pack(anchor="w")
        
        self.logo_version = ctk.CTkLabel(self.logo_text_container, text="v1.6", font=("Segoe UI", 11), text_color=COLORS["text_muted"], anchor="w")
        self.logo_version.pack(anchor="w")

        # Category: Dashboard Link
        self.nav_buttons = {}
        
        self.btn_db = ctk.CTkButton(
            self.sidebar_frame,
            text="  🏠  Dashboard",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 12),
            command=lambda: self.on_sidebar_click("dashboard")
        )
        self.btn_db.pack(fill="x", padx=15, pady=(5, 10))
        self.nav_buttons["dashboard"] = self.btn_db

        # Category: APPLICATIONS
        self.sidebar_header_app = ctk.CTkLabel(self.sidebar_frame, text="APLICAÇÕES", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_muted"], anchor="w")
        self.sidebar_header_app.pack(fill="x", padx=20, pady=(10, 5))

        self.btn_assembler = ctk.CTkButton(
            self.sidebar_frame,
            text="  📦  AutoAD Content Assembler",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color=COLORS["hook"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_main"],
            font=("Segoe UI", 12, "bold"),
            command=lambda: self.on_sidebar_click("assembler")
        )
        self.btn_assembler.pack(fill="x", padx=15, pady=3)
        self.nav_buttons["assembler"] = self.btn_assembler

        self.btn_tools = ctk.CTkButton(
            self.sidebar_frame,
            text="  🎛️  Outras Ferramentas",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 12),
            command=lambda: self.on_sidebar_click("tools")
        )
        self.btn_tools.pack(fill="x", padx=15, pady=3)
        self.nav_buttons["tools"] = self.btn_tools

        # Category: SUPPORT
        self.sidebar_header_support = ctk.CTkLabel(self.sidebar_frame, text="SUPORTE", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_muted"], anchor="w")
        self.sidebar_header_support.pack(fill="x", padx=20, pady=(18, 5))

        self.support_buttons = {}
        for key, text, icon, cmd in [
            ("suporte", "Suporte", "🎧", lambda: messagebox.showinfo("Suporte", "Para suporte e assistência, envie e-mail para: contato@autoad.suite")),
            ("documentacao", "Documentação", "📖", lambda: messagebox.showinfo("Documentação", "Documentação detalhada e guias no repositório oficial do AutoAD Suite.")),
            ("sobre", "Sobre", "ℹ️", lambda: messagebox.showinfo("Sobre AutoAD", "AutoAD Suite v1.6.0\nSolução modular para automação de vídeo.\n\nDesenvolvido com carinho.")),
        ]:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {icon}  {text}",
                anchor="w",
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS["bg_hover"],
                text_color=COLORS["text_light"],
                font=("Segoe UI", 12),
                command=cmd
            )
            btn.pack(fill="x", padx=15, pady=3)
            self.support_buttons[key] = btn

        # Category: SETTINGS
        self.sidebar_header_config = ctk.CTkLabel(self.sidebar_frame, text="CONFIGURAÇÕES", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_muted"], anchor="w")
        self.sidebar_header_config.pack(fill="x", padx=20, pady=(18, 5))

        self.config_buttons = {}
        btn_config = ctk.CTkButton(
            self.sidebar_frame,
            text="  ⚙️  Configurações",
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_light"],
            font=("Segoe UI", 12),
            command=self.abrir_configuracoes
        )
        btn_config.pack(fill="x", padx=15, pady=3)
        self.config_buttons["configuracoes"] = btn_config

        # Bottom Frame inside Sidebar
        self.sidebar_bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_bottom_frame.pack(side="bottom", fill="x", padx=15, pady=25)

        # Language dropdown
        self.language_menu = ctk.CTkOptionMenu(
            self.sidebar_bottom_frame,
            values=["🌐 Português (BR)", "🌐 English"],
            variable=self.language_sidebar_var,
            fg_color=COLORS["bg_panel"],
            button_color=COLORS["bg_panel"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_panel"],
            dropdown_hover_color=COLORS["border"],
            dropdown_text_color=COLORS["text_main"],
            text_color=COLORS["text_main"],
            font=("Segoe UI", 12),
            command=self.on_sidebar_language_change
        )
        self.language_menu.pack(fill="x", pady=(0, 15))

        # Theme toggle slider sun/moon
        self.theme_frame = ctk.CTkFrame(self.sidebar_bottom_frame, fg_color=COLORS["bg_panel"], height=32, corner_radius=16)
        self.theme_frame.pack(fill="x")
        
        self.theme_lbl_sun = ctk.CTkLabel(self.theme_frame, text="☀️", font=("Segoe UI", 11))
        self.theme_lbl_sun.pack(side="left", padx=(15, 5), pady=3)
        
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame, 
            text="", 
            width=40,
            progress_color=COLORS["hook"],
            command=self.toggle_theme_mode
        )
        self.theme_switch.pack(side="left", padx=5)
        self.theme_switch.select() # default to dark
        
        self.theme_lbl_moon = ctk.CTkLabel(self.theme_frame, text="🌙", font=("Segoe UI", 11))
        self.theme_lbl_moon.pack(side="left", padx=(5, 15), pady=3)


        # ==========================================
        # RIGHT CONTENT AREA
        # ==========================================
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.main_content_frame.pack(side="right", fill="both", expand=True)

        # Header Row
        self.header_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent", height=70)
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        self.header_title_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_title_container.pack(side="left")

        self.title_row = ctk.CTkFrame(self.header_title_container, fg_color="transparent")
        self.title_row.pack(anchor="w")

        self.title_label = ctk.CTkLabel(
            self.title_row, text="AutoAD Content Assembler", font=("Segoe UI", 20, "bold"), text_color=COLORS["text_main"]
        )
        self.title_label.pack(side="left")

        # v1.6 badge
        self.badge_frame = ctk.CTkFrame(self.title_row, fg_color=COLORS["hook"], corner_radius=6, height=20, width=40)
        self.badge_frame.pack(side="left", padx=(8, 0))
        self.badge_frame.pack_propagate(False)
        self.badge_lbl = ctk.CTkLabel(self.badge_frame, text="v1.6", font=("Segoe UI", 10, "bold"), text_color=COLORS["text_main"])
        self.badge_lbl.place(relx=0.5, rely=0.5, anchor="center")

        self.subtitle_label = ctk.CTkLabel(
            self.header_title_container,
            text="Monte, organize e exporte seus conteúdos de forma rápida e eficiente.",
            font=FONTS["text_normal"],
            text_color=COLORS["text_muted"]
        )
        self.subtitle_label.pack(anchor="w", pady=(3, 0))

        # Status badge on right side of header
        self.status_pill_frame = ctk.CTkFrame(
            self.header_frame, 
            fg_color=COLORS["bg_panel"], 
            border_width=SIZES["border_thin"], 
            border_color=COLORS["border"], 
            height=30,
            corner_radius=15
        )
        self.status_pill_frame.pack(side="right", padx=(10, 5))
        self.status_pill_frame.pack_propagate(False)

        # Dot
        self.status_dot_lbl = ctk.CTkLabel(self.status_pill_frame, text="●", text_color=COLORS["success"], font=("Segoe UI", 12))
        self.status_dot_lbl.pack(side="left", padx=(12, 5))

        self.status_pill_label = ctk.CTkLabel(
            self.status_pill_frame, 
            text="Sistema Online", 
            font=("Segoe UI", 11, "bold"), 
            text_color=COLORS["text_light"]
        )
        self.status_pill_label.pack(side="left", padx=(0, 12))

        # Middle view container
        self.view_container = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        # View 1: Main Container Scrollable (Assembler)
        self.main_container = ctk.CTkScrollableFrame(self.view_container, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # View 2: Dashboard Mock
        self.dashboard_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        
        self.db_title = ctk.CTkLabel(self.dashboard_view, text="Visão Geral do AutoAD Suite", font=("Segoe UI", 16, "bold"), text_color=COLORS["text_main"])
        self.db_title.pack(anchor="w", pady=(10, 20))
        
        self.db_grid = ctk.CTkFrame(self.dashboard_view, fg_color="transparent")
        self.db_grid.pack(fill="x", pady=10)
        self.db_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.card1 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card1.grid(row=0, column=0, padx=10, sticky="ew")
        self.card1.pack_propagate(False)
        lbl1 = ctk.CTkLabel(self.card1, text="Total de Projetos", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl1.pack(pady=(15, 5))
        self.db_stat_projects = ctk.CTkLabel(self.card1, text="0", font=("Segoe UI", 24, "bold"), text_color=COLORS["hook"])
        self.db_stat_projects.pack()
        
        self.card2 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card2.grid(row=0, column=1, padx=10, sticky="ew")
        self.card2.pack_propagate(False)
        lbl2 = ctk.CTkLabel(self.card2, text="Renderizador", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl2.pack(pady=(15, 5))
        self.db_stat_renderer = ctk.CTkLabel(self.card2, text="FFmpeg", font=("Segoe UI", 16, "bold"), text_color=COLORS["cta"])
        self.db_stat_renderer.pack()
        
        self.card3 = ctk.CTkFrame(self.db_grid, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], height=100, corner_radius=12)
        self.card3.grid(row=0, column=2, padx=10, sticky="ew")
        self.card3.pack_propagate(False)
        lbl3 = ctk.CTkLabel(self.card3, text="Status do Sistema", font=("Segoe UI", 11), text_color=COLORS["text_muted"])
        lbl3.pack(pady=(15, 5))
        self.db_stat_status = ctk.CTkLabel(self.card3, text="Online", font=("Segoe UI", 16, "bold"), text_color=COLORS["success"])
        self.db_stat_status.pack()

        # View 3: Tools Placeholder
        self.tools_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.tools_title = ctk.CTkLabel(self.tools_view, text="Outras Ferramentas Compiladas", font=("Segoe UI", 16, "bold"), text_color=COLORS["text_main"])
        self.tools_title.pack(anchor="w", pady=(10, 20))
        
        self.tools_list_frame = ctk.CTkFrame(self.tools_view, fg_color=COLORS["bg_panel"], border_width=1, border_color=COLORS["border"], corner_radius=12)
        self.tools_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tools_placeholder = ctk.CTkLabel(
            self.tools_list_frame, 
            text="🎛️ Novas ferramentas serão disponibilizadas em breve.\nEstamos trabalhando para compilar novas automações de vídeo aqui!", 
            font=("Segoe UI", 13), 
            text_color=COLORS["text_muted"],
            justify="center"
        )
        self.tools_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # Footer Frame
        self.footer_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent", height=30)
        self.footer_frame.pack(side="bottom", fill="x", padx=25, pady=5)
        
        self.footer_status_label = ctk.CTkLabel(
            self.footer_frame, 
            text="● Sistema operacional normal", 
            font=("Segoe UI", 10), 
            text_color=COLORS["success"]
        )
        self.footer_status_label.pack(side="left")

        self.footer_version_label = ctk.CTkLabel(
            self.footer_frame, 
            text="AutoAD Content Assembler v1.6.0", 
            font=("Segoe UI", 10), 
            text_color=COLORS["text_muted"]
        )
        self.footer_version_label.pack(side="right")

        # PANELS INSTANTIATION
        self.hooks_panel = HooksPanel(self.main_container, self.selecionar_hooks, self.limpar_hooks)
        self.hooks_panel.pack(fill="x", padx=20, pady=(15, 10))

        from core.utils import select_directory
        self.corpos_panel = CorposPanel(
            self.main_container,
            select_directory,
            self.atualizar_total,
            self.add_log,
        )
        self.corpos_panel.pack(fill="x", padx=20, pady=10)

        self.cta_panel = CTAPanel(self.main_container, self.selecionar_cta, self.limpar_cta)
        self.cta_panel.pack(fill="x", padx=20, pady=10)

        # OUTPUT PANEL
        self.output_panel = OutputPanel(
            self.main_container,
            self.auto_open_var,
            self.selecionar_output,
            self.clear_output,
            self.salvar_configuracoes
        )
        self.output_panel.pack(fill="x", padx=20, pady=10)

        # CONTROLES
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

