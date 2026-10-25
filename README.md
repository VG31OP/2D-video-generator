# 🎬 ToonForge — Autonomous AI Cartoon Video Generator & Instagram Automation Suite

> **Topic in → High-Retention Animated Short out.**  
> Create viral 9:16 vertical 2D cartoon shorts with persistent characters, senior motion graphics, neural multi-voice acting, kinetic bouncing typography, dynamic SFX, sidechain ducked music, and fully autonomous Instagram publishing.

---

## 🌟 Key Features

### 🎥 Senior Motion Director Engine (20-Year Motion Designer Quality)
- **Physics-Based Camera Mechanics**: Replaced flat linear pans with **Damped Harmonic Oscillators** and **Cubic Hermite S-Curves** (`(1 - e^{-kt} \cos(\omega t))` and `3\tau^2 - 2\tau^3`) for snap-and-settle camera recoil.
- **2.5D Multiplane Parallax Depth**: Moves backgrounds at independent fractional velocity with subtle depth-of-field drift while foreground character rigs execute organic breathing and expressive reaction bobs.
- **16 Senior Camera Choreographies**: Anticipation pull-back, snap punch-ins, Steadicam organic drift, whip pans with motion-blur emulation, Dutch angles with counter-balanced panning, and decaying seismic shockwave impacts.
- **Studio Optical Vignette & Grading**: Integrated soft radial vignette (`vignette=PI/4`) to lock viewer focus onto character action, combined with studio contrast and saturation enhancement (`eq=contrast=1.05:saturation=1.08`).

### 🔤 Kinetic Typography Subtitle Engine (MrBeast / Vox Style)
- **Word-Level Spring Pop Animation**: Words pop with elastic spring physics (`{\t(0,70,\fscx120\fscy120)\t(70,160,\fscx100\fscy100)}`).
- **High-Contrast Design**: Heavy 9px pure black outline with 4px soft drop shadows and bold typography (Arial Black / Impact).
- **Vibrant Accent Palettes**: Contextual color-coded active highlights (Cyber Gold `&H002BF5FF&`, Neon Lime `&H0033FF55&`, Electric Cyan, Hot Coral, Vivid Magenta).
- **Mobile UI Safe Zone**: Positioned at `MarginV = 440` so text is never obscured by Instagram Reels or YouTube Shorts interface buttons.

### 🤖 Autonomous Instagram Reels Suite
- **Hands-Free Authentication**: Persistent session and cookie management via browser state capture (`scripts/instagram_auth.py`).
- **One-Command CLI Manager**: Comprehensive CLI (`scripts/instagram_manager.py`) to inspect profiles, upload reels, publish projects, like, comment, and share to story.
- **Autonomous Post-Reel Engagement**: Automatically likes the published reel, pins a high-converting engagement comment, and reshares the reel directly to Instagram Stories with custom stickers.
- **Draft Vault**: Dedicated draft generation and isolation (`scripts/generate_trending_draft.py`) allowing offline review before publishing.

### 🧠 Domain-Aware Narrative Engine
- **Procedural Viral Scripting**: Multi-arc story engine (`apps/api/providers/narrative_engine.py`) covering AI Tools, AI Agents, Software Development, Cybersecurity, and Universal Dynamic Arcs.
- **Zero Script Duplication**: Dynamic scene-by-scene script synthesis that guarantees unique hooks, escalating comedic conflicts, and high-CTR punchlines for any given topic.

### 🎨 10 Distinct Cartoon Visual Styles
1. **Cyberpunk Neon Animated**: Glowing cyan/magenta visors, circuit overlays, and dark grid backgrounds.
2. **Chibi / Kawaii Cute**: Sparkling anime eyes, soft pastel gradients, rosy blushes, and floating hearts.
3. **Dark Noir Detective**: High-contrast black-and-white silhouettes, rain textures, and dramatic Venetian blind shadows.
4. **Comic Book Pop Art**: Halftone Ben-Day dots, bold ink outlines, action sound effect bursts (*POW! BAM!*).
5. **Pixel Art 16-Bit Arcade**: Chunky 16-bit retro arcade sprites and scanline grids.
6. **90s Saturday Morning Retro**: Vintage pie-cut cartoon eyes and pastel Saturday morning warmth.
7. **Anime Comic Shorts**: High-speed action convergence lines and expressive anime eyes.
8. **Claymation / Stop-Motion Style**: Warm handcrafted clay borders and textured plasticine aesthetics.
9. **Doodle / Stick Figure Comedy**: Notebook paper lined backgrounds, red margins, and sketch figures.
10. **Modern 2D Cartoon**: Vector cel-shaded character designs with vibrant modern palettes.

---

## 🏗️ Architecture & Pipeline Flow

```text
User enters Topic or CLI triggers Viral Trend
                       ↓
  AI Narrative Engine (Viral Hook & Multi-Arc Dialogue)
                       ↓
  Character Bible Generation & Multi-Expression Rigs
                       ↓
  2D Scene Background & Composite Generation (10 Styles)
                       ↓
  Edge Neural Multi-Voice Speech Synthesis & Timestamps
                       ↓
  Kinetic Subtitle Synchronization (Word Spring Pop ASS)
                       ↓
  Procedural SFX & Sidechain Ducked BGM Mix
                       ↓
  Senior Motion Director Engine (16 Physics Moves & 2.5D Parallax)
                       ↓
  FFmpeg 1080x1920 30fps Video Encoding & Quality Control
                       ↓
       ┌───────────────┴───────────────┐
       ↓                               ↓
 Saved to Local Draft Vault     Instagram Reels Autonomous Suite
 (storage/drafts/...)           (Publish Reel + Pinned Comment + Story Share)
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.11, 3.12, 3.14)
- **Node.js 18+** & **npm**
- **FFmpeg** installed and accessible in `PATH` (Run `ffmpeg -version` to verify)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/VG31OP/2D-video-generator.git
cd 2D-video-generator

# Install web frontend dependencies
npm install --prefix apps/web

# Install backend dependencies
python -m pip install fastapi uvicorn websockets pydantic pydantic-settings sqlalchemy aiosqlite pillow edge-tts httpx python-dotenv instagrapi playwright
```

### 3. Environment Configuration

Copy the sample environment file:
```bash
cp .env.example .env
```

Edit `.env` (optional for local fallbacks, or add your keys):
```env
APP_ENV=development
PORT=8000
HOST=0.0.0.0
DATABASE_URL=sqlite+aiosqlite:///./storage/toonforge.db
STORAGE_PATH=./storage

# Optional: Google Gemini API Key for neural writing
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

# Optional: Local Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 4. Running the Development Servers

**Backend API (`http://localhost:8000`):**
```bash
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Web Dashboard (`http://localhost:5173`):**
```bash
npm --prefix apps/web run dev
```

---

## 📱 Instagram Automation CLI

Manage Instagram Reels directly from your terminal:

```bash
# 1. Capture Login Session (runs Playwright browser to log in safely)
python scripts/instagram_auth.py

# 2. Check Instagram Profile & Auth Status
python scripts/instagram_manager.py status

# 3. List Recent Posts & Media
python scripts/instagram_manager.py list-media --limit 10

# 4. Generate a Trending Reel & Save to Draft (Offline)
python scripts/generate_trending_draft.py

# 5. Publish Any Project or Draft to Instagram Reels
python scripts/instagram_manager.py publish-project <project_id>

# 6. Autonomous End-to-End: Generate & Publish Multiple Trending Reels
python scripts/generate_and_publish_trending_reels.py
```

---

## 🔒 Security & Privacy

- All user sessions, authentication tokens, cookies, SQLite databases (`*.db`), and generated media drafts are strictly ignored via `.gitignore`.
- No sensitive credentials or session tokens are stored in version control.
- Designed with zero-dependency local procedural fallbacks (ToonVector, Edge TTS, Procedural SFX) so the application functions out-of-the-box without requiring third-party cloud API keys.

---

## 📄 License

MIT License. Crafted with modern design engineering and physics-based motion choreography.
