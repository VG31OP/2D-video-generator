"""
Autonomous Trending Tech Reels Generator & Publisher
Generates 2 viral tech reels using ToonForge pipeline, uploads them to Instagram Reels,
and executes post-reel engagement (like own reel, pinned CTA comment, and share to story).
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


REELS_CONFIG = [
    {
        "id_prefix": "reel_aitools",
        "topic": "3 Secret AI Tools in 2026 That Feel Completely Illegal to Know",
        "title": "3 Secret AI Tools That Feel Illegal",
        "art_style": "Cyberpunk Neon Animated",
        "duration": 30,
        "caption": (
            "3 Secret AI Tools that feel completely illegal to know in 2026 🤯🔥\n\n"
            "Stop paying for 10 different subscriptions. These 3 tools do 90% of your work in seconds:\n\n"
            "1️⃣ DeepSeek & Claude: Writes complete software applications with 1 single prompt.\n"
            "2️⃣ NotebookLM: Converts hundreds of pages of messy PDFs into a 10-minute conversational podcast.\n"
            "3️⃣ Gamma App: Turns raw notes into a 20-slide presentation in 15 seconds flat.\n\n"
            "📌 SAVE this reel so you don't lose them!\n"
            "Drop a ❤️ and follow @vrj.ai for daily secret AI hacks & tech automation! 🚀\n"
            ".\n.\n"
            "#ai #aitools #artificialintelligence #tech #futuretech #technews #productivity #techhacks #reels #viral #explorepage #reelsinstagram"
        ),
        "comment": "📌 Save this reel so you don't lose these tools! Which one are you trying first? Drop it below! 👇",
        "story_caption": "3 Secret AI Tools in 2026 🔥 Watch now!",
    },
    {
        "id_prefix": "reel_aiagents",
        "topic": "Why Autonomous AI Agents Are Replacing 9-to-5 Jobs in 2026",
        "title": "Why AI Agents Are Replacing 9-to-5 Jobs",
        "art_style": "Modern 2D Cartoon",
        "duration": 30,
        "caption": (
            "Why Autonomous AI Agents are replacing 9-to-5 jobs in 2026 🤖💼\n\n"
            "Everyone is still prompting ChatGPT like a Google search bar. But smart creators are building AI Agents that work while they sleep.\n\n"
            "Here is the difference:\n"
            "❌ Chatbot: Waits for you to give it every single command.\n"
            "✅ Autonomous Agent: You give it one goal—research 50 competitors, code a script, or create viral videos—and it executes hundreds of steps completely by itself.\n\n"
            "The future belongs to those who build and manage agents, not those who compete with them.\n\n"
            "Share this with someone who needs to hear this! 💡\n"
            "Follow @vrj.ai for the latest tech secrets and automation breakdowns. 🙌\n"
            ".\n.\n"
            "#aiagents #automation #tech #coding #futureofwork #chatgpt #techtrends #innovation #reelsinstagram #viral #explorepage #ai"
        ),
        "comment": "🤖 Are you using AI agents in your daily workflow yet? Tell me your favorite agent below! 👇",
        "story_caption": "The AI Agent Revolution is here 🤖 Watch the full breakdown!",
    }
]


async def generate_single_reel(cfg: dict) -> str:
    """Generates a complete animated short project and returns project_id."""
    project_id = f"{cfg['id_prefix']}_{uuid.uuid4().hex[:6]}"
    print("\n" + "=" * 65)
    print(f"🎬 GENERATING REEL: {cfg['title']}")
    print(f"   Project ID : {project_id}")
    print(f"   Topic      : {cfg['topic']}")
    print(f"   Style      : {cfg['art_style']}")
    print("=" * 65)

    async with AsyncSessionLocal() as session:
        proj = Project(
            id=project_id,
            title=cfg["title"],
            topic=cfg["topic"],
            status="Queued",
            duration_seconds=float(cfg["duration"]),
            art_style=cfg["art_style"],
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
            stage_message="Starting generation pipeline...",
            started_at=datetime.datetime.utcnow()
        )
        session.add(job)
        await session.commit()

    # Progress logger
    async def log_progress(data: dict):
        stage = data.get("stage", "")
        progress = data.get("progress", 0)
        msg = data.get("message", "")
        print(f"  [{progress:3d}%] [{stage}] {msg}")

    pipeline = GenerationPipeline()
    await pipeline.execute_project_pipeline(
        project_id=project_id,
        db_session_factory=AsyncSessionLocal,
        progress_callback=log_progress
    )

    print(f"[✓] Generation complete for project: {project_id}")
    return project_id


async def main():
    print("=" * 65)
    print("   AUTONOMOUS INSTAGRAM REELS PRODUCTION & PUBLISHING ENGINE   ")
    print("=" * 65)

    # 1. Verify DB
    await init_db()

    # 2. Verify Instagram Authentication
    if not instagram_service.is_authenticated():
        print("[✗] Error: Instagram is not authenticated.")
        print("    Please run 'python scripts/instagram_manager.py login' first.")
        sys.exit(1)

    profile = instagram_service.get_profile()
    print(f"[✓] Connected Account: @{profile['username']} ({profile.get('full_name', '')})")
    print(f"    Current Posts: {profile.get('media_count', 0)}")
    print(f"    Followers    : {profile.get('follower_count', 0)}")
    print("=" * 65)

    published_reels = []

    for i, cfg in enumerate(REELS_CONFIG, 1):
        print(f"\n>>> [Reel {i}/2] Processing: '{cfg['title']}'...")
        
        # Step A: Generate the video
        project_id = await generate_single_reel(cfg)

        # Find rendered video
        proj_dir = ROOT_DIR / "storage" / "projects" / project_id / "renders"
        video_candidates = list(proj_dir.glob("*final*.mp4")) + list(proj_dir.glob("*.mp4"))
        if not video_candidates:
            print(f"[✗] Rendered video not found in {proj_dir}")
            continue

        video_path = video_candidates[0]
        thumb_candidates = list(proj_dir.glob("*.jpg")) + list(proj_dir.glob("*.png"))
        thumb_path = thumb_candidates[0] if thumb_candidates else None

        print(f"\n[+] Video ready: {video_path.name} ({video_path.stat().st_size / 1024 / 1024:.2f} MB)")

        # Step B: Upload to Instagram Reels
        print("[+] Publishing video to Instagram Reels...")
        try:
            upload_res = instagram_service.upload_reel(
                video_path=str(video_path),
                caption=cfg["caption"],
                thumbnail_path=str(thumb_path) if thumb_path else None
            )

            media_id = upload_res.get("media_id")
            reel_url = upload_res.get("url")
            print("\n" + "*" * 60)
            print("  🎉 REEL PUBLISHED TO INSTAGRAM! 🎉")
            print(f"  Media ID : {media_id}")
            print(f"  URL      : {reel_url}")
            print("*" * 60)

            # Step C: Post-reel Boost (Like, Comment, Story)
            print("\n[+] Executing post-reel engagement actions...")
            boost_res = instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=cfg["comment"],
                like=True,
                share_story=True,
                video_path=str(video_path)
            )

            print(f"    - Liked own reel     : {'[✓] SUCCESS' if boost_res['liked'] else '[✗] FAILED'}")
            print(f"    - Posted CTA comment : {'[✓] SUCCESS' if boost_res['commented'] else '[✗] FAILED'}")
            print(f"    - Shared to Story    : {'[✓] SUCCESS' if boost_res['shared_to_story'] else '[✗] FAILED'}")
            if boost_res.get("errors"):
                print(f"    - Notes: {boost_res['errors']}")

            published_reels.append({
                "title": cfg["title"],
                "media_id": media_id,
                "url": reel_url,
                "boost": boost_res
            })

            # Cool-down wait between uploads to keep session healthy
            if i < len(REELS_CONFIG):
                print("\n[i] Waiting 10 seconds before starting Reel 2...")
                await asyncio.sleep(10)

        except Exception as e:
            print(f"[✗] Failed to publish reel: {e}")

    # Summary
    print("\n" + "=" * 65)
    print("             PRODUCTION & PUBLISHING COMPLETE!             ")
    print("=" * 65)
    for r in published_reels:
        print(f"• {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  Actions: Liked ({r['boost']['liked']}), Commented ({r['boost']['commented']}), Story ({r['boost']['shared_to_story']})")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
