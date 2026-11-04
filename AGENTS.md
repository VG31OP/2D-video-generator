# AGENTS.md — Developer & AI Agent Guidelines

This document provides operational context, architectural contracts, and safety rules for AI coding assistants (Claude Code, Antigravity, Cursor, Codex) and developers maintaining this repository.

---

## 🏛️ Repository Architecture

- `main.py`: Primary CLI entrypoint for generating and publishing Zack D. Films 3D explainer reels.
- `setup.py`, `setup.bat`, `setup.sh`: 1-click cross-platform environment installer (Python deps, Playwright browser, Three.js template).
- `core/`: Dedicated, portable engine package:
  - `config.py`: Dynamic discovery of Kokoro ONNX models, Chromium browser, FFmpeg, and paths.
  - `script_engine.py`: Viral 8-sentence Zack D. formula (Hook -> Misconception -> Twist -> 4-Step Mechanism -> Payoff).
  - `voice_engine.py`: Kokoro ONNX (`am_michael` 1.12x) with Edge-TTS auto-fallback + word timestamps.
  - `scene_builder.py`: Three.js procedural WebGL scene builder with Apple Fluid camera easing.
  - `renderer.py`: Playwright WebGL frame capture + FFmpeg EBU R128 normalization (`-14 LUFS, -1.5 dBFS TP`) + Lanczos 1080x1920 scaling + thumbnail generator.
  - `instagram.py`: Instagrapi wrapper with interactive/saved credential management, Reel upload, and auto-boost.
  - `pipeline.py`: Master orchestrator class connecting all modules.
- `templates/zach_engine/`: Bundled Three.js WebGL engine template with shaders, human rig, materials, textures, and `render.mjs`.
- `scripts/`: Reusable management CLIs and analytics (no one-off per-video scripts).
- `storage/`: Local data directory (100% ignored by git).

---

## ⚠️ Critical Development Rules

### 1. Security & Credentials
- **NEVER** commit `.env`, `instagram_session.json`, `instagram_cookies.json`, `*.db`, `*.sqlite`, `.onnx`, `.bin`, or video files to git.
- Verify `git status` before committing any code changes.
- All session and media files must remain in `storage/` and are strictly ignored via `.gitignore`.

### 2. Windows Platform Specifics
- **Python Unicode Output**: Always configure console output using `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`. Never use fragile detached buffer wrappers.
- **FFmpeg PATH**: Dynamically resolved via `core.config.get_ffmpeg_path()`.

### 3. Motion & Camera Framing Standards
- **Framing (Mandatory)**: Always maintain comfortable **zoomed-out framing (FOV 42°–45°, pullback distance Z=1.6m–2.4m)** to prevent character shoulders, hands, or props from getting cropped by the narrow 9:16 vertical edges.
- All camera movements should use physics-based easing curves (Apple Fluid / Emil Kowalski design principles):
  - Cubic Hermite S-Curves (`3\tau^2 - 2\tau^3`) for camera pans and pushes.
  - Damped Harmonic Oscillators for snap/shock reveals.
  - Never introduce jarring, un-eased linear zooms.

### 4. Audio & Subtitles
- Audio: 48 kHz AAC stereo, normalized to EBU R128 standard (`loudnorm=I=-14:TP=-1.5:LRA=9`).
- Subtitles: 1-to-3 word kinetic captions kept safely above the bottom 440px Instagram UI zone (`MarginV = 440`).

### 5. Clean Repository & No Per-Video Scripts in Git
- **NEVER create or commit one-off per-video generator scripts into `scripts/`** (e.g., `run_<topic>_pipeline.py`, `build_<topic>_reel.py`, etc.).
- All generation must use `python main.py "<Topic>"` or the generic CLI.
- Topic-specific working files must remain confined to `storage/reels/<topic>/` (which is git-ignored).
