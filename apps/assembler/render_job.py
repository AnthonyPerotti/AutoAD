class RenderJob:

    def __init__(
        self,
        videos,
        output
    ):

        self.videos = videos

        self.output = output

        self.status = "pending"

        self.progress = 0

        self.error = None
