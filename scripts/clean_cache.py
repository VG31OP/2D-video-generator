"""
Clean Python, Media, and Local Temporary Caches
"""

import os
import sys
import shutil
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent

def clean_pycache():
    count_dirs = 0
    count_files = 0
    for root, dirs, files in os.walk(ROOT_DIR, topdown=False):
        if "node_modules" in root or ".git" in root:
            continue
        for d in dirs:
            if d == "__pycache__":
                full_dir = Path(root) / d
                try:
                    shutil.rmtree(full_dir, ignore_errors=True)
                    count_dirs += 1
                except Exception as e:
                    print(f"Error removing {full_dir}: {e}")
        for f in files:
            if f.endswith((".pyc", ".pyo", ".pyd")):
                full_file = Path(root) / f
                try:
                    full_file.unlink(missing_ok=True)
                    count_files += 1
                except Exception as e:
                    print(f"Error removing {full_file}: {e}")
    print(f"[✓] Removed {count_dirs} __pycache__ directories and {count_files} bytecode files.")

def clean_visual_cache():
    visual_cache = ROOT_DIR / "storage" / "assets" / "visual_cache"
    if visual_cache.exists():
        shutil.rmtree(visual_cache, ignore_errors=True)
        print(f"[✓] Removed visual cache: {visual_cache}")

    keyart = ROOT_DIR / "storage" / "assets" / "creator_reel_keyart.png"
    if keyart.exists():
        keyart.unlink(missing_ok=True)
        print(f"[✓] Removed keyart cache: {keyart}")

def clean_scratch_test_media():
    scratch_dir = ROOT_DIR / "scratch"
    if scratch_dir.exists():
        # Clean subdirectories and test media
        removed_items = 0
        for item in scratch_dir.iterdir():
            if item.name.startswith("test_") and item.suffix in [".py"]:
                continue # keep test scripts
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
                removed_items += 1
            elif item.suffix in [".png", ".jpg", ".mp4", ".wav", ".ass"]:
                item.unlink(missing_ok=True)
                removed_items += 1
        print(f"[✓] Cleaned {removed_items} scratch test media folders/files in {scratch_dir}")

def clean_intermediate_reel_renders():
    # Remove silent.mp4 intermediate render files
    reels_dir = ROOT_DIR / "storage" / "reels"
    count = 0
    if reels_dir.exists():
        for silent in reels_dir.rglob("silent.mp4"):
            try:
                silent.unlink(missing_ok=True)
                count += 1
                print(f"[✓] Removed intermediate silent render: {silent.name}")
            except Exception as e:
                print(f"Error removing {silent}: {e}")
    print(f"[✓] Cleaned {count} intermediate video render passes.")

def clean_temp_storage():
    temp_dir = ROOT_DIR / "storage" / "temp"
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
        print(f"[✓] Emptied temporary storage: {temp_dir}")

if __name__ == "__main__":
    print("=" * 60)
    print("      CLEANING LOCAL CACHES & TEMPORARY MEDIA FILES      ")
    print("=" * 60)
    clean_pycache()
    clean_visual_cache()
    clean_scratch_test_media()
    clean_intermediate_reel_renders()
    clean_temp_storage()
    print("=" * 60)
    print("               CACHE CLEANUP COMPLETE!               ")
    print("=" * 60)
