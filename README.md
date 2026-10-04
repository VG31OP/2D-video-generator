# 🎬 ToonForge — Autonomous AI Cartoon YouTube Shorts Generator

> **Title in → Finished YouTube Short out.**  
> Create viral 9:16 vertical animated 2D cartoon shorts with consistent characters, neural voice acting, dynamic subtitles, SFX, music ducking, and auto-editing with zero manual work.

---

## 🌟 Key Features

- **🚀 100% Autonomous Pipeline**: Enter a topic like *"A lazy student accidentally creates an AI that becomes smarter than him"* and click **Generate Short**. The system creates the entire video from scratch to MP4.
- **📖 AI Story & Hook Generator**: YouTube Shorts optimized structure (0–3s viral hook, setup, comedic escalation, punchline/plot twist, and CTA).
- **🎭 Character Bible & Consistency Lock**: Defines persistent characters with fixed palettes, outfits, hairstyles, and multi-expression rigs (happy, shocked, talking open/closed, smug).
- **🎨 2D Cartoon Visual Engine**: High-contrast, vibrant 1080x1920 compositions (bedrooms, tech labs, classrooms, cafes, chaotic dimensions) with multi-layer character sprites and comedic props.
- **🗣️ Neural Multi-Voice Speech (TTS)**: Casts distinct voice personalities (Protagonist, Robot AI, Sarcastic sidekick, Cat, Narrator) with accurate word boundaries and timestamps.
- **✨ Shorts-Style ASS Subtitles**: Large high-contrast animated subtitles with word highlight animations and safe margin positioning for YouTube's mobile interface.
- **🔊 SFX & Background Music Mix**: Automatic sound effect placement (*whoosh, vine boom, record scratch, ding, comedic pop*) and royalty-free BGM with sidechain ducking during speech.
- **🎥 2D Motion-Comic Rendering Engine**: Ken Burns camera zooms, horizontal pans, impact shakes, smooth cuts, and transitions encoded to 1080x1920 60fps/30fps H.264 MP4 with FFmpeg.
- **🖼️ Auto Thumbnail & YouTube Metadata**: High-CTR thumbnail with speed rays and title banners + optimized YouTube Shorts Title, Description, and Hashtags (`#shorts #cartoon #animation #funny #ai`).
- **💻 Open-Source & Local AI First**: Seamless support for local Ollama models (`llama3.2`, `mistral`, `qwen2.5`) with built-in zero-dependency fallbacks so the app runs out-of-the-box.

---

## 🏗️ Architecture & Workflow

```text
User enters title
        ↓
Generate Short
        ↓
AI creates story & viral hook (0-3s)
        ↓
AI writes engaging script & dialogue
        ↓
AI creates persistent Character Bible
        ↓
AI renders character expression rigs
        ↓
AI generates 2D cartoon backgrounds
        ↓
AI synthesizes multi-character neural voice
        ↓
AI aligns word-level timestamps & subtitles
        ↓
AI positions sound effects (whoosh, boom, pop)
        ↓
AI generates background music with speech ducking
        ↓
AI renders 2D motion camera moves (pan/zoom/shake)
        ↓
FFmpeg compiles final 1080x1920 MP4
        ↓
AI designs YouTube Shorts thumbnail & metadata
        ↓
Final Short Ready for Download & Preview!
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11, 3.12, 3.14)
- **Node.js 18+** & **npm**
- **FFmpeg** installed and added to system `PATH` (Run `ffmpeg -version` to verify)

### 2. Install Dependencies

```bash
# Install root & frontend dependencies
cd "e:\Project\ai video auto"
npm install --prefix apps/web

# Install Python backend dependencies
python -m pip install fastapi uvicorn websockets pydantic sqlalchemy aiosqlite pillow edge-tts httpx python-dotenv
```

### 3. Start Development Servers

**Option A: Start both frontend and backend concurrently:**

In Terminal 1 (Backend API on `http://localhost:8000`):
```bash
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

In Terminal 2 (Web Frontend on `http://localhost:5173`):
```bash
npm --prefix apps/web run dev
```

Open your browser to:
👉 **`http://localhost:5173`**

---

## ⚙️ AI Provider Options

### 1. LLM (Story, Script, Characters)
- **Local Ollama**: Install Ollama (`https://ollama.com`) and run:
  ```bash
  ollama run llama3.2
  ```
  Set `OLLAMA_BASE_URL=http://localhost:11434` in Settings.
- **Smart Cartoon Engine (Built-in)**: If Ollama is not running, ToonForge automatically uses its built-in cartoon script & storyboard engine with zero downtime.

### 2. Voice (Speech Dialogue)
- **EdgeTTS (Default)**: Free neural multi-voice synthesis in English, Hindi, Hinglish, etc.
- **Offline Harmonic Synth**: Built-in procedural vocal synthesizer when offline.

### 3. Visuals & Rendering
- **ToonVector Visual Engine (Default)**: Generates 1080x1920 2D cartoon scenes, backgrounds, character expression rigs, and motion layers using PIL/FFmpeg.
- **ComfyUI / Local SD**: Configurable via the settings tab.

---

## 📁 Monorepo Structure

```text
toonforge/
├── apps/
│   ├── web/                     # React + TypeScript + Vite + Tailwind CSS Frontend
│   │   ├── src/
│   │   │   ├── components/      # VideoPlayer, CharacterBibleViewer, SceneStoryboard, etc.
│   │   │   ├── pages/           # Dashboard, CreateShort, GenerateProgress, Result, Settings
│   │   │   ├── services/        # API client & WebSocket subscription hook
│   │   │   └── types/           # TypeScript data interfaces
│   │   └── package.json
│   │
│   └── api/                     # FastAPI Backend & Orchestration Pipeline
│       ├── main.py              # App entry & WebSocket router
│       ├── config.py            # App settings & storage paths
│       ├── database.py          # SQLite Async SQLAlchemy engine
│       ├── models/              # Project, Character, Scene, GenerationJob models
│       ├── routes/              # /api/projects, /api/settings
│       ├── services/            # Pipeline, AudioService, VideoService, SubtitleService, QC
│       └── providers/           # LLMProvider, VoiceProvider, VisualProvider, SFX, Music
│
├── storage/
│   └── projects/                # Organized generated assets per short project
│
├── .env.example
├── README.md
└── package.json
```

---

## 📄 License
MIT License © 2026 ToonForge Team.
