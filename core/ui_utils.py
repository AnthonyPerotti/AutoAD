import os
import customtkinter as ctk
from core.theme import COLORS, FONTS, SIZES


class AutoScrollableFrame(ctk.CTkScrollableFrame):
    """Smart CTkScrollableFrame that auto-hides its scrollbar when content fits."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent_canvas.bind("<Configure>", self._check_scrollbars, add="+")
        self._parent_frame.bind("<Configure>", self._check_scrollbars, add="+")

    def _check_scrollbars(self, event=None):
        self.after(50, self._perform_check)

    def _perform_check(self):
        try:
            if self._orientation == "vertical":
                canvas_h = self._parent_canvas.winfo_height()
                frame_h = self._parent_frame.winfo_reqheight()
                if frame_h <= canvas_h:
                    self._scrollbar.grid_remove()
                else:
                    self._scrollbar.grid(row=0, column=1, sticky="ns")
            elif self._orientation == "horizontal":
                canvas_w = self._parent_canvas.winfo_width()
                frame_w = self._parent_frame.winfo_reqwidth()
                if frame_w <= canvas_w:
                    self._scrollbar.grid_remove()
                else:
                    self._scrollbar.grid(row=1, column=0, sticky="ew")
        except Exception:
            pass


def show_completion_popup(parent, lang: dict, task_name: str, output_path: str):
    """
    Displays a non-blocking completion popup in the current application language.
    Offers the user an 'Open Folder' button and a 'Close' button.

    Args:
        parent:      The parent widget (the view frame).
        lang:        The active language dictionary from translations.py.
        task_name:   The human-readable task name (e.g. "Audio Toolkit").
        output_path: The full path to the output file or directory.
    """
    is_pt = lang.get("title", "").startswith("AutoAD") and "Adicionar" in lang.get("add_videos", "")

    title   = lang.get("popup_done_title",   "Task Complete" if not is_pt else "Tarefa Concluída")
    body    = lang.get("popup_done_body",    "{task} finished successfully.\nOutput saved to:").format(task=task_name)
    btn_open  = lang.get("popup_open_folder", "Open Folder"  if not is_pt else "Abrir Pasta")
    btn_close = lang.get("popup_close",       "Close"        if not is_pt else "Fechar")

    popup = ctk.CTkToplevel(parent)
    popup.title(title)
    popup.geometry("480x220")
    popup.resizable(False, False)
    popup.grab_set()
    popup.lift()
    popup.focus_force()

    ctk.CTkLabel(popup, text=title, font=FONTS["title_section"], text_color=COLORS["success"]).pack(anchor="w", padx=25, pady=(20, 5))
    ctk.CTkLabel(popup, text=body,  font=FONTS["text_normal"],   text_color=COLORS["text_main"]).pack(anchor="w", padx=25)

    path_frame = ctk.CTkFrame(popup, fg_color=COLORS["bg_panel"], corner_radius=SIZES["corner_pill"])
    path_frame.pack(fill="x", padx=25, pady=(8, 15))
    ctk.CTkLabel(
        path_frame, text=output_path,
        font=("Consolas", 10), text_color=COLORS["text_muted"],
        anchor="w", wraplength=420
    ).pack(padx=12, pady=8, anchor="w")

    btn_row = ctk.CTkFrame(popup, fg_color="transparent")
    btn_row.pack(fill="x", padx=25, pady=(0, 20))

    def _open_and_close():
        popup.destroy()
        if output_path and os.path.exists(output_path):
            target = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
            try:
                os.startfile(target)
            except Exception:
                pass

    ctk.CTkButton(
        btn_row, text=btn_open, fg_color=COLORS["btn_action"], hover_color=COLORS["btn_action_hover"],
        text_color=COLORS["text_main"], command=_open_and_close, width=140
    ).pack(side="left", padx=(0, 10))

    ctk.CTkButton(
        btn_row, text=btn_close, fg_color="transparent", border_width=1, border_color=COLORS["border"],
        hover_color=COLORS["bg_hover"], text_color=COLORS["text_main"],
        command=popup.destroy, width=100
    ).pack(side="left")

