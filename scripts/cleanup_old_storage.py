"""
Storage Cleanup Tool
Removes old completed projects, obsolete drafts, test reels, and caches.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = ROOT_DIR / "storage"


def safe_delete_folder(folder_path: Path) -> int:
    """Deletes a folder safely, unlinking any junction points first."""
    if not folder_path.exists():
        return 0

    total_bytes = 0
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            fp = Path(root) / f
            try:
                total_bytes += fp.stat().st_size
            except Exception:
                pass

    # If node_modules junction exists, unlink it first via cmd rmdir
    nm = folder_path / "node_modules"
    if nm.exists():
        try:
            subprocess.run(["cmd", "/c", "rmdir", str(nm)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    try:
        shutil.rmtree(folder_path)
    except Exception as e:
        print(f"    [!] Warning removing {folder_path.name}: {e}")

    return total_bytes


def main():
    print("=" * 65)
    print("🧹 TOONFORGE STORAGE PURGE & CLEANUP")
    print("=" * 65)

    reclaimed_bytes = 0

    # 1. Purge old storage/projects/
    projects_dir = STORAGE_DIR / "projects"
    if projects_dir.exists():
        print("[+] Purging obsolete projects in storage/projects/...")
        for item in projects_dir.iterdir():
            if item.is_dir() and item.name != ".gitkeep":
                sz = safe_delete_folder(item)
                reclaimed_bytes += sz
                print(f"    - Removed project: {item.name} ({sz / 1024 / 1024:.2f} MB)")

    # 2. Purge old storage/drafts/
    drafts_dir = STORAGE_DIR / "drafts"
    if drafts_dir.exists():
        print("[+] Purging obsolete drafts in storage/drafts/...")
        for item in drafts_dir.iterdir():
            if item.is_dir() and item.name != ".gitkeep":
                sz = safe_delete_folder(item)
                reclaimed_bytes += sz
                print(f"    - Removed draft: {item.name} ({sz / 1024 / 1024:.2f} MB)")

    # 3. Purge obsolete / test reels in storage/reels/
    reels_dir = STORAGE_DIR / "reels"
    test_reels = ["minimal_internet", "stick_figure_pirate"]
    if reels_dir.exists():
        print("[+] Purging test/unneeded reels in storage/reels/...")
        for reel_name in test_reels:
            reel_path = reels_dir / reel_name
            if reel_path.exists():
                sz = safe_delete_folder(reel_path)
                reclaimed_bytes += sz
                print(f"    - Removed test reel: {reel_name} ({sz / 1024 / 1024:.2f} MB)")

        # 4. Clean temporary intermediate audio passes in published reels
        print("[+] Cleaning intermediate line-by-line audio WAVs in active reels...")
        for reel_dir in reels_dir.iterdir():
            if reel_dir.is_dir():
                audio_dir = reel_dir / "audio"
                if audio_dir.exists():
                    for line_wav in audio_dir.glob("line_*.wav"):
                        sz = line_wav.stat().st_size
                        reclaimed_bytes += sz
                        line_wav.unlink(missing_ok=True)
                    vo_kokoro = audio_dir / "vo_kokoro.wav"
                    if vo_kokoro.exists():
                        sz = vo_kokoro.stat().st_size
                        reclaimed_bytes += sz
                        vo_kokoro.unlink(missing_ok=True)
                # Remove any leftover silent.mp4 or test_check stills
                for stale in reel_dir.glob("silent*.mp4"):
                    sz = stale.stat().st_size
                    reclaimed_bytes += sz
                    stale.unlink(missing_ok=True)
                for stale_dir in ["test_check", "test_stills"]:
                    p = reel_dir / stale_dir
                    if p.exists():
                        sz = safe_delete_folder(p)
                        reclaimed_bytes += sz

    # 5. Clean local Python bytecode caches
    print("[+] Cleaning Python bytecode caches across workspace...")
    pycache_count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if "__pycache__" in dirs:
            pyc_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pyc_path)
                pycache_count += 1
            except Exception:
                pass
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                try:
                    (Path(root) / f).unlink()
                except Exception:
                    pass

    print("-" * 65)
    print(f"🎉 CLEANUP COMPLETE!")
    print(f" Total Space Reclaimed : {reclaimed_bytes / 1024 / 1024:.2f} MB")
    print(f" Bytecode Dirs Cleaned : {pycache_count}")
    print("=" * 65)

    return 0


if __name__ == "__main__":
    sys.exit(main())

