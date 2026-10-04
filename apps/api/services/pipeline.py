import os
import json
import asyncio
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.config import settings, PROJECTS_DIR
from apps.api.models.schema import Project, Character, Scene, GenerationJob
from apps.api.providers.llm_provider import LLMFactory, LLMProvider
from apps.api.providers.voice_provider import VoiceFactory, VoiceProvider
from apps.api.providers.visual_provider import VisualFactory, VisualProvider
from apps.api.providers.lip_sync_provider import LipSyncFactory, LipSyncProvider, MouthFlapFallbackProvider
from apps.api.providers.animation_provider import AnimationFactory, AnimationProvider, MotionComicFallbackProvider
from apps.api.providers.sfx_provider import SFXProvider
from apps.api.providers.music_provider import MusicProvider
from apps.api.services.subtitle_service import SubtitleService
from apps.api.services.audio_service import AudioService
from apps.api.services.video_service import VideoService
from apps.api.services.thumbnail_service import ThumbnailService
from apps.api.services.qc_service import QCService

class GenerationPipeline:
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        voice_provider: Optional[VoiceProvider] = None,
        visual_provider: Optional[VisualProvider] = None,
        lip_sync_provider: Optional[LipSyncProvider] = None,
        animation_provider: Optional[AnimationProvider] = None,
        sfx_provider: Optional[SFXProvider] = None,
        music_provider: Optional[MusicProvider] = None
    ):
        self.llm = llm_provider
        self.voice = voice_provider
        self.visual = visual_provider
        self.lip_sync = lip_sync_provider
        self.animation = animation_provider
        self.sfx = sfx_provider or SFXProvider()
        self.music = music_provider or MusicProvider()
        
        self.sub_svc = SubtitleService()
        self.video_svc = VideoService(width=settings.DEFAULT_WIDTH, height=settings.DEFAULT_HEIGHT, fps=settings.DEFAULT_FPS)
        self.thumb_svc = ThumbnailService(width=settings.DEFAULT_WIDTH, height=settings.DEFAULT_HEIGHT)
        self.qc_svc = QCService()

    async def execute_project_pipeline(
        self,
        project_id: str,
        db_session_factory,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        resume_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the autonomous end-to-end cartoon short generation pipeline
        with stage persistence, AI provider attribution, and resumption capabilities.
        """
        project_dir = PROJECTS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        chars_dir = project_dir / "characters"
        bgs_dir = project_dir / "backgrounds"
        audio_dir = project_dir / "audio"
        scenes_dir = project_dir / "scenes"
        renders_dir = project_dir / "renders"
        
        for d in [chars_dir, bgs_dir, audio_dir, scenes_dir, renders_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Dynamic provider detection & selection
        llm_engine = self.llm or await LLMFactory.get_best_provider()
        voice_engine = self.voice or await VoiceFactory.get_best_provider()
        visual_engine = self.visual or await VisualFactory.get_best_provider()
        lip_sync_engine = self.lip_sync or await LipSyncFactory.get_best_provider()
        animation_engine = self.animation or await AnimationFactory.get_best_provider()
        
        audio_svc = AudioService(voice_engine, self.sfx, self.music)

        llm_mode = getattr(llm_engine, 'get_provider_type', lambda: 'FALLBACK')()
        visual_mode = getattr(visual_engine, 'get_provider_type', lambda: 'FALLBACK')()
        voice_mode = getattr(voice_engine, 'get_provider_type', lambda: 'REAL TTS')()
        lip_sync_mode = getattr(lip_sync_engine, 'get_provider_type', lambda: 'FALLBACK')()
        animation_mode = getattr(animation_engine, 'get_provider_type', lambda: 'FALLBACK')()

        provider_selection = {
            "story": {
                "provider": llm_engine.get_provider_name(),
                "mode": llm_mode,
                "reason": "Ollama service offline" if llm_mode == "FALLBACK" else "Ollama model ready"
            },
            "visuals": {
                "provider": visual_engine.get_provider_name(),
                "mode": visual_mode,
                "reason": "ComfyUI unavailable" if visual_mode == "FALLBACK" else "ComfyUI checkpoint active"
            },
            "voice": {
                "provider": voice_engine.get_provider_name(),
                "mode": voice_mode,
                "reason": "Neural cloud speech API operational"
            },
            "lip_sync": {
                "provider": lip_sync_engine.get_provider_name(),
                "mode": lip_sync_mode,
                "reason": "Speech-synchronized 2D sprite mouth flaps"
            },
            "animation": {
                "provider": animation_engine.get_provider_name(),
                "mode": animation_mode,
                "reason": "Cinematic camera movement (Pan/Zoom/Shake)"
            },
            "sfx": {
                "provider": "Procedural SFX Engine",
                "mode": "PROCEDURAL"
            },
            "music": {
                "provider": "Mood-Adaptive Procedural Engine",
                "mode": "PROCEDURAL"
            },
            "renderer": {
                "provider": "FFmpeg",
                "mode": "RENDERER",
                "reason": "FFmpeg libass & libx264 1080x1920 30fps"
            }
        }

        provider_report = {
            "story": f"{llm_engine.get_provider_name()} / {llm_mode}",
            "visuals": f"{visual_engine.get_provider_name()} / {visual_mode}",
            "voice": f"{voice_engine.get_provider_name()} / {voice_mode}",
            "lip_sync": f"{lip_sync_engine.get_provider_name()} / {lip_sync_mode}",
            "animation": f"{animation_engine.get_provider_name()} / {animation_mode}",
            "sfx": "Procedural",
            "music": "Procedural",
            "renderer": "FFmpeg"
        }

        async def update_status(stage: str, percent: int, msg: str):
            async with db_session_factory() as session:
                proj = await session.get(Project, project_id)
                if proj:
                    proj.status = "Generating" if percent < 88 else ("Rendering" if percent < 100 else "Completed")
                job_res = await session.execute(
                    select(GenerationJob).where(GenerationJob.project_id == project_id).order_by(GenerationJob.started_at.desc())
                )
                job = job_res.scalars().first()
                if job:
                    job.current_stage = stage
                    job.progress_percent = percent
                    job.stage_message = msg
                    logs = json.loads(job.log_messages_json or "[]")
                    timestamp = datetime.datetime.utcnow().strftime("%H:%M:%S")
                    logs.append(f"[{timestamp}] [{stage}] {msg}")
                    job.log_messages_json = json.dumps(logs)
                    if percent >= 100:
                        job.status = "Completed"
                        job.completed_at = datetime.datetime.utcnow()
                await session.commit()
                
            if progress_callback:
                try:
                    await progress_callback({
                        "project_id": project_id,
                        "stage": stage,
                        "progress": percent,
                        "message": msg,
                        "providers": provider_report,
                        "provider_selection": provider_selection
                    })
                except Exception:
                    pass

        try:
            # 1. Fetch project from DB
            async with db_session_factory() as session:
                project = await session.get(Project, project_id)
                if not project:
                    raise ValueError(f"Project {project_id} not found")
                topic = project.topic
                style = project.art_style
                language = project.language
                duration = int(project.duration_seconds or settings.DEFAULT_DURATION_TARGET)
            
            # Step 1: Story & Script Planning
            await update_status("Story Planning", 8, f"Crafting viral cartoon story via {llm_engine.get_provider_name()}...")
            story_data = await llm_engine.generate_story_and_script(
                topic=topic,
                style=style,
                language=language,
                duration_seconds=duration
            )
            
            async with db_session_factory() as session:
                proj = await session.get(Project, project_id)
                proj.title = story_data.get("title", proj.title)
                proj.story_json = json.dumps(story_data)
                meta = story_data.get("metadata", {})
                meta["providers"] = provider_report
                meta["provider_selection"] = provider_selection
                proj.metadata_json = json.dumps(meta)
                await session.commit()
                
            # Step 2: Build Character Bible & Multi-Expression Sprites
            await update_status("Character Bible", 22, f"Generating consistent character bibles & expression rigs via {visual_engine.get_provider_name()}...")
            raw_characters = story_data.get("characters", [])
            char_map: Dict[str, Dict[str, Any]] = {}
            
            async with db_session_factory() as session:
                existing_chars = await session.execute(select(Character).where(Character.project_id == project_id))
                for c in existing_chars.scalars().all():
                    await session.delete(c)
                await session.commit()
                
                for idx, c_data in enumerate(raw_characters):
                    c_name = c_data.get("name", f"Char_{idx+1}")
                    char_id = f"char_{project_id[:8]}_{idx+1}"
                    
                    sprites = await visual_engine.generate_character_rig(c_data, str(chars_dir))
                    
                    char_entry = Character(
                        id=char_id,
                        project_id=project_id,
                        name=c_name,
                        role=c_data.get("role", "Protagonist"),
                        age=c_data.get("age", "19"),
                        gender=c_data.get("gender", "Neutral"),
                        body_type=c_data.get("body_type", "Cartoon build"),
                        hair_style=c_data.get("hair_style", "Messy anime"),
                        hair_color=c_data.get("hair_color", "#2d3748"),
                        skin_tone=c_data.get("skin_tone", "#f6d5b8"),
                        outfit_desc=c_data.get("outfit_desc", "Casual hoodie"),
                        outfit_color=c_data.get("outfit_color", "#3b82f6"),
                        personality=c_data.get("personality", "Energetic"),
                        voice_id=c_data.get("voice_type", "energetic_male"),
                        voice_name=c_data.get("voice_type", "energetic_male"),
                        voice_pitch=c_data.get("voice_pitch", "+0Hz"),
                        voice_rate=c_data.get("voice_rate", "+0%"),
                        avatar_url=f"/storage/projects/{project_id}/characters/{Path(sprites.get('avatar', '')).name}",
                        mouth_open_url=f"/storage/projects/{project_id}/characters/{Path(sprites.get('talking_open', '')).name}",
                        mouth_closed_url=f"/storage/projects/{project_id}/characters/{Path(sprites.get('talking_closed', '')).name}",
                        expression_shock_url=f"/storage/projects/{project_id}/characters/{Path(sprites.get('shock', '')).name}",
                        expression_happy_url=f"/storage/projects/{project_id}/characters/{Path(sprites.get('happy', '')).name}"
                    )
                    session.add(char_entry)
                    char_map[c_name] = {**c_data, "sprites": sprites, "char_id": char_id}
                await session.commit()

            # Step 3: Plan & Generate Scenes
            await update_status("Scene Composition", 40, f"Generating 2D backgrounds & scenes via {visual_engine.get_provider_name()}...")
            raw_scenes = story_data.get("scenes", [])
            rendered_scenes_data = []
            
            async with db_session_factory() as session:
                existing_scenes = await session.execute(select(Scene).where(Scene.project_id == project_id))
                for s in existing_scenes.scalars().all():
                    await session.delete(s)
                await session.commit()
                
                for s_idx, s_data in enumerate(raw_scenes):
                    s_num = s_data.get("scene_id", s_idx + 1)
                    scene_id = f"scene_{project_id[:8]}_{s_num}"
                    location = s_data.get("location", "Room")
                    emotion = s_data.get("emotion", "comedy")
                    
                    # Background
                    bg_file = str(bgs_dir / f"bg_scene_{s_num}.png")
                    await visual_engine.generate_background(
                        location=location,
                        prompt=s_data.get("visual_prompt", ""),
                        output_path=bg_file,
                        width=settings.DEFAULT_WIDTH,
                        height=settings.DEFAULT_HEIGHT
                    )
                    
                    # Characters in this scene
                    scene_char_specs = []
                    scene_char_names = s_data.get("characters", [])
                    speaker_name = s_data.get("speaker", scene_char_names[0] if scene_char_names else "Narrator")
                    
                    for cname in scene_char_names:
                        c_info = char_map.get(cname)
                        if c_info:
                            sprites = c_info.get("sprites", {})
                            if emotion in ["shock", "panic"]:
                                spr = sprites.get("shock") or sprites.get("avatar")
                            elif emotion in ["happy", "excited"]:
                                spr = sprites.get("happy") or sprites.get("avatar")
                            elif cname == speaker_name:
                                spr = sprites.get("talking_open") or sprites.get("avatar")
                            else:
                                spr = sprites.get("avatar")
                            scene_char_specs.append({"name": cname, "sprite_path": spr})
                            
                    # Composite Scene Frame
                    comp_file = str(scenes_dir / f"scene_{s_num}_comp.png")
                    await visual_engine.compose_scene_frame(
                        bg_path=bg_file,
                        char_specs=scene_char_specs,
                        action_desc=s_data.get("action", ""),
                        emotion=emotion,
                        output_path=comp_file,
                        width=settings.DEFAULT_WIDTH,
                        height=settings.DEFAULT_HEIGHT
                    )
                    
                    # Speech Dialogue Voice
                    voice_file = str(audio_dir / f"voice_scene_{s_num}.mp3")
                    speaker_info = char_map.get(speaker_name, {})
                    voice_res = await audio_svc.generate_scene_voice(
                        dialogue=s_data.get("dialogue", ""),
                        speaker_char=speaker_info,
                        output_path=voice_file,
                        emotion=emotion,
                        pause_before=float(s_data.get("pause_before", 0.0) or 0.0),
                        pause_after=float(s_data.get("pause_after", 0.0) or 0.0)
                    )
                    
                    actual_duration = max(2.5, round(voice_res.get("duration", 3.0) + 0.3, 2))
                    
                    scene_entry = Scene(
                        id=scene_id,
                        project_id=project_id,
                        scene_number=s_num,
                        duration=actual_duration,
                        location=location,
                        visual_prompt=s_data.get("visual_prompt", ""),
                        action_desc=s_data.get("action", ""),
                        dialogue_text=s_data.get("dialogue", ""),
                        speaker_name=speaker_name,
                        camera_motion=s_data.get("camera", "slow zoom in"),
                        transition=s_data.get("transition", "cut"),
                        sfx_json=json.dumps(s_data.get("sfx", [])),
                        emotion=emotion,
                        background_url=f"/storage/projects/{project_id}/backgrounds/{Path(bg_file).name}",
                        scene_image_url=f"/storage/projects/{project_id}/scenes/{Path(comp_file).name}",
                        audio_url=f"/storage/projects/{project_id}/audio/{Path(voice_file).name}",
                        subtitles_json=json.dumps(voice_res.get("words", []))
                    )
                    session.add(scene_entry)
                    
                    rendered_scenes_data.append({
                        "scene_id": scene_id,
                        "scene_number": s_num,
                        "comp_path": comp_file,
                        "audio_path": voice_file,
                        "duration": actual_duration,
                        "camera": s_data.get("camera", "slow zoom in"),
                        "sfx": s_data.get("sfx", []),
                        "dialogue": s_data.get("dialogue", ""),
                        "words": voice_res.get("words", [])
                    })
                await session.commit()

            # Step 4: Subtitles & Dynamic Audio Mix
            await update_status("Audio & Subtitles", 62, f"Synchronizing {voice_engine.get_provider_name()} timestamps, SFX & dynamic subtitles...")
            ass_path = str(project_dir / "subtitles.ass")
            self.sub_svc.generate_ass_subtitles(rendered_scenes_data, ass_path)
            
            master_audio_path = str(renders_dir / "master_audio.wav")
            await audio_svc.build_audio_mix(
                scenes_data=rendered_scenes_data,
                music_mood="comedy",
                output_path=master_audio_path
            )

            # Step 5: Render Animated Scenes via AnimationProvider
            await update_status("Motion Animation", 76, f"Rendering scene animation via {animation_engine.get_provider_name()}...")
            scene_clips = []
            for s in rendered_scenes_data:
                clip_out = str(scenes_dir / f"clip_scene_{s['scene_number']}.mp4")
                await animation_engine.render_scene_animation(
                    image_path=s["comp_path"],
                    duration=s["duration"],
                    camera_motion=s["camera"],
                    output_path=clip_out,
                    width=settings.DEFAULT_WIDTH,
                    height=settings.DEFAULT_HEIGHT,
                    fps=settings.DEFAULT_FPS
                )
                scene_clips.append(clip_out)

            # Step 6: Final 9:16 Video Concat & Subtitle Burn
            await update_status("Final Video Assembly", 88, f"Encoding 1080x1920 {settings.DEFAULT_FPS}fps YouTube Short with FFmpeg...")
            final_mp4_path = str(renders_dir / f"{project_id}_final.mp4")
            self.video_svc.assemble_final_short(
                scene_clips=scene_clips,
                audio_path=master_audio_path,
                subtitle_ass_path=ass_path,
                output_path=final_mp4_path
            )

            # Step 7: Generate High-CTR Thumbnail & Metadata
            await update_status("Thumbnail & Metadata", 95, "Generating YouTube Shorts thumbnail & SEO tags...")
            thumb_path = str(renders_dir / "thumbnail.jpg")
            main_char = raw_characters[0] if raw_characters else {}
            main_sprite = char_map.get(main_char.get("name", ""), {}).get("sprites", {}).get("shock") or \
                          char_map.get(main_char.get("name", ""), {}).get("sprites", {}).get("avatar")
            
            self.thumb_svc.generate_thumbnail(
                title=story_data.get("title", "Cartoon Short"),
                character_sprite=main_sprite,
                output_path=thumb_path
            )

            # Step 8: Multi-Checkpoint Quality Control
            await update_status("Quality Control", 98, "Validating video resolution, duration, streams, and integrity...")
            qc_result = self.qc_svc.validate_project_assets(
                video_path=final_mp4_path,
                scenes_data=rendered_scenes_data,
                characters_data=raw_characters,
                subtitles_path=ass_path,
                thumbnail_path=thumb_path
            )
            
            total_short_duration = sum(s["duration"] for s in rendered_scenes_data)
            async with db_session_factory() as session:
                proj = await session.get(Project, project_id)
                proj.status = "Completed"
                proj.duration_seconds = total_short_duration
                proj.video_url = f"/storage/projects/{project_id}/renders/{Path(final_mp4_path).name}"
                proj.thumbnail_url = f"/storage/projects/{project_id}/renders/thumbnail.jpg"
                proj.audio_mix_url = f"/storage/projects/{project_id}/renders/master_audio.wav"
                proj.subtitles_url = f"/storage/projects/{project_id}/subtitles.ass"
                meta = json.loads(proj.metadata_json or "{}")
                meta["providers"] = provider_report
                meta["provider_selection"] = provider_selection
                meta["qc"] = qc_result
                proj.metadata_json = json.dumps(meta)
                await session.commit()
                
            await update_status("Completed", 100, f"Short ready! Story: {llm_engine.get_provider_name()} | Visuals: {visual_engine.get_provider_name()} | Duration: {total_short_duration:.1f}s")
            
            return {
                "success": True,
                "project_id": project_id,
                "video_url": f"/storage/projects/{project_id}/renders/{Path(final_mp4_path).name}",
                "thumbnail_url": f"/storage/projects/{project_id}/renders/thumbnail.jpg",
                "duration": total_short_duration,
                "providers": provider_report,
                "provider_selection": provider_selection,
                "qc": qc_result
            }

        except Exception as e:
            error_msg = str(e)
            print(f"[Pipeline Error for {project_id}]: {error_msg}")
            async with db_session_factory() as session:
                proj = await session.get(Project, project_id)
                if proj:
                    proj.status = "Failed"
                    proj.error_message = error_msg
                job_res = await session.execute(
                    select(GenerationJob).where(GenerationJob.project_id == project_id).order_by(GenerationJob.started_at.desc())
                )
                job = job_res.scalars().first()
                if job:
                    job.status = "Failed"
                    job.error_message = error_msg
                await session.commit()
            raise e
