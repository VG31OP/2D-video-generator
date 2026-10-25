"""
Instagram API Endpoints for ToonForge
Allows viewing Instagram profile metrics, triggering browser login,
and publishing videos or projects directly to Instagram Reels.
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, BackgroundTasks

from apps.api.config import STORAGE_DIR
from apps.api.services.instagram_service import instagram_service

router = APIRouter(prefix="/api/instagram", tags=["instagram"])

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROJECT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_storage_path(path_str: str) -> Path:
    target_path = Path(path_str).resolve()
    storage_root = STORAGE_DIR.resolve()
    try:
        target_path.relative_to(storage_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Path must remain within the storage directory.")
    if not target_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {target_path.name}")
    return target_path


class ReelUploadRequest(BaseModel):
    project_id: Optional[str] = None
    video_path: Optional[str] = None
    caption: Optional[str] = None
    thumbnail_path: Optional[str] = None


class CommentRequest(BaseModel):
    media_id: str
    text: str


@router.get("/status")
def get_instagram_status():
    """Checks authentication status and returns profile analytics if logged in."""
    is_auth = instagram_service.is_authenticated()
    if not is_auth:
        return {
            "authenticated": False,
            "profile": None,
            "message": "Not logged in. Use 'python scripts/instagram_manager.py login' or click Connect below."
        }

    try:
        profile = instagram_service.get_profile()
        return {
            "authenticated": True,
            "profile": profile,
            "message": "Instagram connected"
        }
    except Exception as e:
        return {
            "authenticated": False,
            "profile": None,
            "error": str(e),
            "message": "Session expired or invalid. Please re-authenticate."
        }


@router.post("/login/launch-browser")
async def launch_browser_login(background_tasks: BackgroundTasks):
    """Launches the interactive browser login capture process."""
    def _run_auth():
        python_exe = sys.executable
        script = ROOT_DIR / "scripts" / "instagram_auth.py"
        subprocess.run([python_exe, str(script)], cwd=str(ROOT_DIR))

    background_tasks.add_task(_run_auth)
    return {
        "status": "launched",
        "message": "Browser window launched. Please log into Instagram in the browser window."
    }


@router.post("/upload")
def upload_reel(req: ReelUploadRequest):
    """Publishes a video or short project to Instagram Reels."""
    if not instagram_service.is_authenticated():
        raise HTTPException(
            status_code=401,
            detail="Instagram not authenticated. Run 'python scripts/instagram_manager.py login'."
        )

    try:
        if req.project_id:
            if not PROJECT_ID_PATTERN.match(req.project_id):
                raise HTTPException(status_code=400, detail="Invalid project_id format.")
            res = instagram_service.upload_project_to_reels(
                project_id=req.project_id,
                custom_caption=req.caption
            )
        elif req.video_path:
            valid_video = _validate_storage_path(req.video_path)
            valid_thumb = _validate_storage_path(req.thumbnail_path) if req.thumbnail_path else None
            res = instagram_service.upload_reel(
                video_path=str(valid_video),
                caption=req.caption or "",
                thumbnail_path=str(valid_thumb) if valid_thumb else None
            )
        else:
            raise HTTPException(status_code=400, detail="Must provide either project_id or video_path.")

        return res
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload to Instagram failed: {str(e)}")


@router.get("/reels")
def list_recent_reels(count: int = 12):
    """Fetches recent posts and Reels with view/like counts."""
    if not instagram_service.is_authenticated():
        raise HTTPException(status_code=401, detail="Instagram not authenticated.")

    try:
        reels = instagram_service.get_recent_reels(amount=count)
        return {"reels": reels}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reels/{media_id}")
def delete_reel(media_id: str):
    """Deletes a post or reel."""
    if not instagram_service.is_authenticated():
        raise HTTPException(status_code=401, detail="Instagram not authenticated.")

    try:
        success = instagram_service.delete_media(media_id)
        return {"success": success, "media_id": media_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comment")
def post_comment(req: CommentRequest):
    """Posts a comment on a Reel."""
    if not instagram_service.is_authenticated():
        raise HTTPException(status_code=401, detail="Instagram not authenticated.")

    try:
        res = instagram_service.comment(req.media_id, req.text)
        return {"success": True, "comment": res}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
