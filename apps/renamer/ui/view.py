import os
# pyrefly: ignore [missing-import]
import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.theme import COLORS, FONTS, SIZES

class RenamerView(ctk.CTkFrame):
    def __init__(self, parent, hub):
        super().__init__(parent, fg_color="transparent")
        self.hub = hub
        self.target_dir = ""
        self.files = []
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- HEADER / FOLDER SELECT ---
        self.header_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        self.btn_select = ctk.CTkButton(
            self.header_frame, text="📂 Selecionar Pasta", font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["export_btn"], hover_color=COLORS["export_btn_hover"], text_color=COLORS["text_main"],
            command=self.select_directory
        )
        self.btn_select.pack(side="left", padx=15, pady=15)
        
        self.lbl_path = ctk.CTkLabel(self.header_frame, text="Nenhuma pasta selecionada", font=("Segoe UI", 12), text_color=COLORS["text_muted"])
        self.lbl_path.pack(side="left", padx=10, fill="x", expand=True)

        # --- RULES PANEL ---
        self.rules_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.rules_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Find / Replace
        row1 = ctk.CTkFrame(self.rules_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(row1, text="Procurar:", width=60, anchor="w").pack(side="left")
        self.entry_find = ctk.CTkEntry(row1, width=150)
        self.entry_find.pack(side="left", padx=(5, 15))
        self.entry_find.bind("<KeyRelease>", self.update_preview)
        
        ctk.CTkLabel(row1, text="Substituir:", width=60, anchor="w").pack(side="left")
        self.entry_replace = ctk.CTkEntry(row1, width=150)
        self.entry_replace.pack(side="left", padx=(5, 15))
        self.entry_replace.bind("<KeyRelease>", self.update_preview)
        
        # Prefix / Suffix
        row2 = ctk.CTkFrame(self.rules_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(row2, text="Prefixo:", width=60, anchor="w").pack(side="left")
        self.entry_prefix = ctk.CTkEntry(row2, width=150)
        self.entry_prefix.pack(side="left", padx=(5, 15))
        self.entry_prefix.bind("<KeyRelease>", self.update_preview)
        
        ctk.CTkLabel(row2, text="Sufixo:", width=60, anchor="w").pack(side="left")
        self.entry_suffix = ctk.CTkEntry(row2, width=150)
        self.entry_suffix.pack(side="left", padx=(5, 15))
        self.entry_suffix.bind("<KeyRelease>", self.update_preview)

        # Numbering & Execute
        row3 = ctk.CTkFrame(self.rules_frame, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=(5, 15))
        
        self.var_numbering = ctk.BooleanVar(value=False)
        self.chk_numbering = ctk.CTkCheckBox(row3, text="Adicionar numeração (_001)", variable=self.var_numbering, command=self.update_preview)
        self.chk_numbering.pack(side="left")
        
        self.btn_execute = ctk.CTkButton(
            row3, text="Renomear Arquivos", font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"], text_color=COLORS["text_main"],
            command=self.execute_rename
        )
        self.btn_execute.pack(side="right")

        # --- PREVIEW PANEL ---
        self.preview_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_panel"])
        self.preview_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Visualização aparecerá aqui...", font=("Consolas", 12), text_color=COLORS["text_muted"], justify="left", anchor="nw")
        self.preview_label.pack(fill="both", expand=True, padx=10, pady=10)

    def select_directory(self):
        folder = filedialog.askdirectory(title="Selecione a pasta com os arquivos para renomear")
        if folder:
            self.target_dir = folder
            self.lbl_path.configure(text=folder)
            self.load_files()

    def load_files(self):
        try:
            self.files = [f for f in os.listdir(self.target_dir) if os.path.isfile(os.path.join(self.target_dir, f))]
            self.update_preview()
        except Exception as e:
            self.preview_label.configure(text=f"Erro ao ler pasta: {e}")

    def get_new_name(self, original_name, index):
        name, ext = os.path.splitext(original_name)
        
        # 1. Find / Replace
        find_val = self.entry_find.get()
        replace_val = self.entry_replace.get()
        if find_val:
            name = name.replace(find_val, replace_val)
            
        # 2. Prefix / Suffix
        prefix_val = self.entry_prefix.get()
        suffix_val = self.entry_suffix.get()
        name = f"{prefix_val}{name}{suffix_val}"
        
        # 3. Numbering
        if self.var_numbering.get():
            num_str = str(index + 1).zfill(3)
            name = f"{name}_{num_str}"
            
        return f"{name}{ext}"

    def update_preview(self, event=None):
        if not self.files:
            self.preview_label.configure(text="Nenhum arquivo na pasta.")
            return
            
        lines = []
        for i, f in enumerate(self.files[:50]): # preview up to 50
            new_name = self.get_new_name(f, i)
            if new_name != f:
                lines.append(f"{f}  →  {new_name}")
            else:
                lines.append(f)
                
        if len(self.files) > 50:
            lines.append(f"... e mais {len(self.files) - 50} arquivos.")
            
        self.preview_label.configure(text="\n".join(lines), text_color=COLORS["text_main"])

    def execute_rename(self):
        if not self.files:
            return
            
        count = 0
        for i, f in enumerate(self.files):
            new_name = self.get_new_name(f, i)
            if new_name != f:
                old_path = os.path.join(self.target_dir, f)
                new_path = os.path.join(self.target_dir, new_name)
                
                # avoid collision if target exists
                if not os.path.exists(new_path):
                    try:
                        os.rename(old_path, new_path)
                        count += 1
                    except Exception as e:
                        print(f"Erro renomeando {f}: {e}")
                        
        messagebox.showinfo("Sucesso", f"{count} arquivos renomeados com sucesso!")
        self.load_files() # refresh

    def update_language(self, lang):
        pass # Placeholder for actual translation logic
