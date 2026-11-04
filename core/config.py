"""
Core Configuration & Cross-Platform Dynamic Discovery
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = ROOT_DIR / "storage"
TEMPLATES_DIR = ROOT_DIR / "templates" / "zach_engine"
MODELS_DIR = STORAGE_DIR / "models"
REELS_DIR = STORAGE_DIR / "reels"
DRAFTS_DIR = STORAGE_DIR / "drafts"

SESSION_FILE = STORAGE_DIR / "instagram_session.json"
COOKIES_FILE = STORAGE_DIR / "instagram_cookies.json"
DB_PATH = STORAGE_DIR / "toonforge.db"

# Ensure storage directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
REELS_DIR.mkdir(parents=True, exist_ok=True)
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def find_model_paths() -> Tuple[Path, Path]:
    """Dynamically locates Kokoro ONNX model and voices bin across system."""
    candidates = [
        MODELS_DIR,
        Path.home() / ".gemini" / "config" / "skills" / "animation-kit" / "models",
        Path.home() / ".cache" / "kokoro",
    ]
    for c in candidates:
        m = c / "kokoro-v1.0.onnx"
        v = c / "voices-v1.0.bin"
        if m.exists() and v.exists():
            return m, v
    return MODELS_DIR / "kokoro-v1.0.onnx", MODELS_DIR / "voices-v1.0.bin"


def find_node_modules() -> Optional[Path]:
    """Locates Three.js node_modules across project or system."""
    candidates = [
        TEMPLATES_DIR / "node_modules",
        ROOT_DIR / "node_modules",
        Path.home() / ".gemini" / "config" / "skills" / "animation-kit" / "node_modules",
    ]
    for c in candidates:
        if c.exists() and (c / "three").exists():
            return c
    return None


def find_chrome_executable() -> Optional[str]:
    """Dynamically locates Chrome / Chromium across Windows, macOS, and Linux."""
    # 1. Environment override
    env_chrome = os.getenv("CHROME_PATH") or os.getenv("CHROME")
    if env_chrome and Path(env_chrome).exists():
        return env_chrome

    # 2. Local Playwright browser cache
    if sys.platform == "win32":
        local_app = os.getenv("LOCALAPPDATA")
        if local_app:
            pw_dir = Path(local_app) / "ms-playwright"
            if pw_dir.exists():
                for c in pw_dir.glob("chromium-*/chrome-win64/chrome.exe"):
                    if c.exists():
                        return str(c)
                for c in pw_dir.glob("chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe"):
                    if c.exists():
                        return str(c)
    elif sys.platform == "darwin":
        mac_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
        if mac_cache.exists():
            for c in mac_cache.glob("chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
                if c.exists():
                    return str(c)
    else:
        linux_cache = Path.home() / ".cache" / "ms-playwright"
        if linux_cache.exists():
            for c in linux_cache.glob("chromium-*/chrome-linux/chrome"):
                if c.exists():
                    return str(c)

    # 3. System browser binary
    for bin_name in ["google-chrome", "chrome", "chromium", "msedge"]:
        which_path = shutil.which(bin_name)
        if which_path:
            return which_path

    return None


def get_ffmpeg_path() -> str:
    """Locates FFmpeg executable in PATH or via imageio_ffmpeg fallback."""
    env_ff = os.getenv("FFMPEG_PATH")
    if env_ff and shutil.which(env_ff):
        return env_ff
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

