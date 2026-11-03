"""
Build Zach D. Films Style Reel: How the Internet Actually Works
Topic: How the Internet Actually Works: A message travels through routers, cables, servers and DNS to reach another person across the planet.
Resolution: 1080x1920 (9:16 Vertical, 30fps)
Engine: Three.js WebGL procedural 3D animation (Playwright headless Chromium)
Voice: Kokoro TTS am_michael 1.12
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
REEL_DIR = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works"
NODE_MODULES = REEL_DIR / "node_modules"
CHROME_PATH = r"C:\Users\ROHITBHAI\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe"
PYTHON_BIN = sys.executable

def main():
    print("=" * 70)
    print("  🎬 PRODUCING /zach-d-films REEL: How the Internet Actually Works")
    print("  Style    : 3D Procedural Cartoon Animation (Three.js WebGL)")
    print("  Topic    : Message travels through routers, fiber cables, servers & DNS")
    print("  Canvas   : 1080x1920 (9:16 Vertical, 30fps)")
    print("  Voice    : Kokoro TTS am_michael 1.12")
    print("=" * 70)

    # 1. Synthesize Voice if not present
    vo_wav = REEL_DIR / "audio" / "vo.wav"
    if not vo_wav.exists():
        print("\n[+] Synthesizing Kokoro voiceover...")
        subprocess.run([PYTHON_BIN, "build_voice.py"], cwd=str(REEL_DIR), check=True)
    print(f"    [✓] Voiceover verified: {vo_wav.name}")

    # 2. Render 3D Video via Playwright Chromium
    print("\n[+] Rendering 3D Three.js animation via Playwright Chromium...")
    env = os.environ.copy()
    env["CHROME"] = CHROME_PATH

    silent_mp4 = REEL_DIR / "silent.mp4"
    cmd_render = ["node", "render.mjs", "video", "silent.mp4", "30"]
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
        if "frame" in line_str or "done" in line_str or "still" in line_str:
            print(f"    - {line_str}")

    proc.wait()
    if proc.returncode != 0 or not silent_mp4.exists():
        print("[✗] 3D Frame rendering failed!")
        sys.exit(1)

    print(f"    [✓] Visual frames rendered: silent.mp4 ({silent_mp4.stat().st_size / 1024 / 1024:.2f} MB)")

    # 3. Final Mux with Broadcast Loudness Normalization & 1080x1920 Scaling
    print("\n[+] Muxing audio & video into broadcast-ready 1080x1920 reel...")
    final_mp4 = REEL_DIR / "zach_how_internet_works_final.mp4"

    cmd_mux = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(silent_mp4),
        "-i", str(vo_wav),
        "-map", "0:v",
        "-map", "1:a",
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-af", "apad,loudnorm=I=-14:TP=-1.5",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(final_mp4)
    ]
    subprocess.run(cmd_mux, check=True)

    # 4. Extract High-CTR Cover Frame (at t=1.2s - Zack holding glowing message)
    cover_jpg = REEL_DIR / "cover.jpg"
    cmd_thumb = [
        "ffmpeg", "-y", "-ss", "00:00:01.200",
        "-i", str(final_mp4),
        "-vframes", "1", "-q:v", "2",
        str(cover_jpg)
    ]
    subprocess.run(cmd_thumb, capture_output=True)

    # Clean intermediate silent.mp4 to keep disk clean
    if silent_mp4.exists():
        silent_mp4.unlink(missing_ok=True)
        print("    [✓] Intermediate silent render cleaned.")

    size_mb = final_mp4.stat().st_size / (1024 * 1024)
    print("\n" + "*" * 70)
    print("  🎉 ZACK D. FILMS 3D REEL PRODUCTION COMPLETE! 🎉")
    print(f"  File     : {final_mp4.name}")
    print(f"  Size     : {size_mb:.2f} MB")
    print(f"  Duration : ~35.91 seconds (8 dynamic 3D shots)")
    print(f"  Path     : {final_mp4}")
    print(f"  Cover    : {cover_jpg}")
    print("*" * 70 + "\n")
    return str(final_mp4)

if __name__ == "__main__":
    main()

