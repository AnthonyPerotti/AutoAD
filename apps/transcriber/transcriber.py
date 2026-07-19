import os
import threading

SUPPORTED_EXTENSIONS = {".mp4", ".mp3", ".m4a", ".wav", ".flac"}
OUTPUT_FILENAME = "transcricoes_agrupadas.txt"
DEFAULT_MODEL = "large-v3"

# Minimum CUDA compute capability to use float16 precision (Pascal and newer)
_MIN_CAPABILITY_FLOAT16 = (6, 0)
# Minimum compute capability to attempt CUDA at all (Maxwell and newer)
_MIN_CAPABILITY_CUDA = (5, 0)


def detect_device_and_compute(device_pref: str = "auto", compute_pref: str = "auto"):
    """
    Determine the best (device, compute_type) pair based on available hardware.

    device_pref:   "auto" | "cuda" | "cpu"
    compute_pref:  "auto" | "int8_float16" | "float32" | "int8"

    Returns (device, compute_type, hw_description)
    """
    if device_pref == "cpu":
        compute = compute_pref if compute_pref != "auto" else "int8"
        return "cpu", compute, "cpu"

    try:
        import torch
        if torch.cuda.is_available():
            capability = torch.cuda.get_device_capability(0)
            name = torch.cuda.get_device_name(0)

            if capability >= _MIN_CAPABILITY_FLOAT16:
                # Pascal+ (GTX 1000 series and newer): full float16 support
                compute = compute_pref if compute_pref != "auto" else "int8_float16"
                return "cuda", compute, f"cuda:{name}"
            elif capability >= _MIN_CAPABILITY_CUDA:
                # Maxwell/Kepler (GTX 900 / GTX 700): float32 only
                # Only use GPU if compute was explicitly set or is float32/int8_float16
                if compute_pref in ("int8_float16", "float32", "auto"):
                    compute = "float32"
                    return "cuda", compute, f"cuda_fallback:{name}"
                # If user forced int8, still try (ctranslate2 may handle it)
                return "cuda", compute_pref, f"cuda_fallback:{name}"
            else:
                # GPU too old (pre-Maxwell), fall back to CPU
                return "cpu", "int8", "cpu"
    except ImportError:
        pass

    return "cpu", "int8", "cpu"


class WhisperTranscriber:
    """Batch transcription engine using Faster-Whisper with adaptive hardware detection."""

    def __init__(self):
        self.is_running = False
        self.stop_requested = False
        self._model_cache = None
        self._cached_model_size = None

    def stop(self):
        self.stop_requested = True

    def _load_model(self, model_size: str, device: str, compute_type: str, log_callback):
        cache_key = (model_size, device, compute_type)
        if self._model_cache is not None and self._cached_model_size == cache_key:
            return self._model_cache

        from faster_whisper import WhisperModel
        log_callback(f"Loading model '{model_size}' on {device.upper()} (compute: {compute_type})...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self._model_cache = model
        self._cached_model_size = cache_key
        log_callback("Model loaded successfully.\n")
        return model

    def process_batch(
        self,
        input_dir: str,
        model_size: str = DEFAULT_MODEL,
        language: str = "pt",
        device_pref: str = "auto",
        compute_pref: str = "auto",
        log_callback=print,
        progress_callback=None,
        finish_callback=None,
    ):
        """
        Start batch transcription in a background thread.

        device_pref:  "auto" | "cuda" | "cpu"
        compute_pref: "auto" | "int8_float16" | "float32" | "int8"
        """
        self.is_running = True
        self.stop_requested = False

        thread = threading.Thread(
            target=self._run,
            args=(input_dir, model_size, language, device_pref, compute_pref,
                  log_callback, progress_callback, finish_callback),
            daemon=True,
        )
        thread.start()

    def _run(self, input_dir, model_size, language, device_pref, compute_pref,
             log_callback, progress_callback, finish_callback):
        output_path = os.path.join(input_dir, OUTPUT_FILENAME)
        errored = []

        try:
            all_files = sorted([
                f for f in os.listdir(input_dir)
                if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
                and f != OUTPUT_FILENAME
            ])

            if not all_files:
                log_callback("No supported media files found in the selected folder.")
                self.is_running = False
                if finish_callback:
                    finish_callback(False, None, [])
                return

            total = len(all_files)
            log_callback(f"Found {total} file(s) to transcribe.\n")

            device, compute_type, hw_desc = detect_device_and_compute(device_pref, compute_pref)
            log_callback(f"Hardware: {hw_desc}  |  Compute: {compute_type}")

            model = self._load_model(model_size, device, compute_type, log_callback)

            for idx, filename in enumerate(all_files):
                if self.stop_requested:
                    log_callback("\nTranscription cancelled by user.")
                    break

                file_path = os.path.join(input_dir, filename)
                name_base = os.path.splitext(filename)[0]

                log_callback(f"Processing [{idx + 1}/{total}]: {filename}...")

                try:
                    segments, info = model.transcribe(
                        file_path,
                        language=language,
                        beam_size=5,
                        condition_on_previous_text=False,
                    )

                    duration = info.duration if info.duration and info.duration > 0 else 1.0

                    with open(output_path, "a", encoding="utf-8") as f_out:
                        f_out.write(f"TITLE: {name_base}\n\n")

                        for segment in segments:
                            if self.stop_requested:
                                break
                            f_out.write(segment.text.strip() + " ")

                            pct = min(segment.end / duration, 1.0)
                            print(f"\r  Progress: {pct * 100:.1f}%", end="", flush=True)

                            if progress_callback:
                                global_pct = (idx + pct) / total
                                progress_callback(global_pct)

                        f_out.write("\n\n" + "=" * 50 + "\n\n")

                    print()
                    log_callback(f"Done: {filename}")

                except Exception as e:
                    errored.append(filename)
                    log_callback(f"Error transcribing '{filename}': {e}")

        except Exception as e:
            log_callback(f"Critical engine error: {e}")
            self.is_running = False
            if finish_callback:
                finish_callback(False, None, [])
            return

        self.is_running = False
        stopped = self.stop_requested

        if finish_callback:
            finish_callback(not stopped and not errored, output_path, errored)
