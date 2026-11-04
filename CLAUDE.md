# CLAUDE.md — Agent & Developer Guide

Autonomous 3D Zack D. Films Explainer Generator & Instagram Reels Auto-Publisher.
Designed for instant cloning and execution by humans or AI coding assistants (Claude Code, Antigravity, Cursor, Codex).

---

## ⚡ Quickstart Commands

```bash
# 1. One-click setup (installs python deps, Playwright browser, Three.js template)
python setup.py
# (On Windows: setup.bat | On macOS/Linux: ./setup.sh)

# 2. Generate 3D Zack D. Explainer Reel locally (No publish)
python main.py "How Solar Panels Actually Work" --no-publish

# 3. Generate and publish directly to your connected Instagram account with auto-boost
python main.py "Why We Dream When Sleeping" --publish

# 4. Connect or switch your Instagram account anytime
python main.py --login

# 4. Save video and metadata to storage/drafts/
python main.py "How Touchscreens Detect Your Fingers" --draft

# 5. Check Instagram authentication status & profile metrics
python main.py --status
```

---

## 🏛️ Project Architecture

```
├── main.py                     # Root CLI entrypoint (topic -> render -> publish)
├── setup.py                    # Automated cross-platform environment installer
├── setup.bat / setup.sh        # OS one-click setup scripts
├── requirements.txt            # Pinned Python dependencies
│
├── core/                       # Core Autonomous Engine
│   ├── config.py               # Dynamic model, browser, FFmpeg, and path discovery
│   ├── script_engine.py        # 8-sentence viral formula (Hook -> Misconception -> Twist -> 4-Step -> Payoff)
│   ├── voice_engine.py         # Neural TTS (Kokoro ONNX am_michael 1.12x + Edge-TTS fallback) + word timestamps
│   ├── scene_builder.py        # Three.js 3D WebGL scene generator with zoomed-out camera framing
│   ├── renderer.py             # Playwright Chromium WebGL capture + FFmpeg EBU R128 1080x1920 muxer
│   ├── instagram.py            # Instagrapi client: interactive/saved login, Reel upload, and auto-boost
│   ├── pipeline.py             # Master orchestrator class connecting all stages
│   └── __init__.py             # Clean module exports
│
├── templates/zach_engine/      # Self-contained Three.js WebGL template
│   ├── render.mjs              # Playwright headless WebGL frame capturer
│   ├── index.html              # WebGL rendering canvas
│   └── src/                    # Procedural shaders, human rig, materials, camera easing
│
├── scripts/                    # Reusable system tools & analytics
│   ├── create_and_publish_zach_reel.py  # Standalone CLI wrapper
│   ├── instagram_manager.py             # Instagram CLI (status, upload, comments, story)
│   ├── profile_analytics.py             # Performance & viewer analytics
│   └── publish_draft.py                 # Publish existing drafts
│
└── storage/                    # Local runtime storage (ALL git-ignored)
    ├── reels/                  # Generated video projects (storage/reels/zach_<slug>/)
    ├── drafts/                 # Stored drafts
    └── models/                 # Neural TTS weights (kokoro-v1.0.onnx)
```

---

## 📐 Zack D. Films 3D Explainer Standards

Every generated video strictly adheres to these broadcast principles:

1. **8-Sentence Script Structure**:
   - Shot 1: Scenario / Hook
   - Shot 2: Common Misconception
   - Shot 3: "But" Twist (with dip to black)
   - Shots 4–7: 4-Step Physical/Microscopic Mechanism Breakdown
   - Shot 8: Surprise / Comedic Payoff

2. **Camera Framing & Pullback (Mandatory)**:
   - Always maintain comfortable **zoomed-out framing (FOV 42°–45°, pullback distance Z=1.6m–2.4m)**.
   - Prevents character shoulders, hands, or props from getting cropped by the narrow 9:16 vertical edges.
   - Camera movements must use Apple Fluid physics easing (`anim.js` cubic hermite / smoothstep).

3. **Audio & Loudness**:
   - Neural voice: Kokoro `am_michael` at 1.12x speed (or Edge-TTS fallback).
   - EBU R128 loudness normalization (`loudnorm=I=-14:TP=-1.5:LRA=9`).
   - 48 kHz AAC audio.

4. **Subtitles**:
   - Word-level bounce kinetic captions (1 to 3 words per flash).
   - Safe margin: Keep text safely above the bottom 440px Instagram UI zone (`MarginV = 440`).

---

## 🔒 Security & Git Hygiene Rules

1. **Zero Media in Git**: Never commit `.mp4`, `.wav`, `.png`, `.jpg`, `.onnx`, `.bin`, `.db`, or `.json` session files to Git. All media belongs in `storage/` and is strictly ignored via `.gitignore`.
2. **No Per-Video Scripts in Git**: Never create or commit one-off generator scripts into `scripts/` (e.g., `run_topic_pipeline.py`). Use `main.py "<Topic>"` or the generic CLI.
3. **Windows Encoding**: Always wrap console output with `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.

