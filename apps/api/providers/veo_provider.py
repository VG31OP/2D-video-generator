"""
Google Veo Video Generation Provider
====================================
Integrates Google's flagship Veo video generation model (veo-2.0-generate-001 / veo-3.1-generate-preview)
into the ToonForge video generation and animation pipeline.

Supports:
- Image-to-Video (I2V): Animates reference seed frames with realistic camera dynamics and lighting.
- Text-to-Video (T2V): Synthesizes high-fidelity vertical 9:16 video scenes directly from cinematic scene prompts.
- Audio synchronization: Conforms generated Veo clips to scene dialogue durations using FFmpeg.
"""

import os
import time
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from apps.api.config import settings
from apps.api.providers.animation_provider import AnimationProvider, SeniorMotionDirectorEngine

logger = logging.getLogger(__name__)


class GoogleVeoAnimationProvider(AnimationProvider):
    """
    Production-grade Google Veo Video Generation Provider.
    Calls Google GenAI SDK (client.models.generate_videos) to synthesize
    photorealistic or stylized vertical 9:16 video clips with neural motion.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        aspect_ratio: str = "9:16",
        resolution: str = "720p",
        person_generation: str = "allow_adult",
        fallback_engine: Optional[AnimationProvider] = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or settings.GEMINI_API_KEY
            or ""
        ).strip()
        self.model = (
            model
            or os.getenv("VEO_MODEL")
            or getattr(settings, "VEO_MODEL", "veo-2.0-generate-001")
        ).strip()
        self.aspect_ratio = aspect_ratio or getattr(settings, "VEO_ASPECT_RATIO", "9:16")
        self.resolution = resolution or getattr(settings, "VEO_RESOLUTION", "720p")
        self.person_generation = person_generation or getattr(settings, "VEO_PERSON_GENERATION", "allow_adult")
        self.fallback_engine = fallback_engine or SeniorMotionDirectorEngine()

    def get_provider_name(self) -> str:
        return f"Google Veo ({self.model})"

    def get_provider_type(self) -> str:
        return "REAL AI VIDEO (Google Veo)"

    def is_available(self) -> bool:
        """Checks whether google-genai is installed and an API key is provided."""
        if not self.api_key:
            return False
        try:
            from google import genai  # noqa: F401
            return True
        except ImportError:
            return False

    def _build_veo_prompt(
        self,
        action_desc: Optional[str],
        visual_prompt: Optional[str],
        camera_motion: Optional[str],
        style: Optional[str],
        emotion: Optional[str]
    ) -> str:
        """Constructs an optimized cinematic prompt adhering to ai-video-generation best practices."""
        motion_map = {
            "dramatic push in": "Smooth cinematic dolly push-in camera movement towards the subject, shallow depth of field",
            "slow zoom in": "Slow, elegant optical push-in shot, cinematic lighting",
            "pan right": "Smooth horizontal track to the right, cinematic background parallax",
            "pan left": "Smooth horizontal track to the left, cinematic background parallax",
            "crash zoom": "Dynamic rapid crash zoom into subject's face, high intensity motion",
            "shake_impact": "Energetic handheld camera tremor, sudden comedic shock reaction",
            "comic bounce": "Playful, buoyant vertical bobbing motion, vibrant animation physics",
            "organic float": "Steadicam floating camera drift, subtle natural breathing movement",
            "suspense pulse": "Tension-building slow creeping camera with pulsing ambient light",
        }
        motion_desc = motion_map.get(
            (camera_motion or "").lower(),
            f"Cinematic {camera_motion or 'steady'} camera motion"
        )
        art_style = style or "Cyberpunk Neon Animated"
        core_action = action_desc or visual_prompt or "A character reacting with emotion"
        details = visual_prompt or ""

        prompt = (
            f"A masterwork vertical 9:16 video in {art_style} style. "
            f"Scene action: {core_action}. {details}. "
            f"Camera: {motion_desc}. "
            f"Lighting: High-contrast volumetric atmosphere, sharp 8k details, fluid motion, pristine cinematic quality. "
            f"No jitter, no distortion, no text overlays, no watermarks."
        )
        return prompt

    async def render_scene_animation(
        self,
        image_path: str,
        duration: float,
        camera_motion: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        bg_path: Optional[str] = None,
        char_specs: Optional[List[Dict[str, Any]]] = None,
        emotion: Optional[str] = None,
        style: Optional[str] = None,
        action_desc: Optional[str] = None,
        visual_prompt: Optional[str] = None,
        dialogue: Optional[str] = None,
        logger_func=None,
        **kwargs
    ) -> str:
        """
        Renders a scene animation clip using Google Veo.
        If API key is missing or generation fails, seamlessly falls back to SeniorMotionDirectorEngine.
        """
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.is_available():
            msg = (
                f"[Google Veo] GEMINI_API_KEY is not set or google-genai is missing. "
                f"Falling back to Senior Motion Director Engine for '{camera_motion}'."
            )
            print(msg)
            if logger_func:
                await logger_func(msg)
            return await self.fallback_engine.render_scene_animation(
                image_path=image_path,
                duration=duration,
                camera_motion=camera_motion,
                output_path=output_path,
                width=width,
                height=height,
                fps=fps,
                bg_path=bg_path,
                char_specs=char_specs,
                emotion=emotion,
                style=style,
                **kwargs
            )

        # Veo Generation via google-genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = self._build_veo_prompt(action_desc, visual_prompt, camera_motion, style, emotion)

            # Check if reference image is available for Image-to-Video
            img_input = None
            if image_path and os.path.exists(image_path):
                try:
                    img_input = types.Image.from_file(location=str(image_path))
                    if logger_func:
                        await logger_func(f"[Google Veo] Guiding neural video generation with seed image: {Path(image_path).name}")
                except Exception as img_err:
                    logger.warning(f"Could not load image for Veo: {img_err}")

            if logger_func:
                await logger_func(f"[Google Veo] Submitting video generation ({self.model}, 9:16)...")

            config = types.GenerateVideosConfig(
                aspect_ratio=self.aspect_ratio,
                resolution=self.resolution,
                person_generation=self.person_generation,
                negative_prompt="blurry, distorted, low quality, warped face, extra limbs, watermark, artifacts",
            )

            # Run in thread executor because generate_videos is a blocking HTTP call
            loop = asyncio.get_running_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    image=img_input,
                    config=config
                )
            )

            # Poll operation until complete
            poll_interval = 12
            max_wait_seconds = 360  # 6 minutes timeout
            elapsed = 0

            while not operation.done and elapsed < max_wait_seconds:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                operation = await loop.run_in_executor(
                    None,
                    lambda: client.operations.get(operation)
                )
                if logger_func:
                    await logger_func(f"[Google Veo] Rendering video in cloud ({elapsed}s elapsed)...")

            if not operation.done:
                raise TimeoutError(f"Google Veo video generation timed out after {max_wait_seconds} seconds")

            if getattr(operation, "error", None):
                raise RuntimeError(f"Google Veo error: {operation.error}")

            generated_videos = getattr(operation.response, "generated_videos", [])
            if not generated_videos:
                raise ValueError("Google Veo returned no generated videos in response")

            raw_video = generated_videos[0].video
            raw_tmp_path = str(out_file.with_suffix(".raw_veo.mp4"))

            # Download video bytes or via client.files.download
            if hasattr(raw_video, "video_bytes") and raw_video.video_bytes:
                with open(raw_tmp_path, "wb") as f:
                    f.write(raw_video.video_bytes)
            else:
                await loop.run_in_executor(
                    None,
                    lambda: client.files.download(file=raw_video, destination=raw_tmp_path)
                )

            if logger_func:
                await logger_func(f"[Google Veo] Clip downloaded. Conforming to {duration:.2f}s @ {fps}fps...")

            # Post-process with FFmpeg: conform exact duration, frame rate, and 1080x1920 vertical canvas
            self._conform_video_clip(
                raw_path=raw_tmp_path,
                out_path=str(out_file),
                target_duration=duration,
                width=width,
                height=height,
                fps=fps
            )

            # Clean up temp raw video
            try:
                if os.path.exists(raw_tmp_path):
                    os.remove(raw_tmp_path)
            except Exception:
                pass

            return str(out_file)

        except Exception as e:
            error_msg = f"[Google Veo Error]: {e}. Falling back to Senior Motion Director Engine."
            print(error_msg)
            if logger_func:
                await logger_func(error_msg)
            return await self.fallback_engine.render_scene_animation(
                image_path=image_path,
                duration=duration,
                camera_motion=camera_motion,
                output_path=output_path,
                width=width,
                height=height,
                fps=fps,
                bg_path=bg_path,
                char_specs=char_specs,
                emotion=emotion,
                style=style,
                **kwargs
            )

    def _conform_video_clip(
        self,
        raw_path: str,
        out_path: str,
        target_duration: float,
        width: int,
        height: int,
        fps: int
    ):
        """Conforms raw Veo video to project specifications using FFmpeg."""
        ffmpeg_bin = settings.get_ffmpeg_path()
        vf_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"fps={fps},"
            f"format=yuv420p"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-stream_loop", "-1",
            "-i", str(Path(raw_path).resolve()),
            "-vf", vf_filter,
            "-t", f"{target_duration:.3f}",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-an",
            str(Path(out_path).resolve())
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)

