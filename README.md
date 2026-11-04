# 🎬 Zack D. Films 3D Explainer & Autonomous Instagram Reels Suite

> **Topic in → Broadcast-Quality 3D Explainer Reel out.**  
> Create viral 9:16 vertical 3D procedural cartoon explainer shorts in the signature **Zack D. Films** style (Three.js WebGL, Kokoro neural voice, word timestamps, kinetic bounce captions, zoomed-out camera framing, EBU R128 loudness normalization) and automatically publish directly to Instagram Reels (`@vrj.ai`) with automated engagement boost.

---

## 🌟 Key Capabilities

### 🎬 Signature Zack D. Films 3D Explainer Formula
- **8-Sentence Viral Scripting**: Hook → Misconception → "But" Twist (with dip to black) → 4-Step Physical/Microscopic Mechanism Breakdown → Comedic/Surprise Payoff.
- **Three.js WebGL Procedural 3D Worlds**: Rendered via headless Playwright Chromium with ACES Filmic tone mapping, PCF soft shadows, Bokeh depth of field, Unreal Bloom, and film grain.
- **Comfortable Zoomed-Out 9:16 Framing (FOV 42°–45°, Pullback Z=1.6m–2.4m)**: Characters, props, and dynamic animations are never cropped or clipped by the narrow vertical 9:16 phone viewport.
- **Apple Fluid Camera Mechanics**: Physics-based Cubic Hermite S-curves and damped harmonic oscillators for natural, organic camera motion.

### 🎙️ Neural Voiceover & Kinetic Typography
- **Kokoro Neural TTS (`am_michael` 1.12x)**: Clean, studio-grade speech synthesis with automatic fallback to Edge-TTS.
- **Word-Level Kinetic Bounce Subtitles**: Fast-paced 1-to-3 word captions timed to speech phonemes.
- **Mobile Safe Margin**: All text kept safely above `MarginV = 440` so buttons and account usernames never cover the captions.
- **EBU R128 Loudness Normalization**: Master audio rendered at `-14 LUFS, -1.5 dBFS True Peak, 48kHz AAC stereo`.

### 🚀 Autonomous Instagram Auto-Publish & Growth Suite
- **Zero-Headache Authentication**: Supports saved sessions, cookies, or interactive CLI credentials prompt on first run.
- **Autonomous Reel Upload**: Direct 1080x1920 30fps upload with custom cover thumbnail extraction and viral tech/science hashtags.
- **Automated Algorithm Boost**: Automatically likes the reel, pins a high-converting CTA comment, and reshares the reel to Instagram Stories.
- **Local Draft Vault**: Save renders and metadata directly to `storage/drafts/` for offline review.

---

## ⚡ Quickstart (1-Click Setup)

Anyone (or AI coding assistants like Claude Code, Antigravity, Cursor, or Codex) can clone and run this repository immediately:

### 1. Clone & Setup
```bash
git clone https://github.com/VG31OP/2D-video-generator.git
cd 2D-video-generator

# Windows (One-Click):
setup.bat

# macOS / Linux:
chmod +x setup.sh && ./setup.sh

# Or directly with Python:
python setup.py
```

### 2. Generate Your First 3D Explainer Reel

```bash
# Generate video locally (no Instagram upload):
python main.py "How Solar Panels Actually Work" --no-publish

# Generate and publish directly to Instagram Reels (@vrj.ai):
python main.py "Why We Dream When Sleeping" --publish

# Save as draft to storage/drafts/:
python main.py "How Touchscreens Detect Your Fingers" --draft

# Check Instagram account status & follower analytics:
python main.py --status
```

---

## 🏛️ Project Architecture

```
├── main.py                     # Primary CLI entrypoint (Topic -> 3D Video -> Instagram)
├── setup.py                    # Automated cross-platform environment installer
├── setup.bat / setup.sh        # OS one-click setup scripts
├── requirements.txt            # Clean, pinned Python dependencies
├── CLAUDE.md                   # Complete guidelines for Claude Code, Antigravity, and Codex
├── AGENTS.md                   # Operational contracts, camera framing, and safety rules
│
├── core/                       # Autonomous Core Engine Package
│   ├── config.py               # Dynamic path resolution (FFmpeg, Chromium, Models)
│   ├── script_engine.py        # 8-sentence viral Zack D. formula with domain libraries
│   ├── voice_engine.py         # Kokoro ONNX + Edge-TTS fallback + word timestamps
│   ├── scene_builder.py        # Three.js 3D WebGL scene generator with zoomed-out framing
│   ├── renderer.py             # Playwright WebGL frame capture + FFmpeg EBU R128 muxer
│   ├── instagram.py            # Instagrapi client: login prompt, Reel upload, auto-boost
│   ├── pipeline.py             # Master orchestrator class connecting all modules
│   └── __init__.py             # Module exports
│
├── templates/zach_engine/      # Bundled Three.js WebGL engine template
│   ├── render.mjs              # Playwright headless WebGL frame capturer
│   ├── index.html              # WebGL canvas and shader setup
│   └── src/                    # Materials, human rig, props, camera easing curves
│
├── scripts/                    # Reusable system tools & analytics
│   ├── create_and_publish_zach_reel.py  # Standalone CLI wrapper
│   ├── instagram_manager.py             # Instagram CLI (status, upload, comments, story)
│   ├── profile_analytics.py             # Account performance & viewer analytics
│   └── publish_draft.py                 # Publish existing drafts
│
└── storage/                    # Local runtime storage (ALL git-ignored)
    ├── reels/                  # Generated video projects (storage/reels/zach_<slug>/)
    ├── drafts/                 # Stored drafts
    └── models/                 # Neural TTS weights (kokoro-v1.0.onnx)
```

---

## 📋 Command Line Reference

```
usage: main.py [-h] [--publish] [--no-publish] [--draft]
               [--script-file SCRIPT_FILE] [--username USERNAME]
               [--password PASSWORD] [--session-id SESSION_ID] [--status]
               [topic]

Autonomous 3D Zack D. Films explainer generator & Instagram publisher

positional arguments:
  topic                 Topic or question for the 3D explainer short (e.g.
                        'How Touchscreens Detect Fingers')

options:
  -h, --help            show this help message and exit
  --publish             Upload directly to Instagram Reels and execute
                        automated engagement boost
  --no-publish          Render the master 1080x1920 MP4 locally without
                        uploading to Instagram
  --draft               Save render and metadata into storage/drafts/ for
                        review
  --script-file SCRIPT_FILE
                        Path to custom 8-sentence JSON script file
  --username USERNAME   Instagram username (if not already authenticated)
  --password PASSWORD   Instagram password (if not already authenticated)
  --session-id SESSION_ID
                        Instagram sessionid cookie value
  --status              Check Instagram authentication status and profile
                        information
```

---

## 🔒 Security & Git Hygiene

- **Zero Media & Cache in Git**: All `.mp4`, `.wav`, `.onnx`, `.bin`, `.db`, and `.json` session files are stored in `storage/` and are strictly ignored via `.gitignore`.
- **Reusable Tools Only**: Per-video one-off scripts are never added to `scripts/`. All generation operates through `main.py` or `core.pipeline`.
- **Cross-Platform Compatibility**: Tested and verified on Windows 11, macOS, and Linux.
