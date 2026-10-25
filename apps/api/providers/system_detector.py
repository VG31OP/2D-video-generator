import os
import sys
import shutil
import subprocess
import httpx
try:
    import torch
except ImportError:
    torch = None
from typing import Dict, Any, List
from apps.api.config import settings

async def detect_system_capabilities() -> Dict[str, Any]:
    """
    Scans the local environment, hardware, network endpoints, and Python libraries
    to detect available AI engines, checkpoints, and hardware acceleration.
    """
    capabilities = {
        "system": {
            "python_version": sys.version.split()[0],
            "python_ok": True,
            "os": sys.platform
        },
        "hardware": {
            "gpu_available": False,
            "gpu_name": "CPU (No CUDA GPU detected)",
            "cuda_available": False,
            "device_count": 0,
            "vram_total_gb": 0.0,
        },
        "llm": {
            "selected_provider": settings.LLM_PROVIDER,
            "gemini_available": False,
            "gemini_configured": bool(settings.GEMINI_API_KEY.strip()),
            "gemini_model": settings.GEMINI_MODEL,
            "ollama_available": False,
            "ollama_url": settings.OLLAMA_BASE_URL,
            "configured_model": settings.OLLAMA_MODEL,
            "model_ready": False,
            "available_models": [],
            "smart_engine_available": True,
            "active_provider_type": "FALLBACK"
        },
        "visual": {
            "comfyui_available": False,
            "comfyui_url": "http://localhost:8188",
            "available_checkpoints": [],
            "active_checkpoint": None,
            "toon_vector_available": True,
            "active_provider_type": "FALLBACK"
        },
        "voice": {
            "kokoro_available": False,
            "piper_available": False,
            "edge_tts_available": False,
            "fallback_synth_available": True,
            "active_provider_type": "FALLBACK"
        },
        "speech": {
            "whisper_available": False,
            "whisper_flavor": None
        },
        "lip_sync": {
            "real_lipsync_available": False,
            "mouth_flap_available": True,
            "active_provider_type": "FALLBACK"
        },
        "animation": {
            "ai_animation_available": False,
            "motion_comic_available": True,
            "active_provider_type": "FALLBACK"
        },
        "rendering": {
            "ffmpeg_available": False,
            "ffmpeg_version": "",
            "ffprobe_available": False,
            "libass_supported": False,
        }
    }

    # 1. GPU & CUDA Detection
    try:
        if torch and torch.cuda.is_available():
            capabilities["hardware"]["gpu_available"] = True
            capabilities["hardware"]["cuda_available"] = True
            capabilities["hardware"]["device_count"] = torch.cuda.device_count()
            capabilities["hardware"]["gpu_name"] = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            capabilities["hardware"]["vram_total_gb"] = round(vram_bytes / (1024 ** 3), 2)
    except Exception:
        pass

    # 2. Google Gemini Verification
    gemini_key = settings.GEMINI_API_KEY.strip()
    if gemini_key:
        capabilities["llm"]["gemini_configured"] = True
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}?key={gemini_key}"
                )
                if res.status_code == 200:
                    capabilities["llm"]["gemini_available"] = True
                    capabilities["llm"]["model_ready"] = True
                    capabilities["llm"]["configured_model"] = settings.GEMINI_MODEL
                    capabilities["llm"]["active_provider_type"] = f"REAL AI (Gemini: {settings.GEMINI_MODEL})"
                elif res.status_code in [400, 404]:
                    res_fb = await client.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash?key={gemini_key}"
                    )
                    if res_fb.status_code == 200:
                        capabilities["llm"]["gemini_available"] = True
                        capabilities["llm"]["model_ready"] = True
                        capabilities["llm"]["configured_model"] = "gemini-3.5-flash"
                        capabilities["llm"]["active_provider_type"] = "REAL AI (Gemini: gemini-3.5-flash)"
        except Exception:
            capabilities["llm"]["gemini_available"] = False

    # 3. Ollama Deep Verification (Tags + Model check)
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name") for m in data.get("models", [])]
                capabilities["llm"]["ollama_available"] = True
                capabilities["llm"]["available_models"] = models
                if not capabilities["llm"]["gemini_available"]:
                    if any(settings.OLLAMA_MODEL in m for m in models):
                        capabilities["llm"]["model_ready"] = True
                        capabilities["llm"]["active_provider_type"] = f"REAL AI (Ollama: {settings.OLLAMA_MODEL})"
                    elif models:
                        capabilities["llm"]["configured_model"] = models[0]
                        capabilities["llm"]["model_ready"] = True
                        capabilities["llm"]["active_provider_type"] = f"REAL AI (Ollama: {models[0]})"
    except Exception:
        capabilities["llm"]["ollama_available"] = False

    # 3. ComfyUI Deep Verification (Endpoint + Checkpoint discovery)
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get("http://localhost:8188/system_stats")
            if res.status_code == 200:
                capabilities["visual"]["comfyui_available"] = True
                try:
                    obj_res = await client.get("http://localhost:8188/object_info/CheckpointLoaderSimple")
                    if obj_res.status_code == 200:
                        obj_data = obj_res.json()
                        ckpt_list = obj_data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
                        capabilities["visual"]["available_checkpoints"] = ckpt_list
                        if ckpt_list:
                            capabilities["visual"]["active_checkpoint"] = ckpt_list[0]
                            capabilities["visual"]["active_provider_type"] = "REAL AI"
                except Exception:
                    pass
    except Exception:
        capabilities["visual"]["comfyui_available"] = False
        capabilities["visual"]["active_provider_type"] = "FALLBACK"

    # 4. Voice Packages Detection
    try:
        import kokoro
        capabilities["voice"]["kokoro_available"] = True
        capabilities["voice"]["active_provider_type"] = "REAL AI"
    except ImportError:
        capabilities["voice"]["kokoro_available"] = False

    try:
        import piper
        capabilities["voice"]["piper_available"] = True
        if capabilities["voice"]["active_provider_type"] == "FALLBACK":
            capabilities["voice"]["active_provider_type"] = "REAL AI"
    except ImportError:
        capabilities["voice"]["piper_available"] = False

    try:
        import edge_tts
        capabilities["voice"]["edge_tts_available"] = True
        if capabilities["voice"]["active_provider_type"] == "FALLBACK":
            capabilities["voice"]["active_provider_type"] = "REAL TTS"
    except ImportError:
        capabilities["voice"]["edge_tts_available"] = False

    # 5. Whisper / faster-whisper
    try:
        import faster_whisper
        capabilities["speech"]["whisper_available"] = True
        capabilities["speech"]["whisper_flavor"] = "faster-whisper"
    except ImportError:
        try:
            import whisper
            capabilities["speech"]["whisper_available"] = True
            capabilities["speech"]["whisper_flavor"] = "openai-whisper"
        except ImportError:
            capabilities["speech"]["whisper_available"] = False

    # 6. FFmpeg Detection
    try:
        ffmpeg_bin = settings.get_ffmpeg_path()
        res = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True)
        if res.returncode == 0:
            capabilities["rendering"]["ffmpeg_available"] = True
            first_line = res.stdout.split("\n")[0]
            capabilities["rendering"]["ffmpeg_version"] = first_line[:50]
            capabilities["rendering"]["libass_supported"] = "--enable-libass" in res.stdout
    except Exception:
        capabilities["rendering"]["ffmpeg_available"] = False

    try:
        res_probe = subprocess.run([settings.FFPROBE_PATH, "-version"], capture_output=True, text=True)
        capabilities["rendering"]["ffprobe_available"] = (res_probe.returncode == 0)
    except Exception:
        capabilities["rendering"]["ffprobe_available"] = False

    return capabilities


async def run_provider_tests() -> Dict[str, Any]:
    """
    Executes live lightweight tests across all providers and returns granular results.
    """
    results = {
        "system": {"status": "ok", "python": sys.version.split()[0], "platform": sys.platform},
        "ffmpeg": {"status": "unknown", "version": ""},
        "cuda": {"status": "unknown", "gpu": "None"},
        "gemini": {"status": "unknown", "connected": False},
        "ollama": {"status": "unknown", "connected": False, "models": []},
        "comfyui": {"status": "unknown", "connected": False, "checkpoints": []},
        "voice_edge_tts": {"status": "unknown"},
        "voice_kokoro": {"status": "unknown"},
        "voice_piper": {"status": "unknown"},
        "whisper": {"status": "unknown"}
    }

    # FFmpeg test
    try:
        ffmpeg_bin = settings.get_ffmpeg_path()
        p = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True)
        if p.returncode == 0:
            results["ffmpeg"] = {"status": "passed", "version": p.stdout.split("\n")[0][:40], "libass": "--enable-libass" in p.stdout}
        else:
            results["ffmpeg"] = {"status": "failed", "error": "Non-zero exit code"}
    except Exception as e:
        results["ffmpeg"] = {"status": "failed", "error": str(e)}

    # Google Gemini test
    gemini_key = settings.GEMINI_API_KEY.strip()
    if not gemini_key:
        results["gemini"] = {"status": "not_configured", "connected": False, "message": "No GEMINI_API_KEY set"}
    else:
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                r = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}?key={gemini_key}"
                )
                if r.status_code == 200:
                    results["gemini"] = {"status": "passed", "connected": True, "model": settings.GEMINI_MODEL}
                elif r.status_code in [400, 404]:
                    r_fb = await client.get(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash?key={gemini_key}"
                    )
                    if r_fb.status_code == 200:
                        results["gemini"] = {"status": "passed", "connected": True, "model": "gemini-3.5-flash"}
                    else:
                        results["gemini"] = {"status": "failed", "connected": False, "code": r.status_code, "error": r.text[:120]}
                else:
                    results["gemini"] = {"status": "failed", "connected": False, "code": r.status_code, "error": r.text[:120]}
        except Exception as e:
            results["gemini"] = {"status": "failed", "connected": False, "error": str(e)}

    # CUDA test
    try:
        if torch is not None and torch.cuda.is_available():
            results["cuda"] = {"status": "passed", "gpu": torch.cuda.get_device_name(0), "vram_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)}
        else:
            results["cuda"] = {"status": "not_available", "gpu": "CPU mode"}
    except Exception as e:
        results["cuda"] = {"status": "failed", "error": str(e)}

    # Ollama test
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name") for m in data.get("models", [])]
                results["ollama"] = {"status": "passed", "connected": True, "models": models}
            else:
                results["ollama"] = {"status": "failed", "connected": False, "code": r.status_code}
    except Exception:
        results["ollama"] = {"status": "offline", "connected": False, "message": "Ollama service offline on port 11434"}

    # ComfyUI test
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get("http://localhost:8188/system_stats")
            if r.status_code == 200:
                results["comfyui"] = {"status": "passed", "connected": True}
            else:
                results["comfyui"] = {"status": "offline", "connected": False}
    except Exception:
        results["comfyui"] = {"status": "offline", "connected": False, "message": "ComfyUI service offline on port 8188"}

    # Edge TTS test
    try:
        import edge_tts
        results["voice_edge_tts"] = {"status": "passed", "message": "EdgeTTS module loaded"}
    except ImportError:
        results["voice_edge_tts"] = {"status": "not_installed"}

    # Kokoro test
    try:
        import kokoro
        results["voice_kokoro"] = {"status": "passed", "message": "Kokoro module loaded"}
    except ImportError:
        results["voice_kokoro"] = {"status": "not_installed"}

    # Piper test
    try:
        import piper
        results["voice_piper"] = {"status": "passed", "message": "Piper module loaded"}
    except ImportError:
        results["voice_piper"] = {"status": "not_installed"}

    # Whisper test
    try:
        import faster_whisper
        results["whisper"] = {"status": "passed", "flavor": "faster-whisper"}
    except ImportError:
        try:
            import whisper
            results["whisper"] = {"status": "passed", "flavor": "openai-whisper"}
        except ImportError:
            results["whisper"] = {"status": "not_installed"}

    return results
