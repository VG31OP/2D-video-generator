"""Render a single-style 2D sketch reel without ToonForge's provider pipeline.

The renderer is deliberately self-contained: Pillow draws every visual frame,
the same ink-and-paper art direction is used in every shot, and FFmpeg only
encodes the finished frame stream. No LLM, image model, TTS, provider, or
external service is invoked.
"""

import base64
import io
import json
import math
import random
import shutil
import struct
import subprocess
import sys
import uuid
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
WIDTH, HEIGHT, FPS, TOTAL_SECONDS = 540, 960, 24, 22.0
INK, PAPER, PAPER_SHADOW = "#202431", "#F7F0DE", "#E5D8BF"
CYAN, CORAL, GOLD, NAVY, MINT = "#23B7C7", "#ED6A5A", "#F4C95D", "#27324A", "#92D5B2"
SCENES = [
    (4.2, "ONE IDEA", "STARTS AS A SCRIBBLE", "sketch"),
    (4.4, "GIVE IT A CHARACTER", "WITH A POINT OF VIEW", "character"),
    (4.4, "ADD A LITTLE MOTION", "AND A LOT OF FEELING", "motion"),
    (4.4, "LET THE STORY", "BREATHE BETWEEN BEATS", "story"),
    (4.6, "DRAW. MOVE. SHARE.", "ONE STYLE. ONE WORLD.", "final"),
]
VOICE_SSML = """<speak version='1.0' xml:lang='en-US'>
<prosody rate='-8%' pitch='+2st'>Every great reel starts with a tiny scribble.</prosody>
<break time='1300ms'/>
<prosody rate='-8%' pitch='+2st'>Give that scribble a character, and a clear point of view.</prosody>
<break time='1250ms'/>
<prosody rate='-8%' pitch='+2st'>Then add motion with bounce, rhythm, and feeling.</prosody>
<break time='1200ms'/>
<prosody rate='-8%' pitch='+2st'>Leave space between each beat, so the story can breathe.</prosody>
<break time='1200ms'/>
<prosody rate='-8%' pitch='+2st'>One style. One world. Draw it, move it, and share it.</prosody>
</speak>"""


def font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    names = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"] if bold else ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


FONT_L, FONT_M, FONT_S = font(39), font(24), font(15)


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def ease_out_back(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return 1 + 2.70158 * (value - 1) ** 3 + 1.70158 * (value - 1) ** 2


def paper_texture() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    rng = random.Random(311)
    for _ in range(1700):
        draw.point((rng.randrange(WIDTH), rng.randrange(HEIGHT)), fill=rng.choice([(231, 218, 193), (255, 250, 236), (219, 203, 174)]))
    for y in range(90, HEIGHT, 54):
        draw.line((0, y, WIDTH, y), fill=(193, 211, 219), width=1)
    draw.line((66, 0, 66, HEIGHT), fill=(231, 142, 126), width=2)
    return image


PAPER_BASE = paper_texture()


def line(draw: ImageDraw.ImageDraw, coords, fill=INK, width=3, jitter=0, seed=0) -> None:
    if jitter:
        rng = random.Random(seed)
        coords = [(int(x + rng.uniform(-jitter, jitter)), int(y + rng.uniform(-jitter, jitter))) for x, y in coords]
    draw.line(coords, fill=fill, width=width, joint="curve")


def outlined_ellipse(draw: ImageDraw.ImageDraw, box, fill, width=3, seed=0) -> None:
    draw.ellipse(box, fill=fill, outline=INK, width=width)
    offset = random.Random(seed).choice([-1, 1])
    draw.ellipse((box[0] + offset, box[1], box[2] + offset, box[3]), outline=INK, width=1)


def outlined_polygon(draw: ImageDraw.ImageDraw, points, fill, width=3) -> None:
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=INK, width=width, joint="curve")


def burst(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, progress: float, color=GOLD) -> None:
    for index in range(int(16 * smoothstep(progress))):
        angle = (index / 16) * math.tau + 0.12 * math.sin(index * 4)
        line(draw, [(cx + math.cos(angle) * radius * 0.62, cy + math.sin(angle) * radius * 0.62), (cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)], color, 3, 1, index)


def draw_pencil(draw: ImageDraw.ImageDraw, x: float, y: float, angle: float, scale: float = 1.0) -> None:
    length, half = 150 * scale, 10 * scale
    ux, uy, vx, vy = math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle)
    def point(along, across): return (x + ux * along + vx * across, y + uy * along + vy * across)
    outlined_polygon(draw, [point(-length / 2, -half), point(length / 2, -half), point(length / 2, half), point(-length / 2, half)], GOLD)
    outlined_polygon(draw, [point(length / 2, -half), point(length / 2 + 25 * scale, 0), point(length / 2, half)], PAPER_SHADOW)
    line(draw, [point(length / 2 + 21 * scale, 0), point(length / 2 + 27 * scale, 0)], INK, 4)
    line(draw, [point(-length / 2 + 15 * scale, -half), point(-length / 2 + 15 * scale, half)], CORAL, 4)


def draw_character(draw: ImageDraw.ImageDraw, cx: float, base_y: float, pose: str, seconds: float, scale: float = 1.0) -> None:
    """One reusable model sheet: black ink, cyan jacket, and coral scarf."""
    bob = math.sin(seconds * 4.2) * 3 * scale
    jump = -30 * scale * max(0.0, math.sin(seconds * 3.4)) ** 2 if pose == "jump" else 0
    base_y += bob + jump
    head_y, body_top, skin = base_y - 250 * scale, base_y - 150 * scale, "#EFB58F"
    draw.ellipse((cx - 78 * scale, base_y - 8 * scale, cx + 78 * scale, base_y + 17 * scale), fill=(73, 66, 57))
    for side in (-1, 1):
        x = cx + side * 29 * scale
        line(draw, [(x, body_top + 122 * scale), (x + side * 16 * scale, base_y - 13 * scale)], NAVY, int(18 * scale))
        outlined_ellipse(draw, (x + side * 5 * scale - 28 * scale, base_y - 14 * scale, x + side * 5 * scale + 29 * scale, base_y + 13 * scale), "#FFFFFF", 2, int(seconds * 10 + side))
    outlined_polygon(draw, [(cx - 76 * scale, body_top), (cx + 76 * scale, body_top), (cx + 92 * scale, body_top + 126 * scale), (cx - 92 * scale, body_top + 126 * scale)], CYAN)
    draw.rectangle((cx - 10 * scale, body_top, cx + 10 * scale, body_top + 125 * scale), fill=PAPER)
    line(draw, [(cx, body_top), (cx, body_top + 125 * scale)], INK, 2)
    outlined_polygon(draw, [(cx - 49 * scale, body_top + 1 * scale), (cx + 45 * scale, body_top + 1 * scale), (cx + 20 * scale, body_top + 32 * scale), (cx - 42 * scale, body_top + 26 * scale)], CORAL, 2)
    outlined_ellipse(draw, (cx - 66 * scale, head_y - 64 * scale, cx + 66 * scale, head_y + 66 * scale), skin, 3, int(seconds * 7))
    outlined_polygon(draw, [(cx - 70 * scale, head_y - 23 * scale), (cx - 55 * scale, head_y - 75 * scale), (cx - 18 * scale, head_y - 87 * scale), (cx + 7 * scale, head_y - 71 * scale), (cx + 40 * scale, head_y - 83 * scale), (cx + 70 * scale, head_y - 26 * scale), (cx + 46 * scale, head_y - 44 * scale), (cx + 17 * scale, head_y - 32 * scale), (cx - 8 * scale, head_y - 46 * scale), (cx - 38 * scale, head_y - 30 * scale)], NAVY, 3)
    blink, eye_y = abs(math.sin(seconds * 1.7)) < 0.045, head_y - 3 * scale
    for ex in (-24, 24):
        if blink: line(draw, [(cx + ex * scale - 7 * scale, eye_y), (cx + ex * scale + 7 * scale, eye_y)], INK, 2)
        else:
            outlined_ellipse(draw, (cx + ex * scale - 6 * scale, eye_y - 7 * scale, cx + ex * scale + 6 * scale, eye_y + 7 * scale), "#FFFFFF", 1, int(seconds * 13))
            draw.ellipse((cx + ex * scale - 2 * scale, eye_y - 3 * scale, cx + ex * scale + 3 * scale, eye_y + 3 * scale), fill=INK)
    smile = 9 * scale + (4 * scale if pose in ("celebrate", "jump") else 0)
    line(draw, [(cx - 16 * scale, head_y + 28 * scale), (cx, head_y + 28 * scale + smile), (cx + 16 * scale, head_y + 28 * scale)], CORAL, 3)
    shoulder_y = body_top + 37 * scale
    if pose == "draw":
        line(draw, [(cx + 55 * scale, shoulder_y), (cx + 113 * scale, base_y - 100 * scale), (cx + 155 * scale, base_y - 57 * scale)], skin, int(15 * scale))
        outlined_ellipse(draw, (cx + 145 * scale, base_y - 68 * scale, cx + 169 * scale, base_y - 44 * scale), skin, 2)
    elif pose in ("celebrate", "jump"):
        for side in (-1, 1):
            line(draw, [(cx + side * 55 * scale, shoulder_y), (cx + side * 108 * scale, body_top - 56 * scale)], skin, int(15 * scale))
            outlined_ellipse(draw, (cx + side * 108 * scale - 13 * scale, body_top - 70 * scale, cx + side * 108 * scale + 14 * scale, body_top - 43 * scale), skin, 2)
    else:
        for side in (-1, 1):
            line(draw, [(cx + side * 55 * scale, shoulder_y), (cx + side * 105 * scale, base_y - 95 * scale)], skin, int(15 * scale))
            outlined_ellipse(draw, (cx + side * 105 * scale - 13 * scale, base_y - 108 * scale, cx + side * 105 * scale + 14 * scale, base_y - 82 * scale), skin, 2)


def caption(draw: ImageDraw.ImageDraw, top: str, bottom: str, phase: float) -> None:
    scale = min(1.0, ease_out_back(phase * 6.5)); box_y = int(704 + (1 - scale) * 38)
    draw.rounded_rectangle((88, box_y, WIDTH - 30, box_y + 124), radius=20, fill="#FFF9EB", outline=INK, width=3)
    draw.rectangle((88, box_y, 98, box_y + 124), fill=CORAL)
    for text, y, fill in ((top, box_y + 20, INK), (bottom, box_y + 64, CORAL)):
        x0, _, x1, _ = draw.textbbox((0, 0), text, font=FONT_M)
        draw.text(((WIDTH - (x1 - x0)) // 2 + 4, y + 4), text, font=FONT_M, fill=PAPER_SHADOW)
        draw.text(((WIDTH - (x1 - x0)) // 2, y), text, font=FONT_M, fill=fill)


def scene_frame(seconds: float) -> Image.Image:
    elapsed, scene_index = seconds, len(SCENES) - 1
    for index, (duration, _top, _bottom, _kind) in enumerate(SCENES):
        if elapsed < duration: scene_index = index; break
        elapsed -= duration
    duration, top, bottom, kind = SCENES[scene_index]
    phase, intro = elapsed / duration, smoothstep((elapsed / duration) / 0.22)
    image = PAPER_BASE.copy().convert("RGBA"); draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((30, 32, WIDTH - 30, 655), radius=22, outline=INK, width=4)
    draw.rectangle((45, 50, 184, 78), fill=INK); draw.text((56, 56), f"FRAME 0{scene_index + 1}", font=FONT_S, fill="#FFFFFF")
    for index in range(5):
        fill = [CORAL, CYAN, GOLD, MINT, NAVY][index] if index == scene_index else PAPER_SHADOW
        draw.ellipse((400 + index * 20, 56, 414 + index * 20, 70), fill=fill, outline=INK if index == scene_index else None)
    if kind == "sketch":
        glow = 40 + 31 * ease_out_back(intro)
        outlined_ellipse(draw, (270 - glow, 258 - glow, 270 + glow, 258 + glow), "#FFF5BF", 3, 7)
        line(draw, [(270, 295), (270, 333)], GOLD, 6)
        for dx in (-17, -6, 6, 17): line(draw, [(270 + dx, 333), (270 + dx * 0.8, 348)], INK, 3)
        burst(draw, 270, 258, 83, intro, CORAL); draw_character(draw, 202, 606, "draw", seconds, 0.98)
        pencil_y = 545 + 10 * math.sin(seconds * 8); draw_pencil(draw, 358, pencil_y, -0.63 + 0.08 * math.sin(seconds * 8), 0.8)
        line(draw, [(332, 562), (372, 579), (407, 561)], CYAN, 3, 2, int(seconds * 10))
    elif kind == "character":
        draw.rounded_rectangle((100, 151, 440, 480), radius=18, fill="#FFF9EB", outline=INK, width=3); draw.text((136, 171), "MODEL SHEET", font=FONT_M, fill=INK)
        draw_character(draw, 270, 532, "stand", seconds, 1.0)
        for y, colour, label in ((538, CYAN, "VOICE"), (570, CORAL, "STYLE"), (602, GOLD, "ENERGY")):
            draw.ellipse((92, y, 108, y + 16), fill=colour, outline=INK, width=1); draw.text((119, y - 2), label, font=FONT_S, fill=INK)
        burst(draw, 270, 305, 130, intro, CYAN)
    elif kind == "motion":
        path_y = 432; line(draw, [(92, path_y), (170, path_y - 52), (260, path_y + 15), (350, path_y - 80), (450, path_y)], INK, 3, 2, 5)
        for x in (122, 220, 324, 420): draw.ellipse((x, path_y + 69, x + 9, path_y + 78), fill=CORAL)
        x = 136 + 268 * smoothstep(phase); draw_character(draw, x, 602, "jump", seconds, 0.82)
        for offset in (0, 13, 27): line(draw, [(x - 82 - offset, 518 + offset), (x - 46 - offset, 502 + offset)], CYAN, 3)
        burst(draw, x, 378, 88, intro, GOLD)
    elif kind == "story":
        panel_y = 190
        for index in range(3):
            px = 67 + index * 148; draw.rounded_rectangle((px, panel_y, px + 122, panel_y + 164), radius=12, fill="#FFF9EB", outline=INK, width=3)
            if index == 0: draw.ellipse((px + 42, panel_y + 35, px + 80, panel_y + 73), fill=CYAN, outline=INK, width=2)
            elif index == 1: draw.polygon([(px + 61, panel_y + 30), (px + 94, panel_y + 78), (px + 34, panel_y + 78)], fill=GOLD, outline=INK)
            else: draw.ellipse((px + 36, panel_y + 31, px + 86, panel_y + 81), fill=CORAL, outline=INK, width=2)
            line(draw, [(px + 26, panel_y + 114), (px + 98, panel_y + 114)], PAPER_SHADOW, 3); line(draw, [(px + 26, panel_y + 132), (px + 84, panel_y + 132)], PAPER_SHADOW, 3)
        line(draw, [(128, 395), (258, 445), (406, 391)], CORAL, 5, 1, 31); draw_character(draw, 274, 620, "draw", seconds, 0.88); draw_pencil(draw, 392, 537, -0.6, 0.65)
    else:
        draw.ellipse((145, 146, 395, 394), fill="#FFF9EB", outline=INK, width=4); draw_character(draw, 270, 608, "celebrate", seconds, 1.02); burst(draw, 270, 273, 160, intro, CYAN)
        for index in range(8):
            a = index * math.tau / 8 + seconds * 0.55; x, y = 270 + math.cos(a) * 157, 274 + math.sin(a) * 112
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=[CORAL, GOLD, CYAN][index % 3], outline=INK, width=1)
    caption(draw, top, bottom, intro); draw.text((88, 864), "INKFRAME STUDIO  /  HAND-DRAWN MOTION", font=FONT_S, fill=INK); draw.text((88, 888), "A SINGLE-STYLE 2D ANIMATION STUDY", font=FONT_S, fill="#5C5B57")
    return image.convert("RGB")


def make_audio(output: Path) -> None:
    rate, frames = 48_000, int(TOTAL_SECONDS * 48_000)
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(rate); buffer = bytearray(); notes = (220.0, 277.18, 329.63, 392.0, 329.63, 277.18)
        for sample in range(frames):
            t, beat, note = sample / rate, (sample / rate) % 0.5, notes[int(sample / rate / 0.5) % len(notes)]
            value = max(-0.22, min(0.22, math.sin(math.tau * note * t) * 0.12 * math.exp(-beat * 6.5) + math.sin(math.tau * (note / 2) * t) * 0.045 + (math.sin(math.tau * 1600 * t) * 0.025 if beat < 0.018 else 0)))
            buffer.extend(struct.pack("<hh", int(value * 32767), int((value * 0.93 + 0.01 * math.sin(math.tau * 0.19 * t)) * 32767)))
            if len(buffer) > 262_144: wav.writeframes(buffer); buffer.clear()
        if buffer: wav.writeframes(buffer)


def make_voiceover(output: Path) -> None:
    """Create the narration with the local Windows voice--no network or API."""
    if sys.platform != "win32":
        raise RuntimeError("The self-contained voice-over renderer currently requires Windows SAPI")
    # UTF-16 encoded PowerShell avoids shell quoting issues and preserves SSML exactly.
    script = f"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {{
  # Use the OS default voice: it is the most reliable output device in a
  # non-interactive render process, including systems without the desktop tokens.
  $voice.Volume = 95
  $voice.SetOutputToWaveFile('{str(output.resolve()).replace("'", "''")}')
  $voice.SpeakSsml(@'
{VOICE_SSML}
'@)
}} finally {{
  $voice.Dispose()
}}
"""
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    result = subprocess.run(["powershell", "-STA", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Local SAPI voice-over failed: {result.stderr.strip()}")


def find_ffmpeg() -> str:
    if found := shutil.which("ffmpeg"): return found
    bundled = Path(sys.executable).parent / "Scripts" / "ffmpeg.exe"
    if bundled.exists(): return str(bundled)
    raise FileNotFoundError("FFmpeg was not found on PATH or in the Python Scripts directory")


def main() -> None:
    draft = STORAGE / "drafts" / f"single_style_sketch_reel_{uuid.uuid4().hex[:6]}"; draft.mkdir(parents=True, exist_ok=False)
    audio_path, voice_path = draft / "sketch_score.wav", draft / "voiceover.wav"
    silent_video, video_path, thumbnail = draft / "video_silent.mp4", draft / "single_style_sketch_reel.mp4", draft / "thumbnail.jpg"
    print(f"Rendering one-style 2D reel into: {draft}"); make_audio(audio_path); make_voiceover(voice_path)
    scene_frame(18.2).resize((1080, 1920), Image.Resampling.LANCZOS).save(thumbnail, quality=95)
    command = [find_ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS), "-i", "-", "-vf", "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-an", str(silent_video)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for index in range(int(TOTAL_SECONDS * FPS)):
            process.stdin.write(scene_frame(index / FPS).tobytes())
            if index % FPS == 0: print(f"Rendered {index // FPS + 1:02d}/{int(TOTAL_SECONDS):02d} seconds")
        process.stdin.close(); stderr = process.stderr.read().decode("utf-8", errors="replace")
        if process.wait() != 0: raise RuntimeError(f"FFmpeg encoding failed: {stderr}")
    finally:
        if process.stdin and not process.stdin.closed: process.stdin.close()
    mix_command = [find_ffmpeg(), "-y", "-loglevel", "error", "-i", str(silent_video), "-i", str(audio_path), "-i", str(voice_path), "-filter_complex", "[1:a]volume=0.42[music];[music][2:a]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[ducked];[ducked][2:a]amix=inputs=2:normalize=0[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(video_path)]
    subprocess.run(mix_command, check=True, capture_output=True, text=True)
    silent_video.unlink(missing_ok=True)
    manifest = {"title": "One Style, One World", "format": "1080x1920 H.264/AAC, 30 fps", "duration_seconds": TOTAL_SECONDS, "art_direction": "single hand-drawn ink, paper, cyan, coral, and gold style", "renderer": "self-contained Pillow frame renderer + FFmpeg encoder", "voice_over": "Microsoft Zira Desktop via local Windows SAPI", "providers_used": [], "video_path": str(video_path.resolve()), "thumbnail_path": str(thumbnail.resolve())}
    manifest_path = draft / "manifest.json"; manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"REEL_VIDEO={video_path}"); print(f"REEL_THUMBNAIL={thumbnail}"); print(f"REEL_MANIFEST={manifest_path}")


if __name__ == "__main__": main()
