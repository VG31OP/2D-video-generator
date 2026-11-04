"""
Full Pipeline Runner: How Face ID Actually Works
Renders 3D animation, muxes with broadcast audio, publishes to Instagram, and executes engagement boost.
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service

REEL_DIR = ROOT_DIR / "storage" / "reels" / "zach_face_id"
VO_WAV = REEL_DIR / "audio" / "vo.wav"
SILENT_MP4 = REEL_DIR / "silent.mp4"
FINAL_MP4 = REEL_DIR / "zach_face_id_final.mp4"
COVER_JPG = REEL_DIR / "cover.jpg"

def step1_render_3d():
    print("[1/4] Rendering 3D Three.js animation via Playwright Chromium (30fps)...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        ["node", "render.mjs", "video", "silent.mp4", "30"],
        cwd=str(REEL_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in proc.stdout:
        line_str = line.strip()
        if "frame" in line_str or "done" in line_str:
            print(f"    - {line_str}", flush=True)
    proc.wait()
    if proc.returncode != 0 or not SILENT_MP4.exists():
        raise RuntimeError("3D frame rendering failed!")
    print(f"    [✓] Visual frames rendered successfully ({SILENT_MP4.stat().st_size / 1024 / 1024:.2f} MB)")

def step2_mux_broadcast_video():
    print("[2/4] Muxing audio & scaling to 1080x1920 vertical with EBU R128 loudness normalization...")
    cmd_mux = [
        "ffmpeg", "-v", "error", "-y",
        "-i", str(SILENT_MP4),
        "-i", str(VO_WAV),
        "-map", "0:v",
        "-map", "1:a",
        "-vf", "scale=1080:1920:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-af", "apad,loudnorm=I=-14:TP=-1.5",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(FINAL_MP4)
    ]
    subprocess.run(cmd_mux, check=True)

    # Extract High-CTR Cover Frame at t=14.8s (dot projector firing lasers)
    cmd_thumb = [
        "ffmpeg", "-y", "-ss", "00:00:14.800",
        "-i", str(FINAL_MP4),
        "-vframes", "1", "-q:v", "2",
        str(COVER_JPG)
    ]
    subprocess.run(cmd_thumb, capture_output=True)

    # Clean silent render pass
    if SILENT_MP4.exists():
        SILENT_MP4.unlink()
    print(f"    [✓] Master video created: {FINAL_MP4.name} ({FINAL_MP4.stat().st_size / 1024 / 1024:.2f} MB)")

def step3_publish_instagram():
    print("[3/4] Uploading Reel to Instagram (@vrj.ai)...")
    caption = (
        "Wait... is this REALLY how Face ID scans your face?! 🤯📱✨\n\n"
        "Here is what actually happens when you unlock in pitch black:\n"
        "• Your camera is NEVER turned on 🚫\n"
        "• Flood illuminator coats your face in invisible infrared light 💡\n"
        "• A microscopic dot projector fires 30,000 laser beams across your skin 🎯\n"
        "• The neural engine maps your unique 3D depth mesh in milliseconds ⚡\n\n"
        "Did you think the camera was taking a photo before? Drop your thoughts below! 👇\n\n"
        "Follow @vrj.ai for more insane 3D tech explainers, viral engineering & digital secrets! 🚀\n"
        ".\n.\n"
        "#faceid #apple #tech #iphone #3danimation #howitworks #technology #animation #viral #reels #explainer #vrjai #interestingfacts #engineering"
    )
    comment = "Did you think Face ID was just a normal selfie camera? Drop your thoughts below! 👇"

    res = instagram_service.upload_reel(
        video_path=str(FINAL_MP4),
        caption=caption,
        thumbnail_path=str(COVER_JPG) if COVER_JPG.exists() else None
    )
    media_id = res.get("media_id")
    url = res.get("url")
    print(f"    [✓] Reel published! URL: {url} (Media ID: {media_id})")

    if media_id:
        print("[4/4] Executing engagement boost (like, pinned comment, story share)...")
        boost_res = instagram_service.post_reel_engagement(
            media_id=media_id,
            comment_text=comment,
            like=True,
            share_story=True,
            video_path=str(FINAL_MP4)
        )
        print(f"    [✓] Engagement boost complete: {boost_res}")

    return media_id, url

def step4_register_db(media_id, url):
    db_path = ROOT_DIR / "storage" / "toonforge.db"
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO projects (
            id, title, topic, status, duration_seconds, width, height, fps,
            language, art_style, script_text, video_url, thumbnail_url,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "zach_face_id",
        "How Face ID Actually Works",
        "How Face ID Actually Works: 30,000 invisible infrared lasers, flood illuminator and 3D depth mesh",
        "Completed",
        40.84,
        1080,
        1920,
        30,
        "en-US",
        "Zack D. Films 3D Explainer",
        "When you unlock your phone in the pitch dark...",
        str(FINAL_MP4),
        str(COVER_JPG),
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    print("    [✓] Registered project in toonforge.db")

if __name__ == "__main__":
    print("=" * 70)
    print(" 🚀 STARTING FULL AUTONOMOUS PIPELINE: HOW FACE ID ACTUALLY WORKS")
    print("=" * 70)
    step1_render_3d()
    step2_mux_broadcast_video()
    media_id, url = step3_publish_instagram()
    step4_register_db(media_id, url)
    print("=" * 70)
    print(" 🎉 VIDEO 1 (FACE ID) PUBLISHED SUCCESSFULLY! 🎉")
    print(f" URL: {url}")
    print("=" * 70)

