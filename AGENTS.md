# AGENTS.md — Developer & AI Agent Guidelines

This document provides operational context, architectural contracts, and safety rules for AI coding assistants and developers maintaining the **ToonForge** codebase.

---

## 🏛️ Repository Architecture

- `apps/api/`: FastAPI asynchronous backend service.
  - `apps/api/config.py`: Pydantic settings, platform-specific FFmpeg PATH resolution.
  - `apps/api/database.py`: Async SQLAlchemy session factory and SQLite connection (`storage/toonforge.db`).
  - `apps/api/models/schema.py`: Database models (`Project`, `Character`, `Scene`, `GenerationJob`).
  - `apps/api/providers/`: Pluggable AI engine providers:
    - `animation_provider.py`: `SeniorMotionDirectorEngine` (16 physics-based camera moves, multiplane 2.5D parallax, damped harmonic recoil).
    - `narrative_engine.py`: Domain-aware viral script generators (AI Tools, AI Agents, Dev, Security).
    - `visual_provider.py`: `ToonVectorVisualProvider` (10 distinct art styles) & `ComfyUIVisualProvider`.
    - `voice_provider.py`: `EdgeTTSVoiceProvider` neural speech synthesis with word timestamps.
    - `sfx_provider.py` & `music_provider.py`: Procedural sound and mood-adaptive ducked BGM.
  - `apps/api/services/`:
    - `pipeline.py`: `GenerationPipeline` orchestrating the 7-step autonomous short generation.
    - `subtitle_service.py`: `SubtitleService` producing word-level spring pop ASS subtitles.
    - `video_service.py`: `VideoService` handling clip concatenation and subtitle burn-in.
    - `instagram_service.py`: `InstagramService` managing private Instagram API uploads, session reuse, and post-reel engagement.
- `apps/web/`: React + TypeScript + Vite frontend dashboard.
  - `apps/web/src/pages/`: `CreateShortPage`, `ResultPage`, `SettingsPage`.
  - `apps/web/src/services/api.ts`: API client connecting to backend endpoints.
- `scripts/`: Standalone automation scripts:
  - `scripts/instagram_auth.py`: Playwright browser session capture.
  - `scripts/instagram_manager.py`: Instagram CLI for status, uploads, comments, and story sharing.
  - `scripts/generate_and_publish_trending_reels.py`: Autonomous multi-reel generator & Instagram publisher.
  - `scripts/generate_trending_draft.py`: Offline trending reel generator saving directly to draft.
- `storage/`: Local data directory (ignored by git, except static assets).

---

## ⚠️ Critical Development Rules

### 1. Security & Credentials
- **NEVER** commit `.env`, `instagram_session.json`, `instagram_cookies.json`, `instagram_browser_state.json`, `*.db`, `*.sqlite`, or draft video files to git.
- Verify `git status` before committing any code changes.
- All session files must remain in `storage/` and are strictly ignored via `.gitignore`.

### 2. Windows Platform Specifics
- **FFmpeg PATH**: On Windows, FFmpeg is located in `apps/api/config.py` using `os.pathsep` directory splitting.
- **Python Unicode Output**: Always wrap `sys.stdout` and `sys.stderr` in `io.TextIOWrapper(encoding='utf-8')` in scripts that output emojis or special characters on Windows consoles.
- **File Paths in FFmpeg Concat**: Always convert Windows backslashes (`\`) to forward slashes (`/`) when writing `scenes_concat.txt` or subtitle file references for FFmpeg.

### 3. Motion & Animation Standards
- All camera movements should use physics-based easing curves (Apple Fluid / Emil Kowalski design principles):
  - Use Damped Harmonic Oscillators (`(1 - e^{-kt} \cos(\omega t))`) for snap/shock reveals.
  - Use Cubic Hermite S-Curves (`3\tau^2 - 2\tau^3`) for camera pans and pushes.
  - Never introduce jarring, un-eased linear zooms.
  - Multiplane parallax is favored when both background and character layers are available.

### 4. Subtitle Typography
- Subtitles must be generated using `SubtitleService` with ASS format (`v4.00+`).
- Word-level bounce must be preserved (`{\t(0,70,\fscx120\fscy120)\t(70,160,\fscx100\fscy100)}`).
- Keep safe margin `MarginV = 440` to avoid being blocked by Instagram/TikTok UI controls.

### 5. Running Tests & Scripts
- Use Python 3.12: `& "C:\Users\ROHITBHAI\AppData\Local\Programs\Python\Python312\python.exe" <script_path>`
- Always ensure `sys.path.insert(0, ".")` or `PYTHONPATH=.` is set when running standalone scripts.
