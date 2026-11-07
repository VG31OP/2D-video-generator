"""
Publish Any Saved Reel Draft to Instagram (@vrj.ai)
"""

import sys
import json
import argparse
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service


def list_drafts():
    drafts_dir = ROOT_DIR / "storage" / "drafts"
    if not drafts_dir.exists():
        print("[!] No drafts directory found.")
        return []

    drafts = []
    for d in drafts_dir.iterdir():
        if d.is_dir():
            manifest = d / "draft_manifest.json"
            if manifest.exists():
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                    drafts.append(data)
                except Exception:
                    pass
    return drafts


def main():
    parser = argparse.ArgumentParser(description="Publish a saved draft to Instagram")
    parser.add_argument("--id", type=str, default="zach_touchscreens", help="Project ID / Draft folder name")
    parser.add_argument("--list", action="store_true", help="List all saved drafts")
    parser.add_argument("--trial", action="store_true", help="Publish as an unlisted Trial Reel (hidden from feed)")
    parser.add_argument("--story", action="store_true", help="Also share to Story during engagement boost (default: False)")
    args = parser.parse_args()

    drafts = list_drafts()

    if args.list:
        print("=" * 65)
        print(f"📦 SAVED REEL DRAFTS ({len(drafts)} available)")
        print("=" * 65)
        for i, d in enumerate(drafts, 1):
            print(f"{i}. ID: {d.get('project_id', 'unknown')}")
            print(f"   Title   : {d.get('title', '')}")
            print(f"   Style   : {d.get('art_style', '')}")
            print(f"   Duration: {d.get('duration_seconds', 0)}s")
            print(f"   Video   : {d.get('video_path', '')}")
        print("=" * 65)
        return 0

    draft_dir = ROOT_DIR / "storage" / "drafts" / args.id
    manifest_file = draft_dir / "draft_manifest.json"

    if not manifest_file.exists():
        print(f"[✗] Draft manifest not found at: {manifest_file}")
        return 1

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    video_path = Path(manifest["video_path"])
    thumb_path = Path(manifest.get("thumbnail_path", ""))

    if not video_path.exists():
        print(f"[✗] Draft video file missing: {video_path}")
        return 1

    print("=" * 65)
    print(f"🚀 PUBLISHING DRAFT TO INSTAGRAM: {manifest.get('title')}")
    print("=" * 65)
    print(f" Video Path : {video_path}")
    print(f" Thumbnail  : {thumb_path}")
    print(f" Trial Mode : {'Yes (Hidden from grid)' if args.trial else 'Standard (Public Reel)'}")

    try:
        res = instagram_service.upload_reel(
            video_path=str(video_path),
            caption=manifest["caption"],
            thumbnail_path=str(thumb_path) if thumb_path.exists() else None,
            show_preview_in_feed=not args.trial,
            trial=args.trial
        )
        media_id = res.get("media_id")
        reel_url = res.get("url")

        print("\n" + "=" * 65)
        print("       🎉 DRAFT REEL PUBLISHED TO INSTAGRAM! 🎉       ")
        print("=" * 65)
        print(f" Media ID : {media_id}")
        print(f" URL      : {reel_url}")
        print("=" * 65 + "\n")

        if media_id:
            boost = instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=manifest.get("pinned_comment"),
                like=True,
                share_story=args.story,
                video_path=str(video_path)
            )
            print(f"    - Liked own reel     : {'[✓]' if boost.get('liked') else '[✗]'}")
            print(f"    - Posted CTA comment : {'[✓]' if boost.get('commented') else '[✗]'}")
            print(f"    - Shared to Story    : {'[✓]' if boost.get('shared_to_story') else '[✗]'}")

        return 0
    except Exception as e:
        print(f"[✗] Failed to publish draft: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

