import os
import math
import struct
import wave
import random
from pathlib import Path

class MusicProvider:
    def __init__(self, music_cache_dir: str = None):
        if music_cache_dir:
            self.cache_dir = Path(music_cache_dir)
        else:
            self.cache_dir = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "assets" / "music"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_provider_name(self) -> str:
        return "Adaptive Mood Music Synthesizer"

    async def get_background_music(self, mood: str = "comedy", duration_seconds: float = 45.0, output_path: str = None) -> str:
        clean_mood = mood.lower().replace(" ", "_")
        target_file = Path(output_path) if output_path else (self.cache_dir / f"bgm_{clean_mood}_{int(duration_seconds)}s.wav")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        if target_file.exists():
            return str(target_file)
            
        self._synthesize_bgm(clean_mood, duration_seconds, target_file)
        return str(target_file)

    def _synthesize_bgm(self, mood: str, total_duration: float, out_path: Path):
        sample_rate = 44100
        num_samples = int(sample_rate * total_duration)
        raw_data = bytearray()
        
        # BPM & Chords per mood
        if "suspense" in mood:
            bpm = 100.0
            chords = [
                [130.81, 155.56, 196.00], # Cm
                [116.54, 146.83, 174.61], # Bbm
                [123.47, 146.83, 185.00], # B
                [130.81, 164.81, 196.00], # C
            ]
        elif "action" in mood or "chaotic" in mood:
            bpm = 135.0
            chords = [
                [220.00, 261.63, 329.63], # Am
                [174.61, 220.00, 261.63], # F
                [196.00, 246.94, 293.66], # G
                [164.81, 207.65, 246.94], # E
            ]
        elif "emotional" in mood:
            bpm = 92.0
            chords = [
                [220.00, 261.63, 329.63], # Am
                [174.61, 220.00, 261.63], # F
                [261.63, 329.63, 392.00], # C
                [196.00, 246.94, 293.66], # G
            ]
        else: # comedy / upbeat
            bpm = 124.0
            chords = [
                [261.63, 329.63, 392.00], # C4
                [196.00, 246.94, 293.66], # G3
                [220.00, 261.63, 329.63], # Am3
                [174.61, 220.00, 261.63], # F3
            ]
        
        beat_duration = 60.0 / bpm
        chord_len = beat_duration * 4
        
        for i in range(num_samples):
            t = i / sample_rate
            measure_t = t % (chord_len * len(chords))
            chord_idx = int(measure_t / chord_len) % len(chords)
            cur_chord = chords[chord_idx]
            beat_t = t % beat_duration
            
            # 1. Bass Kick
            kick_env = math.exp(-beat_t * 18.0)
            kick_freq = 110.0 * math.exp(-beat_t * 25.0) + 38.0
            kick = math.sin(2 * math.pi * kick_freq * beat_t) * kick_env * 0.4
            
            # 2. Hi-Hat
            hihat_env = math.exp(-((beat_t - beat_duration * 0.5) % beat_duration) * 35.0) if beat_t >= beat_duration * 0.4 else 0
            hihat = (random.random() * 2 - 1) * hihat_env * 0.12
            
            # 3. Funky Bassline
            bass_root = cur_chord[0] * 0.5
            bass_env = math.exp(-(t % (beat_duration * 0.5)) * 12.0)
            bass = math.sin(2 * math.pi * bass_root * t) * bass_env * 0.28
            
            # 4. Melodic Arpeggio
            arp_step = int((t % beat_duration) / (beat_duration / 4))
            arp_note = cur_chord[arp_step % len(cur_chord)] * 2.0
            arp_t = (t % (beat_duration / 4))
            arp_env = math.exp(-arp_t * 15.0)
            arp = math.sin(2 * math.pi * arp_note * t) * arp_env * 0.18
            
            fade_in = min(1.0, t / 1.0)
            fade_out = min(1.0, (total_duration - t) / 1.5)
            master_env = fade_in * fade_out
            
            sample = (kick + hihat + bass + arp) * master_env
            int_val = int(sample * 16000)
            int_val = max(-32768, min(32767, int_val))
            raw_data.extend(struct.pack("<h", int_val))
            
        with wave.open(str(out_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(raw_data)
