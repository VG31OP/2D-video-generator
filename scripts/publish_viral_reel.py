"""
Publish Viral Reel - Powered by omer-metin/skills-for-antigravity
=================================================================
This autonomous video production and publishing engine implements the exact
principles from the newly installed skills:
- ai-video-generation: Seed Frame Technique, Impossible Camera, Multiplane Parallax
- viral-hooks: Pattern Interrupt, Curiosity Gap, 0-2s Scroll Stopper
- video-scriptwriting: The Hook-Hold-Payoff Structure (Hook 0-3s, Hold 4-22s, Payoff 23-29s)
- video-production: 9:16 Vertical (1080x1920 30fps), Safe Zone Subtitles (MarginV=440), High CTR Cover

Publishes directly to Instagram Reels (@vrj.ai) with full post-reel boost engagement.
"""

import os
import sys
import uuid
import datetime
import asyncio
from pathlib import Path

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.database import init_db, AsyncSessionLocal
from apps.api.models.schema import Project, GenerationJob
from apps.api.services.pipeline import GenerationPipeline
from apps.api.services.instagram_service import instagram_service


REEL_SPEC = {
    "topic": "Why Autonomous AI Agents Are Replacing 9-to-5 Jobs in 2026",
    "title": "Why AI Agents Are Replacing 9-to-5 Jobs",
    "art_style": "Cyberpunk Neon Animated",
    "duration": 30,
    "caption": (
        "Why Autonomous AI Agents are replacing the 9-to-5 grind in 2026 🤖💼🔥\n\n"
        "Most people are still treating AI like a glorified search bar. "
        "Meanwhile, smart builders are deploying autonomous agents that run complete businesses while they sleep.\n\n"
        "Here's the massive shift happening right now:\n"
        "❌ Chatbots: Wait for you to type every single prompt.\n"
        "✅ AI Agents: You assign 1 high-level goal — they analyze competitors, write full-stack code, and publish content autonomously.\n\n"
        "The future isn't about working harder; it's about managing autonomous agents.\n\n"
        "📌 SAVE this reel for later!\n"
        "Drop a ❤️ and follow @vrj.ai for daily secret AI breakdowns & automation secrets! 🚀\n"
        ".\n.\n"
        "#aiagents #artificialintelligence #futureofwork #techtrends #aitools #automation #coding #softwareengineer #chatgpt #deepseek #viral #explorepage #reelsinstagram"
    ),
    "comment": "🤖 Are you using autonomous agents in your daily workflow yet? Drop your favorite tool below! 👇",
    "story_caption": "The AI Agent Revolution is here 🤖 Watch the breakdown!",
}


async def main():
    print("=" * 70)
    print("  🚀 TOONFORGE VIRAL REEL PRODUCTION & INSTAGRAM PUBLISHER")
    print("  Framework: omer-metin/skills-for-antigravity")
    print("  Skills   : ai-video-generation | viral-hooks | video-scriptwriting")
    print("=" * 70)

    # 1. Initialize Database
    await init_db()

    # 2. Verify Instagram Authentication
    if not instagram_service.is_authenticated():
        print("[✗] Error: Instagram is not authenticated.")
        print("    Please ensure storage/instagram_session.json exists or login first.")
        sys.exit(1)

    profile = instagram_service.get_profile()
    print(f"\n[✓] Connected Instagram Account: @{profile['username']} ({profile.get('full_name', '')})")
    print(f"    Current Posts: {profile.get('media_count', 0)} | Followers: {profile.get('follower_count', 0)}")

    # 3. Create Project in DB
    project_id = f"reel_skills_{uuid.uuid4().hex[:6]}"
    print("\n" + "-" * 70)
    print(f"🎬 [1/3] PRODUCING REEL: {REEL_SPEC['title']}")
    print(f"   Project ID : {project_id}")
    print(f"   Topic      : {REEL_SPEC['topic']}")
    print(f"   Visual Arc : {REEL_SPEC['art_style']} (9:16 Vertical, 1080x1920)")
    print(f"   Structure  : Hook-Hold-Payoff (30s target)")
    print("-" * 70)

    async with AsyncSessionLocal() as session:
        proj = Project(
            id=project_id,
            title=REEL_SPEC["title"],
            topic=REEL_SPEC["topic"],
            status="Queued",
            duration_seconds=float(REEL_SPEC["duration"]),
            art_style=REEL_SPEC["art_style"],
            language="English",
            width=1080,
            height=1920,
            fps=30
        )
        session.add(proj)

        job = GenerationJob(
            id=str(uuid.uuid4()),
            project_id=project_id,
            status="Running",
            progress_percent=0,
            current_stage="Initializing",
            stage_message="Starting generation pipeline with viral skills framework...",
            started_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        )
        session.add(job)
        await session.commit()

    # Progress logger
    async def log_progress(data: dict):
        stage = data.get("stage", "")
        progress = data.get("progress", 0)
        msg = data.get("message", "")
        print(f"  [{progress:3d}%] [{stage}] {msg}")

    # 4. Execute Autonomous Generation Pipeline
    pipeline = GenerationPipeline()
    await pipeline.execute_project_pipeline(
        project_id=project_id,
        db_session_factory=AsyncSessionLocal,
        progress_callback=log_progress
    )

    print(f"\n[✓] Video generation complete for project: {project_id}")

    # 5. Locate Rendered Output
    proj_dir = ROOT_DIR / "storage" / "projects" / project_id / "renders"
    video_candidates = list(proj_dir.glob("*final*.mp4")) + list(proj_dir.glob("*.mp4"))
    if not video_candidates:
        print(f"[✗] Error: Rendered video not found in {proj_dir}")
        sys.exit(1)

    video_path = video_candidates[0]
    thumb_candidates = list(proj_dir.glob("*.jpg")) + list(proj_dir.glob("*.png"))
    thumb_path = thumb_candidates[0] if thumb_candidates else None

    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    print("\n" + "-" * 70)
    print(f"📦 [2/3] VIDEO READY FOR BROADCAST")
    print(f"   File : {video_path.name}")
    print(f"   Size : {file_size_mb:.2f} MB")
    print(f"   Path : {video_path}")
    print("-" * 70)

    # 6. Publish to Instagram Reels
    print(f"\n🚀 [3/3] PUBLISHING TO INSTAGRAM REELS (@{profile['username']})...")
    try:
        upload_res = instagram_service.upload_reel(
            video_path=str(video_path),
            caption=REEL_SPEC["caption"],
            thumbnail_path=str(thumb_path) if thumb_path else None
        )

        media_id = upload_res.get("media_id")
        reel_url = upload_res.get("url")
        print("\n" + "*" * 70)
        print("  🎉 REEL SUCCESSFULLY PUBLISHED TO INSTAGRAM! 🎉")
        print(f"  Media ID : {media_id}")
        print(f"  URL      : {reel_url}")
        print("*" * 70)

        # 7. Post-Reel Engagement Boost (Like, CTA Comment, Story Share)
        print("\n[+] Executing immediate post-reel engagement boost...")
        boost_res = instagram_service.post_reel_engagement(
            media_id=media_id,
            comment_text=REEL_SPEC["comment"],
            like=True,
            share_story=True,
            video_path=str(video_path)
        )

        print(f"    - Liked own reel     : {'[✓] SUCCESS' if boost_res['liked'] else '[✗] FAILED'}")
        print(f"    - Posted CTA comment : {'[✓] SUCCESS' if boost_res['commented'] else '[✗] FAILED'}")
        print(f"    - Shared to Story    : {'[✓] SUCCESS' if boost_res['shared_to_story'] else '[✗] FAILED'}")
        if boost_res.get("errors"):
            print(f"    - Notes: {boost_res['errors']}")

        print("\n" + "=" * 70)
        print("  ✅ WORKFLOW FINISHED: VIDEO CREATED AND PUBLISHED TO INSTAGRAM!")
        print(f"  Watch it live at: {reel_url}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[✗] Failed to publish reel to Instagram: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

