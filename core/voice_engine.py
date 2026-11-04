"""
Neural Voice & Word-Level Timestamp Engine
Supports Kokoro Neural ONNX (am_michael 1.12x) with Edge-TTS auto-fallback.
"""

import os
import re
import json
import asyncio
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from core.config import find_model_paths, get_ffmpeg_path


class VoiceEngine:
    def __init__(self):
        self._kokoro = None
        self.model_path, self.voices_path = find_model_paths()

    def _get_kokoro(self):
        if self._kokoro is None and self.model_path.exists() and self.voices_path.exists():
            try:
                from kokoro_onnx import Kokoro, EspeakConfig
                import espeakng_loader

                espeak = EspeakConfig(
                    lib_path=espeakng_loader.get_library_path(),
                    data_path=espeakng_loader.get_data_path()
                )
                self._kokoro = Kokoro(str(self.model_path), str(self.voices_path), espeak_config=espeak)
            except Exception as e:
                self._kokoro = None
        return self._kokoro

    def synthesize(self, script: List[str], output_dir: Path) -> Dict[str, Any]:
        """
        Synthesizes voiceover from the 8-sentence script.
        Uses Kokoro ONNX if model weights exist, otherwise Edge-TTS neural voice.
        Returns paths to vo.wav, audio.m4a, words.json, captions list, and total duration.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        k = self._get_kokoro()
        if k:
            return self._synthesize_kokoro(script, audio_dir, output_dir)
        else:
            return self._synthesize_edgetts(script, audio_dir, output_dir)

    def _synthesize_kokoro(self, script: List[str], audio_dir: Path, output_dir: Path) -> Dict[str, Any]:
        k = self._get_kokoro()
        voice = "am_michael"
        speed = 1.12
        gap_sec = 0.12

        out_samples = []
        t = 0.0
        meta_lines = []
        all_words = []

        for i, line in enumerate(script):
            clean_line = line.strip()
            samples, sr = k.create(clean_line, voice=voice, speed=speed, lang="en-us")

            # Trim silence
            a = np.abs(samples)
            thr = 0.01
            idx = np.where(a > thr)[0]
            if len(idx) > 0:
                samples = samples[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]

            line_dur = len(samples) / sr
            line_start = t
            sf.write(str(audio_dir / f"line_{i:02d}.wav"), samples, sr)

            meta_lines.append({
                "i": i,
                "text": clean_line,
                "start": round(line_start, 3),
                "dur": round(line_dur, 3)
            })
            out_samples.append(samples)

            # Word timestamps
            raw_words = clean_line.split()
            total_chars = sum(max(1, len(w.rstrip(",.?!:;"))) for w in raw_words)
            usable_dur = line_dur * 0.94
            curr_wt = line_start

            for w in raw_words:
                clean_w = w.rstrip(",.?!:;")
                w_dur = max(0.12, (max(1, len(clean_w)) / total_chars) * usable_dur)
                all_words.append({"w": w, "s": round(curr_wt, 3), "e": round(curr_wt + w_dur, 3)})
                curr_wt += w_dur + (line_dur * 0.06 / len(raw_words))

            gap = gap_sec + (0.12 if i == 0 or clean_line.rstrip().endswith(('?', '!')) else 0)
            out_samples.append(np.zeros(int(gap * sr), dtype=samples.dtype))
            t += line_dur + gap

        vo = np.concatenate(out_samples)
        total_duration = round(len(vo) / sr, 2)
        vo_wav = audio_dir / "vo.wav"
        sf.write(str(vo_wav), vo, sr)

        # M4A preview
        audio_m4a = output_dir / "audio.m4a"
        ff = get_ffmpeg_path()
        subprocess.run([ff, "-y", "-v", "error", "-i", str(vo_wav), "-c:a", "aac", "-b:a", "192k", str(audio_m4a)], check=True)

        words_json = audio_dir / "vo.words.json"
        with open(words_json, "w", encoding="utf-8") as f:
            json.dump(all_words, f, indent=2)

        captions = self._chunk_captions(all_words)
        return {
            "vo_wav": vo_wav,
            "audio_m4a": audio_m4a,
            "words_json": words_json,
            "captions": captions,
            "duration": total_duration,
            "meta_lines": meta_lines,
            "engine": "Kokoro Neural ONNX"
        }

    def _synthesize_edgetts(self, script: List[str], audio_dir: Path, output_dir: Path) -> Dict[str, Any]:
        """Edge-TTS fallback: Zero model download required."""
        import edge_tts

        full_text = " ".join(script)
        vo_mp3 = audio_dir / "vo_raw.mp3"
        vo_wav = audio_dir / "vo.wav"
        audio_m4a = output_dir / "audio.m4a"

        async def _run():
            communicate = edge_tts.Communicate(full_text, voice="en-US-ChristopherNeural", rate="+12%")
            await communicate.save(str(vo_mp3))

        asyncio.run(_run())

        ff = get_ffmpeg_path()
        subprocess.run([ff, "-y", "-v", "error", "-i", str(vo_mp3), "-ar", "24000", str(vo_wav)], check=True)
        subprocess.run([ff, "-y", "-v", "error", "-i", str(vo_wav), "-c:a", "aac", "-b:a", "192k", str(audio_m4a)], check=True)

        info = sf.info(str(vo_wav))
        total_duration = round(info.duration, 2)

        # Estimate word timestamps
        words = full_text.split()
        dur_per_word = (total_duration * 0.95) / max(1, len(words))
        all_words = []
        cur_t = 0.0
        for w in words:
            all_words.append({"w": w, "s": round(cur_t, 3), "e": round(cur_t + dur_per_word, 3)})
            cur_t += dur_per_word

        words_json = audio_dir / "vo.words.json"
        with open(words_json, "w", encoding="utf-8") as f:
            json.dump(all_words, f, indent=2)

        captions = self._chunk_captions(all_words)
        return {
            "vo_wav": vo_wav,
            "audio_m4a": audio_m4a,
            "words_json": words_json,
            "captions": captions,
            "duration": total_duration,
            "meta_lines": [],
            "engine": "Edge-TTS Neural"
        }

    def _chunk_captions(self, words: List[Dict[str, Any]]) -> List[List[Any]]:
        small = {'a', 'an', 'the', 'at', 'to', 'of', 'in', 'on', 'and', 'or', 'but', 'for', 'with', 'by', 'it', 'is', 'like', 'as', 'so'}
        captions = []
        cur = []
        for j, w in enumerate(words):
            cur.append(w)
            text = ' '.join(x['w'] for x in cur)
            stop = any(w['w'].endswith(p) for p in ['.', ',', '?', '!', ';', ':'])
            dangling = w['w'].lower() in small and j + 1 < len(words) and len(cur) < 4
            if stop or ((len(cur) >= 3 or len(text) >= 18) and not dangling):
                c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
                captions.append([round(cur[0]['s'], 2), c_text])
                cur = []
        if cur:
            c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
            captions.append([round(cur[0]['s'], 2), c_text, round(cur[-1]['e'] + 0.3, 2)])
        return captions


voice_engine = VoiceEngine()

