"""
Instagram Authentication & Session Capture Tool
Allows zero-friction, one-time Instagram login capture with automatic cookie extraction.
Supports 2FA, SMS OTP, Facebook Login, and direct credentials.
Saves session to storage/instagram_session.json and storage/instagram_browser_state.json
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Ensure UTF-8 stdout on Windows console for emojis and unicode symbols
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = ROOT_DIR / "storage"
SESSION_FILE = STORAGE_DIR / "instagram_session.json"
BROWSER_STATE_FILE = STORAGE_DIR / "instagram_browser_state.json"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def verify_session_with_instagrapi(session_id: str, ds_user_id: str = None) -> dict:
    """Verifies the captured session ID using instagrapi and returns profile info."""
    try:
        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]
        
        print("\n[+] Verifying session with Instagram API...")
        cl.login_by_sessionid(session_id)
        
        # Test fetching user info with full profile metrics
        user_info = cl.user_info(cl.user_id)
        profile_data = {
            "pk": user_info.pk,
            "username": user_info.username,
            "full_name": user_info.full_name,
            "is_private": user_info.is_private,
            "profile_pic_url": str(user_info.profile_pic_url) if user_info.profile_pic_url else "",
            "media_count": getattr(user_info, "media_count", 0),
            "follower_count": getattr(user_info, "follower_count", 0),
            "following_count": getattr(user_info, "following_count", 0),
            "biography": getattr(user_info, "biography", ""),
        }
        
        # Save complete instagrapi settings so subsequent calls are 100% authenticated
        cl.dump_settings(str(SESSION_FILE))
        print(f"[✓] Session confirmed valid for @{profile_data['username']}!")
        return profile_data
    except Exception as e:
        print(f"[!] Warning during instagrapi verification: {e}")
        return None


def capture_interactive_login(timeout_seconds: int = 300) -> bool:
    """
    Opens Chromium browser to Instagram login page.
    Waits for the user to log in and automatically captures session cookies.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed. Run: pip install playwright && python -m playwright install chromium")
        return False

    print("=" * 65)
    print("      INSTAGRAM AUTOMATIC LOGIN CAPTURE      ")
    print("=" * 65)
    print("\n[+] Opening visible browser window...")
    print("[+] Please log into your Instagram account in the browser.")
    print("    - 2FA / SMS codes / Google / Facebook login are supported.")
    print("    - As soon as login completes, your session will be saved automatically.")
    print(f"[+] Waiting up to {timeout_seconds} seconds...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            viewport=None,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto("https://www.instagram.com/accounts/login/")

        start_time = time.time()
        captured_session = None

        while time.time() - start_time < timeout_seconds:
            time.sleep(2)
            try:
                cookies = context.cookies()
            except Exception:
                break

            cookie_dict = {c["name"]: c["value"] for c in cookies if "instagram.com" in c.get("domain", "")}

            session_id = cookie_dict.get("sessionid")
            ds_user_id = cookie_dict.get("ds_user_id")

            # Check if sessionid cookie exists and page is past login
            current_url = page.url
            is_past_login = "/accounts/login" not in current_url and "/accounts/onetap" not in current_url

            if session_id and (is_past_login or ds_user_id):
                print("\n[✓] Login detected! Capturing cookies and session tokens...")
                captured_session = {
                    "sessionid": session_id,
                    "ds_user_id": ds_user_id or "",
                    "csrftoken": cookie_dict.get("csrftoken", ""),
                    "mid": cookie_dict.get("mid", ""),
                    "ig_did": cookie_dict.get("ig_did", ""),
                    "rur": cookie_dict.get("rur", ""),
                    "captured_at": time.time(),
                }

                # Save browser storage state
                context.storage_state(path=str(BROWSER_STATE_FILE))
                print(f"[✓] Browser state saved to: {BROWSER_STATE_FILE}")

                # Save raw session cookies
                raw_session_path = STORAGE_DIR / "instagram_cookies.json"
                with open(raw_session_path, "w", encoding="utf-8") as f:
                    json.dump(captured_session, f, indent=2)

                break

        try:
            browser.close()
        except Exception:
            pass

        if not captured_session:
            print("\n[✗] Login capture timed out or browser was closed before login completed.")
            return False

        # Verify with instagrapi
        profile = verify_session_with_instagrapi(
            captured_session["sessionid"],
            captured_session.get("ds_user_id")
        )

        if not profile:
            print("\n[✗] Session verification failed. Could not authenticate with Instagram API.")
            return False

        print("\n" + "=" * 65)
        print("          INSTAGRAM LOGIN SUCCESSFUL! 🎉          ")
        print("=" * 65)
        if "username" in profile:
            print(f" Account   : @{profile['username']}")
            print(f" Name      : {profile.get('full_name', '')}")
            print(f" Followers : {profile.get('follower_count', 0):,}")
            print(f" Posts     : {profile.get('media_count', 0):,}")
        print(f" Session   : {SESSION_FILE}")
        print("=" * 65)
        print("\nYou can now upload reels and manage Instagram completely automatically!")
        print("Example command: python scripts/instagram_manager.py status")
        return True


def direct_credentials_login(username: str, password: str, verification_code: str = None) -> bool:
    """Logs in using username & password directly via instagrapi."""
    try:
        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]

        print(f"[+] Logging into Instagram directly as @{username}...")
        
        if verification_code:
            cl.login(username, password, verification_code=verification_code)
        else:
            cl.login(username, password)

        cl.dump_settings(str(SESSION_FILE))
        user_info = cl.user_info(cl.user_id)

        print(f"[✓] Login successful! Saved session for @{user_info.username}")
        return True
    except Exception as e:
        print(f"[✗] Direct login failed: {e}")
        print("Tip: Use interactive browser capture (default) to bypass security challenges safely!")
        return False


def main():
    parser = argparse.ArgumentParser(description="Instagram Login & Session Capture")
    parser.add_argument("--interactive", action="store_true", default=True, help="Launch interactive browser to capture login")
    parser.add_argument("--username", "-u", type=str, help="Instagram username (for direct login)")
    parser.add_argument("--password", "-p", type=str, help="Instagram password (for direct login)")
    parser.add_argument("--code", "-c", type=str, help="2FA verification code (if required)")
    parser.add_argument("--timeout", type=int, default=300, help="Interactive login timeout in seconds (default: 300)")

    args = parser.parse_args()

    if args.username and args.password:
        success = direct_credentials_login(args.username, args.password, args.code)
    else:
        success = capture_interactive_login(args.timeout)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
