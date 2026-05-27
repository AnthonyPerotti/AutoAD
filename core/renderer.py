import os
import itertools
import subprocess
import uuid
import threading

from core.ffmpeg import FFMPEG_PATH
from core.render_job import RenderJob

TEMP_DIR = "temp"

os.makedirs(TEMP_DIR, exist_ok=True)


class RenderManager:

    def __init__(self):

        self.stop_requested = False

        self.renderizando = False

    def stop(self):

        self.stop_requested = True

    def render_video(self, videos, output_file, encoder):

        temp_txt = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.txt")

        with open(temp_txt, "w", encoding="utf-8") as f:

            for video in videos:

                video = video.replace("\\", "/")

                f.write(f"file '{video}'\n")

        codec = {
            "CPU (libx264)": "libx264",
            "NVIDIA (NVENC)": "h264_nvenc",
            "AMD (AMF)": "h264_amf",
            "Intel (QSV)": "h264_qsv",
        }.get(encoder, "libx264")

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

        startupinfo = subprocess.STARTUPINFO()

        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        stdout, stderr = process.communicate()

        try:

            os.remove(temp_txt)

        except:

            pass

        return (process.returncode, stderr)

    def generate(
        self,
        hooks_path,
        corpos_paths,
        cta_path,
        output_path,
        encoder,
        on_log,
        on_progress,
        on_job_update,
        on_finish
    ):

        self.stop_requested = False

        self.renderizando = True

        def worker():

            try:

                hooks = [
                    f for f in os.listdir(hooks_path) if f.lower().endswith(".mp4")
                ]

                ctas = [f for f in os.listdir(cta_path) if f.lower().endswith(".mp4")]

                corpos_listas = []

                for pasta in corpos_paths:

                    videos = [
                        f for f in os.listdir(pasta) if f.lower().endswith(".mp4")
                    ]

                    corpos_listas.append((pasta, videos))

                jobs = []

                for hook in hooks:

                    for cta in ctas:

                        corpos_videos = []

                        for pasta, videos in corpos_listas:

                            corpos_videos.append(
                                [os.path.join(pasta, v) for v in videos]
                            )

                        for combinacao in itertools.product(*corpos_videos):

                            lista = []

                            lista.append(os.path.join(hooks_path, hook))

                            lista.extend(combinacao)

                            lista.append(os.path.join(cta_path, cta))

                            hook_id = hook.split("_")[1].split(".")[0]

                            cta_id = cta.split("_")[1].split(".")[0]

                            corpos_formatados = []

                            for i, corpo in enumerate(lista[1:-1]):

                                corpo_nome = os.path.splitext(
                                    os.path.basename(corpo)
                                )[0]

                                try:

                                    corpo_id = corpo_nome.split("_")[-1]

                                except:

                                    corpo_id = str(i + 1)

                                if len(lista[1:-1]) > 1:

                                    corpos_formatados.append(
                                        f"D{corpo_id}-{i+1}"
                                    )

                                else:

                                    corpos_formatados.append(
                                        f"D{corpo_id}"
                                    )

                            nome_final = (
                                f"H{hook_id}_"
                                f"{'_'.join(corpos_formatados)}_"
                                f"C{cta_id}.mp4"
                            )

                            output_file = os.path.join(
                                output_path,
                                nome_final
                            )

                            job = RenderJob(
                                lista,
                                output_file
                            )

                            jobs.append(job)
                            on_log(job.output)
                            on_job_update(job)

                on_log(f"Hooks: {len(hooks)}")
                on_log(f"CTAs: {len(ctas)}")

                for i, (_, vids) in enumerate(corpos_listas):

                    on_log(
                        f"Corpo {i+1}: {len(vids)} vídeos"
                    )
                
                total = len(jobs)

                on_log(f"{total} vídeos serão gerados.")

                for index, job in enumerate(jobs):

                    if self.stop_requested:

                        on_log("Render interrompido.")

                        break

                    job.status = "rendering"

                    on_job_update(job)

                    on_log(f"Gerando {index+1}/{total}")

                    returncode, stderr = self.render_video(
                        job.videos,
                        job.output,
                        encoder
                    )

                    if returncode != 0:

                        job.status = "error"

                        job.error = stderr

                        on_log(f"ERRO FFmpeg:\n{stderr}")

                    else:

                        job.status = "done"

                        job.progress = 100

                    on_job_update(job)

                    progresso = (index + 1) / total

                    on_progress(progresso, index + 1, total)

            finally:

                self.renderizando = False

                on_finish(self.stop_requested, jobs)

        threading.Thread(target=worker, daemon=True).start()
