"""
Generate 1 Crazy Trending Tech Reel and Save to Draft
Generates a complete animated short project using the Senior Motion Director Engine & Kinetic Subtitles,
saves all rendered assets into the project database and creates a draft manifest ready for publishing.
"""

import os
import sys
import uuid
import json
import asyncio
from pathlib import Path

# Ensure UTF-8 on Windows stdout
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.database import init_db, AsyncSessionLocal
from apps.api.models.schema import Project, GenerationJob
from apps.api.services.pipeline import GenerationPipeline
from apps.api.config import PROJECTS_DIR, STORAGE_DIR

DRAFT_CONFIG = {
    "topic": "Autonomous AI Humanoid Swarms: Tesla Optimus & Figure 02 Just Got Upgraded With Multimodal Reasoning",
    "title": "Autonomous AI Humanoids Are Taking Over 2026",
    "art_style": "Cyberpunk Neon Animated",
    "duration": 30,
    "caption": (
        "Autonomous AI Humanoid Robots are officially entering factories in 2026 🤯🤖\n\n"
        "Forget chatbots. The biggest tech leap this week is Physical AI:\n\n"
        "1️⃣ Tesla Optimus Gen 3: Now sorting parts and navigating dynamic warehouse floors with zero human teleoperation.\n"
        "2️⃣ Figure 02: Powered by real-time visual-language neural models, holding natural voice conversations while packing boxes at superhuman speed.\n"
        "3️⃣ Autonomous Swarm Coordination: Multiple humanoids communicating peer-to-peer over local neural nets to solve complex tasks together.\n\n"
        "Are we ready for robot coworkers by 2027? Drop your thoughts below! 👇\n\n"
        "📌 SAVE this reel & follow @vrj.ai for the craziest daily AI & robotics breakthroughs! 🚀\n"
        ".\n.\n"
        "#ai #humanoid #robotics #tesla #futuretech #technews #innovation #cyberpunk #aiagents #reelsinstagram #viral #explorepage"
    ),
    "pinned_comment": "🤖 Would you work alongside an autonomous humanoid robot coworker? Vote YES or NO below! 👇",
    "story_caption": "Physical AI just got real 🤯 Watch the humanoid robot breakdown!"
}

async def make_trending_draft():
    await init_db()
    project_id = f"draft_humanoids_{uuid.uuid4().hex[:6]}"
    
    print("\n" + "=" * 70)
    print("🎬 CREATING CRAZY TRENDING TECH SHORT (SAVING TO DRAFT)")
    print(f"   Project ID : {project_id}")
    print(f"   Topic      : {DRAFT_CONFIG['topic']}")
    print(f"   Title      : {DRAFT_CONFIG['title']}")
    print(f"   Style      : {DRAFT_CONFIG['art_style']}")
    print("=" * 70)

    # 1. Register project in database
    async with AsyncSessionLocal() as session:
        proj = Project(
            id=project_id,
            title=DRAFT_CONFIG["title"],
            topic=DRAFT_CONFIG["topic"],
            status="Queued",
            duration_seconds=float(DRAFT_CONFIG["duration"]),
            art_style=DRAFT_CONFIG["art_style"],
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
            current_stage="Initiation",
            progress_percent=5,
            stage_message="Starting senior motion graphics pipeline..."
        )
        session.add(job)
        await session.commit()

    # 2. Execute pipeline with Senior Motion Director Engine
    pipeline = GenerationPipeline()
    print("\n[Pipeline] Launching autonomous generation pipeline...")
    result = await pipeline.execute_project_pipeline(
        project_id=project_id,
        db_session_factory=AsyncSessionLocal,
        progress_callback=lambda p: print(f"[{p.get('stage')}] {p.get('progress')}% - {p.get('message')}")
    )

    # 3. Locate rendered video & thumbnail
    proj_dir = PROJECTS_DIR / project_id
    renders_dir = proj_dir / "renders"
    video_path = renders_dir / f"{project_id}_final.mp4"
    thumb_path = renders_dir / "thumbnail.jpg"

    if not video_path.exists():
        # Look for any mp4 in renders
        mp4s = list(renders_dir.glob("*.mp4"))
        if mp4s:
            video_path = mp4s[0]

    print(f"\n[Video] Rendered Video: {video_path} ({video_path.stat().st_size} bytes)")
    print(f"[Thumbnail] Thumbnail: {thumb_path}")

    # 4. Save to dedicated Drafts directory
    drafts_dir = STORAGE_DIR / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)
    draft_folder = drafts_dir / project_id
    draft_folder.mkdir(parents=True, exist_ok=True)

    import shutil
    draft_video = draft_folder / f"{project_id}_reel.mp4"
    draft_thumb = draft_folder / f"{project_id}_thumb.jpg"
    shutil.copy(str(video_path), str(draft_video))
    if thumb_path.exists():
        shutil.copy(str(thumb_path), str(draft_thumb))

    # Draft metadata manifest
    manifest = {
        "project_id": project_id,
        "is_draft": True,
        "topic": DRAFT_CONFIG["topic"],
        "title": DRAFT_CONFIG["title"],
        "art_style": DRAFT_CONFIG["art_style"],
        "duration_seconds": DRAFT_CONFIG["duration"],
        "video_path": str(draft_video.resolve()),
        "thumbnail_path": str(draft_thumb.resolve()) if draft_thumb.exists() else "",
        "caption": DRAFT_CONFIG["caption"],
        "pinned_comment": DRAFT_CONFIG["pinned_comment"],
        "story_caption": DRAFT_CONFIG["story_caption"],
        "created_at": str(asyncio.get_event_loop().time())
    }

    manifest_path = draft_folder / "draft_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Update project metadata in DB to mark as Draft ready
    async with AsyncSessionLocal() as session:
        p = await session.get(Project, project_id)
        if p:
            meta = json.loads(p.metadata_json or "{}")
            meta["is_draft"] = True
            meta["draft_manifest"] = str(manifest_path)
            meta["instagram_caption"] = DRAFT_CONFIG["caption"]
            p.metadata_json = json.dumps(meta)
            p.status = "Draft"
            await session.commit()

    print("\n" + "=" * 70)
    print("✅ REEL GENERATED AND SAVED TO DRAFT SUCCESSFULLY!")
    print(f"   Project ID     : {project_id}")
    print(f"   Draft Folder   : {draft_folder}")
    print(f"   Draft Video    : {draft_video}")
    print(f"   Draft Manifest : {manifest_path}")
    print("   To publish to Instagram anytime, simply run:")
    print(f"   python scripts/instagram_manager.py publish-project {project_id}")
    print("=" * 70)
    return project_id

if __name__ == "__main__":
    asyncio.run(make_trending_draft())
