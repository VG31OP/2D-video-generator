"""
Instagram Autonomous Manager CLI
Single-command interface to manage Instagram:
- Login session capture
- Upload Reels (any video or AI generated project)
- List recent Reels and analytics (views, likes, comments)
- Delete posts
- Post comments
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 stdout on Windows console for emojis in bios & captions
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service


def cmd_login(args):
    """Launches interactive browser login session capture."""
    from scripts.instagram_auth import capture_interactive_login, direct_credentials_login

    if args.username and args.password:
        success = direct_credentials_login(args.username, args.password, args.code)
    else:
        success = capture_interactive_login(timeout_seconds=args.timeout)

    return 0 if success else 1


def cmd_status(args):
    """Displays current Instagram authentication status and profile analytics."""
    if not instagram_service.is_authenticated():
        print("[!] Not authenticated with Instagram.")
        print("    Run: python scripts/instagram_manager.py login")
        return 1

    try:
        profile = instagram_service.get_profile()
        print("\n" + "=" * 55)
        print("          INSTAGRAM ACCOUNT STATUS          ")
        print("=" * 55)
        print(f" Username    : @{profile['username']}")
        print(f" Full Name   : {profile.get('full_name', '')}")
        print(f" Followers   : {profile.get('follower_count', 0):,}")
        print(f" Following   : {profile.get('following_count', 0):,}")
        print(f" Total Posts : {profile.get('media_count', 0):,}")
        print(f" Bio         : {profile.get('biography', '').replace(chr(10), ' ')}")
        print(f" Private     : {'Yes' if profile.get('is_private') else 'No'}")
        print(f" Verified    : {'Yes' if profile.get('is_verified') else 'No'}")
        print("=" * 55)
        print("[✓] Instagram connection is active and healthy.\n")
        return 0
    except Exception as e:
        print(f"[✗] Failed to fetch account status: {e}")
        print("    Try refreshing your session: python scripts/instagram_manager.py login")
        return 1


def cmd_upload_reel(args):
    """Uploads a standalone video file as an Instagram Reel."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"[✗] Video file does not exist: {video_path}")
        return 1

    print(f"\n[+] Preparing to upload Reel: {video_path.name}")
    print(f"[+] Caption:\n{args.caption}\n")

    try:
        res = instagram_service.upload_reel(
            video_path=str(video_path),
            caption=args.caption or "",
            thumbnail_path=args.thumb
        )
        media_id = res.get('media_id')
        print("\n" + "=" * 55)
        print("       🎉 REEL SUCCESSFULLY PUBLISHED! 🎉       ")
        print("=" * 55)
        print(f" Media ID : {media_id}")
        print(f" URL      : {res.get('url')}")
        print("=" * 55 + "\n")

        if getattr(args, "boost", False) and media_id:
            print("[+] Auto-boosting reel (like, comment, story share)...")
            instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=args.comment or "Drop a ❤️ and save this for later! Follow @vrj.ai for more secret AI & tech hacks! 🚀",
                like=True,
                share_story=True,
                video_path=str(video_path)
            )

        return 0
    except Exception as e:
        print(f"[✗] Reel upload failed: {e}")
        return 1


def cmd_upload_project(args):
    """Uploads a generated short project directly to Instagram Reels."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    project_id = args.project_id
    print(f"\n[+] Preparing to publish Project [{project_id}] to Instagram Reels...")

    try:
        res = instagram_service.upload_project_to_reels(
            project_id=project_id,
            custom_caption=args.caption
        )
        media_id = res.get('media_id')
        print("\n" + "=" * 55)
        print("       🎉 REEL SUCCESSFULLY PUBLISHED! 🎉       ")
        print("=" * 55)
        print(f" Project  : {project_id}")
        print(f" Media ID : {media_id}")
        print(f" URL      : {res.get('url')}")
        print("=" * 55 + "\n")

        if getattr(args, "boost", False) and media_id:
            print("[+] Auto-boosting project reel (like, comment, story share)...")
            instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=args.comment or "Save this for later! 📌 Which AI tool are you trying first? Drop a comment below! 👇",
                like=True,
                share_story=True
            )

        return 0
    except Exception as e:
        print(f"[✗] Project upload failed: {e}")
        return 1


def cmd_list_reels(args):
    """Fetches and displays recent Reels and analytics."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    print(f"\n[+] Fetching recent {args.count} posts/reels...")
    try:
        reels = instagram_service.get_recent_reels(amount=args.count)
        if not reels:
            print("[i] No posts found on this account yet.")
            return 0

        print("\n" + "=" * 80)
        print(f"{'MEDIA ID':<20} | {'VIEWS':<8} | {'LIKES':<8} | {'COMMS':<6} | {'URL / SHORTCODE'}")
        print("-" * 80)
        for r in reels:
            print(f"{r['id']:<20} | {r['view_count']:<8} | {r['like_count']:<8} | {r['comment_count']:<6} | {r['url']}")
            cap = (r['caption'] or '').replace('\n', ' ')
            if cap:
                print(f"  └─ Caption: {cap[:70]}...")
        print("=" * 80 + "\n")
        return 0
    except Exception as e:
        print(f"[✗] Failed to list reels: {e}")
        return 1


def cmd_delete(args):
    """Deletes a Reel or post by ID or URL."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    target = args.media_id
    confirm = input(f"Are you sure you want to delete media '{target}'? (y/N): ") if not args.yes else "y"
    if confirm.lower() != "y":
        print("[i] Cancelled.")
        return 0

    try:
        success = instagram_service.delete_media(target)
        if success:
            print(f"[✓] Successfully deleted media: {target}")
            return 0
        else:
            print(f"[!] Media delete returned False for: {target}")
            return 1
    except Exception as e:
        print(f"[✗] Failed to delete media: {e}")
        return 1


def cmd_comment(args):
    """Posts a comment on a Reel."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    try:
        res = instagram_service.comment(args.media_id, args.text)
        print(f"[✓] Comment posted! (Comment ID: {res.get('id')})")
        return 0
    except Exception as e:
        print(f"[✗] Failed to comment: {e}")
        return 1


def cmd_like(args):
    """Likes a Reel or post."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    try:
        success = instagram_service.like_media(args.media_id)
        print(f"[✓] Liked media: {args.media_id} (Success: {success})")
        return 0
    except Exception as e:
        print(f"[✗] Failed to like media: {e}")
        return 1


def cmd_share_story(args):
    """Shares a Reel to Instagram Story."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    try:
        story = instagram_service.share_to_story(args.media_id, caption=args.caption or "New Reel 🎬🔥 Watch now!")
        print(f"[✓] Shared to story! (Story ID: {getattr(story, 'pk', '')})")
        return 0
    except Exception as e:
        print(f"[✗] Failed to share to story: {e}")
        return 1


def cmd_boost(args):
    """Executes full post-reel engagement: like, comment, and story share."""
    if not instagram_service.is_authenticated():
        print("[!] Please login first: python scripts/instagram_manager.py login")
        return 1

    print(f"\n[+] Running post-reel boost on media: {args.media_id}...")
    res = instagram_service.post_reel_engagement(
        media_id=args.media_id,
        comment_text=args.comment or "Drop a ❤️ if this helped! Follow @vrj.ai for more secret AI & tech tools! 🚀",
        like=True,
        share_story=not args.no_story
    )
    print(f"    - Liked own reel     : {'[✓]' if res['liked'] else '[✗]'}")
    print(f"    - Posted CTA comment : {'[✓]' if res['commented'] else '[✗]'}")
    print(f"    - Shared to Story    : {'[✓]' if res['shared_to_story'] else '[✗]'}")
    if res["errors"]:
        print("    Warnings/Errors:", res["errors"])
    return 0


def main():
    parser = argparse.ArgumentParser(description="Instagram Autonomous CLI Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # login
    p_login = subparsers.add_parser("login", help="Capture login session in browser or credentials")
    p_login.add_argument("-u", "--username", help="Instagram username (for direct credentials login)")
    p_login.add_argument("-p", "--password", help="Instagram password (for direct credentials login)")
    p_login.add_argument("-c", "--code", help="2FA verification code")
    p_login.add_argument("--timeout", type=int, default=300, help="Interactive login timeout in seconds")

    # status
    subparsers.add_parser("status", help="Check login status and account analytics")
    subparsers.add_parser("profile", help="Check login status and account analytics")

    # upload-reel
    p_upload = subparsers.add_parser("upload-reel", help="Upload a video to Instagram Reels")
    p_upload.add_argument("--video", "-v", required=True, help="Path to MP4 video")
    p_upload.add_argument("--caption", help="Caption text with hashtags")
    p_upload.add_argument("--thumb", help="Optional path to custom cover image")
    p_upload.add_argument("--boost", action="store_true", help="Automatically like, comment, and share to story after upload")
    p_upload.add_argument("--comment", help="Custom comment for boost")

    # upload-project
    p_proj = subparsers.add_parser("upload-project", help="Upload a generated short project to Reels")
    p_proj.add_argument("--project-id", "-i", required=True, help="Project ID")
    p_proj.add_argument("--caption", help="Optional custom caption (otherwise generated from script)")
    p_proj.add_argument("--boost", action="store_true", help="Automatically like, comment, and share to story after upload")
    p_proj.add_argument("--comment", help="Custom comment for boost")

    # list-reels
    p_list = subparsers.add_parser("list-reels", help="List recent Reels and analytics")
    p_list.add_argument("--count", "-n", type=int, default=10, help="Number of items to fetch (default: 10)")

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a post or reel")
    p_del.add_argument("--media-id", "-m", required=True, help="Media ID or Instagram URL")
    p_del.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # comment
    p_comm = subparsers.add_parser("comment", help="Post a comment on a Reel")
    p_comm.add_argument("--media-id", "-m", required=True, help="Media ID or Instagram URL")
    p_comm.add_argument("--text", "-t", required=True, help="Comment text")

    # like
    p_like = subparsers.add_parser("like", help="Like a Reel or post")
    p_like.add_argument("--media-id", "-m", required=True, help="Media ID or Instagram URL")

    # share-story
    p_story = subparsers.add_parser("share-story", help="Share a Reel to your Instagram Story")
    p_story.add_argument("--media-id", "-m", required=True, help="Media ID or Instagram URL")
    p_story.add_argument("--caption", help="Optional story text caption")

    # boost
    p_boost = subparsers.add_parser("boost", help="Run full post-reel engagement (like, comment, story)")
    p_boost.add_argument("--media-id", "-m", required=True, help="Media ID or Instagram URL")
    p_boost.add_argument("--comment", help="Custom comment text")
    p_boost.add_argument("--no-story", action="store_true", help="Skip story sharing")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "login": cmd_login,
        "status": cmd_status,
        "profile": cmd_status,
        "upload-reel": cmd_upload_reel,
        "upload-project": cmd_upload_project,
        "list-reels": cmd_list_reels,
        "delete": cmd_delete,
        "comment": cmd_comment,
        "like": cmd_like,
        "share-story": cmd_share_story,
        "boost": cmd_boost,
    }

    cmd_fn = dispatch.get(args.command)
    if cmd_fn:
        sys.exit(cmd_fn(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
