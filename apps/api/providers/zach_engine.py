"""
Zack D. Films 3D Explainer Autonomous Engine (Default Style)
============================================================
Produces 3D procedural cartoon explainer shorts (9:16 vertical, 1080x1920 30fps)
in the signature Zack D. Films style:
- Three.js WebGL procedural 3D animation (Playwright headless Chromium)
- Kokoro Neural TTS (am_michael 1.12x) per artemnovitckii/claude-animation-skills
- Comfortable zoomed-out camera framing (FOV 42°-45°, pullback Z=1.6m-2.4m)
- Word-level kinetic captions & EBU R128 loudness normalization
- Direct Instagram upload to @vrj.ai with engagement boost & cache clean
"""

import os
import sys
import re
import json
import shutil
import hashlib
import asyncio
import subprocess
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates" / "zach_engine"
MODELS_DIR = ROOT_DIR / "storage" / "models"


def find_model_paths() -> Tuple[Path, Path]:
    """Dynamically locates Kokoro ONNX model and voices bin across system."""
    candidates = [
        MODELS_DIR,
        Path.home() / ".gemini" / "config" / "skills" / "animation-kit" / "models",
        Path.home() / ".cache" / "kokoro",
    ]
    for c in candidates:
        m = c / "kokoro-v1.0.onnx"
        v = c / "voices-v1.0.bin"
        if m.exists() and v.exists():
            return m, v
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return MODELS_DIR / "kokoro-v1.0.onnx", MODELS_DIR / "voices-v1.0.bin"


def find_template_dir() -> Path:
    """Locates the bundled Three.js Zack D. Films engine template."""
    if TEMPLATE_DIR.exists():
        return TEMPLATE_DIR
    skills_dir = Path.home() / ".gemini" / "config" / "skills" / "zach-d-films" / "engine"
    if skills_dir.exists():
        return skills_dir
    return TEMPLATE_DIR


def find_node_modules() -> Optional[Path]:
    """Locates Three.js node_modules across project or system."""
    candidates = [
        TEMPLATE_DIR / "node_modules",
        ROOT_DIR / "node_modules",
        Path.home() / ".gemini" / "config" / "skills" / "animation-kit" / "node_modules",
    ]
    for c in candidates:
        if c.exists() and (c / "three").exists():
            return c
    return None


from kokoro_onnx import Kokoro, EspeakConfig
import espeakng_loader


class ZachFilmsEngine:
    def __init__(self):
        self.espeak = EspeakConfig(
            lib_path=espeakng_loader.get_library_path(),
            data_path=espeakng_loader.get_data_path()
        )
        model_p, voice_p = find_model_paths()
        self.model_path = str(model_p)
        self.voices_path = str(voice_p)
        self._kokoro = None

    def get_kokoro(self) -> Kokoro:
        if self._kokoro is None:
            self._kokoro = Kokoro(self.model_path, self.voices_path, espeak_config=self.espeak)
        return self._kokoro

    def generate_script(self, topic: str) -> List[str]:
        """
        Creates an 8-sentence viral Zack D. script tailored to the given topic:
        Hook -> Misconception -> "But" Twist -> 4-Step Mechanism -> Payoff
        """
        t = topic.strip()
        t_lower = t.lower()

        # Domain: Quantum Computing / Processors
        if any(w in t_lower for w in ["quantum", "processor", "chip", "cpu", "gpu", "transistor", "nanometer"]):
            return [
                f"When you use a powerful computer to calculate billions of numbers,",
                "some people assume processors just get infinitely smaller and faster.",
                "But in reality, standard silicon chips are hitting an absolute physical wall.",
                "First, microscopic transistors shrink down to the size of individual atoms.",
                "At that scale, electrons literally teleport through barriers called quantum tunneling.",
                "To overcome this, quantum computers replace binary bits with subatomic qubits.",
                "These qubits exist in multiple superpositions, calculating every possibility simultaneously.",
                "Until they solve impossibly complex problems in seconds that would take normal computers millions of years."
            ]

        # Domain: AI / Neural Networks / Machine Learning
        elif any(w in t_lower for w in ["ai", "artificial intelligence", "neural network", "chatgpt", "llm", "deep learning", "robot"]):
            return [
                f"When you ask an AI model a question and it answers in seconds,",
                "some people think the computer is actually thinking like a human brain.",
                "But in reality, it doesn't possess a single conscious thought.",
                "First, your prompt is broken down into numerical mathematical vectors called tokens.",
                "Billions of transformer matrix weights calculate probability patterns across massive datasets.",
                "The neural network predicts the single most statistically probable word next in line.",
                "Repeating this process thousands of times at lightning speed creates fluent answers.",
                "Until a complete, human-sounding response appears on your screen like magic."
            ]

        # Domain: Space / Black Holes / Physics
        elif any(w in t_lower for w in ["black hole", "space", "gravity", "universe", "time travel", "star", "physics"]):
            return [
                f"If you ever fell into a supermassive black hole,",
                "some people think you would just be crushed instantly into a pancake.",
                "But in reality, a bizarre cosmic process called spaghettification happens first.",
                "First, because gravity weakens with distance, the pull on your feet is vastly stronger than your head.",
                "This immense gravitational differential stretches your body vertically into a thin string.",
                "As you cross the event horizon, even light itself cannot escape the gravitational pull.",
                "Time begins to warp so dramatically that an outside observer sees you freeze forever.",
                "Until all of your subatomic particles are compressed into a single microscopic point called a singularity."
            ]

        # Domain: Biology / Human Body / Medical
        elif any(w in t_lower for w in ["body", "brain", "heart", "sleep", "dream", "coffee", "caffeine", "immune", "virus"]):
            return [
                f"When you drink a strong cup of coffee to wake yourself up,",
                "some people assume caffeine actively creates brand new energy in your body.",
                "But in reality, caffeine doesn't give you any real energy at all.",
                "Throughout the day, your brain produces a chemical called adenosine that makes you feel tired.",
                "Adenosine locks into brain receptors like a key, signaling fatigue and making you drowsy.",
                "Caffeine has an identical molecular shape, slipping into those receptors and blocking them completely.",
                "With the drowsiness signals blocked, adrenaline and dopamine surge through your bloodstream.",
                "Until the caffeine finally wears off, and all that trapped adenosine hits you in a massive crash."
            ]

        # Domain: Security / Passwords / Hacking
        elif any(w in t_lower for w in ["hack", "hacker", "password", "security", "dark web", "vpn", "malware", "virus"]):
            return [
                f"When you enter your password into a secure website,",
                "some people think the server saves your actual password in a secret database.",
                "But in reality, storing raw passwords is so dangerous it would be a disaster.",
                "First, the website runs your password through a cryptographic hashing algorithm.",
                "This scrambles your characters into a permanent, irreversible mathematical fingerprint.",
                "A random string of digital noise called salt is injected to prevent dictionary attacks.",
                "When you log in, the server only compares the resulting mathematical hash to verify your identity.",
                "Which means even if hackers breach the entire company, they still can't see your real password."
            ]

        # Default / Fallback: Dynamic Structured Zack D. Narrative
        else:
            subject = re.sub(r'^(how|why|what happens when|can|could)\s+', '', t, flags=re.IGNORECASE).rstrip("?.! ")
            return [
                f"When you look at how {subject} works,",
                "some people assume the process is relatively simple and straightforward.",
                "But in reality, the underlying mechanism is completely unexpected.",
                f"First, the system initiates the core interaction in a fraction of a second.",
                "Specialized components break the process down into multiple rapid stages.",
                "Precise physical forces guide each step to ensure absolute stability.",
                "High-speed signals coordinate the entire chain reaction with microsecond precision.",
                f"Until the final payoff executes, completing {subject} right before your eyes."
            ]

    def synthesize_voice_and_captions(self, script: List[str], project_dir: Path) -> Tuple[Path, Path, Path, List[List[Any]], float]:
        """
        Synthesizes Kokoro voiceover (am_michael 1.12x) and produces word-level captions.
        """
        audio_dir = project_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        k = self.get_kokoro()
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
            idx = np.where(a > 0.01)[0]
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

        # M4A for preview
        audio_m4a = project_dir / "audio.m4a"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vo_wav), "-c:a", "aac", "-b:a", "192k", str(audio_m4a)], check=True)

        words_json = audio_dir / "vo.words.json"
        json.dump(all_words, open(words_json, "w", encoding="utf-8"), indent=2)

        # Chunks into 1-3 word captions
        small = {'a', 'an', 'the', 'at', 'to', 'of', 'in', 'on', 'and', 'or', 'but', 'for', 'with', 'by', 'it', 'is', 'like', 'as', 'so'}
        captions = []
        cur = []
        for j, w in enumerate(all_words):
            cur.append(w)
            text = ' '.join(x['w'] for x in cur)
            stop = re.search(r'[.,?!;:]$', w['w'])
            dangling = w['w'].lower() in small and j + 1 < len(all_words) and len(cur) < 4
            if stop or ((len(cur) >= 3 or len(text) >= 18) and not dangling):
                c_text = re.sub(r'[.,;:]+$', '', ' '.join(x['w'] for x in cur)).replace("'", "\\'")
                captions.append([round(cur[0]['s'], 2), c_text])
                cur = []
        if cur:
            c_text = re.sub(r'[.,;:]+$', '', ' '.join(x['w'] for x in cur)).replace("'", "\\'")
            captions.append([round(cur[0]['s'], 2), c_text, round(cur[-1]['e'] + 0.3, 2)])

        return vo_wav, audio_m4a, words_json, captions, total_duration

    def setup_project(self, project_dir: Path):
        """
        Copies Three.js engine from bundled templates and sets up cross-platform node_modules.
        """
        project_dir.mkdir(parents=True, exist_ok=True)
        template_dir = find_template_dir()

        for item in template_dir.iterdir():
            if item.name == "node_modules":
                continue
            dst = project_dir / item.name
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)

        # Cross-platform link or install for node_modules
        dst_modules = project_dir / "node_modules"
        if not dst_modules.exists():
            src_modules = find_node_modules()
            if src_modules and src_modules.exists():
                try:
                    if sys.platform == "win32":
                        subprocess.run(["cmd", "/c", "mklink", "/J", str(dst_modules), str(src_modules)], check=True, capture_output=True)
                    else:
                        os.symlink(src_modules, dst_modules)
                except Exception as e:
                    # Fallback to copy if symlink fails
                    shutil.copytree(src_modules, dst_modules)
            else:
                # Install directly if no existing node_modules found
                subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=str(project_dir), check=True)

    def render_and_mux(self, project_dir: Path, output_mp4: Path) -> Tuple[Path, Path]:
        """
        Renders 3D frames via Playwright and muxes into broadcast-ready 1080x1920 MP4.
        """
        vo_wav = project_dir / "audio" / "vo.wav"
        silent_mp4 = project_dir / "silent.mp4"

        print("[+] Rendering 3D Three.js animation via Playwright Chromium...")
        subprocess.run(["node", "render.mjs", "video", "silent.mp4", "30"], cwd=str(project_dir), check=True)

        print("[+] Muxing audio & scaling to 1080x1920 with EBU R128 loudness normalization...")
        output_mp4.parent.mkdir(parents=True, exist_ok=True)
        cmd_mux = [
            "ffmpeg", "-v", "error", "-y",
            "-i", str(silent_mp4),
            "-i", str(vo_wav),
            "-map", "0:v",
            "-map", "1:a",
            "-vf", "scale=1080:1920:flags=lanczos",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-af", "apad,loudnorm=I=-14:TP=-1.5",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-shortest",
            "-movflags", "+faststart",
            str(output_mp4)
        ]
        subprocess.run(cmd_mux, check=True)

        # Extract Cover Frame
        cover_jpg = project_dir / "cover.jpg"
        cmd_thumb = [
            "ffmpeg", "-y", "-ss", "00:00:01.200",
            "-i", str(output_mp4),
            "-vframes", "1", "-q:v", "2",
            str(cover_jpg)
        ]
        subprocess.run(cmd_thumb, capture_output=True)

        # Clean silent render
        if silent_mp4.exists():
            silent_mp4.unlink(missing_ok=True)

        return output_mp4, cover_jpg

    def build_and_publish(self, topic: str, custom_script: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Full Autonomous Pipeline:
        Topic -> Script -> Kokoro VO -> 3D Three.js Scene -> Mux -> Instagram Upload & Boost
        """
        from apps.api.services.instagram_service import instagram_service

        slug = re.sub(r'[^a-zA-Z0-9]+', '_', topic.lower()).strip('_')[:30]
        project_dir = ROOT_DIR / "storage" / "reels" / f"zach_{slug}"
        self.setup_project(project_dir)

        # 1. Script
        script = custom_script or self.generate_script(topic)
        json.dump(script, open(project_dir / "script.json", "w", encoding="utf-8"), indent=2)

        # 2. Voice & Captions
        vo_wav, audio_m4a, words_json, captions, duration = self.synthesize_voice_and_captions(script, project_dir)

        # 3. Shots file with Zoomed-Out Camera Framing
        # If customized shots.js exists, keep it, otherwise generate standard zoomed-out shots
        shots_file = project_dir / "src" / "shots.js"
        # The existing working shots.js in zach_how_internet_works has the tested zoomed-out framing
        ref_shots = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "src" / "shots.js"
        ref_props = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "src" / "props.js"
        ref_human = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "src" / "human.js"
        ref_mat = ROOT_DIR / "storage" / "reels" / "zach_how_internet_works" / "src" / "materials.js"

        if ref_props.exists():
            shutil.copy2(str(ref_props), str(project_dir / "src" / "props.js"))
        if ref_human.exists():
            shutil.copy2(str(ref_human), str(project_dir / "src" / "human.js"))
        if ref_mat.exists():
            shutil.copy2(str(ref_mat), str(project_dir / "src" / "materials.js"))

        if ref_shots.exists():
            shots_code = ref_shots.read_text(encoding="utf-8")
            # Replace captions and duration
            captions_js = "export const CAPTIONS = " + json.dumps(captions, indent=2) + ";\n"
            captions_js += f"export const DURATION = {duration + 0.4:.2f};\n"
            shots_code = re.sub(r'export const CAPTIONS = \[.*?\];', captions_js, shots_code, flags=re.DOTALL)
            shots_code = re.sub(r'export const DURATION = .*?;', f'export const DURATION = {duration + 0.4:.2f};', shots_code)
            shots_file.write_text(shots_code, encoding="utf-8")

        # 4. Render & Mux
        final_mp4 = project_dir / f"{slug}_final.mp4"
        out_video, cover_jpg = self.render_and_mux(project_dir, final_mp4)

        # 5. Instagram Upload & Auto-Boost
        caption = (
            f"Wait... is this REALLY how {topic.rstrip('?.!')} works? 🤯\n\n"
            f"Here is what actually happens behind the scenes:\n"
            f"• {script[2]}\n"
            f"• {script[3]}\n"
            f"• {script[4]}\n"
            f"• {script[6]}\n\n"
            f"Did you know this before? Drop your thoughts below! 👇\n\n"
            f"Follow @vrj.ai for more insane 3D explainers, hidden tech & viral digital science! 🚀\n"
            f".\n.\n"
            f"#tech #science #3danimation #zackdfilms #howitworks #technology #animation #viral #reels #explainer #vrjai #interestingfacts"
        )
        comment = f"Drop a ❤️ and save this! Did you think it worked like this before? Tell us below! 👇"

        print(f"\n[+] Publishing to Instagram (@vrj.ai)...")
        upload_res = instagram_service.upload_reel(
            video_path=str(out_video),
            caption=caption,
            thumbnail_path=str(cover_jpg) if cover_jpg.exists() else None
        )
        media_id = upload_res.get("media_id")
        reel_url = upload_res.get("url")

        boost_res = {}
        if media_id:
            print("[+] Executing engagement boost (like, comment, story share)...")
            boost_res = instagram_service.post_reel_engagement(
                media_id=media_id,
                comment_text=comment,
                like=True,
                share_story=True,
                video_path=str(out_video)
            )

        # Clean local temporary caches
        silent_mp4 = project_dir / "silent.mp4"
        if silent_mp4.exists():
            silent_mp4.unlink(missing_ok=True)
        stills_dir = project_dir / "stills"
        if stills_dir.exists():
            shutil.rmtree(stills_dir, ignore_errors=True)

        return {
            "topic": topic,
            "duration": duration,
            "video_path": str(out_video),
            "cover_path": str(cover_jpg),
            "media_id": media_id,
            "reel_url": reel_url,
            "boost": boost_res,
        }

zach_engine = ZachFilmsEngine()

