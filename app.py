import os
import sys
import itertools
import subprocess
import customtkinter as ctk

from tkinter import filedialog
from tkinter import messagebox

# ============================================
# CONFIG
# ============================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("580x620")
app.title("AutoAdd")
app.resizable(True, True)


# ============================================
# PATH BASE
# ============================================

BASE_DIR = os.path.dirname(
    sys.executable if getattr(sys, "frozen", False) else __file__
)

FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "bin", "ffmpeg.exe")

# ============================================
# VARIÁVEIS
# ============================================

stop_requested = False
corpo_container = None
btn_add_corpo = None
hooks_path = ""
ctas_path = ""
output_path = ""

corpos_paths = []

MAX_CORPOS = 6

# ============================================
# LOG
# ============================================


def adicionar_log(texto):

    log_box.insert("end", texto + "\n")

    log_box.see("end")

    app.update()


def parar_geracao():

    global stop_requested

    stop_requested = True

    adicionar_log("PARADA SOLICITADA...")


# ============================================
# SELEÇÕES
# ============================================


def selecionar_hooks():

    global hooks_path

    hooks_path = filedialog.askdirectory()

    hooks_label.configure(
        text=hooks_path if hooks_path else "Nenhuma pasta selecionada"
    )

    atualizar_total_previsto()


def selecionar_ctas():

    global ctas_path

    ctas_path = filedialog.askdirectory()

    ctas_label.configure(text=ctas_path if ctas_path else "Nenhuma pasta selecionada")

    atualizar_total_previsto()


def selecionar_output():

    global output_path

    output_path = filedialog.askdirectory()

    output_label.configure(
        text=output_path if output_path else "Nenhuma pasta selecionada"
    )

    atualizar_total_previsto()


# ============================================
# CORPOS DINÂMICOS
# ============================================

corpo_frames = []


def atualizar_botoes():

    # ESCONDE botão + ao chegar em 6
    if len(corpo_frames) >= MAX_CORPOS:

        btn_add_corpo.grid_remove()

    else:

        btn_add_corpo.grid()


def remover_corpo(frame, data):

    # NÃO DEIXA REMOVER O ÚLTIMO
    if len(corpo_frames) == 1:

        messagebox.showwarning("Aviso", "É necessário pelo menos 1 corpo.")

        return

    frame.destroy()

    corpo_frames.remove(data)

    reorganizar_corpos()

    atualizar_botoes()

    atualizar_total_previsto()


def reorganizar_corpos():

    for i, corpo in enumerate(corpo_frames):

        corpo["button"].configure(text=f"Selecionar Pasta de Corpo {i + 1}")


def adicionar_corpo():

    if len(corpo_frames) >= MAX_CORPOS:
        return

    frame = ctk.CTkFrame(corpo_container)

    frame.pack(fill="x", pady=10, padx=20)

    corpo_data = {"path": "", "frame": frame}

    # ============================================
    # LINHA
    # ============================================

    linha = ctk.CTkFrame(frame, fg_color="transparent")

    linha.pack(fill="x")

    # ============================================
    # SELECIONAR PASTA
    # ============================================

    def selecionar():

        pasta = filedialog.askdirectory()

        corpo_data["path"] = pasta

        label.configure(text=pasta if pasta else "Nenhuma pasta selecionada")

        atualizar_total_previsto()

    btn = ctk.CTkButton(
        linha,
        text=f"Selecionar Pasta de Corpo {len(corpo_frames) + 1}",
        width=240,
        height=45,
        command=selecionar,
    )

    btn.pack(side="left", padx=(0, 10))

    corpo_data["button"] = btn

    # ============================================
    # BOTÃO REMOVER
    # ============================================

    # Corpo 1 não pode remover
    if len(corpo_frames) > 0:

        btn_remove = ctk.CTkButton(
            linha,
            text="-",
            width=45,
            height=45,
            fg_color="#b22222",
            hover_color="#8b0000",
            command=lambda: remover_corpo(frame, corpo_data),
        )

        btn_remove.pack(side="left")

    # ============================================
    # LABEL
    # ============================================

    label = ctk.CTkLabel(frame, text="Nenhuma pasta selecionada", wraplength=700)

    label.pack(pady=(8, 0))

    corpo_data["label"] = label

    corpo_frames.append(corpo_data)

    atualizar_botoes()


# ============================================
# TOTAL PREVISTO
# ============================================


def atualizar_total_previsto():

    try:

        # hooks obrigatório
        if not hooks_path:
            total_label.configure(text="Total previsto: 0 vídeos")
            return

        # ctas obrigatório
        if not ctas_path:
            total_label.configure(text="Total previsto: 0 vídeos")
            return

        total = 1

        # ============================================
        # HOOKS
        # ============================================

        hooks = len([f for f in os.listdir(hooks_path) if f.lower().endswith(".mp4")])

        total *= hooks

        # ============================================
        # CORPOS
        # ============================================

        for corpo in corpo_frames:

            pasta = corpo["path"]

            # se existir corpo vazio
            if not pasta:

                total_label.configure(text="Total previsto: 0 vídeos")

                return

            qtd = len([f for f in os.listdir(pasta) if f.lower().endswith(".mp4")])

            total *= qtd

        # ============================================
        # CTAS
        # ============================================

        ctas = len([f for f in os.listdir(ctas_path) if f.lower().endswith(".mp4")])

        total *= ctas

        # ============================================

        total_label.configure(text=f"Total previsto: {total} vídeos")

    except:

        total_label.configure(text="Total previsto: 0 vídeos")


# ============================================
# GERAR VÍDEOS
# ============================================


def gerar_videos():

    global stop_requested

    stop_requested = False

    log_box.delete("1.0", "end")

    adicionar_log("Iniciando geração...")

    # ============================================

    if not hooks_path:

        messagebox.showerror("Erro", "Selecione a pasta de Hooks.")

        return

    if not ctas_path:

        messagebox.showerror("Erro", "Selecione a pasta de CTAs.")

        return

    if not output_path:

        messagebox.showerror("Erro", "Selecione a pasta de saída.")

        return

    if len(corpo_frames) == 0:

        messagebox.showerror("Erro", "Adicione pelo menos 1 corpo.")

        return

    # ============================================

    hooks = sorted([f for f in os.listdir(hooks_path) if f.lower().endswith(".mp4")])

    ctas = sorted([f for f in os.listdir(ctas_path) if f.lower().endswith(".mp4")])

    corpos_listas = []

    for corpo in corpo_frames:

        pasta = corpo["path"]

        if not pasta:

            messagebox.showerror("Erro", "Existe corpo sem pasta selecionada.")

            return

        videos = sorted([f for f in os.listdir(pasta) if f.lower().endswith(".mp4")])

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

            for combinacao_corpos in itertools.product(*corpos_videos):

                lista = []

                # HOOK
                lista.append(os.path.join(hooks_path, hook))

                # CORPOS
                lista.extend(combinacao_corpos)

                # CTA
                lista.append(os.path.join(ctas_path, cta))

                lista_final.append(lista)

    # ============================================
    # TOTAL
    # ============================================

    total = len(lista_final)

    total_label.configure(text=f"Total previsto: {total} vídeos")

    app.update()

    adicionar_log(f"Total previsto: {total} vídeos.")

    # ============================================
    # CONFIRMAÇÃO
    # ============================================

    if total > 100:

        continuar = messagebox.askyesno(
            "Confirmação",
            (
                f"Serão gerados {total} vídeos.\n\n"
                f"Isso pode demorar bastante.\n\n"
                f"Deseja continuar?"
            ),
        )

        if not continuar:

            adicionar_log("Geração cancelada pelo usuário.")

            return

    adicionar_log(f"Iniciando geração de {total} vídeos...")

    # ============================================
    # LOOP PRINCIPAL
    # ============================================

    for index, videos in enumerate(lista_final):

        # ============================================
        # STOP
        # ============================================

        if stop_requested:

            adicionar_log("Geração interrompida.")

            messagebox.showwarning("Parado", "Geração interrompida pelo usuário.")

            break

        adicionar_log(f"[{index+1}/{total}] Gerando vídeo...")

        temp_txt = os.path.join(BASE_DIR, f"temp_{index}.txt")

        with open(temp_txt, "w", encoding="utf-8") as f:

            for video in videos:

                video = video.replace("\\", "/")

                f.write(f"file '{video}'\n")

        # ============================================
        # NOMES
        # ============================================

        hook_nome = os.path.splitext(os.path.basename(videos[0]))[0]

        cta_nome = os.path.splitext(os.path.basename(videos[-1]))[0]

        corpos_nomes = []

        for corpo_video in videos[1:-1]:

            nome = os.path.splitext(os.path.basename(corpo_video))[0]

            corpos_nomes.append(nome)

        nome_corpos = "_".join(corpos_nomes)

        nome_final = f"{hook_nome}" f"_{nome_corpos}" f"_{cta_nome}.mp4"

        output_file = os.path.join(output_path, nome_final)

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            temp_txt,
            "-c",
            "copy",
            output_file,
        ]

        try:

            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            adicionar_log(f"OK -> {nome_final}")

        except Exception as e:

            adicionar_log(f"ERRO -> {str(e)}")

        if os.path.exists(temp_txt):

            os.remove(temp_txt)

        progresso = (index + 1) / total

        progressbar.set(progresso)

        progresso_label.configure(text=f"{index+1}/{total}")

        app.update()

    progressbar.set(1)

    adicionar_log("Finalizado.")

    messagebox.showinfo("Concluído", f"{total} vídeos gerados.")


# ============================================
# CONTAINER PRINCIPAL
# ============================================

main_frame = ctk.CTkScrollableFrame(app, fg_color="transparent")

main_frame.pack(fill="both", expand=True, padx=15, pady=15)

# ============================================
# TÍTULO
# ============================================

titulo = ctk.CTkLabel(main_frame, text="AutoAdd", font=("Arial", 24, "bold"))

titulo.grid(row=0, column=0, columnspan=3, pady=(5, 20))

# ============================================
# HOOKS
# ============================================

hooks_title = ctk.CTkLabel(main_frame, text="HOOKS", font=("Arial", 14, "bold"))

hooks_title.grid(row=1, column=0, sticky="w", pady=(0, 5))

btn_hooks = ctk.CTkButton(
    main_frame, text="Selecionar Pasta", width=220, height=34, command=selecionar_hooks
)

btn_hooks.grid(row=2, column=0, sticky="w")

hooks_label = ctk.CTkLabel(
    main_frame,
    text="Nenhuma pasta selecionada",
    wraplength=420,
    anchor="w",
    justify="left",
)

hooks_label.grid(row=3, column=0, sticky="w", pady=(5, 15))

# ============================================
# CORPOS
# ============================================

corpo_title = ctk.CTkLabel(main_frame, text="CORPOS", font=("Arial", 14, "bold"))

corpo_title.grid(row=4, column=0, sticky="w", pady=(0, 5))

corpo_container = ctk.CTkFrame(main_frame, fg_color="transparent")

corpo_container.grid(row=5, column=0, sticky="w")

btn_add_corpo = ctk.CTkButton(
    main_frame, text="+ Adicionar Corpo", width=180, height=32, command=adicionar_corpo
)

btn_add_corpo.grid(row=6, column=0, sticky="w", pady=(10, 20))

# PRIMEIRO CORPO
adicionar_corpo()

# ============================================
# CTA
# ============================================

cta_title = ctk.CTkLabel(main_frame, text="CTAs", font=("Arial", 14, "bold"))

cta_title.grid(row=7, column=0, sticky="w", pady=(0, 5))

btn_ctas = ctk.CTkButton(
    main_frame, text="Selecionar Pasta", width=220, height=34, command=selecionar_ctas
)

btn_ctas.grid(row=8, column=0, sticky="w")

ctas_label = ctk.CTkLabel(
    main_frame,
    text="Nenhuma pasta selecionada",
    wraplength=420,
    anchor="w",
    justify="left",
)

ctas_label.grid(row=9, column=0, sticky="w", pady=(5, 15))

# ============================================
# OUTPUT
# ============================================

output_title = ctk.CTkLabel(main_frame, text="SAÍDA", font=("Arial", 14, "bold"))

output_title.grid(row=10, column=0, sticky="w", pady=(0, 5))

btn_output = ctk.CTkButton(
    main_frame, text="Selecionar Pasta", width=220, height=34, command=selecionar_output
)

btn_output.grid(row=11, column=0, sticky="w")

output_label = ctk.CTkLabel(
    main_frame,
    text="Nenhuma pasta selecionada",
    wraplength=420,
    anchor="w",
    justify="left",
)

output_label.grid(row=12, column=0, sticky="w", pady=(5, 20))

# ============================================
# BOTÕES
# ============================================

btn_gerar = ctk.CTkButton(
    main_frame,
    text="GERAR VÍDEOS",
    width=220,
    height=40,
    font=("Arial", 14, "bold"),
    command=gerar_videos,
)

btn_gerar.grid(row=13, column=0, sticky="w")

btn_stop = ctk.CTkButton(
    main_frame,
    text="STOP",
    width=120,
    height=40,
    fg_color="#b22222",
    hover_color="#8b0000",
    command=parar_geracao,
)

btn_stop.grid(row=13, column=1, padx=(10, 0), sticky="w")

# ============================================
# PROGRESSO
# ============================================

progressbar = ctk.CTkProgressBar(main_frame, width=360)

progressbar.grid(row=14, column=0, columnspan=2, sticky="w", pady=(20, 5))

progressbar.set(0)

progresso_label = ctk.CTkLabel(main_frame, text="0/0")

progresso_label.grid(row=15, column=0, sticky="w")

total_label = ctk.CTkLabel(
    main_frame, text="Total previsto: 0 vídeos", font=("Arial", 13, "bold")
)

total_label.grid(row=16, column=0, sticky="w", pady=(5, 20))

# ============================================
# LOG
# ============================================

log_title = ctk.CTkLabel(main_frame, text="LOG", font=("Arial", 14, "bold"))

log_title.grid(row=17, column=0, sticky="w", pady=(0, 5))

log_box = ctk.CTkTextbox(main_frame, width=520, height=100)

log_box.grid(row=18, column=0, columnspan=3, sticky="w")

creditos = ctk.CTkLabel(
    main_frame, text="by Anthony Perotti", font=("Arial", 11), text_color="#7a7a7a"
)

creditos.grid(row=99, column=0, sticky="sw", pady=(20, 5), padx=5)

app.mainloop()
