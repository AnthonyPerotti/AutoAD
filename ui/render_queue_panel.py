import customtkinter as ctk

class RenderQueuePanel(ctk.CTkFrame):

    def __init__(
        self,
        parent
    ):

        super().__init__(
            parent,
            corner_radius=18,
            fg_color="#10151f",
            border_width=1,
            border_color="#334155"
        )

        # ============================================
        # TITLE
        # ============================================

        self.title = ctk.CTkLabel(
            self,
            text="🎞 Render Queue",
            font=("Segoe UI", 20, "bold")
        )

        self.title.pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        # ============================================
        # SCROLL
        # ============================================

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#0f172a"
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.job_widgets = {}

    def clear(self):

        for widget in self.scroll.winfo_children():

            widget.destroy()

        self.job_widgets.clear()

    def add_job(
        self,
        job
    ):

        card = ctk.CTkFrame(
            self.scroll,
            corner_radius=12,
            fg_color="#111827"
        )

        card.pack(
            fill="x",
            padx=5,
            pady=5
        )

        name = job.output.split("\\")[-1]

        title = ctk.CTkLabel(
            card,
            text=name,
            anchor="w",
            font=("Segoe UI", 13, "bold")
        )

        title.pack(
            fill="x",
            padx=15,
            pady=(10, 5)
        )

        status = ctk.CTkLabel(
            card,
            text="Pending",
            text_color="#9ca3af"
        )

        status.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        progress = ctk.CTkProgressBar(
            card,
            height=10
        )

        progress.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        progress.set(0)

        self.job_widgets[job] = {
            "status": status,
            "progress": progress
        }

    def update_job(
        self,
        job
    ):

        if job not in self.job_widgets:
            return

        widgets = self.job_widgets[job]

        status_text = {
            "pending": "Pending",
            "rendering": "Rendering",
            "done": "Done",
            "error": "Error"
        }.get(
            job.status,
            "Unknown"
        )

        color = {
            "pending": "#9ca3af",
            "rendering": "#f59e0b",
            "done": "#22c55e",
            "error": "#ef4444"
        }.get(
            job.status,
            "#9ca3af"
        )

        widgets["status"].configure(
            text=status_text,
            text_color=color
        )

        widgets["progress"].set(
            job.progress / 100
        )