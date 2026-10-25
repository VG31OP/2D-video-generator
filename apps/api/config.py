import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
PROJECTS_DIR = STORAGE_DIR / "projects"
ASSETS_DIR = STORAGE_DIR / "assets"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "ToonForge API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{STORAGE_DIR}/toonforge.db"
    
    # Storage
    STORAGE_PATH: str = str(STORAGE_DIR)
    
    # AI Providers Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")            # auto, gemini, ollama, smart_cartoon
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "toon_vector") # toon_vector, comfyui, sd_webui, replicate
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "edge_tts")     # edge_tts, kokoro, piper, system
    ANIMATION_PROVIDER: str = os.getenv("ANIMATION_PROVIDER", "motion_comic") # motion_comic, svd, animate_diff
    
    # Default Render Config
    DEFAULT_WIDTH: int = 1080
    DEFAULT_HEIGHT: int = 1920
    DEFAULT_FPS: int = 30
    DEFAULT_DURATION_TARGET: int = int(os.getenv("DEFAULT_DURATION_TARGET", "30")) # seconds
    
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    FFPROBE_PATH: str = os.getenv("FFPROBE_PATH", "ffprobe")

    def get_ffmpeg_path(self) -> str:
        import shutil
        if self.FFMPEG_PATH and shutil.which(self.FFMPEG_PATH):
            return self.FFMPEG_PATH
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        try:
            import imageio_ffmpeg
            raw_exe = imageio_ffmpeg.get_ffmpeg_exe()
            target_dir = os.path.dirname(raw_exe)
            alias_exe = os.path.join(target_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            if not os.path.exists(alias_exe):
                try:
                    shutil.copy2(raw_exe, alias_exe)
                except Exception:
                    pass
            return alias_exe if os.path.exists(alias_exe) else raw_exe
        except Exception:
            return self.FFMPEG_PATH

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure resolved FFmpeg executable is available in PATH for all subprocess invocations
try:
    _ffmpeg_bin = settings.get_ffmpeg_path()
    if _ffmpeg_bin and os.path.isabs(_ffmpeg_bin):
        _ffmpeg_dir = os.path.dirname(_ffmpeg_bin)
        _target_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        _alias = os.path.join(_ffmpeg_dir, _target_name)
        if not os.path.exists(_alias):
            import shutil
            shutil.copy2(_ffmpeg_bin, _alias)
        path_entries = os.environ.get("PATH", "").split(os.pathsep)
        if _ffmpeg_dir not in path_entries:
            os.environ["PATH"] = os.pathsep.join([_ffmpeg_dir] + [p for p in path_entries if p])
except Exception:
    pass
