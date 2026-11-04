#!/usr/bin/env python3
"""
ToonForge / VRJ.AI — One-Click Environment Setup Script
Automates dependency installation, browser binaries, storage initialization, and verification.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def check_python_version():
    print("[1/7] Checking Python version...")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        print(f"  [✗] Error: Python 3.10+ required. You are running Python {v.major}.{v.minor}.{v.micro}")
        sys.exit(1)
    print(f"  [✓] Python {v.major}.{v.minor}.{v.micro} verified.")


def install_python_deps():
    print("\n[2/7] Installing Python dependencies (requirements.txt)...")
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        print("  [✗] requirements.txt not found!")
        sys.exit(1)
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(req_file)]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("  [✗] Failed to install Python dependencies.")
        sys.exit(1)
    print("  [✓] Python dependencies installed successfully.")


def install_playwright_browsers():
    print("\n[3/7] Installing Playwright Chromium browser...")
    cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("  [!] Warning: Playwright browser install reported an issue. WebGL rendering will attempt system Chrome.")
    else:
        print("  [✓] Playwright Chromium ready.")


def install_node_deps():
    print("\n[4/7] Checking Node.js and installing npm packages...")
    npm_path = shutil.which("npm")
    if not npm_path:
        print("  [!] Warning: npm/node not found in PATH.")
        print("      Please install Node.js (https://nodejs.org) to build the React frontend and render 3D scenes.")
        return

    # 1. Frontend Web App
    web_dir = ROOT_DIR / "apps" / "web"
    if web_dir.exists() and (web_dir / "package.json").exists():
        if not (web_dir / "node_modules").exists():
            print("  - Installing frontend packages (apps/web)...")
            subprocess.run([npm_path, "install", "--no-audit", "--no-fund"], cwd=str(web_dir), check=False)
        else:
            print("  [✓] apps/web dependencies already present.")

    # 2. 3D Engine Template
    engine_dir = ROOT_DIR / "templates" / "zach_engine"
    if engine_dir.exists() and (engine_dir / "package.json").exists():
        if not (engine_dir / "node_modules").exists():
            print("  - Installing 3D engine packages (templates/zach_engine)...")
            subprocess.run([npm_path, "install", "--no-audit", "--no-fund"], cwd=str(engine_dir), check=False)
        else:
            print("  [✓] 3D engine dependencies already present.")


def check_ffmpeg():
    print("\n[5/7] Checking FFmpeg installation...")
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        print(f"  [✓] FFmpeg detected in PATH: {ffmpeg_bin}")
    else:
        # Check imageio_ffmpeg fallback
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and Path(exe).exists():
                print(f"  [✓] FFmpeg auto-resolved via imageio_ffmpeg: {exe}")
                return
        except Exception:
            pass
        print("  [!] Warning: ffmpeg not detected.")
        if sys.platform == "win32":
            print("      Install via Windows Terminal: winget install Gyan.FFmpeg")
        elif sys.platform == "darwin":
            print("      Install via Homebrew: brew install ffmpeg")
        else:
            print("      Install via package manager: sudo apt update && sudo apt install ffmpeg")


def initialize_storage_and_env():
    print("\n[6/7] Initializing storage directories & environment configuration...")
    dirs = [
        ROOT_DIR / "storage",
        ROOT_DIR / "storage" / "projects",
        ROOT_DIR / "storage" / "drafts",
        ROOT_DIR / "storage" / "reels",
        ROOT_DIR / "storage" / "assets",
        ROOT_DIR / "storage" / "assets" / "sfx",
        ROOT_DIR / "storage" / "models",
        ROOT_DIR / "storage" / "temp",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  [✓] Storage directory tree verified.")

    # Copy .env.example -> .env if .env doesn't exist
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        shutil.copy2(env_example, env_file)
        print("  [✓] Generated default .env file from .env.example.")
    else:
        print("  [✓] .env file is present.")


def verify_models():
    print("\n[7/7] Verifying voice synthesis models...")
    models_dir = ROOT_DIR / "storage" / "models"
    onnx = models_dir / "kokoro-v1.0.onnx"
    bin_f = models_dir / "voices-v1.0.bin"

    home_models = Path.home() / ".gemini" / "config" / "skills" / "animation-kit" / "models"
    if not onnx.exists() and home_models.exists() and (home_models / "kokoro-v1.0.onnx").exists():
        print("  - Linking Kokoro ONNX model from local cache...")
        try:
            shutil.copy2(home_models / "kokoro-v1.0.onnx", onnx)
            shutil.copy2(home_models / "voices-v1.0.bin", bin_f)
        except Exception:
            pass

    if onnx.exists() and bin_f.exists():
        print(f"  [✓] Kokoro ONNX model ready ({onnx.stat().st_size / (1024*1024):.1f} MB).")
    else:
        print("  [i] Kokoro ONNX model is optional. Edge-TTS neural voice operates out-of-the-box with zero downloads!")


def main():
    print("=" * 70)
    print("      🚀 TOONFORGE / VRJ.AI — AUTOMATED ENVIRONMENT SETUP      ")
    print("=" * 70)

    check_python_version()
    install_python_deps()
    install_playwright_browsers()
    install_node_deps()
    check_ffmpeg()
    initialize_storage_and_env()
    verify_models()

    print("\n" + "=" * 70)
    print("                   🎉 SETUP COMPLETE! 🎉                   ")
    print("=" * 70)
    print(" You are all set! You can now run:\n")
    print("  1. Generate a 3D Zack D. Explainer Reel:")
    print("     python scripts/create_and_publish_zach_reel.py \"How Solar Panels Work\"\n")
    print("  2. Connect Instagram Account:")
    print("     python scripts/instagram_manager.py login\n")
    print("  3. Check Instagram Profile & Stats:")
    print("     python scripts/instagram_manager.py status\n")
    print("  4. Launch Full Web Dashboard & API:")
    print("     npm run dev:web   (Frontend at http://localhost:5173)")
    print("     npm run dev:api   (Backend API at http://localhost:8000)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
