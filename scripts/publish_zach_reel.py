"""
Upload Zack D. Films 3D Reel to Instagram (@vrj.ai)
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
    video_path = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "zach_how_internet_works_final.mp4"
    cover_path = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "cover.jpg"

    if not video_path.exists():
        print(f"[✗] Video file not found: {video_path}")
        sys.exit(1)

    print(f"[+] Publishing Zack D. Films Reel: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")
    if cover_path.exists():
        print(f"[+] Custom Cover Poster: {cover_path.name}")

    caption = (
        "Wait... is this REALLY how the internet actually works? 🌐💀\n\n"
        "When you send a text to someone across the world, it doesn't beam through satellites in space. Almost 99% of all internet traffic travels underground!\n\n"
        "Here is what happens behind the scenes:\n"
        "1️⃣ Your phone chops your text into thousands of tiny binary packets.\n"
        "2️⃣ Your Wi-Fi router converts them into light pulses and shoots them down fiber cables.\n"
        "3️⃣ A DNS server looks up the exact destination IP address in milliseconds.\n"
        "4️⃣ Those light pulses race across thousands of miles of deep-sea ocean cables at nearly the speed of light.\n"
        "5️⃣ A server on the other side reassembles the message directly onto their screen! 📱✨\n\n"
        "Did you know this before? Drop your thoughts below! 👇\n\n"
        "Follow @vrj.ai for more insane 3D tech explainers, viral digital science & secret hacks! 🚀\n"
        ".\n.\n"
        "#tech #science #3danimation #zackdfilms #howitworks #technology #animation #viral #reels #explainer #vrjai #fiberoptic #internet #coder"
    )

    comment = "Drop a ❤️ and save this! Did you think your messages went through space satellites before? Tell us below! 👇"

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
            print(f"    - Liked own reel     : {'[✓]' if boost.get('liked') else '[✗]'}")
            print(f"    - Posted CTA comment : {'[✓]' if boost.get('commented') else '[✗]'}")
            print(f"    - Shared to Story    : {'[✓]' if boost.get('shared_to_story') else '[✗]'}")

        return 0
    except Exception as e:
        print(f"[✗] Failed to publish reel: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

