import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from apps.api.config import settings
from apps.api.providers.system_detector import detect_system_capabilities, run_provider_tests

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingsUpdateRequest(BaseModel):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    image_provider: str = "toon_vector"
    voice_provider: str = "edge_tts"
    default_style: str = "Modern 2D Cartoon"
    default_language: str = "English"
    default_duration: int = 45
    width: int = 1080
    height: int = 1920
    fps: int = 30

@router.get("")
async def get_settings():
    return {
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "image_provider": settings.IMAGE_PROVIDER,
        "voice_provider": settings.VOICE_PROVIDER,
        "animation_provider": settings.ANIMATION_PROVIDER,
        "default_style": "Modern 2D Cartoon",
        "default_language": "English",
        "default_duration": settings.DEFAULT_DURATION_TARGET,
        "width": settings.DEFAULT_WIDTH,
        "height": settings.DEFAULT_HEIGHT,
        "fps": settings.DEFAULT_FPS
    }

@router.post("")
async def update_settings(req: SettingsUpdateRequest):
    settings.OLLAMA_BASE_URL = req.ollama_base_url
    settings.OLLAMA_MODEL = req.ollama_model
    settings.IMAGE_PROVIDER = req.image_provider
    settings.VOICE_PROVIDER = req.voice_provider
    settings.DEFAULT_DURATION_TARGET = req.default_duration
    settings.DEFAULT_WIDTH = req.width
    settings.DEFAULT_HEIGHT = req.height
    settings.DEFAULT_FPS = req.fps
    return {"message": "Settings updated successfully"}

@router.get("/health")
async def get_system_health():
    """
    Returns live detection of GPU, CUDA, Ollama, ComfyUI, TTS engines, and FFmpeg.
    """
    return await detect_system_capabilities()

@router.post("/test-all")
async def execute_test_all_providers():
    """
    Executes live verification tests across all AI, TTS, speech, and rendering providers.
    """
    return await run_provider_tests()

@router.get("/test-ollama")
async def test_ollama(url: str = "http://localhost:11434"):
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{url}/api/tags")
            if res.status_code == 200:
                models = [m.get("name") for m in res.json().get("models", [])]
                return {"connected": True, "models": models}
    except Exception as e:
        return {"connected": False, "error": str(e)}
    return {"connected": False, "error": "Unknown error"}
