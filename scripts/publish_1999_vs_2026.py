"""
Publish 1999 vs 2026 Stick Figure Reel to Instagram (@vrj.ai)
"""

import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service

def main():
    video_path = ROOT_DIR / "storage" / "reels" / "stick_figure_1999_vs_2026" / "stick_figure_1999_vs_2026_final.mp4"
    cover_path = ROOT_DIR / "storage" / "reels" / "stick_figure_1999_vs_2026" / "cover.jpg"

    if not video_path.exists():
        print(f"[✗] Video file not found: {video_path}")
        sys.exit(1)

    print(f"[+] Publishing Reel: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")
    if cover_path.exists():
        print(f"[+] Custom Cover: {cover_path.name}")

    caption = (
        "Wait... did you actually live through 1999 internet? 💾💀\n\n"
        "In 1999:\n"
        "• Downloading 1 song took 45 minutes on LimeWire / Napster\n"
        "• Your mom picked up the landline and destroyed your download\n"
        "• The 56k dial-up screech was music to our ears\n\n"
        "In 2026:\n"
        "• 10Gbps fiber optic speeds in your pocket\n"
        "• Your smart fridge is arguing with your smart speaker\n"
        "• AI generates entire video games in 3 seconds\n\n"
        "What was the first website you ever visited? Drop it below! 👇\n\n"
        "Follow @vrj.ai for more insane tech evolution, hidden AI tools & viral digital hacks! 🚀\n"
        ".\n.\n"
        "#retro #tech #1999 #nostalgia #ai #stickfigure #animation #technology #techtok #reels #computermuseum #dialup #futuretech #vrjai #coder #programmer"
    )

    comment = "💾 Be honest: Did you ever get yelled at for blocking the house phone line in the 90s? Drop your memories below! 👇"

    try:
        res = instagram_service.upload_reel(
            video_path=str(video_path),
            caption=caption,
            thumbnail_path=str(cover_path) if cover_path.exists() else None
        )
        media_id = res.get("media_id")
        reel_url = res.get("url")

        print("\n" + "=" * 60)
        print("       🎉 REEL SUCCESSFULLY PUBLISHED TO INSTAGRAM! 🎉       ")
        print("=" * 60)
        print(f" Media ID : {media_id}")
        print(f" URL      : {reel_url}")
        print("=" * 60 + "\n")

        if media_id:
            print("[+] Executing engagement boost (like, comment, story share)...")
            boost = instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=comment,
                like=True,
                share_story=True,
                video_path=str(video_path)
            )
            print(f"    - Liked own reel     : {'[✓]' if boost['liked'] else '[✗]'}")
            print(f"    - Posted CTA comment : {'[✓]' if boost['commented'] else '[✗]'}")
            print(f"    - Shared to Story    : {'[✓]' if boost['shared_to_story'] else '[✗]'}")

        return 0
    except Exception as e:
        print(f"[✗] Failed to publish reel: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

