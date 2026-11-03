"""
Build 1999 vs 2026 Stick Figure Reel
====================================
End-to-end production of the /stick-figure reel:
"The Internet in 1999 vs 2026"
- 9 Shots, 43.15s duration, 1080x1920 30fps
- Procedural Butterworth audio (modem screech, phone ring, robot bleeps, pluck score)
- Playwright Chromium headless canvas rendering
- Broadcast loudness normalized final MP4
"""

import os
import sys
import subprocess
from pathlib import Path

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

REEL_DIR = ROOT_DIR / "storage" / "reels" / "stick_figure_1999_vs_2026"


def main():
    print("=" * 70)
    print("  🎬 PRODUCING STICK-FIGURE REEL: The Internet in 1999 vs 2026")
    print("  Style    : Hand-Drawn Animated Stick Figures with Procedural Audio")
    print("  Canvas   : 1080x1920 (9:16 Vertical, 30fps)")
    print("  Duration : ~43.15 seconds (9 Shots)")
    print("=" * 70)

    # 1. Synthesize Procedural Audio Mix
    print("\n[+] Synthesizing procedural audio mix (audio.py)...")
    res_audio = subprocess.run([PYTHON_BIN, "audio.py"], cwd=str(REEL_DIR), capture_output=True, text=True)
    if res_audio.returncode != 0:
        print(f"[✗] Audio synthesis failed: {res_audio.stderr}")
        sys.exit(1)
    print("    [✓] Procedural audio ready: audio/mix.wav")

    # 2. Render Canvas Frames via Playwright Chromium
    print("\n[+] Rendering 1080x1920 30fps frames via Playwright Chromium...")
    env = os.environ.copy()
    env["NODE_PATH"] = str(NODE_MODULES)
    env["CHROME"] = CHROME_PATH

    render_script = STICK_ENGINE / "tools" / "render.js"
    silent_mp4 = REEL_DIR / "silent.mp4"

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

    proc.wait()
    if proc.returncode != 0 or not silent_mp4.exists():
        print("[✗] Frame rendering failed!")
        sys.exit(1)

    print(f"    [✓] Visual frames rendered: silent.mp4 ({silent_mp4.stat().st_size / 1024 / 1024:.2f} MB)")

    # 3. Final Mux with Broadcast Loudness Normalization
    print("\n[+] Muxing audio & video into broadcast-ready reel...")
    final_mp4 = REEL_DIR / "stick_figure_1999_vs_2026_final.mp4"
    mix_wav = REEL_DIR / "audio" / "mix.wav"

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

    # 4. Extract Cover Poster Frame (at 23.5s - AR glasses sparkle)
    cover_jpg = REEL_DIR / "cover.jpg"
    cmd_thumb = [
        "ffmpeg", "-y", "-ss", "00:00:23.500",
        "-i", str(final_mp4),
        "-vframes", "1", "-q:v", "2",
        str(cover_jpg)
    ]
    subprocess.run(cmd_thumb, capture_output=True)

    size_mb = final_mp4.stat().st_size / (1024 * 1024)
    print("\n" + "*" * 70)
    print("  🎉 REEL PRODUCTION COMPLETE: 1999 vs 2026! 🎉")
    print(f"  File     : {final_mp4.name}")
    print(f"  Size     : {size_mb:.2f} MB")
    print(f"  Duration : ~43.15 seconds")
    print(f"  Path     : {final_mp4}")
    print(f"  Cover    : {cover_jpg}")
    print("*" * 70 + "\n")
    return str(final_mp4)


if __name__ == "__main__":
    main()

