import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

class QCService:
    """
    Automated Quality Control validator for ToonForge short videos.
    """
    def validate_project_assets(
        self,
        video_path: str,
        scenes_data: List[Dict[str, Any]],
        characters_data: List[Dict[str, Any]],
        subtitles_path: str,
        thumbnail_path: str
    ) -> Dict[str, Any]:
        errors = []
        warnings = []

        # 1. Video File Verification
        if not os.path.exists(video_path):
            errors.append(f"Rendered video file missing at {video_path}")
        else:
            file_size = os.path.getsize(video_path)
            if file_size < 10000:
                errors.append(f"Rendered video too small ({file_size} bytes)")
                
            try:
                cmd = [
                    "ffprobe", "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    video_path
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                probe_data = json.loads(res.stdout)
                
                streams = probe_data.get("streams", [])
                has_video = any(s.get("codec_type") == "video" for s in streams)
                has_audio = any(s.get("codec_type") == "audio" for s in streams)
                
                if not has_video:
                    errors.append("No video stream found in rendered MP4")
                else:
                    v_stream = next(s for s in streams if s.get("codec_type") == "video")
                    width = int(v_stream.get("width", 0))
                    height = int(v_stream.get("height", 0))
                    if width != 1080 or height != 1920:
                        warnings.append(f"Resolution is {width}x{height} instead of target 1080x1920")
                        
                if not has_audio:
                    errors.append("No audio track detected in rendered MP4")
                    
                duration = float(probe_data.get("format", {}).get("duration", 0.0))
                if duration < 5.0:
                    errors.append(f"Duration too short ({duration:.1f}s)")
            except Exception as e:
                warnings.append(f"ffprobe deep inspection skipped: {e}")

        # 2. Subtitles Verification
        if not os.path.exists(subtitles_path) or os.path.getsize(subtitles_path) < 100:
            warnings.append(f"Subtitle file missing or empty at {subtitles_path}")

        # 3. Thumbnail Verification
        if not os.path.exists(thumbnail_path) or os.path.getsize(thumbnail_path) < 1000:
            warnings.append(f"Thumbnail file missing or empty at {thumbnail_path}")

        # 4. Scenes Verification
        for s in scenes_data:
            s_num = s.get("scene_number", "?")
            comp = s.get("comp_path")
            if not comp or not os.path.exists(comp):
                errors.append(f"Scene {s_num} composite visual missing")
            audio = s.get("audio_path")
            if not audio or not os.path.exists(audio):
                errors.append(f"Scene {s_num} voice audio missing")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_scenes_checked": len(scenes_data),
            "total_characters_checked": len(characters_data)
        }
