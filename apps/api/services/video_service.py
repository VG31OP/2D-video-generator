import os
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from apps.api.config import settings

class VideoService:
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps

    def render_scene_clip(
        self,
        image_path: str,
        duration: float,
        camera_motion: str,
        output_path: str,
        bg_path: Optional[str] = None,
        char_specs: Optional[List[Dict[str, Any]]] = None,
        emotion: Optional[str] = None,
        style: Optional[str] = None
    ) -> str:
        """
        Renders an animated 2D motion-comic scene video clip using SeniorMotionDirectorEngine.
        """
        from apps.api.providers.animation_provider import SeniorMotionDirectorEngine
        engine = SeniorMotionDirectorEngine()
        
        # Run async engine in event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                res = pool.submit(
                    asyncio.run,
                    engine.render_scene_animation(
                        image_path=image_path,
                        duration=duration,
                        camera_motion=camera_motion,
                        output_path=output_path,
                        width=self.width,
                        height=self.height,
                        fps=self.fps,
                        bg_path=bg_path,
                        char_specs=char_specs,
                        emotion=emotion,
                        style=style
                    )
                ).result()
                return res
        else:
            return loop.run_until_complete(
                engine.render_scene_animation(
                    image_path=image_path,
                    duration=duration,
                    camera_motion=camera_motion,
                    output_path=output_path,
                    width=self.width,
                    height=self.height,
                    fps=self.fps,
                    bg_path=bg_path,
                    char_specs=char_specs,
                    emotion=emotion,
                    style=style
                )
            )

    def assemble_final_short(self, scene_clips: List[str], audio_path: str, subtitle_ass_path: str, output_path: str) -> str:
        """
        Concatenates all scene clips, muxes master audio, and applies dynamic kinetic ASS subtitles.
        Optimized for high-quality 1080x1920 30fps vertical Shorts/Reels with compact file size (10-25 MB).
        """
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        work_dir = out_file.parent
        ffmpeg_bin = settings.get_ffmpeg_path()
        
        # 1. Create concat list
        concat_list_file = work_dir / "scenes_concat.txt"
        with open(str(concat_list_file), "w", encoding="utf-8") as f:
            for clip in scene_clips:
                clean_path = str(Path(clip).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")
                
        sub_path = Path(subtitle_ass_path).resolve()
        
        # 2. Try rendering with subtitles
        rendered = False
        if sub_path.exists():
            try:
                # Copy subtitles to work_dir as subs.ass for clean relative path without drive letters
                local_sub = work_dir / "subs.ass"
                import shutil
                shutil.copy(str(sub_path), str(local_sub))
                
                cmd = [
                    ffmpeg_bin, "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", "scenes_concat.txt",
                    "-i", str(Path(audio_path).resolve()),
                    "-vf", "ass=subs.ass",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "22",
                    "-pix_fmt", "yuv420p",
                    "-r", str(self.fps),
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    str(out_file.name)
                ]
                subprocess.run(cmd, cwd=str(work_dir), capture_output=True, text=True, check=True, timeout=90)
                rendered = True
            except Exception as e:
                print(f"[VideoService] Subtitle burn failed: {e}. Falling back to direct mux.")

        if not rendered:
            cmd_direct = [
                ffmpeg_bin, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", "scenes_concat.txt",
                "-i", str(Path(audio_path).resolve()),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-r", str(self.fps),
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(out_file.name)
            ]
            subprocess.run(cmd_direct, cwd=str(work_dir), capture_output=True, text=True, check=True, timeout=90)
            
        return str(out_file)
