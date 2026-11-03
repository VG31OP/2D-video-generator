"""
Upload Zack D. Films 3D Reel to Instagram (@vrj.ai) with Automated Engagement Boost
"""

import sys
import argparse
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service


def parse_args():
    parser = argparse.ArgumentParser(description="Publish Zack D. Films Reel to Instagram")
    parser.add_argument("--folder", type=str, default="zach_wireless_charging", help="Folder inside storage/reels/")
    parser.add_argument("--video", type=str, default=None, help="Explicit video filename (e.g. zach_wireless_charging_final.mp4)")
    parser.add_argument("--caption", type=str, default=None, help="Custom caption")
    parser.add_argument("--comment", type=str, default=None, help="Custom CTA comment")
    return parser.parse_args()


DEFAULT_CAPTIONS = {
    "zach_noise_cancelling": (
        "Wait... is this REALLY how noise-cancelling headphones work? 🎧🤫💀\n\n"
        "When you put on active noise-cancelling headphones, the foam padding DOES NOT physically absorb every sound wave. If it did, deafening jet engine rumbles would still blow your ears out! ✈️😱\n\n"
        "Here is the secret physics behind the silence:\n"
        "1️⃣ Tiny microphones on the outside listen to ambient noise in real time.\n"
        "2️⃣ A dedicated sound processor instantly calculates the exact inverted, opposite soundwave (a mirror image!).\n"
        "3️⃣ The internal speaker driver plays this anti-noise wave directly into your ear canal.\n"
        "4️⃣ When the sound waves collide—the peak meets the trough—they cancel each other out in complete destructive interference! 💥➡️➖\n"
        "5️⃣ Leaving you in pure, eerie, peaceful silence... even in the middle of a screaming airplane cabin! ☁️✨\n\n"
        "Drop a ❤️ if you use ANC headphones every day! What gadget should we break down next? 👇\n\n"
        "Follow @vrj.ai for more viral 3D tech explainers, science breakdowns & animation magic! 🚀\n"
        ".\n.\n"
        "#tech #science #noisecancelling #headphones #howitworks #3danimation #zackdfilms #audio #technology #physics #engineering #gadgets #viral #reels #vrjai #audiophile"
    ),
    "zach_wireless_charging": (
        "Wait... is this REALLY how wireless charging works? 🔋⚡💀\n\n"
        "When you place your phone onto a wireless charging pad, electricity DOES NOT jump through the air into your battery. If it did, you'd get shocked every single time! ⚡😱\n\n"
        "Here is what actually happens inside:\n"
        "1️⃣ The charging pad contains a tightly coiled copper wire.\n"
        "2️⃣ Running electricity through this coil creates an invisible fluctuating magnetic field.\n"
        "3️⃣ Inside your phone, a second matching copper coil catches these magnetic waves.\n"
        "4️⃣ This changing magnetic field pushes electrons inside your phone's coil, forcing them to flow.\n"
        "5️⃣ That motion converts magnetism back into electricity, charging your battery without a single cord! 📱✨\n\n"
        "Drop a ❤️ if you learned something new! What tech gadget should we break down next? 👇\n\n"
        "Follow @vrj.ai for viral 3D tech explainers, science breakdowns & animation magic! 🚀\n"
        ".\n.\n"
        "#tech #science #wirelesscharging #howitworks #3danimation #zackdfilms #technology #physics #engineering #gadgets #viral #reels #vrjai #animation"
    ),
    "zach_how_internet_works": (
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
}

DEFAULT_COMMENTS = {
    "zach_noise_cancelling": "Drop a ❤️ and save this! Did you know your headphones play 'anti-noise' to cancel sound? Tell us below! 👇🎧",
    "zach_wireless_charging": "Drop a ❤️ and save this! Did you think electricity jumped through the air before? Tell us below! 👇⚡",
    "zach_how_internet_works": "Drop a ❤️ and save this! Did you think your messages went through space satellites before? Tell us below! 👇"
}


def main():
    args = parse_args()
    reel_dir = ROOT_DIR / "storage" / "reels" / args.folder

    if not reel_dir.exists():
        print(f"[✗] Reel directory not found: {reel_dir}")
        sys.exit(1)

    if args.video:
        video_path = reel_dir / args.video
    else:
        candidates = list(reel_dir.glob("*_final.mp4"))
        if candidates:
            video_path = candidates[0]
        else:
            candidates = list(reel_dir.glob("*.mp4"))
            video_path = candidates[0] if candidates else (reel_dir / f"{args.folder}_final.mp4")

    cover_path = reel_dir / "cover.jpg"

    if not video_path.exists():
        print(f"[✗] Video file not found: {video_path}")
        sys.exit(1)

    print(f"[+] Publishing Zack D. Films Reel: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")
    if cover_path.exists():
        print(f"[+] Custom Cover Poster: {cover_path.name}")

    caption = args.caption or DEFAULT_CAPTIONS.get(args.folder, DEFAULT_CAPTIONS["zach_wireless_charging"])
    comment = args.comment or DEFAULT_COMMENTS.get(args.folder, DEFAULT_COMMENTS["zach_wireless_charging"])

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
