class AppState:

    def __init__(self):

        # ============================================
        # PATHS
        # ============================================

        self.hooks_path = ""

        self.cta_path = ""

        self.output_path = ""

        # ============================================
        # RENDER
        # ============================================

        self.renderizando = False

        self.stop_requested = False

        # ============================================
        # CONFIG
        # ============================================

        self.encoder = "CPU (libx264)"

        self.language = "Português"

        self.auto_open = False
