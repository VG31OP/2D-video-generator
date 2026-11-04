"""
3D WebGL Renderer & Broadcast Audio/Video Muxer
Handles Playwright Chromium headless rendering, EBU R128 loudness normalization,
Lanczos 1080x1920 scaling, and thumbnail generation.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from core.config import get_ffmpeg_path, find_chrome_executable


class Renderer:
    def __init__(self):
        self.ffmpeg_path = get_ffmpeg_path()
        self.chrome_path = find_chrome_executable()

    def render_webgl(self, project_dir: Path, output_silent_mp4: Optional[Path] = None, fps: int = 30) -> Path:
        """
        Renders the Three.js 3D WebGL scene using headless Playwright Chromium.
        """
        silent_mp4 = output_silent_mp4 or (project_dir / "silent.mp4")
        if silent_mp4.exists():
            silent_mp4.unlink(missing_ok=True)

        env = os.environ.copy()
        if self.chrome_path:
            env["CHROME_PATH"] = str(self.chrome_path)
            env["CHROME"] = str(self.chrome_path)
        if self.ffmpeg_path:
            env["FFMPEG_PATH"] = str(self.ffmpeg_path)

        cmd = ["node", "render.mjs", "video", str(silent_mp4.name), str(fps)]
        print(f"[+] Starting WebGL frame capture ({fps} fps)...")
        res = subprocess.run(cmd, cwd=str(project_dir), env=env, capture_output=True, text=True)

        if res.returncode != 0:
            err_msg = res.stderr or res.stdout
            print(f"[-] WebGL render error:\n{err_msg}")
            raise RuntimeError(f"WebGL frame rendering failed with exit code {res.returncode}:\n{err_msg}")

        if not silent_mp4.exists() or silent_mp4.stat().st_size == 0:
            raise FileNotFoundError(f"Rendered silent video not found at {silent_mp4}")

        print(f"[+] WebGL render finished: {silent_mp4.name} ({silent_mp4.stat().st_size / (1024*1024):.2f} MB)")
        return silent_mp4

    def mux_audio_video(
        self,
        silent_mp4: Path,
        audio_file: Path,
        final_mp4: Path,
        target_w: int = 1080,
        target_h: int = 1920
    ) -> Path:
        """
        Muxes silent WebGL MP4 with neural voiceover, scales to 1080x1920 via Lanczos,
        and applies EBU R128 loudness normalization (-14 LUFS, -1.5 dBFS True Peak).
        """
        final_mp4.parent.mkdir(parents=True, exist_ok=True)
        if final_mp4.exists():
            final_mp4.unlink(missing_ok=True)

        print("[+] Muxing audio & scaling to 1080x1920 with EBU R128 loudness normalization...")

        cmd = [
            self.ffmpeg_path, "-v", "error", "-y",
            "-i", str(silent_mp4),
            "-i", str(audio_file),
            "-map", "0:v",
            "-map", "1:a",
            "-vf", f"scale={target_w}:{target_h}:flags=lanczos",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-af", "apad,loudnorm=I=-14:TP=-1.5:LRA=9",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-shortest",
            "-movflags", "+faststart",
            str(final_mp4)
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg muxing failed:\n{res.stderr}")

        if not final_mp4.exists() or final_mp4.stat().st_size == 0:
            raise FileNotFoundError(f"Final output video not created at {final_mp4}")

        print(f"[+] Master broadcast MP4 ready: {final_mp4.name} ({final_mp4.stat().st_size / (1024*1024):.2f} MB)")
        return final_mp4

    def extract_cover(self, video_path: Path, cover_path: Path, timestamp: float = 1.2) -> Path:
        """
        Extracts high-resolution cover thumbnail at the designated timestamp.
        """
        cover_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.ffmpeg_path, "-y",
            "-ss", f"{timestamp:.3f}",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(cover_path)
        ]
        subprocess.run(cmd, capture_output=True)
        if not cover_path.exists():
            # Fallback to 0.5s if 1.2s failed
            cmd[2] = "0.500"
            subprocess.run(cmd, capture_output=True)
        return cover_path

    def clean_intermediates(self, project_dir: Path) -> None:
        """
        Removes temporary silent video and still frames to conserve disk space.
        """
        silent = project_dir / "silent.mp4"
        if silent.exists():
            silent.unlink(missing_ok=True)

        stills = project_dir / "stills"
        if stills.exists() and stills.is_dir():
            shutil.rmtree(stills, ignore_errors=True)


renderer = Renderer()

