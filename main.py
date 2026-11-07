"""
Zack D. Films 3D Explainer & Autonomous Instagram Publisher CLI
===============================================================
Usage:
    python main.py "How Solar Panels Actually Work" --publish
    python main.py "Why We Dream When Sleeping" --draft
    python main.py "How Touchscreens Detect Your Fingers" --no-publish
    python main.py --status
"""

import sys
import argparse
from pathlib import Path

# Configure Windows console encoding cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from core.pipeline import pipeline
from core.instagram import instagram_publisher


def print_banner():
    print(r"""
======================================================================
  🎬  ZACK D. FILMS 3D EXPLAINER & INSTAGRAM AUTO-PUBLISHER PIPELINE
======================================================================
""")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous 3D Zack D. Films explainer generator & Instagram publisher"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Topic or question for the 3D explainer short (e.g. 'How Touchscreens Detect Fingers')"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Upload directly to Instagram Reels and execute automated engagement boost"
    )
    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Render the master 1080x1920 MP4 locally without uploading to Instagram"
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Save render and metadata into storage/drafts/ for review"
    )
    parser.add_argument(
        "--story",
        action="store_true",
        help="Share the published reel to Instagram Story during engagement boost (default: False)"
    )
    parser.add_argument(
        "--no-story",
        action="store_true",
        help="Deprecated alias (Story sharing is disabled by default)"
    )
    parser.add_argument(
        "--script-file",
        type=str,
        default=None,
        help="Path to custom 8-sentence JSON script file"
    )
    parser.add_argument(
        "--username",
        type=str,
        default=None,
        help="Instagram username (if not already authenticated)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Instagram password (if not already authenticated)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Instagram sessionid cookie value"
    )
    parser.add_argument(
        "--login",
        action="store_true",
        help="Connect or switch to your personal/brand Instagram account"
    )
    parser.add_argument(
        "--logout",
        action="store_true",
        help="Log out and clear stored Instagram session"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check Instagram authentication status and profile information"
    )

    args = parser.parse_args()

    # 1. Login / Logout / Status Operations
    if args.logout:
        print_banner()
        instagram_publisher.logout()
        return 0

    if args.login:
        print_banner()
        if args.session_id or (args.username and args.password):
            instagram_publisher.login_with_credentials(
                username=args.username or "",
                password=args.password or "",
                session_id=args.session_id
            )
        else:
            instagram_publisher.login_interactive()
        return 0

    if args.status:
        print_banner()
        if instagram_publisher.is_authenticated():
            try:
                prof = instagram_publisher.get_profile()
                print(" Instagram Status:  AUTHENTICATED")
                print(f" Account          : @{prof['username']} ({prof['full_name']})")
                print(f" Followers        : {prof['followers']:,}")
                print(f" Posts/Reels      : {prof['media_count']:,}")
            except Exception as e:
                print(f" Instagram Status:  SESSION DETECTED (Validation warning: {e})")
        else:
            print(" Instagram Status:  NOT AUTHENTICATED")
            print(" Run 'python main.py --login' to connect your Instagram account.")
        return 0

    # 2. Topic Input
    topic = args.topic
    if not topic:
        print_banner()
        topic = input("Enter video topic/question (e.g. 'How OLED Screens Actually Work'): ").strip()
        if not topic:
            print("[-] No topic provided. Exiting.")
            return 1

    # Determine publish mode
    publish = args.publish
    if not args.publish and not args.no_publish and not args.draft:
        print_banner()
        choice = input("Do you want to publish to Instagram Reels after rendering? [y/N]: ").strip().lower()
        if choice in ["y", "yes"]:
            publish = True

    # Custom script if provided
    custom_script = None
    if args.script_file:
        import json
        p = Path(args.script_file)
        if p.exists():
            custom_script = json.loads(p.read_text(encoding="utf-8"))

    # Credentials dict
    credentials = None
    if args.session_id or (args.username and args.password):
        credentials = {
            "username": args.username or "",
            "password": args.password or "",
            "session_id": args.session_id or "",
        }

    active_account = ""
    if instagram_publisher.is_authenticated():
        try:
            active_account = f" (@{instagram_publisher.get_profile()['username']})"
        except Exception:
            active_account = " (Saved Session)"
    elif publish:
        active_account = " (Will prompt for your login)"

    share_story = bool(args.story and not args.no_story)

    print_banner()
    print(f"🎯 Target Topic : {topic}")
    print(f"🚀 Publish Reel : {'YES' + active_account if publish else 'NO (Local Render Only)'}")
    if publish:
        print(f"📸 Story Share  : {'YES' if share_story else 'NO (Default: Feed Reel Only)'}")
    print(f"💾 Save Draft   : {'YES' if args.draft else 'NO'}")
    print("-" * 70)

    try:
        res = pipeline.run(
            topic=topic,
            publish=publish,
            draft=args.draft,
            custom_script=custom_script,
            credentials=credentials,
            share_story=share_story
        )

        print("\n" + "=" * 70)
        print("                 🎉 PIPELINE COMPLETE! 🎉                 ")
        print("=" * 70)
        print(f" Master MP4 : {res['video_path']}")
        print(f" Cover JPG  : {res['cover_path']}")
        print(f" Duration   : {res['duration']:.2f}s ({res['file_size_mb']} MB)")

        if res.get("published"):
            print(f" Instagram  : {res.get('reel_url')}")
            print(f" Media ID   : {res.get('media_id')}")
            boost = res.get("boost", {})
            print(f" Liked      : {'Yes' if boost.get('liked') else 'No'}")
            print(f" Story      : {'Yes' if boost.get('story_id') else 'No'}")
        elif res.get("draft"):
            print(f" Draft Path : {res.get('draft_path')}")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\n[-] Pipeline execution error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

