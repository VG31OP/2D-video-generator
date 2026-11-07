"""
Instagram Reels Automation & Auto-Boost Client
Zero-headache authentication: supports saved sessions, cookies, or interactive login prompt.
"""

import os
import sys
import json
import time
import getpass
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from core.config import SESSION_FILE, COOKIES_FILE

logger = logging.getLogger("core.instagram")


class InstagramPublisher:
    def __init__(self):
        self._client = None
        self._cached_profile = None

    def is_authenticated(self) -> bool:
        """Checks if a valid Instagram session or cookie file exists."""
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 50:
            return True
        if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 50:
            return True
        return False

    def get_client(self, force_refresh: bool = False):
        """Initializes and returns an authenticated instagrapi Client."""
        if self._client is not None and not force_refresh:
            return self._client

        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]

        # 1. Try saved session
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 50:
            try:
                cl.load_settings(str(SESSION_FILE))
                if cl.user_id:
                    self._client = cl
                    return cl
            except Exception as e:
                logger.warning(f"Could not load session from {SESSION_FILE}: {e}")

        # 2. Try saved cookies
        if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 50:
            try:
                with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                    cookies_data = json.load(f)
                session_id = cookies_data.get("sessionid")
                if session_id:
                    cl.login_by_sessionid(session_id)
                    cl.dump_settings(str(SESSION_FILE))
                    self._client = cl
                    return cl
            except Exception as e:
                logger.warning(f"Could not login via cookies: {e}")

        return None

    def login_with_credentials(
        self,
        username: str,
        password: Optional[str] = None,
        verification_code: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Authenticates with Instagram and saves session for subsequent automatic reuse.
        """
        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]

        if session_id:
            print(f"[+] Logging into Instagram using session ID...")
            cl.login_by_sessionid(session_id)
        elif username and password:
            print(f"[+] Logging into Instagram as @{username}...")
            cl.login(username, password, verification_code=verification_code or "")
        else:
            raise ValueError("Must provide either username + password or session_id.")

        cl.dump_settings(str(SESSION_FILE))
        self._client = cl
        print(f"[+] Successfully logged in as @{cl.username} (ID: {cl.user_id})")
        return True

    def login_interactive(self) -> bool:
        """
        Interactive terminal prompt for credentials when publishing to a new account.
        """
        print("\n" + "=" * 60)
        print("          📸 INSTAGRAM AUTHENTICATION REQUIRED")
        print("=" * 60)
        print("No saved Instagram session found.")
        print("You can log in with your Instagram Username & Password,")
        print("or use an existing 'sessionid' cookie from your browser.")
        print("-" * 60)

        method = input("Login method? [1] Username/Password  [2] SessionID Cookie (default: 1): ").strip()
        if method == "2":
            session_id = input("Paste your 'sessionid' cookie value: ").strip()
            if not session_id:
                print("[-] No sessionid provided.")
                return False
            return self.login_with_credentials("", session_id=session_id)
        else:
            username = input("Instagram Username: ").strip().lstrip("@")
            password = getpass.getpass("Instagram Password: ")
            two_factor = input("2FA Code (press Enter if disabled): ").strip()
            return self.login_with_credentials(
                username=username,
                password=password,
                verification_code=two_factor if two_factor else None
            )

    def logout(self) -> bool:
        """Clears local session and cookies to allow switching or resetting accounts."""
        if SESSION_FILE.exists():
            SESSION_FILE.unlink(missing_ok=True)
        if COOKIES_FILE.exists():
            COOKIES_FILE.unlink(missing_ok=True)
        self._client = None
        self._cached_profile = None
        print("[+] Logged out. Stored Instagram session cleared.")
        return True

    def get_profile(self) -> Dict[str, Any]:
        """Fetches profile info for the currently authenticated account."""
        cl = self.get_client()
        if not cl:
            raise RuntimeError("Instagram is not authenticated.")
        info = cl.user_info(cl.user_id)
        return {
            "user_id": str(info.pk),
            "username": info.username,
            "full_name": info.full_name,
            "followers": getattr(info, "follower_count", 0),
            "following": getattr(info, "following_count", 0),
            "media_count": getattr(info, "media_count", 0),
        }

    def upload_reel(
        self,
        video_path: str,
        caption: str = "",
        cover_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads a video to Instagram Reels.
        """
        cl = self.get_client()
        if not cl:
            if not self.login_interactive():
                raise RuntimeError("Failed to authenticate with Instagram.")
            cl = self.get_client()

        video_p = Path(video_path)
        if not video_p.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        thumb_p = Path(cover_path) if cover_path and Path(cover_path).exists() else None

        print(f"[+] Uploading Reel: {video_p.name} ({video_p.stat().st_size / (1024*1024):.2f} MB)...")
        media = cl.clip_upload(
            path=video_p,
            caption=caption,
            thumbnail=thumb_p
        )

        media_id = str(media.pk)
        media_code = getattr(media, "code", "")
        reel_url = f"https://www.instagram.com/reel/{media_code}/" if media_code else f"https://www.instagram.com/p/{media_id}/"

        print(f"[+] Reel published successfully!")
        print(f"    Media ID : {media_id}")
        print(f"    Reel URL : {reel_url}")

        return {
            "media_id": media_id,
            "code": media_code,
            "url": reel_url,
            "user_id": str(cl.user_id),
            "username": cl.username,
        }

    def boost_engagement(
        self,
        media_id: str,
        comment_text: Optional[str] = None,
        like: bool = True,
        share_story: bool = False,
        video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes automated algorithm boost immediately after upload:
        1. Self-likes the reel.
        2. Posts a high-engagement CTA comment.
        3. Shares the reel to Story (optional, default: False).
        """
        cl = self.get_client()
        if not cl:
            return {}

        results = {}

        if like:
            try:
                print(f"[+] Liking Reel ({media_id})...")
                cl.media_like(media_id)
                results["liked"] = True
            except Exception as e:
                results["liked"] = False
                logger.warning(f"Failed to like reel: {e}")

        if comment_text:
            try:
                print(f"[+] Posting pinned CTA comment...")
                comment = cl.media_comment(media_id, comment_text)
                results["comment_id"] = str(comment.pk)
                results["comment_text"] = comment_text
            except Exception as e:
                results["comment_id"] = None
                logger.warning(f"Failed to post comment: {e}")

        if share_story and video_path and Path(video_path).exists():
            try:
                print(f"[+] Resharing Reel to Story...")
                time.sleep(1)
                story_media = cl.video_upload_to_story(
                    path=Path(video_path),
                    caption="New explainer out now! Tap to watch 🔥"
                )
                results["story_id"] = str(story_media.pk)
            except Exception as e:
                results["story_id"] = None
                logger.warning(f"Failed to reshare to story: {e}")

        return results


instagram_publisher = InstagramPublisher()

