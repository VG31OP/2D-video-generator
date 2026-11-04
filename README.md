<div align="center">

# 🎬 Zack D Films AI Video Generator & Instagram Auto-Publisher

**Turn any question or topic into a finished Zack D. Films-style 3D animated explainer short and publish it automatically.**

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Three.js-WebGL%203D-black?style=for-the-badge&logo=three.js" alt="Three.js WebGL">
  <img src="https://img.shields.io/badge/Playwright-Chromium%20Capture-45ba4b?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright Chromium">
  <img src="https://img.shields.io/badge/Kokoro-Neural%20TTS-FF6B6B?style=for-the-badge" alt="Kokoro Neural Voice">
  <img src="https://img.shields.io/badge/FFmpeg-EBU%20R128-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg Broadcast">
</p>
<p>
  <img src="https://img.shields.io/badge/Agent%20Native-Claude%20Code%20%C2%B7%20Antigravity%20%C2%B7%20Codex%20%C2%B7%20Cursor-d97757?style=for-the-badge" alt="Agent Native">
  <img src="https://img.shields.io/badge/Instagram-Reels%20Automation-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram Reels Automation">
  <img src="https://img.shields.io/badge/License-MIT-111111?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
</p>

</div>

---

**Zack D Films AI Video Generator** is an agent-native production pipeline for fast, curiosity-driven 3D animated explainer shorts. Give your coding agent one topic and it can plan the curiosity-loop script, build procedural Three.js 3D WebGL scenes, animate them with Apple Fluid physics, synthesize neural voice narration, align kinetic bounce captions, render a broadcast 1080x1920 MP4, and automatically publish it directly to your Instagram Reels with algorithmic engagement boost.

It runs locally with **Three.js**, **Playwright headless Chromium**, **Kokoro Neural ONNX TTS**, and **FFmpeg**, and can be operated seamlessly from **Claude Code**, **Google Antigravity**, **Cursor**, **OpenAI Codex**, or the standalone CLI.

> **Ask your agent:** *"Make me a Zack D Films-style 3D short explaining what happens when you swallow gum and publish it to my Instagram."*

---

## 📺 Live Showcases — Finished 3D Explainer Reels

The 3D explainer shorts below were generated completely in code and published autonomously using this pipeline:

| 📱 How Face ID Actually Works | 🛰️ How GPS Pinpoints Your Phone | 🎧 How Noise-Cancelling Works |
| :---: | :---: | :---: |
| [![How Face ID Actually Works](docs/showcase/face_id_showcase.jpg)](https://www.instagram.com/reel/DfURj8es72J/) | [![How GPS Pinpoints Your Phone](docs/showcase/gps_showcase.jpg)](https://www.instagram.com/reel/DfUTwgAscc8/) | [![How Noise-Cancelling Works](docs/showcase/noise_cancelling_showcase.jpg)](https://www.instagram.com/reel/DfURj8es72J/) |
| **[▶️ Watch on Instagram (40.8s)](https://www.instagram.com/reel/DfURj8es72J/)** | **[▶️ Watch on Instagram (42.2s)](https://www.instagram.com/reel/DfUTwgAscc8/)** | **[▶️ Watch on Instagram (1,470+ Views)](https://www.instagram.com/reel/DfURj8es72J/)** |
| *Dot projector mesh, infrared scan & neural flood illuminator* | *Satellite atomic clocks, 20,000km trilateration & relativity* | *Phase-inverted counter soundwaves & acoustic cancellation* |

---

## 🎥 Shot Breakdown & Curiosity Loop Architecture

Every reel follows the signature Zack D. Films 8-beat formula, combining comedic relatability, curiosity gap hooks, and microscopic science mechanisms:

```
Topic Prompt (e.g., "How Touchscreens Detect Your Fingers")
  ├─ 1. Hook / Scenario      Curiosity interrupt: relatable daily action
  ├─ 2. Misconception        "Some people think the glass just detects pressure..."
  ├─ 3. The "But" Twist      "But in reality, your finger completes an electric circuit." ◀── DIP TO BLACK
  ├─ 4. Step 1 Mechanism     Microscopic transparent indium tin oxide (ITO) grid
  ├─ 5. Step 2 Physics       Human skin capacitance altering electrostatic field
  ├─ 6. Step 3 Controller    Microcontroller measuring voltage drop at cross-points
  ├─ 7. Step 4 OS Response   Display driver mapping coordinates at 120Hz
  └─ 8. Payoff / Resolution  Surprise comedic or scientific conclusion
```

### Shot Timeline & Camera Choreography

| Shot | Story Beat | Camera Move | Physics Easing | Framing Standard |
|---|---|---|---|---|
| `shot_1` | Hook / Scenario | `push_in` (Z=1.95m) | Cubic Hermite S-Curve | Zoomed-out (FOV 43°) |
| `shot_2` | Common Misconception | `pan_left` (Z=1.70m) | Smoothstep settle | Head & shoulders visible (FOV 42°) |
| `shot_3` | The "But" Twist | `recoil_settle` | Dip-to-Black (0.2s) | Dramatic reaction pop (FOV 42°) |
| `shot_4` | Step 1 Mechanism | `pull_back` (Z=1.85m) | Damped Harmonic | Microscopic props in full view |
| `shot_5` | Step 2 Microscopic | `static_macro` (Z=1.25m)| Optical Vignette | Subsurface particle interaction |
| `shot_6` | Step 3 Force / Physics | `drift_orbit` (Z=1.75m)| Apple Fluid | Dynamic field lines & voltage drop |
| `shot_7` | Step 4 Reaction | `counter_pan` (Z=1.45m) | Smoothstep | High-speed processing feedback |
| `shot_8` | Surprise Payoff | `snap_punch` (Z=1.95m) | Harmonic Recoil | Character relief & wide studio view |

---

## ✨ Why It Works

This engine transforms a complex 3D animation and video editing pipeline into an **agent-native, single-command system**:

- **Curiosity-First Scripts** — Engineered around curiosity loops, relatable misconceptions, fast pacing, and punchy payoffs.
- **Consistent Procedural 3D Worlds** — Real-time Three.js WebGL scenes with studio lighting, ACES Filmic tone mapping, PCF soft shadow maps, Bokeh depth of field, and Unreal Bloom.
- **Comfortable Zoomed-Out Framing (Mandatory)** — Wide vertical 9:16 framing (**FOV 42°–45°, camera pullback Z=1.6m–2.4m**) ensures character arms, heads, and props are never cut off by vertical phone edges.
- **Apple Fluid Motion Physics** — Camera movements and character reactions use Cubic Hermite S-Curves (`3τ² - 2τ³`) and Damped Harmonic Oscillators (`1 - e^{-kt}\cos(\omega t)`).
- **Studio Neural Voice** — Kokoro ONNX neural speech (`am_michael` 1.12x) with sub-word phoneme alignment (with zero-download Edge-TTS auto-fallback).
- **Word-Level Kinetic Bounce Subtitles** — 1-to-3 words per flash, positioned safely above `MarginV = 440` so Instagram/TikTok UI buttons never cover text.
- **Broadcast Loudness Normalization** — FFmpeg EBU R128 loudness normalization (`-14 LUFS, -1.5 dBFS True Peak, 48kHz AAC stereo`).
- **Autonomous Instagram Reels Growth** — Direct 1080x1920 MP4 upload to **YOUR personal or brand account**, automated self-like, pinned CTA comment, and story reshare.
- **Agent-Native by Design** — Built with [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md) so Claude Code, Antigravity, Cursor, and Codex can run it autonomously.

---

## 🧩 Pipeline Technology Stack

| Production Stage | Integration / Technology | Output Asset |
|---|---|---|
| **Viral Scripting** | `core/script_engine.py` (8-Sentence Zack D. Formula + Gemini) | `script.json` (8 structured beats) |
| **Speech Synthesis** | Kokoro Neural ONNX (`am_michael` 1.12x) + Edge-TTS | `audio/vo.wav` (48kHz audio) |
| **Phoneme Timestamps** | Sub-word character duration alignment | `words.json` (millisecond accuracy) |
| **3D Procedural Scene** | Three.js WebGL + Custom GLSL Shaders + Human Rig | `src/shots.js` (WebGL timeline) |
| **Camera Mechanics** | Apple Fluid Easing (Hermite & Harmonic Physics) | Zoomed-out 9:16 framing (FOV 42°–45°) |
| **Headless Frame Capture** | Playwright Chromium (Headless GPU pipeline) | `silent.mp4` (1080x1920 30fps) |
| **Audio/Video Muxing** | FFmpeg with Lanczos scaling + EBU R128 normalization | Broadcast master `final.mp4` |
| **Cover Thumbnail** | FFmpeg high-res frame capture at t=1.2s | `cover.jpg` (1080x1920) |
| **Social Publishing** | `core/instagram.py` (Private API Client) | Live Reel URL + Story Share + Pinned Comment |

---

## 🚀 Quick Start (1-Click Setup)

Anyone can clone and run this repository in under 2 minutes:

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/VG31OP/zack-d-3d-explainer-generator.git
cd zack-d-3d-explainer-generator

# Windows (1-Click):
setup.bat

# macOS / Linux:
chmod +x setup.sh && ./setup.sh

# Or directly with Python:
python setup.py
```

### 2. Connect Your Instagram Account

```bash
# Connect YOUR Instagram account once (credentials stored locally, strictly git-ignored):
python main.py --login
```

### 3. Generate & Publish Reels

```bash
# Generate and publish directly to YOUR Instagram Reels with automated boost:
python main.py "Why We Dream When Sleeping" --publish

# Generate video locally (no Instagram upload):
python main.py "How Solar Panels Actually Work" --no-publish

# Save to local drafts vault:
python main.py "How Touchscreens Detect Your Fingers" --draft

# Check your connected Instagram account metrics:
python main.py --status
```

---

## 🤖 For AI Coding Assistants (Claude Code, Antigravity, Cursor, Codex)

This repository includes [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md) out-of-the-box. You can give your agent natural prompts:

> **"Create a Zack D. Films 3D explainer reel on How Noise-Cancelling Headphones Actually Work and publish it to my Instagram."**

The coding agent will:
1. Validate the local environment (`python setup.py`).
2. Run `python main.py "How Noise-Cancelling Headphones Actually Work" --publish`.
3. Interactively handle Instagram authentication on the first run and save it to `storage/instagram_session.json` (git-ignored).
4. Return the live Instagram Reel link.

---

## 📁 Repository Structure

```
├── main.py                     # Primary CLI entrypoint (Topic -> 3D Video -> Instagram)
├── setup.py                    # Automated cross-platform environment installer
├── setup.bat / setup.sh        # OS one-click setup scripts
├── requirements.txt            # Clean, pinned Python dependencies
├── CLAUDE.md                   # Full guidelines for Claude Code, Antigravity, and Codex
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
│   └── __init__.py             # Clean module exports
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

## 📋 CLI Options Reference

```bash
python main.py [TOPIC] [OPTIONS]
```

| Flag | Description |
| :--- | :--- |
| `topic` | Title or topic for the explainer reel (e.g., `"How OLED Screens Burn In"`). |
| `--login` | Connect or switch to your personal/brand Instagram account. |
| `--logout` | Disconnect and clear locally stored Instagram session. |
| `--publish` | Uploads directly to Instagram Reels and executes automated engagement boost. |
| `--no-publish` | Renders the master 1080x1920 MP4 locally without uploading. |
| `--draft` | Saves master MP4 and JSON metadata into `storage/drafts/` for offline review. |
| `--status` | Displays connected Instagram profile handle, follower count, and total reels. |
| `--script-file <path>` | Uses a custom 8-sentence JSON script instead of auto-generating one. |
| `--username <user>` | Instagram username for direct authentication. |
| `--password <pass>` | Instagram password for direct authentication. |
| `--session-id <id>` | Instagram `sessionid` browser cookie for direct authentication. |

---

## 🔒 Security & Git Hygiene Rules

- **Zero Media in Git**: All `.mp4`, `.wav`, `.onnx`, `.bin`, `.db`, and `.json` session files remain in `storage/` and are strictly ignored via `.gitignore`.
- **Zero One-Off Scripts**: Per-video throwaway scripts are forbidden in `scripts/`. All video generation runs through `main.py` or `core.pipeline`.
- **Cross-Platform Compatibility**: Tested and verified on Windows 11, macOS, and Linux.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free to use for personal and commercial projects.

<div align="center">

⭐ **Star this repository if it helps you generate viral 3D shorts!**

</div>
