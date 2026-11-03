"""
Build Stick Figure Reel
=======================
Autonomous renderer and builder for the /stick-figure animation skill on Windows.
- Synthesizes procedural audio (music + whooshes + clangs + footsteps) via audio.py
- Uses Playwright Chromium headless canvas rendering via tools/render.js
- Concatenates and muxes with FFmpeg at 1080x1920 30fps with Instagram safe areas.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = Path(r"C:\Users\ROHITBHAI\.gemini\config\skills")
STICK_ENGINE = SKILLS_DIR / "stick-figure" / "engine"
KIT_DIR = SKILLS_DIR / "animation-kit"
NODE_MODULES = KIT_DIR / "node_modules"
CHROME_PATH = r"C:\Users\ROHITBHAI\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe"
PYTHON_BIN = sys.executable

REEL_DIR = ROOT_DIR / "storage" / "reels" / "stick_figure_pirate"


def build():
    print("=" * 70)
    print("  🎨 CODE-ANIMATED STICK-FIGURE REEL BUILDER (/stick-figure)")
    print("  Visuals : 1080x1920 (9:16 Vertical), Hand-Drawn Cartoon Canvas")
    print("  Sound   : Procedural SFX & Ducked Underscore Synthesized in Code")
    print("=" * 70)

    # 1. Prepare Target Directory
    if REEL_DIR.exists():
        print(f"[+] Reusing existing folder: {REEL_DIR}")
    else:
        print(f"[+] Copying engine template to: {REEL_DIR}")
        REEL_DIR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(STICK_ENGINE / "template", REEL_DIR)

    # Ensure audio setup
    audio_dir = REEL_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    vo_file = audio_dir / "vo.wav"
    vo_kokoro = audio_dir / "vo_kokoro.wav"
    if not vo_file.exists() and vo_kokoro.exists():
        shutil.copy(vo_kokoro, vo_file)

    # 2. Procedural Audio Synthesis (Music + SFX)
    print("\n[+] Synthesizing procedural music & sound effects (audio.py)...")
    res_audio = subprocess.run(
        [PYTHON_BIN, "audio.py"],
        cwd=str(REEL_DIR),
        capture_output=True,
        text=True
    )
    if res_audio.returncode != 0:
        print(f"[✗] audio.py failed: {res_audio.stderr}")
        sys.exit(1)
    print(f"    - {res_audio.stdout.strip()}")
    print("    [✓] Generated: audio/mix.wav")

    # 3. Render Visual Frames with Playwright Chromium
    print("\n[+] Rendering 1080x1920 30fps canvas frames via Playwright Chromium...")
    env = os.environ.copy()
    env["NODE_PATH"] = str(NODE_MODULES)
    env["CHROME"] = CHROME_PATH

    render_script = STICK_ENGINE / "tools" / "render.js"
    silent_mp4 = REEL_DIR / "silent.mp4"

    # Single-pass high-fidelity render directly into silent.mp4
    cmd_render = ["node", str(render_script), "video", "silent.mp4"]
    proc = subprocess.Popen(
        cmd_render,
        cwd=str(REEL_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in proc.stdout:
        line_str = line.strip()
        if "frame" in line_str or "done" in line_str:
            print(f"    - {line_str}")
        elif line_str:
            pass

    proc.wait()
    if proc.returncode != 0 or not silent_mp4.exists():
        print("[✗] Render failed! Check log above.")
        sys.exit(1)

    print(f"    [✓] Visuals rendered: {silent_mp4.name} ({silent_mp4.stat().st_size / 1024 / 1024:.2f} MB)")

    # 4. Final Mux with FFmpeg (Audio Normalization & Metadata)
    print("\n[+] Muxing audio & video with broadcast loudness normalization...")
    final_mp4 = REEL_DIR / "stick_figure_pirate_final.mp4"
    mix_wav = audio_dir / "mix.wav"

    cmd_mux = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(silent_mp4),
        "-i", str(mix_wav),
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "copy",
        "-af", "alimiter=limit=0.8:attack=2:release=60,loudnorm=I=-14:TP=-1.5:LRA=9",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(final_mp4)
    ]

    subprocess.run(cmd_mux, check=True)
    size_mb = final_mp4.stat().st_size / (1024 * 1024)
    print("*" * 70)
    print("  🎉 STICK-FIGURE REEL SUCCESSFULLY PRODUCED! 🎉")
    print(f"  File     : {final_mp4.name}")
    print(f"  Size     : {size_mb:.2f} MB")
    print(f"  Duration : ~37.4 seconds")
    print(f"  Path     : {final_mp4}")
    print("*" * 70 + "\n")
    return str(final_mp4)


if __name__ == "__main__":
    build()

