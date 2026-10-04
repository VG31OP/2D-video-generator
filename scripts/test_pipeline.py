import asyncio
import os
import sys
import uuid
import subprocess
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from apps.api.database import init_db, AsyncSessionLocal
from apps.api.models.schema import Project
from apps.api.services.pipeline import GenerationPipeline
from apps.api.providers.system_detector import detect_system_capabilities
from apps.api.config import settings

async def main():
    print("==================================================")
    print("   TOONFORGE AUTONOMOUS AI SHORT GENERATION TEST   ")
    print("==================================================")
    
    # 1. System health check & Provider Diagnostic Table
    caps = await detect_system_capabilities()
    
    print("\n[SYSTEM DIAGNOSTICS]")
    print(f"Python:   {caps['system']['python_version']} ({caps['system']['os']})")
    print(f"Hardware: GPU={caps['hardware']['gpu_name']} | CUDA={caps['hardware']['cuda_available']}")
    print(f"LLM:      Ollama={caps['llm']['ollama_available']}")
    print(f"Visual:   ComfyUI={caps['visual']['comfyui_available']}")
    print(f"Voice:    EdgeTTS={caps['voice']['edge_tts_available']} | Kokoro={caps['voice']['kokoro_available']}")
    print(f"Speech:   Whisper={caps['speech']['whisper_available']}")
    print(f"Render:   FFmpeg={caps['rendering']['ffmpeg_available']} (libass: {caps['rendering']['libass_supported']})")
    print("--------------------------------------------------")

    await init_db()
    
    project_id = str(uuid.uuid4())
    topic = "A lazy student discovers his AI assistant has been doing his homework"
    
    print(f"\n[1/4] Initializing Project: '{topic}'")
    print(f"      Project ID: {project_id}")
    
    async with AsyncSessionLocal() as session:
        proj = Project(
            id=project_id,
            title="AI Did My Homework",
            topic=topic,
            status="Queued",
            duration_seconds=30,
            art_style="Modern 2D Cartoon",
            language="English"
        )
        session.add(proj)
        await session.commit()

    pipeline = GenerationPipeline()
    
    async def log_progress(event):
        pct = event.get('progress', 0)
        stage = event.get('stage', '')
        msg = event.get('message', '')
        print(f"  [{pct:3d}%] [{stage:20s}] {msg}")
        
    print("\n[2/4] Executing Autonomous AI Pipeline...")
    result = await pipeline.execute_project_pipeline(
        project_id=project_id,
        db_session_factory=AsyncSessionLocal,
        progress_callback=log_progress
    )
    
    print("\n[3/4] Generation Complete!")
    print(f"      Video URL: {result.get('video_url')}")
    print(f"      Thumbnail: {result.get('thumbnail_url')}")
    print(f"      Duration:  {result.get('duration'):.1f}s")
    print(f"      QC Valid:  {result.get('qc', {}).get('valid')}")

    # Inspect story script details
    async with AsyncSessionLocal() as session:
        proj_record = await session.get(Project, project_id)
        if proj_record and proj_record.story_json:
            story = json.loads(proj_record.story_json)
            print("\n" + "=" * 50)
            print("GENERATED SHORTS COMEDY SCRIPT")
            print("=" * 50)
            print(f"Title: {story.get('title')}")
            print(f"Premise: {story.get('premise')}")
            print(f"Hook: {story.get('hook')}")
            print(f"Punchline: {story.get('punchline')}")
            if "quality_eval" in story:
                q = story["quality_eval"]
                print(f"Script Quality Score: {q.get('overall_score')}/10 (Passed: {q.get('passed')})")
                print(f"Breakdown: Hook={q.get('hook_score')} Pacing={q.get('pacing_score')} Dialogue={q.get('dialogue_score')} Humor={q.get('humor_score')} Chars={q.get('personality_score')} Ending={q.get('ending_score')}")
            print("\nCHARACTERS:")
            for ch in story.get("characters", []):
                print(f"  - {ch.get('name')}: {ch.get('personality')} (Voice: {ch.get('voice_type')}, Pitch: {ch.get('voice_pitch')}, Rate: {ch.get('voice_rate')})")
            print("\nSCENE-BY-SCENE DIALOGUE & TIMING:")
            for sc in story.get("scenes", []):
                p_before = sc.get('pause_before', 0.0)
                p_after = sc.get('pause_after', 0.0)
                print(f"  [Scene {sc.get('scene_id')}] ({sc.get('emotion', 'neutral').upper()}) {sc.get('speaker')}: \"{sc.get('dialogue')}\" [Pause Before: {p_before}s, After: {p_after}s]")
            if story.get("cta"):
                print(f"\nCTA: {story.get('cta')}")

    # Inspect generated video with FFprobe
    proj_dir = Path(__file__).resolve().parent.parent / "storage" / "projects" / project_id
    final_video_path = proj_dir / "renders" / f"{project_id}_final.mp4"
    
    print("\n[4/4] Inspecting final MP4 with FFprobe:")
    v_info = {}
    if final_video_path.exists():
        ffprobe_cmd = [
            settings.FFPROBE_PATH,
            "-v", "error",
            "-show_entries", "stream=width,height,codec_name,r_frame_rate,duration",
            "-show_entries", "format=duration,size,bit_rate",
            "-of", "json",
            str(final_video_path)
        ]
        probe_res = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        if probe_res.returncode == 0:
            probe_data = json.loads(probe_res.stdout)
            streams = probe_data.get("streams", [])
            v_stream = next((s for s in streams if s.get("width")), {})
            a_stream = next((s for s in streams if not s.get("width")), {})
            fmt = probe_data.get("format", {})
            
            v_info = {
                "width": v_stream.get("width"),
                "height": v_stream.get("height"),
                "v_codec": v_stream.get("codec_name"),
                "fps": v_stream.get("r_frame_rate"),
                "a_codec": a_stream.get("codec_name", "aac"),
                "duration": float(fmt.get("duration", 0)),
                "size_mb": int(fmt.get("size", 0)) / (1024 * 1024),
                "bitrate_kbps": int(fmt.get("bit_rate", 0)) / 1000
            }
            
            print(f"      Resolution:  {v_info['width']}x{v_info['height']} (9:16 Vertical Short)")
            print(f"      Video Codec: {v_info['v_codec']} @ {v_info['fps']} fps")
            print(f"      Audio Codec: {v_info['a_codec']}")
            print(f"      Duration:    {v_info['duration']:.2f}s")
            print(f"      File Size:   {v_info['size_mb']:.2f} MB")
            print(f"      Bitrate:     {v_info['bitrate_kbps']:.0f} kbps")
        else:
            print(f"      FFprobe error: {probe_res.stderr}")

    providers = result.get("providers", {})
    provider_sel = result.get("provider_selection", {})

    print("\n" + "=" * 50)
    print("TOONFORGE FINAL GENERATION REPORT")
    print("=" * 50)
    print(f"\nStory:\n    {providers.get('story')}")
    if "story" in provider_sel:
        print(f"    Reason: {provider_sel['story'].get('reason')}")
        
    print(f"\nVisuals:\n    {providers.get('visuals')}")
    if "visuals" in provider_sel:
        print(f"    Reason: {provider_sel['visuals'].get('reason')}")
        
    print(f"\nVoice:\n    {providers.get('voice')}")
    print(f"\nLip Sync:\n    {providers.get('lip_sync')}")
    print(f"\nAnimation:\n    {providers.get('animation')}")
    print(f"\nSFX:\n    {providers.get('sfx')}")
    print(f"\nMusic:\n    {providers.get('music')}")
    print(f"\nRenderer:\n    {providers.get('renderer')}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
