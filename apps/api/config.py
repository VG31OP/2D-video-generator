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
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "toon_vector") # toon_vector, comfyui, sd_webui, replicate
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "edge_tts")     # edge_tts, kokoro, piper, system
    ANIMATION_PROVIDER: str = os.getenv("ANIMATION_PROVIDER", "motion_comic") # motion_comic, svd, animate_diff
    
    # Default Render Config
    DEFAULT_WIDTH: int = 1080
    DEFAULT_HEIGHT: int = 1920
    DEFAULT_FPS: int = 30
    DEFAULT_DURATION_TARGET: int = 45 # seconds
    
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    FFPROBE_PATH: str = os.getenv("FFPROBE_PATH", "ffprobe")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
