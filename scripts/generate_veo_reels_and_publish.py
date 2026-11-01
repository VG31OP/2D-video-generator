"""
Autonomous Google Veo Reels Generator & Instagram Publisher
===========================================================
Produces ultra-high-quality vertical (9:16) reels using Google Veo neural video
synthesis (veo-2.0-generate-001 / veo-3.1-generate-preview) combined with
the newly installed skills framework (ai-video-generation, viral-hooks, video-scriptwriting).

Uploads the resulting reel directly to Instagram Reels (@vrj.ai) with full
post-reel engagement boost (like own reel, pinned CTA comment, share to story).
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
from apps.api.providers.veo_provider import GoogleVeoAnimationProvider
from apps.api.services.instagram_service import instagram_service


VEO_REEL_SPEC = {
    "topic": "Google Veo 3 vs OpenAI Sora: The Death of Traditional Hollywood Studios in 2026",
    "title": "Google Veo vs Sora: The Death of Hollywood",
    "art_style": "Cyberpunk Neon Animated",
    "duration": 30,
    "caption": (
        "Google Veo vs OpenAI Sora: Traditional Hollywood studios just had their iPhone moment 🎬🤯🔥\n\n"
        "What used to require a $50,000,000 budget, 400 camera operators, and 6 months in post-production "
        "can now be prompted in 4K with physical fluid dynamics and raytraced lighting in under 60 seconds.\n\n"
        "Here is what Google Veo changes forever:\n"
        "1️⃣ Hollywood-Grade Physics: Fluid camera moves, cinematic dolly zooms, and impossible drone tracking.\n"
        "2️⃣ Temporal Consistency: Characters maintain exact appearance across complex scenes.\n"
        "3️⃣ Zero Production Cost: Indie creators now wield the visual power of Pixar & Warner Bros.\n\n"
        "Are we witnessing the end of traditional film sets?\n"
        "📌 SAVE this reel for later!\n"
        "Drop a ❤️ and follow @vrj.ai for the latest in neural video & AI automation! 🚀\n"
        ".\n.\n"
        "#googleveo #veo #sora #aivideo #futureofcinema #filmmaking #videoproduction #aiagents #generativeai #tech #viral #explorepage #reelsinstagram"
    ),
    "comment": "🎬 Would you watch a full 2-hour movie generated 100% by Google Veo? Tell me your thoughts below! 👇",
    "story_caption": "Google Veo is breaking Hollywood 🎬 Watch the breakdown!",
}


async def main():
    print("=" * 70)
    print("  🎬 GOOGLE VEO HIGH-QUALITY VIDEO PRODUCTION & INSTAGRAM PUBLISHER")
    print("  Engine   : Google Veo (veo-2.0-generate-001 / veo-3.1-generate-preview)")
    print("  Framework: ai-video-generation | viral-hooks | video-scriptwriting")
    print("=" * 70)

    # 1. Initialize Database
    await init_db()

    # 2. Check Google Veo Provider Readiness
    veo_provider = GoogleVeoAnimationProvider()
    print(f"\n[+] Video Engine: {veo_provider.get_provider_name()}")
    print(f"    Engine Type : {veo_provider.get_provider_type()}")
    if veo_provider.is_available():
        print("    Veo Status  : [✓] ACTIVE & CONNECTED TO GOOGLE GENAI CLOUD")
    else:
        print("    Veo Status  : [i] GEMINI_API_KEY is not configured in .env.")
        print("                  Using studio motion graphics fallback until key is added.")

    # 3. Verify Instagram Session
    if not instagram_service.is_authenticated():
        print("\n[✗] Error: Instagram is not authenticated.")
        print("    Please ensure storage/instagram_session.json exists or login first.")
        sys.exit(1)

    profile = instagram_service.get_profile()
    print(f"\n[✓] Connected Instagram Account: @{profile['username']} ({profile.get('full_name', '')})")
    print(f"    Current Posts: {profile.get('media_count', 0)} | Followers: {profile.get('follower_count', 0)}")

    # 4. Create Project
    project_id = f"reel_veo_{uuid.uuid4().hex[:6]}"
    print("\n" + "-" * 70)
    print(f"🎬 [1/3] PRODUCING VEO REEL: {VEO_REEL_SPEC['title']}")
    print(f"   Project ID : {project_id}")
    print(f"   Topic      : {VEO_REEL_SPEC['topic']}")
    print(f"   Visual Arc : {VEO_REEL_SPEC['art_style']} (9:16 Vertical, 1080x1920)")
    print(f"   Format     : Hook-Hold-Payoff (30s target)")
    print("-" * 70)

    async with AsyncSessionLocal() as session:
        proj = Project(
            id=project_id,
            title=VEO_REEL_SPEC["title"],
            topic=VEO_REEL_SPEC["topic"],
            status="Queued",
            duration_seconds=float(VEO_REEL_SPEC["duration"]),
            art_style=VEO_REEL_SPEC["art_style"],
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
            stage_message="Starting Google Veo video generation pipeline...",
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

    # 5. Execute Pipeline with Google Veo Animation Provider
    pipeline = GenerationPipeline(animation_provider=veo_provider)
    await pipeline.execute_project_pipeline(
        project_id=project_id,
        db_session_factory=AsyncSessionLocal,
        progress_callback=log_progress
    )

    print(f"\n[✓] Video generation complete for project: {project_id}")

    # 6. Locate Rendered Output
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
    print(f"📦 [2/3] VEO REEL ASSEMBLED & VERIFIED")
    print(f"   File : {video_path.name}")
    print(f"   Size : {file_size_mb:.2f} MB")
    print(f"   Path : {video_path}")
    print("-" * 70)

    # 7. Publish to Instagram Reels
    print(f"\n🚀 [3/3] PUBLISHING VEO REEL TO INSTAGRAM (@{profile['username']})...")
    try:
        upload_res = instagram_service.upload_reel(
            video_path=str(video_path),
            caption=VEO_REEL_SPEC["caption"],
            thumbnail_path=str(thumb_path) if thumb_path else None
        )

        media_id = upload_res.get("media_id")
        reel_url = upload_res.get("url")
        print("\n" + "*" * 70)
        print("  🎉 GOOGLE VEO REEL PUBLISHED TO INSTAGRAM! 🎉")
        print(f"  Media ID : {media_id}")
        print(f"  URL      : {reel_url}")
        print("*" * 70)

        # 8. Post-Reel Engagement Boost
        print("\n[+] Executing immediate post-reel engagement boost...")
        boost_res = instagram_service.post_reel_engagement(
            media_id=media_id,
            comment_text=VEO_REEL_SPEC["comment"],
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
        print("  ✅ WORKFLOW COMPLETE: VEO REEL PRODUCED AND PUBLISHED LIVE!")
        print(f"  Watch it now at: {reel_url}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n[✗] Failed to publish reel to Instagram: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

