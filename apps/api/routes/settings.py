from typing import Optional
from pathlib import Path
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apps.api.config import settings, BASE_DIR
from apps.api.providers.system_detector import detect_system_capabilities, run_provider_tests

router = APIRouter(prefix="/api/settings", tags=["settings"])

def mask_key(k: str) -> str:
    if not k:
        return ""
    if len(k) > 8:
        return f"{k[:4]}...{k[-4:]}"
    return "********"

ALLOWED_LLM_PROVIDERS = {"auto", "gemini", "ollama", "smart_cartoon"}
ALLOWED_IMAGE_PROVIDERS = {"toon_vector", "comfyui", "sd_webui", "replicate"}
ALLOWED_VOICE_PROVIDERS = {"edge_tts", "kokoro", "piper", "system"}

class SettingsUpdateRequest(BaseModel):
    llm_provider: str = "auto"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    image_provider: str = "toon_vector"
    voice_provider: str = "edge_tts"
    default_style: str = "Modern 2D Cartoon"
    default_language: str = "English"
    default_duration: int = 30
    width: int = 1080
    height: int = 1920
    fps: int = 30

@router.get("")
async def get_settings():
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "gemini_api_key": mask_key(settings.GEMINI_API_KEY),
        "gemini_key_configured": bool(settings.GEMINI_API_KEY.strip()),
        "gemini_model": settings.GEMINI_MODEL,
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
    # Validate provider fields against allow-lists
    if req.llm_provider and req.llm_provider not in ALLOWED_LLM_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid LLM provider: {req.llm_provider}")
    if req.image_provider and req.image_provider not in ALLOWED_IMAGE_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid image provider: {req.image_provider}")
    if req.voice_provider and req.voice_provider not in ALLOWED_VOICE_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid voice provider: {req.voice_provider}")

    settings.LLM_PROVIDER = req.llm_provider
    # Only update gemini_api_key if a newly supplied, unmasked key is provided
    if req.gemini_api_key is not None:
        raw_key = req.gemini_api_key.strip()
        if raw_key and not ("..." in raw_key or set(raw_key) == {"*"}):
            settings.GEMINI_API_KEY = raw_key

    settings.GEMINI_MODEL = req.gemini_model.strip() or "gemini-2.0-flash"
    settings.OLLAMA_BASE_URL = req.ollama_base_url.strip()
    settings.OLLAMA_MODEL = req.ollama_model.strip()
    settings.IMAGE_PROVIDER = req.image_provider
    settings.VOICE_PROVIDER = req.voice_provider
    settings.DEFAULT_DURATION_TARGET = req.default_duration
    settings.DEFAULT_WIDTH = req.width
    settings.DEFAULT_HEIGHT = req.height
    settings.DEFAULT_FPS = req.fps

    # Persist to .env while preserving comments, blank lines, and validating values
    updates = {
        "LLM_PROVIDER": settings.LLM_PROVIDER,
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        "GEMINI_MODEL": settings.GEMINI_MODEL,
        "OLLAMA_BASE_URL": settings.OLLAMA_BASE_URL,
        "OLLAMA_MODEL": settings.OLLAMA_MODEL,
        "IMAGE_PROVIDER": settings.IMAGE_PROVIDER,
        "VOICE_PROVIDER": settings.VOICE_PROVIDER,
        "DEFAULT_DURATION_TARGET": str(settings.DEFAULT_DURATION_TARGET),
        "DEFAULT_WIDTH": str(settings.DEFAULT_WIDTH),
        "DEFAULT_HEIGHT": str(settings.DEFAULT_HEIGHT),
        "DEFAULT_FPS": str(settings.DEFAULT_FPS)
    }

    # Validate against injection (reject newlines or equal signs in values)
    for k, v in updates.items():
        v_str = str(v)
        if "\n" in v_str or "\r" in v_str or "=" in v_str:
            raise HTTPException(status_code=400, detail=f"Invalid characters in setting value for {k}")

    try:
        env_file = BASE_DIR / ".env"
        new_lines = []
        found_keys = set()
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if "=" in line and not stripped.startswith("#"):
                    k, _ = line.split("=", 1)
                    k = k.strip()
                    if k in updates:
                        new_lines.append(f"{k}={updates[k]}")
                        found_keys.add(k)
                        continue
                new_lines.append(line)
        
        for k, v in updates.items():
            if k not in found_keys:
                new_lines.append(f"{k}={v}")

        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to persist settings: {str(e)}")

    return {"message": "Settings updated successfully"}

@router.get("/health")
async def get_system_health():
    """
    Returns live detection of GPU, CUDA, Gemini, Ollama, ComfyUI, TTS engines, and FFmpeg.
    """
    return await detect_system_capabilities()

@router.post("/test-all")
async def execute_test_all_providers():
    """
    Executes live verification tests across all AI, TTS, speech, and rendering providers.
    """
    return await run_provider_tests()

class TestGeminiRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None

@router.post("/test-gemini")
async def test_gemini(req: TestGeminiRequest):
    raw_key = (req.api_key or "").strip()
    if not raw_key or "..." in raw_key or set(raw_key) == {"*"}:
        key = (settings.GEMINI_API_KEY or "").strip()
    else:
        key = raw_key

    m = (req.model or settings.GEMINI_MODEL or "gemini-2.0-flash").strip()
    if not key:
        return {"connected": False, "error": "No Gemini API Key provided"}
    try:
        headers = {"x-goog-api-key": key}
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}",
                headers=headers
            )
            if res.status_code == 200:
                data = res.json()
                display_name = data.get("displayName", m)
                return {"connected": True, "model": m, "displayName": display_name}
            elif res.status_code in [400, 404]:
                # Test with gemini-3.5-flash fallback
                res_fb = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash",
                    headers=headers
                )
                if res_fb.status_code == 200:
                    return {"connected": True, "model": "gemini-3.5-flash", "displayName": "Gemini 3.5 Flash (Active)"}
                err_data = res.json() if "application/json" in res.headers.get("content-type", "") else {}
                err_msg = err_data.get("error", {}).get("message", res.text[:120])
                return {"connected": False, "error": f"Invalid API Key or Model: {err_msg}"}
            else:
                return {"connected": False, "error": f"Gemini API returned HTTP {res.status_code}"}
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.get("/test-gemini")
async def test_gemini_get(api_key: Optional[str] = None, model: Optional[str] = None):
    # Backward compatibility delegate
    return await test_gemini(TestGeminiRequest(api_key=api_key, model=model))

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
