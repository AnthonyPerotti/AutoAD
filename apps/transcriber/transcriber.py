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
        import ctranslate2
        cuda_count = ctranslate2.get_cuda_device_count()
        if cuda_count > 0:
            supported = ctranslate2.get_supported_compute_types("cuda", 0)
            
            # Determine compute type
            if compute_pref != "auto":
                compute = compute_pref
            else:
                if "int8_float16" in supported:
                    compute = "int8_float16"
                elif "float32" in supported:
                    compute = "float32"
                elif "int8" in supported:
                    compute = "int8"
                else:
                    compute = list(supported)[0] if supported else "float32"
            
            # Additional hardware info is harder without torch, but we know it's a CUDA device
            hw_desc = f"cuda (Compute: {compute})"
            return "cuda", compute, hw_desc
    except ImportError:
        pass
    except Exception:
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
        try:
            model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            if device == "cuda" and ("cublas" in str(e).lower() or "cudnn" in str(e).lower() or "library" in str(e).lower()):
                log_callback(f"CUDA libraries missing or failed to load: {e}\nFalling back to CPU (int8)...")
                device = "cpu"
                compute_type = "int8"
                cache_key = (model_size, device, compute_type)
                if self._model_cache is not None and self._cached_model_size == cache_key:
                    return self._model_cache
                model = WhisperModel(model_size, device=device, compute_type=compute_type)
            else:
                raise

        self._model_cache = model
        self._cached_model_size = cache_key
        log_callback("Model loaded successfully.\n")
        return model

    def process_batch(
        self,
        input_path: str,
        model_size: str = DEFAULT_MODEL,
        language: str = "pt",
        device_pref: str = "auto",
        compute_pref: str = "auto",
        input_scope: str = "folder",
        output_mode: str = "grouped",
        output_dir: str = "",
        log_callback=print,
        progress_callback=None,
        finish_callback=None,
    ):
        """
        Start batch transcription in a background thread.
        input_scope: "single", "folder", "recursive"
        output_mode: "grouped", "individual"
        """
        self.is_running = True
        self.stop_requested = False

        thread = threading.Thread(
            target=self._run,
            args=(input_path, model_size, language, device_pref, compute_pref,
                  input_scope, output_mode, output_dir,
                  log_callback, progress_callback, finish_callback),
            daemon=True,
        )
        thread.start()

    def _run(self, input_path, model_size, language, device_pref, compute_pref,
             input_scope, output_mode, output_dir,
             log_callback, progress_callback, finish_callback):
        errored = []
        all_files = []

        try:
            # 1. Gather files based on scope
            if input_scope == "single":
                if os.path.isfile(input_path) and os.path.splitext(input_path)[1].lower() in SUPPORTED_EXTENSIONS:
                    all_files.append(input_path)
            elif input_scope == "recursive":
                for root, _, files in os.walk(input_path):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS and f != OUTPUT_FILENAME:
                            all_files.append(os.path.join(root, f))
            else: # "folder"
                if os.path.isdir(input_path):
                    for f in os.listdir(input_path):
                        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS and f != OUTPUT_FILENAME:
                            full_p = os.path.join(input_path, f)
                            if os.path.isfile(full_p):
                                all_files.append(full_p)

            # Sort files for deterministic processing
            all_files.sort()

            if not all_files:
                log_callback("No supported media files found in the selected location.")
                self.is_running = False
                if finish_callback:
                    finish_callback(False, None, [])
                return

            total = len(all_files)
            log_callback(f"Found {total} file(s) to transcribe.\n")

            device, compute_type, hw_desc = detect_device_and_compute(device_pref, compute_pref)
            log_callback(f"Hardware: {hw_desc}  |  Compute: {compute_type}")

            model = self._load_model(model_size, device, compute_type, log_callback)

            # Resolve actual output directory (fallback to input_path's dir if none provided)
            base_out_dir = output_dir if output_dir else (os.path.dirname(input_path) if input_scope == "single" else input_path)
            if not os.path.exists(base_out_dir):
                os.makedirs(base_out_dir, exist_ok=True)

            def get_unique_path(base):
                if not os.path.exists(base):
                    return base
                d = os.path.dirname(base)
                f = os.path.basename(base)
                n, e = os.path.splitext(f)
                c = 1
                while os.path.exists(os.path.join(d, f"{n} ({c}){e}")):
                    c += 1
                return os.path.join(d, f"{n} ({c}){e}")

            grouped_output_path = get_unique_path(os.path.join(base_out_dir, OUTPUT_FILENAME))
            
            try:
                model = self._load_model(model_size, device, compute_type, log_callback)
            except Exception as e:
                if "int8" in str(e).lower() or "cuda" in str(e).lower() or "compute type" in str(e).lower():
                    log_callback(f"Model loading failed on {device.upper()}: {e}\nFalling back to CPU (int8)...")
                    device = "cpu"
                    compute_type = "int8"
                    model = self._load_model(model_size, device, compute_type, log_callback)
                else:
                    raise e
            
            for idx, file_path in enumerate(all_files):
                if self.stop_requested:
                    log_callback("\nTranscription cancelled by user.")
                    break

                filename = os.path.basename(file_path)
                name_base = os.path.splitext(filename)[0]

                log_callback(f"Processing [{idx + 1}/{total}]: {filename}...")

                def _process_file(current_model):
                    segments, info = current_model.transcribe(
                        file_path,
                        language=language if language != "auto" else None,
                        beam_size=5,
                        condition_on_previous_text=False,
                    )
                    # Compute the very first segment to catch any CUDA initialization errors
                    segments_iterator = iter(segments)
                    try:
                        first_segment = next(segments_iterator)
                    except StopIteration:
                        first_segment = None
                        
                    return segments_iterator, first_segment, info

                try:
                    try:
                        segments_iterator, first_segment, info = _process_file(model)
                    except Exception as e:
                        if "cublas" in str(e).lower() or "cudnn" in str(e).lower() or "library" in str(e).lower() or "cuda" in str(e).lower():
                            log_callback(f"CUDA transcription failed: {e}\nReloading model on CPU...")
                            model = self._load_model(model_size, "cpu", "int8", log_callback)
                            segments_iterator, first_segment, info = _process_file(model)
                        else:
                            raise e

                    duration = info.duration if info.duration and info.duration > 0 else 1.0

                    # Helper to yield all segments (first one + the rest)
                    def generate_all_segments():
                        if first_segment is not None:
                            yield first_segment
                        for seg in segments_iterator:
                            yield seg

                    if output_mode == "individual":
                        # Write to individual file
                        ind_out_path = get_unique_path(os.path.join(base_out_dir, f"{name_base}_transcription.txt"))
                        with open(ind_out_path, "w", encoding="utf-8") as f_out:
                            f_out.write(f"TITLE: {name_base}\n\n")
                            for segment in generate_all_segments():
                                if self.stop_requested:
                                    break
                                f_out.write(segment.text.strip() + " ")
                                pct = min(segment.end / duration, 1.0)
                                if progress_callback:
                                    global_pct = (idx + pct) / total
                                    progress_callback(global_pct)
                    else:
                        # Write to grouped file
                        with open(grouped_output_path, "a", encoding="utf-8") as f_out:
                            f_out.write(f"TITLE: {name_base}\n\n")
                            for segment in generate_all_segments():
                                if self.stop_requested:
                                    break
                                f_out.write(segment.text.strip() + " ")
                                
                                pct = min(segment.end / duration, 1.0)
                                if progress_callback:
                                    global_pct = (idx + pct) / total
                                    progress_callback(global_pct)
                            f_out.write("\n\n" + "="*40 + "\n\n")

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
            finish_callback(not stopped and not errored, base_out_dir, errored)
