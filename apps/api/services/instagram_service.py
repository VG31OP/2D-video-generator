"""
Instagram Automation Service
Provides autonomous session management, Reels uploading, project publishing,
and media analytics using captured Instagram authentication.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
STORAGE_DIR = ROOT_DIR / "storage"
SESSION_FILE = STORAGE_DIR / "instagram_session.json"
COOKIES_FILE = STORAGE_DIR / "instagram_cookies.json"
PROJECTS_DIR = STORAGE_DIR / "projects"


class InstagramService:
    def __init__(self):
        self._client = None
        self._cached_profile = None
        self._session_mtime = 0.0
        self._cookies_mtime = 0.0

    def is_authenticated(self) -> bool:
        """Checks if a valid Instagram session is stored."""
        if SESSION_FILE.exists() and SESSION_FILE.stat().st_size > 50:
            return True
        if COOKIES_FILE.exists() and COOKIES_FILE.stat().st_size > 50:
            return True
        return False

    def get_client(self, force_refresh: bool = False):
        """Initializes and returns an authenticated instagrapi Client."""
        curr_session_mtime = SESSION_FILE.stat().st_mtime if SESSION_FILE.exists() else 0.0
        curr_cookies_mtime = COOKIES_FILE.stat().st_mtime if COOKIES_FILE.exists() else 0.0

        if (
            self._client is not None
            and not force_refresh
            and curr_session_mtime <= self._session_mtime
            and curr_cookies_mtime <= self._cookies_mtime
        ):
            return self._client

        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]

        if SESSION_FILE.exists():
            try:
                cl.load_settings(str(SESSION_FILE))
                # Validate session by getting user_id
                if cl.user_id:
                    self._client = cl
                    self._session_mtime = curr_session_mtime
                    self._cookies_mtime = curr_cookies_mtime
                    return cl
            except Exception as e:
                logger.warning(f"Could not load settings from {SESSION_FILE}: {e}")

        # Fallback to cookies file
        if COOKIES_FILE.exists():
            try:
                with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                    cookies_data = json.load(f)
                session_id = cookies_data.get("sessionid")
                if session_id:
                    cl.login_by_sessionid(session_id)
                    cl.dump_settings(str(SESSION_FILE))
                    self._client = cl
                    self._session_mtime = SESSION_FILE.stat().st_mtime if SESSION_FILE.exists() else 0.0
                    self._cookies_mtime = curr_cookies_mtime
                    return cl
            except Exception as e:
                logger.error(f"Failed to login via sessionid cookies: {e}")

        raise ValueError("Instagram is not logged in. Please run 'python scripts/instagram_auth.py' first.")

    def get_profile(self) -> Dict[str, Any]:
        """Fetches the authenticated Instagram profile information."""
        cl = self.get_client()
        try:
            # cl.user_info(cl.user_id) returns media_count, follower_count, and following_count
            info = cl.user_info(cl.user_id)
            profile = {
                "user_id": str(info.pk),
                "username": info.username,
                "full_name": info.full_name,
                "is_private": info.is_private,
                "is_verified": getattr(info, "is_verified", False),
                "profile_pic_url": str(info.profile_pic_url) if info.profile_pic_url else "",
                "follower_count": getattr(info, "follower_count", 0),
                "following_count": getattr(info, "following_count", 0),
                "media_count": getattr(info, "media_count", 0),
                "biography": getattr(info, "biography", ""),
            }
            self._cached_profile = profile
            return profile
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            raise

    def upload_reel(
        self,
        video_path: str,
        caption: str = "",
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads a video as an Instagram Reel (9:16 vertical video).
        """
        v_path = Path(video_path)
        if not v_path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cl = self.get_client()
        logger.info(f"Starting Instagram Reel upload: {v_path.name}")

        thumb_str = None
        if thumbnail_path:
            t_path = Path(thumbnail_path)
            if t_path.exists():
                thumb_str = str(t_path)

        # Upload clip / Reel
        try:
            media = cl.clip_upload(
                path=str(v_path),
                caption=caption,
                thumbnail=thumb_str
            )

            code = getattr(media, "code", "")
            media_id = str(getattr(media, "pk", ""))
            reel_url = f"https://www.instagram.com/reel/{code}/" if code else ""

            logger.info(f"Reel successfully uploaded! Media ID: {media_id}, URL: {reel_url}")
            return {
                "success": True,
                "media_id": media_id,
                "code": code,
                "url": reel_url,
                "caption": caption,
            }
        except Exception as e:
            logger.error(f"Failed to upload reel: {e}")
            raise

    def upload_project_to_reels(
        self,
        project_id: str,
        custom_caption: Optional[str] = None,
        custom_hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads a completed AI short project directly to Instagram Reels.
        Finds the rendered video, thumbnail, and automatically formats an engaging caption.
        """
        proj_dir = PROJECTS_DIR / project_id
        if not proj_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {proj_dir}")

        # Find final video
        renders_dir = proj_dir / "renders"
        video_candidates = [
            renders_dir / f"{project_id}_final.mp4",
            renders_dir / "final_video.mp4",
        ]
        # Or search for any mp4 in renders
        if renders_dir.exists():
            video_candidates.extend(sorted(renders_dir.glob("*final*.mp4"), reverse=True))
            video_candidates.extend(sorted(renders_dir.glob("*.mp4"), reverse=True))

        video_path = None
        for cand in video_candidates:
            if cand.exists() and cand.stat().st_size > 1024:
                video_path = cand
                break

        if not video_path:
            raise FileNotFoundError(f"No rendered video found in {renders_dir}")

        # Find thumbnail
        thumb_candidates = [
            renders_dir / f"{project_id}_thumb.jpg",
            renders_dir / "thumbnail.jpg",
            renders_dir / "thumbnail.png",
        ]
        thumbnail_path = None
        for cand in thumb_candidates:
            if cand.exists():
                thumbnail_path = cand
                break

        # Load project details to create viral Instagram caption
        project_title = "Animated Short"
        script_summary = ""
        try:
            import sqlite3
            db_path = STORAGE_DIR / "toonforge.db"
            if not db_path.exists():
                db_path = ROOT_DIR / "toonforge.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                c = conn.cursor()
                row = c.execute("SELECT title, script, topic FROM projects WHERE id = ?", (project_id,)).fetchone()
                if row:
                    project_title = row[0] or project_title
                    script_summary = (row[1] or "")[:120]
                conn.close()
        except Exception as e:
            logger.warning(f"Could not read project from DB: {e}")

        # Format caption
        if custom_caption:
            final_caption = custom_caption
        else:
            tags = custom_hashtags or [
                "#reels", "#animation", "#cartoon", "#comedy", "#viral",
                "#explorepage", "#trending", "#instaanimation", "#reelsinstagram", "#shorts"
            ]
            tag_str = " ".join(tags)
            clean_title = re.sub(r'["\']', '', project_title).strip()
            final_caption = f"{clean_title} 🎬✨\n\nDrop a ❤️ and follow for more animated comedy shorts!\n.\n.\n{tag_str}"

        return self.upload_reel(
            video_path=str(video_path),
            caption=final_caption,
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None
        )

    def get_recent_reels(self, amount: int = 10) -> List[Dict[str, Any]]:
        """Fetches the authenticated user's recent posts / Reels."""
        cl = self.get_client()
        try:
            medias = cl.user_medias(cl.user_id, amount=amount)
            results = []
            for m in medias:
                code = getattr(m, "code", "")
                results.append({
                    "id": str(getattr(m, "pk", "")),
                    "code": code,
                    "media_type": getattr(m, "media_type", 1),
                    "product_type": getattr(m, "product_type", ""),
                    "caption": getattr(m, "caption_text", "") or "",
                    "view_count": getattr(m, "view_count", 0) or getattr(m, "play_count", 0) or 0,
                    "like_count": getattr(m, "like_count", 0) or 0,
                    "comment_count": getattr(m, "comment_count", 0) or 0,
                    "thumbnail_url": str(getattr(m, "thumbnail_url", "")) if getattr(m, "thumbnail_url", None) else "",
                    "url": f"https://www.instagram.com/reel/{code}/" if getattr(m, "product_type", "") == "clips" else f"https://www.instagram.com/p/{code}/",
                    "created_at": getattr(m, "taken_at", "").isoformat() if hasattr(getattr(m, "taken_at", None), "isoformat") else str(getattr(m, "taken_at", "")),
                })
            return results
        except Exception as e:
            logger.error(f"Failed to fetch recent reels: {e}")
            raise

    def delete_media(self, media_id: str) -> bool:
        """Deletes a post or reel by its media ID or URL code."""
        cl = self.get_client()
        # If code or url was passed, resolve to pk
        if "/" in media_id:
            parts = [p for p in media_id.strip("/").split("/") if p]
            media_id = cl.media_pk_from_code(parts[-1])
        elif not media_id.isdigit():
            media_id = cl.media_pk_from_code(media_id)

        return cl.media_delete(media_id)

    def comment(self, media_id: str, text: str) -> Dict[str, Any]:
        """Posts a comment on a Reel or post."""
        cl = self.get_client()
        if "/" in media_id:
            parts = [p for p in media_id.strip("/").split("/") if p]
            media_id = cl.media_pk_from_code(parts[-1])
        elif not media_id.isdigit():
            media_id = cl.media_pk_from_code(media_id)

        res = cl.media_comment(media_id, text)
        return {
            "id": str(getattr(res, "pk", "")),
            "text": getattr(res, "text", text),
        }

    def like_media(self, media_id: str) -> bool:
        """Likes a post or reel."""
        cl = self.get_client()
        if "/" in media_id:
            parts = [p for p in media_id.strip("/").split("/") if p]
            media_id = cl.media_pk_from_code(parts[-1])
        elif not media_id.isdigit():
            media_id = cl.media_pk_from_code(media_id)

        return cl.media_like(media_id)

    def share_to_story(self, media_id: str, caption: str = "New Reel 🎬 Check it out!", video_path: Optional[str] = None) -> Any:
        """Shares a post/reel to Instagram Story."""
        cl = self.get_client()
        if "/" in media_id:
            parts = [p for p in media_id.strip("/").split("/") if p]
            media_id = cl.media_pk_from_code(parts[-1])
        elif not media_id.isdigit():
            media_id = cl.media_pk_from_code(media_id)

        try:
            return cl.media_share_to_story(media_id, caption=caption)
        except Exception as e:
            logger.warning(f"media_share_to_story failed: {e}. Attempting video story upload fallback if available...")
            if video_path and Path(video_path).exists():
                return cl.video_upload_to_story(video_path, caption=caption)
            raise

    def post_reel_engagement(
        self,
        media_id: str,
        comment_text: Optional[str] = None,
        like: bool = True,
        share_story: bool = True,
        video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete post-reel growth actions:
        1. Likes own reel
        2. Leaves high-engagement pinned first comment
        3. Shares reel to Instagram Story
        """
        actions = {"liked": False, "commented": False, "shared_to_story": False, "errors": []}

        # 1. Like own reel
        if like:
            try:
                self.like_media(media_id)
                actions["liked"] = True
                logger.info(f"[✓] Liked reel {media_id}")
            except Exception as e:
                logger.warning(f"Could not like reel: {e}")
                actions["errors"].append(f"Like failed: {e}")

        # 2. Add pinned first comment
        if comment_text:
            try:
                res_comment = self.comment(media_id, comment_text)
                actions["commented"] = True
                actions["comment_id"] = res_comment.get("id")
                logger.info(f"[✓] Commented on reel {media_id}")
            except Exception as e:
                logger.warning(f"Could not comment on reel: {e}")
                actions["errors"].append(f"Comment failed: {e}")

        # 3. Share to Story
        if share_story:
            try:
                story_res = self.share_to_story(media_id, video_path=video_path)
                actions["shared_to_story"] = True
                actions["story_id"] = str(getattr(story_res, "pk", ""))
                logger.info(f"[✓] Shared reel {media_id} to Story")
            except Exception as e:
                logger.warning(f"Could not share to story: {e}")
                actions["errors"].append(f"Story share failed: {e}")

        return actions


# Singleton instance
instagram_service = InstagramService()
