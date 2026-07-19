import os
import urllib.request
import json
import zipfile
import tempfile
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

PACKAGES = [
    "nvidia-cublas-cu12",
    "nvidia-cuda-runtime-cu12",
    "nvidia-cudnn-cu12"
]

def _get_wheel_url(package_name, log_callback):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode())
            latest_version = data["info"]["version"]
            urls = data["releases"][latest_version]
            for url_info in urls:
                if "win_amd64" in url_info.get("filename", ""):
                    return url_info["url"]
            log_callback(f"No win_amd64 wheel found for {package_name} v{latest_version}.")
    except Exception as e:
        log_callback(f"Failed to fetch metadata for {package_name}: {e}")
    return None

def download_cuda_dependencies(progress_callback=None, log_callback=None):
    if not progress_callback:
        progress_callback = lambda p, t: None
    if not log_callback:
        log_callback = lambda t: None

    # Resolve destination directory
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    libs_dir = os.path.join(appdata, "AutoADSuite", "libs")
    os.makedirs(libs_dir, exist_ok=True)

    total_packages = len(PACKAGES)
    downloaded_any = False
    
    for idx, pkg in enumerate(PACKAGES):
        log_callback(f"Resolving download URL for {pkg}...")
        url = _get_wheel_url(pkg, log_callback)
        if not url:
            log_callback(f"Could not find Windows package for {pkg}.")
            continue
            
        log_callback(f"Downloading {pkg}...")
        
        try:
            ctx = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                total_size = int(response.getheader('Content-Length', 0))
                downloaded = 0
                downloaded_any = True
                chunk_size = 1024 * 512 # 512KB chunks
                
                # Download to a temporary file
                fd, temp_path = tempfile.mkstemp(suffix=".whl")
                os.close(fd)
                
                with open(temp_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            pkg_pct = downloaded / total_size
                            # Global percentage
                            global_pct = (idx + pkg_pct) / total_packages
                            progress_callback(global_pct, f"Downloading {pkg} ({(downloaded/1024/1024):.1f}MB / {(total_size/1024/1024):.1f}MB)")
                
                log_callback(f"Extracting DLLs from {pkg}...")
                progress_callback((idx + 1) / total_packages, f"Extracting {pkg}...")
                
                # Extract DLLs
                with zipfile.ZipFile(temp_path, 'r') as z:
                    dll_files = [m for m in z.namelist() if m.endswith('.dll') and '/bin/' in m]
                    for dll_member in dll_files:
                        dll_filename = os.path.basename(dll_member)
                        target_path = os.path.join(libs_dir, dll_filename)
                        if not os.path.exists(target_path):
                            with z.open(dll_member) as source, open(target_path, 'wb') as target:
                                target.write(source.read())
                
                # Cleanup temp
                try:
                    os.remove(temp_path)
                except:
                    pass
                
        except Exception as e:
            log_callback(f"Error processing {pkg}: {e}")
            return False

    log_callback("All dependencies downloaded and extracted successfully.")
    return downloaded_any

def inject_cuda_paths():
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    libs_dir = os.path.join(appdata, "AutoADSuite", "libs")
    if os.path.exists(libs_dir):
        os.environ["PATH"] = libs_dir + os.pathsep + os.environ.get("PATH", "")
        try:
            os.add_dll_directory(libs_dir)
        except AttributeError:
            pass
        return True
    return False

def check_cuda_dlls_exist():
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    libs_dir = os.path.join(appdata, "AutoADSuite", "libs")
    required = ["cublas64_12.dll", "cudart64_12.dll"]
    for req in required:
        if not os.path.exists(os.path.join(libs_dir, req)):
            return False
    return True
