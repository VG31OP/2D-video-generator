import os
import math
import random
import hashlib
import json
import asyncio
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from apps.api.config import settings

class VisualProvider:
    def get_provider_name(self) -> str:
        return "GenericVisualProvider"

    def get_provider_type(self) -> str:
        return "FALLBACK"

    async def is_available(self) -> bool:
        return True

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        raise NotImplementedError

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        raise NotImplementedError

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, style: str = "Modern 2D Cartoon", logger_func = None) -> Dict[str, str]:
        raise NotImplementedError

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        raise NotImplementedError


class ComfyUIVisualProvider(VisualProvider):
    """
    Real AI Image Generation Provider via ComfyUI API endpoint.
    Connects to http://localhost:8188, loads available checkpoints,
    submits generation workflows, polls completion, and downloads real diffusion images.
    """
    def __init__(self, base_url: str = "http://localhost:8188"):
        self.base_url = base_url
        self.active_checkpoint = None

    def get_provider_name(self) -> str:
        ckpt_str = f" ({self.active_checkpoint})" if self.active_checkpoint else ""
        return f"ComfyUI AI Diffusion{ckpt_str}"

    def get_provider_type(self) -> str:
        return "REAL AI"

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/system_stats")
                if res.status_code == 200:
                    try:
                        obj_res = await client.get(f"{self.base_url}/object_info/CheckpointLoaderSimple")
                        if obj_res.status_code == 200:
                            obj_data = obj_res.json()
                            ckpts = obj_data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
                            if ckpts:
                                self.active_checkpoint = ckpts[0]
                                return True
                    except Exception:
                        pass
                    return True
                return False
        except Exception:
            return False

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        name = char_data.get("name", "Character")
        prompt = f"masterpiece, best quality, {style} character sheet, {name}, {char_data.get('gender', '')}, {char_data.get('age', '')} years old, {char_data.get('hair_style', '')}, {char_data.get('outfit_desc', '')}, vibrant colors, clean lineart, {style} style, white background"
        
        if logger_func:
            await logger_func(f"[AI] ComfyUI generating character reference sheet for {name} ({style})...")

        success = await self._run_comfyui_workflow(
            positive_prompt=prompt,
            negative_prompt="photorealistic, 3d render, noisy, low quality, deformed anatomy, blurry",
            output_path=output_path,
            width=540,
            height=960,
            logger_func=logger_func
        )
        if success:
            if logger_func:
                await logger_func(f"[AI] ComfyUI character reference sheet saved for {name}.")
            return output_path
            
        fallback = ToonVectorVisualProvider()
        return await fallback.generate_character_reference(char_data, output_path, style=style, logger_func=logger_func)

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        positive_prompt = f"masterpiece, best quality, {style} background, {location}, {prompt}, {style} style, clean vector shapes, vibrant colors, detailed interior scenery, 8k resolution, vertical composition"
        negative_prompt = "low quality, photo, 3d, realistic, deformed, noisy, text, watermark, blurry, human, character, face"

        if logger_func:
            await logger_func(f"[AI] ComfyUI generating AI background for {location} ({style})...")

        success = await self._run_comfyui_workflow(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            output_path=output_path,
            width=540,
            height=960,
            logger_func=logger_func
        )
        if success:
            if logger_func:
                await logger_func(f"[AI] ComfyUI background generated for {location}.")
            return output_path

        fallback = ToonVectorVisualProvider()
        return await fallback.generate_background(location, prompt, output_path, width, height, style=style, logger_func=logger_func)

    async def _run_comfyui_workflow(
        self,
        positive_prompt: str,
        negative_prompt: str,
        output_path: str,
        width: int = 540,
        height: int = 960,
        logger_func = None
    ) -> bool:
        if not await self.is_available():
            return False

        ckpt_name = self.active_checkpoint or "v1-5-pruned-emaonly.safetensors"
        prompt_workflow = {
            "3": {"class_type": "KSampler", "inputs": {"seed": random.randint(1, 1000000000), "steps": 20, "cfg": 7.5, "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt_name}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive_prompt, "clip": ["4", 1]}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["4", 1]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "toonforge_gen", "images": ["8", 0]}}
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                res = await client.post(f"{self.base_url}/prompt", json={"prompt": prompt_workflow})
                if res.status_code != 200:
                    return False
                prompt_id = res.json().get("prompt_id")
                if not prompt_id:
                    return False

                for _ in range(60):
                    await asyncio.sleep(1.5)
                    hist_res = await client.get(f"{self.base_url}/history/{prompt_id}")
                    if hist_res.status_code == 200:
                        hist_data = hist_res.json()
                        if prompt_id in hist_data:
                            outputs = hist_data[prompt_id].get("outputs", {})
                            for node_id, node_out in outputs.items():
                                if "images" in node_out and len(node_out["images"]) > 0:
                                    img_info = node_out["images"][0]
                                    fn = img_info.get("filename")
                                    sub = img_info.get("subfolder", "")
                                    img_url = f"{self.base_url}/view?filename={fn}&subfolder={sub}&type=output"
                                    
                                    img_res = await client.get(img_url)
                                    if img_res.status_code == 200:
                                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                                        with open(output_path, "wb") as f:
                                            f.write(img_res.content)
                                        return True
                return False
        except Exception:
            return False

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, style: str = "Modern 2D Cartoon", logger_func = None) -> Dict[str, str]:
        fallback = ToonVectorVisualProvider()
        return await fallback.generate_character_rig(char_data, output_dir, style=style, logger_func=logger_func)

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        fallback = ToonVectorVisualProvider()
        return await fallback.compose_scene_frame(bg_path, char_specs, action_desc, emotion, output_path, width, height, style=style, logger_func=logger_func)


class ToonVectorVisualProvider(VisualProvider):
    """
    Studio-Grade Modern 2026 2D Cartoon & Vector Visual Engine.
    Engineered with contemporary graphic illustration standards:
    - Stylized anime & modern western cartoon anatomy with multi-tone cel shading.
    - Double specular catchlights, expressive facial kinetics, and layered volumetric hair.
    - Architectural perspective environments with neon gradients, volumetric HUDs, and floor grids.
    - Cinematic compositing with depth-of-field soft focus, ambient rim lighting, and contact occlusion.
    """
    def __init__(self):
        self._font_cache = {}

    def get_provider_name(self) -> str:
        return "ToonVector Visual Engine (Studio 2026)"

    def get_provider_type(self) -> str:
        return "PROCEDURAL 2D"

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        font_key = (size, bold)
        if font_key in self._font_cache:
            return self._font_cache[font_key]
        
        candidate_paths = [
            "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\calibrib.ttf" if bold else "C:\\Windows\\Fonts\\calibri.ttf",
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    f = ImageFont.truetype(p, size)
                    self._font_cache[font_key] = f
                    return f
                except Exception:
                    pass
        f = ImageFont.load_default()
        self._font_cache[font_key] = f
        return f

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGBA", (1080, 1920), (10, 14, 26, 255))
        draw = ImageDraw.Draw(img)
        
        name = char_data.get("name", "Character")
        skin = char_data.get("skin_tone", "#f8dbd3")
        hair = char_data.get("hair_color", "#1e293b")
        outfit = char_data.get("outfit_color", "#0f172a")
        gender = char_data.get("gender", "Male")
        is_robot = "robot" in gender.lower() or "ai" in char_data.get("role", "").lower() or "bot" in name.lower() or "optimus" in name.lower()
        is_cat = "cat" in name.lower() or "cat" in char_data.get("role", "").lower()
        
        if is_robot:
            self._render_modern_robot_character(draw, 540, 950, "avatar", style=style)
        elif is_cat:
            self._render_modern_cat_character(draw, 540, 950, "avatar", skin, hair, style=style)
        else:
            self._render_modern_human_character(draw, 540, 950, "avatar", skin, hair, outfit, char_data.get("hair_style", "Messy Anime"), gender, style=style)
            
        img.convert("RGB").save(str(out_file), "PNG")
        if logger_func:
            await logger_func(f"[STUDIO] Generated 2026 character reference for {name} ({style}).")
        return str(out_file)

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        img = Image.new("RGBA", (width, height), (10, 14, 26, 255))
        loc = location.lower()
        p_lower = (prompt or "").lower()
        
        # High-Detail Modern Vector Environments
        if any(k in loc or k in p_lower for k in ["lab", "server", "tech", "computer", "garage", "cyber", "ai", "robot"]):
            img = self._draw_modern_scifi_lab_bg(width, height, location, style)
        elif any(k in loc or k in p_lower for k in ["space", "chaos", "dimension", "galaxy", "orbit", "alien", "void"]):
            img = self._draw_modern_space_bg(width, height, location, style)
        elif any(k in loc or k in p_lower for k in ["class", "school", "lecture", "college", "hallway", "hall"]):
            img = self._draw_modern_classroom_bg(width, height, location, style)
        elif any(k in loc or k in p_lower for k in ["bedroom", "dorm", "room", "desk", "studio", "office"]):
            img = self._draw_modern_battlestation_bg(width, height, location, style)
        elif any(k in loc or k in p_lower for k in ["gym", "fitness", "workout", "muscle"]):
            img = self._draw_modern_gym_bg(width, height, location, style)
        elif any(k in loc or k in p_lower for k in ["haunted", "ghost", "attic", "mansion", "spooky", "noir"]):
            img = self._draw_modern_haunted_bg(width, height, location, style)
        else:
            img = self._draw_modern_city_street_bg(width, height, location, style)

        # Apply style-specific color grading
        s = (style or "").lower()
        if "pixel" in s or "16-bit" in s:
            dw, dh = width // 4, height // 4
            down = img.resize((dw, dh), Image.Resampling.NEAREST)
            quant = down.convert("RGB").quantize(colors=32, method=Image.Quantize.MEDIANCUT).convert("RGBA")
            img = quant.resize((width, height), Image.Resampling.NEAREST)
        elif "noir" in s:
            gray = img.convert("L")
            img = ImageOps.colorize(gray, black="#080a10", white="#f3f4f6").convert("RGBA")
        elif "cyber" in s:
            tint = Image.new("RGBA", (width, height), (6, 182, 212, 25))
            img = Image.alpha_composite(img, tint)
        elif "doodle" in s:
            gray = img.convert("L")
            img = ImageOps.colorize(gray, black="#18181b", white="#fefefe").convert("RGBA")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, "PNG", quality=95)
        
        if logger_func:
            await logger_func(f"[STUDIO] Rendered high-fidelity background for {location} ({style}).")
        return output_path

    # ==========================================
    # BACKGROUND ILLUSTRATION SUITE (2026 LEVEL)
    # ==========================================

    def _draw_modern_scifi_lab_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        """Renders sprawling nocturnal cyberpunk city through floor-to-ceiling glass wall with floor grid and HUDs."""
        img = Image.new("RGBA", (width, height), (8, 12, 24, 255))
        draw = ImageDraw.Draw(img)

        # 1. Sky Gradient
        for y in range(int(height * 0.65)):
            ratio = y / (height * 0.65)
            r = int(8 + ratio * 28)
            g = int(10 + ratio * 18)
            b = int(24 + ratio * 48)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # 2. Distant Megalopolis Skyscrapers
        random.seed(hash(title) % 10000)
        bldg_y_base = int(height * 0.62)
        
        # Far Silhouette Towers
        x = 0
        while x < width:
            bw = random.randint(70, 140)
            bh = random.randint(380, 800)
            top = bldg_y_base - bh
            draw.rectangle([x, top, x + bw, bldg_y_base], fill=(18, 24, 46, 255), outline=(35, 45, 80, 200), width=1)
            for wy in range(top + 25, bldg_y_base - 20, 24):
                for wx in range(x + 12, x + bw - 12, 16):
                    if random.random() > 0.45:
                        col = (6, 182, 212, random.randint(100, 220)) if random.random() > 0.3 else (236, 72, 153, 180)
                        draw.rectangle([wx, wy, wx + 6, wy + 10], fill=col)
            x += bw - 8

        # Mid-ground Towers with Neon Edge Strips
        x = 30
        while x < width:
            bw = random.randint(110, 190)
            bh = random.randint(280, 600)
            top = bldg_y_base - bh
            draw.rectangle([x, top, x + bw, bldg_y_base], fill=(12, 18, 36, 255), outline=(6, 182, 212, 180), width=2)
            draw.line([(x + 8, top), (x + 8, bldg_y_base)], fill=(236, 72, 153, 230), width=3)
            draw.line([(x + bw - 8, top), (x + bw - 8, bldg_y_base)], fill=(6, 182, 212, 230), width=3)
            x += bw + random.randint(25, 60)

        # 3. Reflective Tech Floor with Perspective Vanishing Grid
        floor_top = int(height * 0.60)
        for y in range(floor_top, height):
            ratio = (y - floor_top) / (height - floor_top)
            r = int(10 + ratio * 8)
            g = int(14 + ratio * 10)
            b = int(28 + ratio * 18)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        vanish_x = width // 2
        vanish_y = floor_top - 60
        for gx in range(-width // 2, width * 2, 85):
            draw.line([(vanish_x, vanish_y), (gx, height)], fill=(6, 182, 212, 75), width=2)
        for gy_idx in range(1, 12):
            y_pos = int(floor_top + (height - floor_top) * (gy_idx / 12) ** 1.8)
            draw.line([(0, y_pos), (width, y_pos)], fill=(6, 182, 212, 65), width=2)

        # 4. Architectural Frame & Hologram HUD Overlays
        draw.polygon([(0, 0), (120, 0), (80, height), (0, height)], fill=(12, 16, 28, 255), outline=(30, 41, 59, 255), width=3)
        draw.line([(100, 0), (60, height)], fill=(6, 182, 212, 190), width=3)
        draw.polygon([(width, 0), (width - 120, 0), (width - 80, height), (width, height)], fill=(12, 16, 28, 255), outline=(30, 41, 59, 255), width=3)
        draw.line([(width - 100, 0), (width - 60, height)], fill=(236, 72, 153, 190), width=3)

        # Floating Holo Terminal
        hud = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(hud)
        hx, hy, hw, hh = 140, 260, 260, 380
        hdraw.rectangle([hx, hy, hx + hw, hy + hh], fill=(6, 182, 212, 25), outline=(6, 182, 212, 190), width=2)
        hdraw.rectangle([hx, hy, hx + hw, hy + 32], fill=(6, 182, 212, 85))
        for li in range(80, hh - 30, 26):
            hdraw.line([(hx + 18, hy + li), (hx + hw - random.randint(30, 100), hy + li)], fill=(56, 189, 248, 150), width=3)
        hdraw.ellipse([hx + hw - 55, hy + hh - 55, hx + hw - 20, hy + hh - 20], outline=(236, 72, 153, 210), width=3)

        # Swarm Radar Core
        rx, ry, rad = width - 230, 320, 95
        hdraw.ellipse([rx - rad, ry - rad, rx + rad, ry + rad], outline=(236, 72, 153, 190), width=2)
        hdraw.ellipse([rx - rad + 25, ry - rad + 25, rx + rad - 25, ry + rad - 25], outline=(6, 182, 212, 150), width=2)
        hdraw.line([(rx - rad, ry), (rx + rad, ry)], fill=(236, 72, 153, 150), width=2)
        hdraw.line([(rx, ry - rad), (rx, ry + rad)], fill=(6, 182, 212, 150), width=2)

        return Image.alpha_composite(img, hud)

    def _draw_modern_battlestation_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        """Renders a sleek high-end creator battlestation room with RGB hex panels, curved ultrawides, and warm lighting."""
        img = Image.new("RGBA", (width, height), (15, 18, 28, 255))
        draw = ImageDraw.Draw(img)

        # Wall Gradient
        for y in range(int(height * 0.65)):
            ratio = y / (height * 0.65)
            r = int(18 + ratio * 15)
            g = int(22 + ratio * 10)
            b = int(36 + ratio * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # Hexagonal Acoustic Foam Wall Panels with RGB ambient backlighting
        hex_points = [
            (int(width * 0.2), int(height * 0.2)),
            (int(width * 0.35), int(height * 0.16)),
            (int(width * 0.5), int(height * 0.2)),
            (int(width * 0.65), int(height * 0.16)),
            (int(width * 0.8), int(height * 0.2)),
        ]
        for hx, hy in hex_points:
            rad = 70
            poly = [
                (hx + int(rad * math.cos(math.radians(a))), hy + int(rad * math.sin(math.radians(a))))
                for a in range(0, 360, 60)
            ]
            draw.polygon(poly, fill=(24, 30, 48, 255), outline=(6, 182, 212, 180), width=3)
            inner_poly = [
                (hx + int((rad - 15) * math.cos(math.radians(a))), hy + int((rad - 15) * math.sin(math.radians(a))))
                for a in range(0, 360, 60)
            ]
            draw.polygon(inner_poly, fill=(15, 20, 34, 255), outline=(236, 72, 153, 140), width=2)

        # Desk Surface (Sleek carbon desk)
        desk_y = int(height * 0.62)
        draw.rectangle([0, desk_y, width, height], fill=(12, 15, 24, 255), outline=(30, 41, 59, 255), width=2)
        # RGB light strip underneath desk edge
        draw.line([(0, desk_y), (width, desk_y)], fill=(6, 182, 212, 255), width=6)
        draw.line([(0, desk_y + 4), (width, desk_y + 4)], fill=(236, 72, 153, 200), width=3)

        # Dual Curved Ultrawide Monitors displaying glowing soundwave / code graphs
        # Monitor 1 (Center)
        mx1, my1, mx2, my2 = int(width * 0.18), int(height * 0.32), int(width * 0.82), int(height * 0.58)
        draw.rectangle([mx1, my1, mx2, my2], fill=(6, 10, 20, 255), outline=(6, 182, 212, 240), width=5)
        # Stand
        draw.rectangle([int(width * 0.46), my2, int(width * 0.54), desk_y], fill=(30, 41, 59, 255))
        draw.ellipse([int(width * 0.42), desk_y - 15, int(width * 0.58), desk_y + 15], fill=(45, 55, 75, 255))

        # Audio Waveform on Monitor
        wave_pts = []
        for i, wx in enumerate(range(mx1 + 20, mx2 - 20, 14)):
            amp = int(45 * math.sin(i * 0.35) * math.cos(i * 0.18))
            wy = (my1 + my2) // 2 + amp
            wave_pts.append((wx, wy))
            draw.line([(wx, (my1 + my2) // 2), (wx, wy)], fill=(6, 182, 212, 200), width=4)
        if len(wave_pts) > 1:
            draw.line(wave_pts, fill=(236, 72, 153, 240), width=3)

        # Studio Boom Arm Microphone (Left side)
        draw.line([(int(width * 0.1), desk_y), (int(width * 0.15), int(height * 0.48)), (int(width * 0.24), int(height * 0.42))], fill=(71, 85, 105, 255), width=8)
        draw.ellipse([int(width * 0.22), int(height * 0.39), int(width * 0.27), int(height * 0.45)], fill=(20, 20, 30, 255), outline=(6, 182, 212, 255), width=3)

        return img

    def _draw_modern_classroom_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        """Modern anime high school classroom with golden hour light beams and chalkboard."""
        img = Image.new("RGBA", (width, height), (35, 30, 42, 255))
        draw = ImageDraw.Draw(img)

        # Golden Hour Sky / Wall
        for y in range(int(height * 0.65)):
            ratio = y / (height * 0.65)
            r = int(245 - ratio * 40)
            g = int(180 - ratio * 60)
            b = int(130 - ratio * 50)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

        # Polished Wooden Floor
        floor_y = int(height * 0.62)
        for y in range(floor_y, height):
            ratio = (y - floor_y) / (height - floor_y)
            draw.line([(0, y), (width, y)], fill=(int(85 + ratio * 20), int(45 + ratio * 15), int(25 + ratio * 10), 255))
        for p in range(0, width + 200, 120):
            draw.line([(width // 2, floor_y - 80), (p, height)], fill=(60, 30, 15, 160), width=3)

        # Large Classroom Chalkboard
        cx1, cy1, cx2, cy2 = int(width * 0.1), int(height * 0.16), int(width * 0.9), int(height * 0.52)
        draw.rectangle([cx1, cy1, cx2, cy2], fill=(24, 48, 38, 255), outline=(130, 90, 50, 255), width=10)
        # Chalk formulas
        draw.line([(cx1 + 40, cy1 + 60), (cx1 + 240, cy1 + 60)], fill=(230, 240, 230, 180), width=4)
        draw.line([(cx1 + 40, cy1 + 100), (cx1 + 180, cy1 + 100)], fill=(230, 240, 230, 180), width=3)

        # Diagonal Golden Sunlight Ray
        sun = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(sun)
        sdraw.polygon([(0, 0), (int(width * 0.45), 0), (width, int(height * 0.85)), (int(width * 0.4), height)], fill=(255, 235, 170, 45))
        img = Image.alpha_composite(img, sun)
        return img

    def _draw_modern_space_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        """Deep cosmic nebula with glowing planetary rings and stars."""
        img = Image.new("RGBA", (width, height), (8, 6, 20, 255))
        draw = ImageDraw.Draw(img)

        # Nebula Gradient
        for y in range(height):
            ratio = y / height
            draw.line([(0, y), (width, y)], fill=(int(10 + ratio * 35), int(5 + ratio * 15), int(30 + ratio * 55), 255))

        random.seed(99)
        # Distant Stars
        for _ in range(140):
            sx, sy = random.randint(0, width), random.randint(0, height)
            srad = random.randint(1, 4)
            col = random.choice([(255, 255, 255), (6, 182, 212), (236, 72, 153), (250, 204, 21)])
            draw.ellipse([sx, sy, sx + srad, sy + srad], fill=col)

        # Giant Ringed Gas Planet (Top Right)
        px, py, prad = int(width * 0.82), int(height * 0.22), 160
        draw.ellipse([px - prad, py - prad, px + prad, py + prad], fill=(236, 72, 153, 255))
        # Rings
        draw.ellipse([px - prad - 80, py - 40, px + prad + 80, py + 40], outline=(6, 182, 212, 200), width=8)

        return img

    def _draw_modern_city_street_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        """Vibrant Neo-Tokyo neon street intersection with wet reflections."""
        img = Image.new("RGBA", (width, height), (12, 15, 28, 255))
        draw = ImageDraw.Draw(img)

        # Sky
        for y in range(int(height * 0.55)):
            ratio = y / (height * 0.55)
            draw.line([(0, y), (width, y)], fill=(int(12 + ratio * 30), int(10 + ratio * 20), int(35 + ratio * 45), 255))

        # Wet Asphalt Floor
        floor_y = int(height * 0.55)
        for y in range(floor_y, height):
            ratio = (y - floor_y) / (height - floor_y)
            draw.line([(0, y), (width, y)], fill=(int(15 + ratio * 10), int(18 + ratio * 12), int(28 + ratio * 15), 255))

        # Neon Signs & Billboards
        draw.rectangle([int(width * 0.1), int(height * 0.15), int(width * 0.35), int(height * 0.45)], fill=(18, 24, 42, 255), outline=(236, 72, 153, 240), width=4)
        draw.rectangle([int(width * 0.65), int(height * 0.1), int(width * 0.92), int(height * 0.4)], fill=(18, 24, 42, 255), outline=(6, 182, 212, 240), width=4)

        # Road Markings & Wet Light Reflections
        draw.line([(width // 2, floor_y), (width // 2, height)], fill=(250, 204, 21, 220), width=8)
        draw.line([(int(width * 0.25), floor_y), (int(width * 0.25), height)], fill=(236, 72, 153, 60), width=24)
        draw.line([(int(width * 0.75), floor_y), (int(width * 0.75), height)], fill=(6, 182, 212, 60), width=24)

        return img

    def _draw_modern_gym_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        img = Image.new("RGBA", (width, height), (15, 20, 32, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, width, int(height * 0.65)], fill=(15, 23, 42, 255))
        draw.rectangle([0, int(height * 0.65), width, height], fill=(30, 41, 59, 255))
        draw.line([(0, int(height * 0.65)), (width, int(height * 0.65))], fill=(239, 68, 68, 255), width=6)
        return img

    def _draw_modern_haunted_bg(self, width: int, height: int, title: str, style: str) -> Image.Image:
        img = Image.new("RGBA", (width, height), (8, 10, 18, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, width, height], fill=(8, 10, 18, 255))
        # Moonlight ray
        draw.polygon([(int(width * 0.1), 0), (int(width * 0.5), 0), (width, height), (int(width * 0.4), height)], fill=(45, 55, 85, 80))
        return img

    # ==========================================
    # CHARACTER RIG GENERATION (2026 ANIME/TOON)
    # ==========================================

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, style: str = "Modern 2D Cartoon", logger_func = None) -> Dict[str, str]:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        name = char_data.get("name", "Character")
        skin = char_data.get("skin_tone", "#f8dbd3")
        hair = char_data.get("hair_color", "#1e293b")
        outfit = char_data.get("outfit_color", "#0f172a")
        hair_style = char_data.get("hair_style", "Messy Anime")
        gender = char_data.get("gender", "Male")
        is_robot = "robot" in gender.lower() or "ai" in char_data.get("role", "").lower() or "bot" in name.lower() or "optimus" in name.lower()
        is_cat = "cat" in name.lower() or "cat" in char_data.get("role", "").lower()

        expressions = ["avatar", "talking_open", "talking_closed", "shock", "happy"]
        sprites = {}
        
        for exp in expressions:
            file_name = f"{name.lower().replace(' ', '_')}_{exp}.png"
            file_path = str(out_dir / file_name)
            
            canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas)
            cx, cy = 540, 1050
            
            if is_robot:
                self._render_modern_robot_character(draw, cx, cy, exp, style=style)
            elif is_cat:
                self._render_modern_cat_character(draw, cx, cy, exp, skin, hair, style=style)
            else:
                self._render_modern_human_character(draw, cx, cy, exp, skin, hair, outfit, hair_style, gender, style=style)

            # Style Post-Processing for Pixel/Noir
            s = (style or "").lower()
            if "pixel" in s or "16-bit" in s:
                dw, dh = 1080 // 4, 1920 // 4
                down = canvas.resize((dw, dh), Image.Resampling.NEAREST)
                canvas = down.resize((1080, 1920), Image.Resampling.NEAREST)
            elif "noir" in s:
                r, g, b, alpha = canvas.split()
                gray = ImageOps.grayscale(canvas.convert("RGB"))
                gray_rgb = ImageOps.colorize(gray, black="#0a0c14", white="#f1f5f9").convert("RGBA")
                gray_rgb.putalpha(alpha)
                canvas = gray_rgb

            canvas.save(file_path, "PNG")
            sprites[exp] = file_path
            
        if logger_func:
            await logger_func(f"[STUDIO] Generated 5-expression high-res character rig for {name} ({style}).")
        return sprites

    def _render_modern_human_character(
        self,
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        emotion: str,
        skin: str,
        hair: str,
        outfit: str,
        hair_style: str,
        gender: str = "Male",
        style: str = "Modern 2D Cartoon"
    ):
        """
        Renders modern anime / western cartoon character with:
        - Angled anime chin & neck shadow
        - Double-highlighted iris eyes with thick lashes
        - Layered spiky/styled locks with specular highlights and rim lighting
        - Modern tech hoodie with collar, zipper, and dual-tone ambient rim light
        """
        skin_base = (248, 219, 195, 255)
        skin_shadow = (226, 185, 156, 255)
        hair_base = (30, 41, 59, 255)
        hair_high = (71, 85, 105, 255)
        hair_rim = (6, 182, 212, 255)
        hoodie_base = (15, 23, 42, 255)
        hoodie_shadow = (10, 15, 30, 255)
        hoodie_rim = (236, 72, 153, 255)

        # 1. TORSO & CLOTHING (Shoulders, chest, hoodie collar, jacket)
        hoodie_poly = [
            (cx - 360, cy + 850),
            (cx - 320, cy + 420),
            (cx - 200, cy + 240),
            (cx - 90, cy + 180),
            (cx + 90, cy + 180),
            (cx + 200, cy + 240),
            (cx + 320, cy + 420),
            (cx + 360, cy + 850),
        ]
        draw.polygon(hoodie_poly, fill=hoodie_base)
        # Shading on right side
        draw.polygon([(cx, cy + 180), (cx + 90, cy + 180), (cx + 200, cy + 240), (cx + 320, cy + 420), (cx + 360, cy + 850), (cx, cy + 850)], fill=hoodie_shadow)
        # Dual-tone rim light edges
        draw.line([(cx - 320, cy + 420), (cx - 200, cy + 240), (cx - 90, cy + 180)], fill=hair_rim, width=6)
        draw.line([(cx + 90, cy + 180), (cx + 200, cy + 240), (cx + 320, cy + 420)], fill=hoodie_rim, width=6)

        # Hoodie Collar
        draw.polygon([(cx - 130, cy + 130), (cx - 150, cy + 220), (cx, cy + 270), (cx + 150, cy + 220), (cx + 130, cy + 130)], fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=5)
        # Zipper & Chest Tech Patch
        draw.line([(cx, cy + 270), (cx, cy + 850)], fill=(6, 182, 212, 255), width=6)
        draw.polygon([(cx - 160, cy + 340), (cx - 90, cy + 310), (cx - 70, cy + 360), (cx - 140, cy + 390)], fill=(6, 182, 212, 220), outline=(255, 255, 255, 220), width=2)

        # 2. NECK with anatomical shadow
        neck_poly = [(cx - 65, cy + 60), (cx - 75, cy + 190), (cx + 75, cy + 190), (cx + 65, cy + 60)]
        draw.polygon(neck_poly, fill=skin_shadow)
        draw.polygon([(cx - 40, cy + 60), (cx - 45, cy + 190), (cx + 45, cy + 190), (cx + 40, cy + 60)], fill=skin_base)

        # 3. HEAD & JAWLINE (Modern anime/vector angled chin)
        head_poly = [
            (cx, cy + 110),          # Chin
            (cx - 75, cy + 75),       # Jaw corner L
            (cx - 150, cy - 20),      # Cheek L
            (cx - 165, cy - 130),     # Temple L
            (cx, cy - 210),          # Forehead top
            (cx + 165, cy - 130),     # Temple R
            (cx + 150, cy - 20),      # Cheek R
            (cx + 75, cy + 75),       # Jaw corner R
        ]
        draw.polygon(head_poly, fill=skin_base, outline=(15, 23, 42, 255), width=5)
        draw.polygon([(cx, cy + 110), (cx - 75, cy + 75), (cx - 150, cy - 20), (cx - 120, cy + 10), (cx - 50, cy + 85)], fill=skin_shadow)

        # Ears
        draw.polygon([(cx - 150, cy - 60), (cx - 195, cy - 30), (cx - 155, cy + 30)], fill=skin_base, outline=(15, 23, 42, 255), width=4)
        draw.line([(cx - 180, cy - 30), (cx - 160, cy)], fill=skin_shadow, width=4)
        draw.polygon([(cx + 150, cy - 60), (cx + 195, cy - 30), (cx + 155, cy + 30)], fill=skin_base, outline=(15, 23, 42, 255), width=4)
        draw.line([(cx + 180, cy - 30), (cx + 160, cy)], fill=skin_shadow, width=4)

        # 4. EYES (Expression-aware)
        if emotion == "happy":
            # Smiling closed-arc joyful eyes
            draw.arc([cx - 110, cy - 40, cx - 35, cy - 10], 200, 340, fill=(15, 23, 42, 255), width=7)
            draw.arc([cx + 35, cy - 40, cx + 110, cy - 10], 200, 340, fill=(15, 23, 42, 255), width=7)
            # Cheerful blushing cheeks
            draw.ellipse([cx - 120, cy, cx - 60, cy + 30], fill=(244, 114, 182, 160))
            draw.ellipse([cx + 60, cy, cx + 120, cy + 30], fill=(244, 114, 182, 160))
        elif emotion == "shock":
            # Wide anime shock eyes with tiny contracted pupils & sweatdrop
            for eye_x in [cx - 72, cx + 72]:
                draw.ellipse([eye_x - 38, cy - 50, eye_x + 38, cy + 10], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=5)
                draw.ellipse([eye_x - 8, cy - 25, eye_x + 8, cy - 10], fill=(6, 182, 212, 255))
                draw.ellipse([eye_x - 4, cy - 21, eye_x + 4, cy - 14], fill=(15, 23, 42, 255))
            # Sweatdrop on temple
            draw.polygon([(cx + 125, cy - 70), (cx + 145, cy - 40), (cx + 105, cy - 40)], fill=(56, 189, 248, 230))
            draw.ellipse([cx + 105, cy - 48, cx + 145, cy - 25], fill=(56, 189, 248, 230))
        else:
            # Confident detailed anime eyes with double catchlights
            for eye_x in [cx - 72, cx + 72]:
                ew_pts = [(eye_x - 42, cy - 30), (eye_x, cy - 48), (eye_x + 42, cy - 30), (eye_x, cy - 12)]
                draw.polygon(ew_pts, fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=4)
                draw.ellipse([eye_x - 22, cy - 42, eye_x + 22, cy - 16], fill=(6, 182, 212, 255))
                draw.ellipse([eye_x - 14, cy - 38, eye_x + 14, cy - 20], fill=(15, 23, 42, 255))
                draw.ellipse([eye_x - 12, cy - 40, eye_x - 4, cy - 32], fill=(255, 255, 255, 255))
                draw.ellipse([eye_x + 6, cy - 26, eye_x + 12, cy - 20], fill=(255, 255, 255, 255))
                draw.line([(eye_x - 46, cy - 30), (eye_x - 15, cy - 50), (eye_x + 46, cy - 30)], fill=(15, 23, 42, 255), width=6)
                draw.line([(eye_x - 25, cy - 12), (eye_x + 25, cy - 12)], fill=(15, 23, 42, 200), width=3)

        # Eyebrows
        if emotion == "shock":
            draw.line([(cx - 110, cy - 78), (cx - 35, cy - 88)], fill=(15, 23, 42, 255), width=8)
            draw.line([(cx + 35, cy - 88), (cx + 110, cy - 78)], fill=(15, 23, 42, 255), width=8)
        else:
            draw.line([(cx - 110, cy - 65), (cx - 35, cy - 75)], fill=(15, 23, 42, 255), width=8)
            draw.line([(cx + 35, cy - 75), (cx + 110, cy - 65)], fill=(15, 23, 42, 255), width=8)

        # Nose
        draw.polygon([(cx, cy - 5), (cx - 8, cy + 18), (cx + 4, cy + 18)], fill=skin_shadow)

        # Mouth
        if emotion in ["talking_open", "shock"]:
            mouth_pts = [(cx - 40, cy + 45), (cx, cy + 40), (cx + 40, cy + 45), (cx + 25, cy + 85), (cx - 25, cy + 85)]
            draw.polygon(mouth_pts, fill=(185, 28, 28, 255), outline=(15, 23, 42, 255), width=4)
            draw.polygon([(cx - 32, cy + 45), (cx + 32, cy + 45), (cx + 20, cy + 55), (cx - 20, cy + 55)], fill=(255, 255, 255, 255))
            draw.ellipse([cx - 20, cy + 68, cx + 20, cy + 85], fill=(244, 114, 182, 255))
        elif emotion == "happy":
            draw.arc([cx - 35, cy + 40, cx + 35, cy + 75], 0, 180, fill=(185, 28, 28, 255), width=6)
        else:
            draw.line([(cx - 32, cy + 52), (cx, cy + 58), (cx + 32, cy + 48)], fill=(15, 23, 42, 255), width=5)

        # 5. HAIR (Multi-layered modern anime spiky locks with highlights & cyan rim)
        hair_back_poly = [
            (cx - 180, cy - 120),
            (cx - 220, cy - 180),
            (cx - 170, cy - 250),
            (cx - 90, cy - 310),
            (cx, cy - 330),
            (cx + 90, cy - 310),
            (cx + 170, cy - 250),
            (cx + 220, cy - 180),
            (cx + 180, cy - 120),
        ]
        draw.polygon(hair_back_poly, fill=hair_base)

        bangs = [
            [(cx - 180, cy - 160), (cx - 120, cy - 20), (cx - 90, cy - 120)],
            [(cx - 110, cy - 160), (cx - 45, cy), (cx - 20, cy - 140)],
            [(cx - 35, cy - 180), (cx + 15, cy - 10), (cx + 40, cy - 150)],
            [(cx + 25, cy - 170), (cx + 95, cy - 30), (cx + 120, cy - 130)],
            [(cx + 105, cy - 150), (cx + 170, cy - 40), (cx + 180, cy - 140)],
        ]
        for b in bangs:
            draw.polygon(b, fill=hair_base, outline=(15, 23, 42, 255), width=3)

        # Highlights & Rim light on hair
        draw.polygon([(cx - 130, cy - 270), (cx - 40, cy - 290), (cx - 20, cy - 260), (cx - 110, cy - 245)], fill=hair_high)
        draw.polygon([(cx + 20, cy - 290), (cx + 110, cy - 270), (cx + 95, cy - 245), (cx + 40, cy - 260)], fill=hair_high)
        draw.line([(cx - 150, cy - 230), (cx - 80, cy - 290), (cx, cy - 310), (cx + 80, cy - 290), (cx + 150, cy - 230)], fill=hair_rim, width=5)

    def _render_modern_robot_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, style: str = "Modern 2D Cartoon"):
        """Sleek modern humanoid android (Tesla Optimus / Figure 02 / Daft Punk style)."""
        body_dark = (15, 23, 42, 255)
        body_metal = (51, 65, 85, 255)
        cyan_glow = (6, 182, 212, 255)
        pink_glow = (236, 72, 153, 255)

        # Shoulders & Torso Chassis
        draw.polygon([(cx - 320, cy + 850), (cx - 280, cy + 380), (cx - 140, cy + 220), (cx + 140, cy + 220), (cx + 280, cy + 380), (cx + 320, cy + 850)], fill=body_dark)
        draw.polygon([(cx - 120, cy + 240), (cx + 120, cy + 240), (cx + 180, cy + 420), (cx - 180, cy + 420)], fill=body_metal, outline=cyan_glow, width=3)
        # Glowing Power Arc Core
        draw.ellipse([cx - 40, cy + 300, cx + 40, cy + 380], fill=cyan_glow, outline=(255, 255, 255, 255), width=3)

        # Neck Mechanical Actuators
        draw.rectangle([cx - 50, cy + 120, cx + 50, cy + 220], fill=(30, 41, 59, 255))
        draw.line([(cx - 30, cy + 120), (cx - 30, cy + 220)], fill=cyan_glow, width=4)
        draw.line([(cx + 30, cy + 120), (cx + 30, cy + 220)], fill=cyan_glow, width=4)

        # Sleek Aerodynamic Android Helmet
        head_pts = [
            (cx - 160, cy - 80),
            (cx - 120, cy - 220),
            (cx, cy - 260),
            (cx + 120, cy - 220),
            (cx + 160, cy - 80),
            (cx + 110, cy + 110),
            (cx, cy + 140),
            (cx - 110, cy + 110),
        ]
        draw.polygon(head_pts, fill=body_dark, outline=cyan_glow, width=5)
        # Visor Bezel
        draw.polygon([(cx - 130, cy - 50), (cx - 100, cy - 140), (cx + 100, cy - 140), (cx + 130, cy - 50), (cx + 80, cy + 40), (cx - 80, cy + 40)], fill=(6, 12, 22, 255), outline=pink_glow, width=3)

        # Matrix Digital HUD Eyes
        if emotion == "shock":
            draw.line([(cx - 70, cy - 30), (cx - 30, cy - 30)], fill=(239, 68, 68, 255), width=8)
            draw.line([(cx + 30, cy - 30), (cx + 70, cy - 30)], fill=(239, 68, 68, 255), width=8)
        elif emotion == "happy":
            draw.arc([cx - 70, cy - 50, cx - 30, cy - 10], 200, 340, fill=cyan_glow, width=8)
            draw.arc([cx + 30, cy - 50, cx + 70, cy - 10], 200, 340, fill=cyan_glow, width=8)
        else:
            # Active Cyber Scan Visor Line
            draw.line([(cx - 85, cy - 30), (cx + 85, cy - 30)], fill=cyan_glow, width=8)
            draw.line([(cx - 35, cy - 30), (cx + 35, cy - 30)], fill=(255, 255, 255, 255), width=8)

    def _render_modern_cat_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, fur: str, ear_inner: str, style: str = "Modern 2D Cartoon"):
        """Stylized anime mascot cat with glowing eyes and collar."""
        draw.polygon([(cx - 140, cy - 60), (cx - 110, cy - 200), (cx - 30, cy - 80)], fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=5)
        draw.polygon([(cx - 120, cy - 70), (cx - 105, cy - 170), (cx - 45, cy - 90)], fill=(244, 114, 182, 255))
        draw.polygon([(cx + 30, cy - 80), (cx + 110, cy - 200), (cx + 140, cy - 60)], fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=5)
        draw.polygon([(cx + 45, cy - 90), (cx + 105, cy - 170), (cx + 120, cy - 70)], fill=(244, 114, 182, 255))
        draw.ellipse([cx - 140, cy - 80, cx + 140, cy + 120], fill=(30, 41, 59, 255), outline=(15, 23, 42, 255), width=5)
        draw.ellipse([cx - 80, cy - 20, cx - 20, cy + 30], fill=(6, 182, 212, 255))
        draw.ellipse([cx + 20, cy - 20, cx + 80, cy + 30], fill=(6, 182, 212, 255))

    # ==========================================
    # CINEMATIC SCENE COMPOSITION SUITE
    # ==========================================

    async def compose_scene_frame(
        self,
        bg_path: str,
        char_specs: List[Dict[str, Any]],
        action_desc: str,
        emotion: str,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
        style: str = "Modern 2D Cartoon",
        logger_func = None
    ) -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load background
        if bg_path and Path(bg_path).exists():
            base_bg = Image.open(bg_path).convert("RGBA")
            if base_bg.size != (width, height):
                base_bg = base_bg.resize((width, height), Image.Resampling.LANCZOS)
        else:
            base_bg = Image.new("RGBA", (width, height), (15, 23, 42, 255))

        # Apply cinematic Depth of Field (soft background blur so character pops)
        bg_blurred = base_bg.filter(ImageFilter.GaussianBlur(radius=5))

        # Create foreground composition layer
        comp = bg_blurred.copy()

        # Render Character Sprites with proper depth & shadow
        if char_specs and len(char_specs) > 0:
            char_item = char_specs[0]
            spr_path = char_item.get("sprite_path")
            if spr_path and Path(spr_path).exists():
                char_img = Image.open(spr_path).convert("RGBA")
                if char_img.size != (width, height):
                    char_img = char_img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Ambient contact shadow on floor
                shadow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                sdraw = ImageDraw.Draw(shadow)
                sdraw.ellipse([width // 2 - 240, int(height * 0.88), width // 2 + 240, int(height * 0.94)], fill=(0, 0, 0, 95))
                comp = Image.alpha_composite(comp, shadow)

                # Composite character over blurred background
                comp = Image.alpha_composite(comp, char_img)

        # Style Post-Processing & Cinematic Atmosphere
        s = (style or "").lower()
        emo = (emotion or "").lower()

        # Action Speedlines for Shock or Punchline
        if emo in ["shock", "panic"] or "punch" in action_desc.lower():
            fx = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            fdraw = ImageDraw.Draw(fx)
            cx, cy = width // 2, int(height * 0.45)
            for deg in range(0, 360, 12):
                rad = math.radians(deg)
                d1 = int(width * 0.45)
                d2 = int(width * 0.85)
                x1 = int(cx + d1 * math.cos(rad))
                y1 = int(cy + d1 * math.sin(rad))
                x2 = int(cx + d2 * math.cos(rad))
                y2 = int(cy + d2 * math.sin(rad))
                fdraw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 90), width=5)
            comp = Image.alpha_composite(comp, fx)

        # Style Enhancements
        if "cyber" in s:
            enhancer = ImageEnhance.Color(comp)
            comp = enhancer.enhance(1.15)
        elif "noir" in s:
            enhancer = ImageEnhance.Contrast(comp)
            comp = enhancer.enhance(1.25)

        comp.convert("RGB").save(str(out_file), "PNG", quality=95)
        if logger_func:
            await logger_func(f"[STUDIO] Composed 2026 scene frame: {out_file.name}")
        return str(out_file)


class VisualFactory:
    @staticmethod
    async def get_best_provider() -> VisualProvider:
        # Check if local ComfyUI AI diffusion is online
        comfy = ComfyUIVisualProvider()
        if await comfy.is_available():
            return comfy
        return ToonVectorVisualProvider()
