import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class VideoService:
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps

    def render_scene_clip(self, image_path: str, duration: float, camera_motion: str, output_path: str) -> str:
        """
        Renders an animated 2D motion-comic scene video clip from a static composite frame.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        frames = max(1, int(duration * self.fps))
        
        # Build zoompan filter based on camera motion
        if "push" in camera_motion:
            # Dramatic push in
            zp = f"zoompan=z='min(zoom+0.0022,1.25)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={self.width}x{self.height}:fps={self.fps}"
        elif "pan" in camera_motion:
            # Subtle horizontal pan
            zp = f"zoompan=z=1.12:x='min((on/{frames})*(iw-iw/zoom),iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s={self.width}x{self.height}:fps={self.fps}"
        elif "shake" in camera_motion:
            # Impact camera shake
            zp = f"zoompan=z=1.06:x='iw/2-(iw/zoom/2)+sin(on*2.5)*8':y='ih/2-(ih/zoom/2)+cos(on*3.0)*8':d={frames}:s={self.width}x{self.height}:fps={self.fps}"
        else:
            # Default slow Ken Burns zoom
            zp = f"zoompan=z='min(zoom+0.0010,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={self.width}x{self.height}:fps={self.fps}"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-vf", f"{zp},format=yuv420p",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(self.fps),
            "-preset", "veryfast",
            "-crf", "22",
            str(out_file)
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return str(out_file)

    def assemble_final_short(self, scene_clips: List[str], audio_path: str, subtitle_ass_path: str, output_path: str) -> str:
        """
        Concatenates all scene clips, muxes master audio, and applies dynamic ASS subtitles.
        Optimized for high-quality 1080x1920 30fps YouTube Shorts with compact file size (10-25 MB).
        """
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        work_dir = out_file.parent
        
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
                    "ffmpeg", "-y",
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
                "ffmpeg", "-y",
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
