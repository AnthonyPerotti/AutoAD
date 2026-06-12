import customtkinter as ctk

class AutoScrollableFrame(ctk.CTkScrollableFrame):
    """
    A smart CTkScrollableFrame that auto-hides its scrollbar when the content 
    is smaller than the visible canvas area.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Bind events to both the canvas (visible area) and the internal frame (actual content)
        self._parent_canvas.bind("<Configure>", self._check_scrollbars, add="+")
        self._parent_frame.bind("<Configure>", self._check_scrollbars, add="+")

    def _check_scrollbars(self, event=None):
        # Allow UI to update its dimensions
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
