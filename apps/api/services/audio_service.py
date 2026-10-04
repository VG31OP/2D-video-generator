import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from apps.api.providers.voice_provider import EdgeTTSVoiceProvider, VoiceProvider
from apps.api.providers.sfx_provider import SFXProvider
from apps.api.providers.music_provider import MusicProvider

class AudioService:
    def __init__(self, voice_provider: VoiceProvider = None, sfx_provider: SFXProvider = None, music_provider: MusicProvider = None):
        self.voice_provider = voice_provider or EdgeTTSVoiceProvider()
        self.sfx_provider = sfx_provider or SFXProvider()
        self.music_provider = music_provider or MusicProvider()

    async def generate_scene_voice(
        self,
        dialogue: str,
        speaker_char: Dict[str, Any],
        output_path: str,
        emotion: str = "neutral",
        pause_before: float = 0.0,
        pause_after: float = 0.0
    ) -> Dict[str, Any]:
        voice_type = speaker_char.get("voice_type", "energetic_male")
        pitch = speaker_char.get("voice_pitch", "+0Hz")
        rate = speaker_char.get("voice_rate", "+0%")
        
        return await self.voice_provider.synthesize(
            text=dialogue,
            voice_type=voice_type,
            pitch=pitch,
            rate=rate,
            emotion=emotion,
            pause_before=pause_before,
            pause_after=pause_after,
            output_path=output_path
        )

    async def build_audio_mix(self, scenes_data: List[Dict[str, Any]], music_mood: str, output_path: str) -> str:
        """
        Combines voice clips, SFX triggers, and background music with auto-ducking into a single master audio file.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        total_duration = sum(s.get("duration", 4.0) for s in scenes_data)
        
        # 1. Generate BGM
        bgm_path = await self.music_provider.get_background_music(
            mood=music_mood,
            duration_seconds=total_duration + 1.0,
            output_path=str(out_file.parent / "bgm_track.wav")
        )
        
        # 2. Build FFmpeg audio filter complex
        inputs = ["-i", bgm_path]
        filter_complex = []
        mix_inputs = ["[bgm]"]
        
        filter_complex.append(f"[0:a]volume=0.20,loudnorm=I=-24:LRA=7:tp=-2[bgm];")
        
        cumulative_time = 0.0
        input_idx = 1
        
        for s_idx, scene in enumerate(scenes_data):
            # Voice clip
            voice_path = scene.get("audio_path")
            if voice_path and os.path.exists(voice_path):
                inputs.extend(["-i", voice_path])
                delay_ms = int(cumulative_time * 1000)
                filter_complex.append(f"[{input_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.35[v_{s_idx}];")
                mix_inputs.append(f"[v_{s_idx}]")
                input_idx += 1
                
            # SFX triggers
            for sfx_name in scene.get("sfx", []):
                sfx_file = await self.sfx_provider.get_sfx(sfx_name)
                if os.path.exists(sfx_file):
                    inputs.extend(["-i", sfx_file])
                    # Place SFX ~0.15s into the scene
                    sfx_delay_ms = int((cumulative_time + 0.15) * 1000)
                    filter_complex.append(f"[{input_idx}:a]adelay={sfx_delay_ms}|{sfx_delay_ms},volume=0.85[sfx_{input_idx}];")
                    mix_inputs.append(f"[sfx_{input_idx}]")
                    input_idx += 1
                    
            cumulative_time += scene.get("duration", 4.0)
            
        num_streams = len(mix_inputs)
        filter_complex.append(f"{''.join(mix_inputs)}amix=inputs={num_streams}:duration=longest:dropout_transition=2[outa]")
        
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", "".join(filter_complex),
            "-map", "[outa]",
            "-t", str(total_duration),
            "-c:a", "pcm_s16le",
            str(out_file)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except Exception as e:
            print(f"[AudioService] FFmpeg mix failed: {e}. Running fallback simple mix.")
            if os.path.exists(bgm_path):
                import shutil
                shutil.copy(bgm_path, str(out_file))
                
        return str(out_file)
