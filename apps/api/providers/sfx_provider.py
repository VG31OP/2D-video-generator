import os
import math
import struct
import wave
import random
from pathlib import Path
from typing import Dict, Any

class SFXProvider:
    def __init__(self, sfx_cache_dir: str = None):
        if sfx_cache_dir:
            self.cache_dir = Path(sfx_cache_dir)
        else:
            self.cache_dir = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "assets" / "sfx"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_sfx(self, sfx_name: str) -> str:
        clean_name = sfx_name.lower().replace(" ", "_")
        target_path = self.cache_dir / f"{clean_name}.wav"
        if target_path.exists():
            return str(target_path)
            
        # Synthesize sound effect
        self._synthesize_sfx(clean_name, target_path)
        return str(target_path)

    def _synthesize_sfx(self, sfx_type: str, out_path: Path):
        sample_rate = 44100
        raw_data = bytearray()
        
        if "whoosh" in sfx_type:
            # Frequency swept white noise whoosh (0.4s)
            duration = 0.4
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                # Bell curve envelope
                env = math.exp(-((t - 0.2) ** 2) / 0.015)
                # Filtered noise + low tone sweep
                noise = (random.random() * 2 - 1)
                freq_sweep = 300 + (t / duration) * 1200
                tone = math.sin(2 * math.pi * freq_sweep * t)
                val = (noise * 0.7 + tone * 0.3) * env
                int_val = int(val * 24000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "vine_boom" in sfx_type or "boom" in sfx_type or "impact" in sfx_type:
            # Heavy sub-bass boom (0.8s)
            duration = 0.8
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 5.0)
                freq = 90.0 * math.exp(-t * 3.5) + 35.0
                tone = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
                # Distortion saturation
                val = math.tanh(tone * 2.2) * env
                int_val = int(val * 28000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "record_scratch" in sfx_type or "scratch" in sfx_type:
            # Vinyl stop scratch (0.5s)
            duration = 0.5
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 4.0)
                freq = 1500.0 * (1.0 - t / duration) ** 3
                tone = math.sin(2 * math.pi * freq * t) * (random.random() * 0.5 + 0.5)
                val = tone * env
                int_val = int(val * 22000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "notification" in sfx_type or "ding" in sfx_type or "bell" in sfx_type:
            # Dual chime bell (0.6s)
            duration = 0.6
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                env1 = math.exp(-t * 6.0)
                tone1 = math.sin(2 * math.pi * 880.0 * t) # A5
                env2 = math.exp(-max(0, t - 0.08) * 6.0) if t >= 0.08 else 0
                tone2 = math.sin(2 * math.pi * 1320.0 * t) # E6
                val = (tone1 * env1 + tone2 * env2) * 0.5
                int_val = int(val * 26000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "comedic_pop" in sfx_type or "pop" in sfx_type:
            # Fast pitch upward pop (0.2s)
            duration = 0.2
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 22.0)
                freq = 250.0 + (t / duration) * 1600.0
                val = math.sin(2 * math.pi * freq * t) * env
                int_val = int(val * 26000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "glitch" in sfx_type:
            # Cyberpunk digital stutter (0.4s)
            duration = 0.4
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                square = 1.0 if int(t * 80) % 2 == 0 else -1.0
                tone = math.sin(2 * math.pi * 440.0 * (int(t * 40) % 5 + 1) * t)
                val = (square * 0.4 + tone * 0.6) * (1.0 - t / duration)
                int_val = int(val * 20000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        elif "keyboard_typing" in sfx_type:
            # Rapid key clicks (0.5s)
            duration = 0.5
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                click_pulse = (int(t * 16) != int((t - 1/sample_rate) * 16))
                click_t = t % (1/16)
                env = math.exp(-click_t * 60.0)
                val = math.sin(2 * math.pi * 2400.0 * click_t) * env * (random.random() * 0.4 + 0.6)
                int_val = int(val * 18000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))
                
        else: # Generic punch / desk hit
            duration = 0.35
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 14.0)
                tone = math.sin(2 * math.pi * (140.0 - t * 180) * t)
                val = (tone * 0.8 + (random.random()*2-1)*0.2) * env
                int_val = int(val * 26000)
                int_val = max(-32768, min(32767, int_val))
                raw_data.extend(struct.pack("<h", int_val))

        with wave.open(str(out_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(raw_data)
