"""
Production Script: Zack D. Films 3D Explainer - How GPS Actually Pinpoints Your Phone
Topic: How GPS Satellites Track Your Phone (Trilateration & Atomic Clocks)
Format: 9:16 Vertical (1080x1920, 30fps)
Voice: Kokoro TTS am_michael 1.12x
Engine: Three.js WebGL procedural 3D (Playwright Headless Chromium)
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
REEL_DIR = ROOT_DIR / "storage" / "reels" / "zach_gps_satellites"
AUDIO_DIR = REEL_DIR / "audio"
SRC_DIR = REEL_DIR / "src"
SKILLS_DIR = Path(r"C:\Users\ROHITBHAI\.gemini\config\skills")
KIT_MODELS = SKILLS_DIR / "animation-kit" / "models"
KIT_MODULES = SKILLS_DIR / "animation-kit" / "node_modules"

SCRIPT = [
    "When you open Google Maps and your exact location appears instantly,",
    "some people assume satellites in space are actively tracking your phone.",
    "But in reality, GPS satellites don't even know you exist.",
    "Your phone never sends a single signal back up into space.",
    "Instead, thirty-one satellites orbit Earth, constantly broadcasting radio signals with atomic clock timestamps.",
    "Your phone picks up signals from four satellites and measures the nanosecond delay of each radio wave.",
    "By calculating where these four radio spheres intersect, it pinpoints your exact position through trilateration.",
    "Meaning satellites aren't tracking you, your phone is doing pure geometry in your pocket."
]

def step1_prepare_directory():
    print("[1/5] Setting up directory structure and node_modules link for GPS reel...")
    REEL_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SRC_DIR.mkdir(parents=True, exist_ok=True)

    nm = REEL_DIR / "node_modules"
    if not nm.exists():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(nm), str(KIT_MODULES)], check=True)

    with open(REEL_DIR / "script.json", "w", encoding="utf-8") as f:
        json.dump(SCRIPT, f, indent=2)

def step2_generate_voice_and_captions():
    print("[2/5] Synthesizing Kokoro neural voiceover & computing word timings for GPS...")
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro, EspeakConfig
    import espeakng_loader

    espeak = EspeakConfig(
        lib_path=espeakng_loader.get_library_path(),
        data_path=espeakng_loader.get_data_path()
    )
    model_path = str(KIT_MODELS / "kokoro-v1.0.onnx")
    voices_path = str(KIT_MODELS / "voices-v1.0.bin")
    k = Kokoro(model_path, voices_path, espeak_config=espeak)

    voice = "am_michael"
    speed = 1.12
    gap_sec = 0.12

    out_samples = []
    t = 0.0
    meta_lines = []
    all_words = []

    for i, line in enumerate(SCRIPT):
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
        sf.write(str(AUDIO_DIR / f"line_{i:02d}.wav"), samples, sr)

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
    vo_wav = AUDIO_DIR / "vo.wav"
    sf.write(str(vo_wav), vo, sr)

    # M4A for browser preview
    audio_m4a = REEL_DIR / "audio.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vo_wav), "-c:a", "aac", "-b:a", "192k", str(audio_m4a)], check=True)

    words_json = AUDIO_DIR / "vo.words.json"
    with open(words_json, "w", encoding="utf-8") as f:
        json.dump(all_words, f, indent=2)

    # 1 to 3 word captions
    small = {'a', 'an', 'the', 'at', 'to', 'of', 'in', 'on', 'and', 'or', 'but', 'for', 'with', 'by', 'it', 'is', 'like', 'as', 'so'}
    captions = []
    cur = []
    for j, w in enumerate(all_words):
        cur.append(w)
        text = ' '.join(x['w'] for x in cur)
        stop = any(w['w'].endswith(p) for p in ['.', ',', '?', '!', ';', ':'])
        dangling = w['w'].lower() in small and j + 1 < len(all_words) and len(cur) < 4
        if stop or ((len(cur) >= 3 or len(text) >= 18) and not dangling):
            c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
            captions.append([round(cur[0]['s'], 2), c_text])
            cur = []
    if cur:
        c_text = ' '.join(x['w'] for x in cur).rstrip('.,;:').replace("'", "\\'")
        captions.append([round(cur[0]['s'], 2), c_text, round(cur[-1]['e'] + 0.3, 2)])

    print(f"    [✓] GPS Audio synthesized: {total_duration:.2f}s, {len(captions)} caption chunks")
    return meta_lines, captions, total_duration

if __name__ == "__main__":
    step1_prepare_directory()
    meta_lines, captions, total_duration = step2_generate_voice_and_captions()
    print("Meta lines:")
    for m in meta_lines:
        print(f"  Line {m['i']}: {m['start']:.2f}s - {m['start']+m['dur']:.2f}s ({m['dur']:.2f}s) -> {m['text']}")

