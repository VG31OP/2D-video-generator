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
    High-Fidelity Dynamic 2D Cartoon Vector Visual Engine (Fallback).
    Generates rich custom cartoon scenery and expressive multi-layer character rigs
    dynamically tailored to each individual prompt.
    """
    def __init__(self):
        self._font_cache = {}

    def get_provider_name(self) -> str:
        return "ToonVector Visual Engine"

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
        img = Image.new("RGBA", (800, 1000), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        
        name = char_data.get("name", "Character")
        skin = char_data.get("skin_tone", "#f6d5b8")
        hair = char_data.get("hair_color", "#2d3748")
        outfit = char_data.get("outfit_color", "#3b82f6")
        gender = char_data.get("gender", "Male")
        is_robot = "robot" in gender.lower() or "ai" in char_data.get("role", "").lower() or "bot" in name.lower()
        is_cat = "cat" in name.lower() or "cat" in char_data.get("role", "").lower()
        
        if is_robot:
            self._render_robot_character(draw, 400, 500, "avatar", outfit, style=style)
        elif is_cat:
            self._render_cat_character(draw, 400, 500, "avatar", skin, hair, style=style)
        else:
            self._render_human_character(draw, 400, 500, "avatar", skin, hair, outfit, char_data.get("hair_style", "Messy Anime"), gender, style=style)
            
        img.convert("RGB").save(str(out_file), "PNG")
        if logger_func:
            await logger_func(f"[FALLBACK] Generated character reference sheet for {name} ({style}).")
        return str(out_file)

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        img = Image.new("RGBA", (width, height), (20, 24, 38, 255))
        draw = ImageDraw.Draw(img)
        loc = location.lower()
        
        if any(k in loc for k in ["gym", "fitness", "workout", "muscle"]):
            self._draw_gym_bg(draw, width, height, location)
        elif any(k in loc for k in ["kitchen", "chef", "cook", "restaurant", "food"]):
            self._draw_kitchen_bg(draw, width, height, location)
        elif any(k in loc for k in ["class", "school", "lecture", "college", "hallway", "hall"]):
            self._draw_classroom_bg(draw, width, height, location)
        elif any(k in loc for k in ["lab", "server", "tech", "computer", "garage"]):
            self._draw_scifi_lab_bg(draw, width, height, location)
        elif any(k in loc for k in ["space", "chaos", "dimension", "galaxy", "orbit", "alien"]):
            self._draw_space_bg(draw, width, height, location)
        elif any(k in loc for k in ["haunted", "ghost", "attic", "mansion", "spooky"]):
            self._draw_haunted_bg(draw, width, height, location)
        elif any(k in loc for k in ["bedroom", "dorm", "room", "desk"]):
            self._draw_bedroom_bg(draw, width, height, location)
        else:
            self._draw_city_street_bg(draw, width, height, location)
            
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
            tint = Image.new("RGBA", (width, height), (6, 182, 212, 35))
            img = Image.alpha_composite(img, tint)
        elif "doodle" in s:
            gray = img.convert("L")
            img = ImageOps.colorize(gray, black="#18181b", white="#fefefe").convert("RGBA")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, "PNG", quality=95)
        
        if logger_func:
            await logger_func(f"[FALLBACK] Rendered dynamic background for {location} ({style}).")
        return output_path

    def _draw_gym_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        draw.rectangle([0, 0, w, int(h * 0.65)], fill=(15, 23, 42))
        draw.rectangle([0, int(h * 0.65), w, h], fill=(30, 41, 59))
        draw.rectangle([int(w * 0.05), int(h * 0.08), int(w * 0.95), int(h * 0.25)], fill=(239, 68, 68), outline=(245, 158, 11), width=8)
        font = self._get_font(46, bold=True)
        draw.text((int(w * 0.1), int(h * 0.12)), "MEGA-FLEX GYM", fill=(255, 255, 255), font=font)
        # Dumbbells rack
        for i in range(5):
            bx = int(w * 0.1 + i * (w * 0.8 / 5))
            draw.rectangle([bx, int(h * 0.45), bx + 100, int(h * 0.62)], fill=(71, 85, 105), outline=(15, 23, 42), width=6)
            draw.ellipse([bx - 20, int(h * 0.48), bx + 20, int(h * 0.58)], fill=(20, 20, 20))
            draw.ellipse([bx + 80, int(h * 0.48), bx + 120, int(h * 0.58)], fill=(20, 20, 20))

    def _draw_kitchen_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        draw.rectangle([0, 0, w, int(h * 0.65)], fill=(254, 243, 199))
        draw.rectangle([0, int(h * 0.65), w, h], fill=(180, 83, 9))
        # Shelves with pots and food
        draw.rectangle([int(w * 0.1), int(h * 0.15), int(w * 0.9), int(h * 0.2)], fill=(120, 53, 15))
        draw.ellipse([int(w * 0.2), int(h * 0.08), int(w * 0.35), int(h * 0.15)], fill=(239, 68, 68))
        draw.ellipse([int(w * 0.5), int(h * 0.08), int(w * 0.65), int(h * 0.15)], fill=(245, 158, 11))
        # Countertop
        draw.rectangle([int(w * 0.05), int(h * 0.6), int(w * 0.95), int(h * 0.85)], fill=(241, 245, 249), outline=(100, 116, 139), width=8)

    def _draw_haunted_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        draw.rectangle([0, 0, w, h], fill=(10, 10, 20))
        # Moonlight beam
        draw.polygon([(int(w * 0.2), 0), (int(w * 0.5), 0), (int(w * 0.9), h), (int(w * 0.1), h)], fill=(30, 41, 70))
        # Spooky web & moon
        draw.ellipse([int(w * 0.65), int(h * 0.1), int(w * 0.9), int(h * 0.25)], fill=(254, 240, 138))

    def _draw_bedroom_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        for y in range(int(h * 0.7)):
            ratio = y / (h * 0.7)
            r = int(24 + (15 - 24) * ratio)
            g = int(28 + (20 - 28) * ratio)
            b = int(50 + (35 - 50) * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        for y in range(int(h * 0.7), h):
            ratio = (y - h * 0.7) / (h * 0.3)
            r = int(45 + (30 - 45) * ratio)
            g = int(35 + (22 - 35) * ratio)
            b = int(30 + (18 - 30) * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        for i in range(12):
            fy = int(h * 0.7 + i * (h * 0.3 / 12))
            draw.line([(0, fy), (w, fy)], fill=(20, 15, 12), width=3)
        wx1, wy1, wx2, wy2 = int(w * 0.1), int(h * 0.12), int(w * 0.45), int(h * 0.45)
        draw.rectangle([wx1, wy1, wx2, wy2], fill=(10, 15, 30), outline=(59, 130, 246), width=8)
        draw.ellipse([wx1 + 40, wy1 + 40, wx1 + 100, wy1 + 100], fill=(254, 240, 138))
        draw.line([(wx1 + (wx2-wx1)//2, wy1), (wx1 + (wx2-wx1)//2, wy2)], fill=(59, 130, 246), width=6)
        draw.line([(wx1, wy1 + (wy2-wy1)//2), (wx2, wy1 + (wy2-wy1)//2)], fill=(59, 130, 246), width=6)
        # Poster
        px1, py1, px2, py2 = int(w * 0.55), int(h * 0.15), int(w * 0.88), int(h * 0.42)
        draw.rectangle([px1, py1, px2, py2], fill=(139, 92, 246), outline=(236, 72, 153), width=6)
        font = self._get_font(28, bold=True)
        draw.text((px1 + 25, py1 + 30), "TOON\nFORGE", fill=(255, 255, 255), font=font)
        # Desk
        dx1, dy1, dx2, dy2 = int(w * 0.05), int(h * 0.62), int(w * 0.95), int(h * 0.85)
        draw.rectangle([dx1, dy1, dx2, dy2], fill=(22, 27, 34), outline=(147, 51, 234), width=6)

    def _draw_classroom_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        draw.rectangle([0, 0, w, int(h * 0.65)], fill=(30, 41, 59))
        draw.rectangle([0, int(h * 0.65), w, h], fill=(71, 85, 105))
        cb_x1, cb_y1, cb_x2, cb_y2 = int(w * 0.1), int(h * 0.12), int(w * 0.9), int(h * 0.52)
        draw.rectangle([cb_x1, cb_y1, cb_x2, cb_y2], fill=(20, 50, 35), outline=(180, 130, 70), width=12)
        title_font = self._get_font(38, bold=True)
        draw.text((cb_x1 + 30, cb_y1 + 30), title.upper()[:28], fill=(255, 255, 255), font=title_font)
        math_font = self._get_font(26, bold=False)
        draw.text((cb_x1 + 30, cb_y1 + 100), "Rule #1: Stay Focused!\nRule #2: Do NOT Press The Red Button!\nGrade: A+++ (Legendary)", fill=(220, 240, 220), font=math_font)

    def _draw_scifi_lab_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        draw.rectangle([0, 0, w, h], fill=(8, 12, 22))
        for y in range(0, h, 80):
            draw.line([(0, y), (w, y)], fill=(15, 23, 42), width=2)
        for x in range(0, w, 80):
            draw.line([(x, 0), (x, h)], fill=(15, 23, 42), width=2)
        cx, cy = w // 2, int(h * 0.35)
        for r in range(250, 50, -40):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(6, 182, 212), width=4)

    def _draw_space_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        for y in range(h):
            ratio = y / h
            r = int(10 + 25 * ratio)
            g = int(5 + 10 * ratio)
            b = int(35 + 45 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        for _ in range(80):
            sx = random.randint(0, w)
            sy = random.randint(0, h)
            rad = random.randint(2, 6)
            color = random.choice([(255, 255, 255), (244, 114, 182), (56, 189, 248), (250, 204, 21)])
            draw.ellipse([sx, sy, sx + rad, sy + rad], fill=color)

    def _draw_city_street_bg(self, draw: ImageDraw.ImageDraw, w: int, h: int, title: str):
        for y in range(int(h * 0.6)):
            ratio = y / (h * 0.6)
            r = int(244 * (1 - ratio) + 217 * ratio)
            g = int(114 * (1 - ratio) + 70 * ratio)
            b = int(182 * (1 - ratio) + 239 * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        draw.rectangle([0, int(h * 0.6), w, h], fill=(30, 41, 59))
        draw.line([(w // 2, int(h * 0.6)), (w // 2, h)], fill=(250, 204, 21), width=10)

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, style: str = "Modern 2D Cartoon", logger_func = None) -> Dict[str, str]:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        name = char_data.get("name", "Character")
        skin = char_data.get("skin_tone", "#f6d5b8")
        hair = char_data.get("hair_color", "#2d3748")
        outfit = char_data.get("outfit_color", "#3b82f6")
        gender = char_data.get("gender", "Male")
        is_robot = "robot" in gender.lower() or "ai" in char_data.get("role", "").lower() or "bot" in name.lower()
        is_cat = "cat" in name.lower() or "cat" in char_data.get("role", "").lower()
        
        sprites = {}
        for exp in ["avatar", "talking_open", "talking_closed", "shock", "happy"]:
            file_path = str(out_dir / f"{name.lower().replace(' ', '_')}_{exp}.png")
            img = Image.new("RGBA", (800, 1000), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            if is_robot:
                self._render_robot_character(draw, 400, 500, exp, outfit, style=style)
            elif is_cat:
                self._render_cat_character(draw, 400, 500, exp, skin, hair, style=style)
            else:
                self._render_human_character(draw, 400, 500, exp, skin, hair, outfit, char_data.get("hair_style", "Messy Anime"), gender, style=style)
                
            s_lower = (style or "").lower()
            if "pixel" in s_lower or "16-bit" in s_lower:
                dw, dh = 800 // 4, 1000 // 4
                down = img.resize((dw, dh), Image.Resampling.NEAREST)
                quant = down.quantize(colors=28, method=Image.Quantize.FASTOCTREE).convert("RGBA")
                img = quant.resize((800, 1000), Image.Resampling.NEAREST)
            elif "noir" in s_lower:
                alpha = img.split()[-1]
                gray = img.convert("L")
                gray_rgb = ImageOps.colorize(gray, black="#0a0c14", white="#f1f5f9").convert("RGBA")
                gray_rgb.putalpha(alpha)
                img = gray_rgb

            img.save(file_path, "PNG")
            sprites[exp] = file_path
            
        if logger_func:
            await logger_func(f"[FALLBACK] Generated 5-expression sprite rig for {name} ({style}).")
        return sprites

    def _render_human_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, skin: str, hair: str, outfit: str, hair_style: str, gender: str = "Male", style: str = "Modern 2D Cartoon"):
        s = (style or "").lower()
        
        # Style palette adjustments
        if "noir" in s:
            skin = "#d1d5db"
            hair = "#1f2937"
            outfit = "#374151"
        elif "cyber" in s:
            outfit = "#0f172a"
            hair = "#06b6d4"
        elif "doodle" in s:
            skin = "#ffffff"
            hair = "#18181b"
            outfit = "#f4f4f5"

        is_chibi = "chibi" in s or "kawaii" in s
        is_doodle = "doodle" in s or "stick" in s
        is_90s = "90s" in s or "retro" in s
        is_cyber = "cyber" in s
        is_noir = "noir" in s
        is_pixel = "pixel" in s or "16-bit" in s
        line_w = 16 if is_90s else (4 if is_doodle else 10)

        # Torso & Clothing
        if is_doodle:
            # Minimalist doodle stick body
            draw.line([(cx, cy + 120), (cx, cy + 450)], fill=(20, 20, 20), width=6)
            draw.line([(cx - 120, cy + 220), (cx + 120, cy + 220)], fill=(20, 20, 20), width=6)
        elif is_chibi:
            # Petite chibi body
            draw.ellipse([cx - 150, cy + 160, cx + 150, cy + 450], fill=outfit, outline=(15, 23, 42), width=line_w)
            draw.ellipse([cx - 50, cy + 140, cx + 50, cy + 200], fill=(240, 240, 240), outline=(15, 23, 42), width=6)
            draw.rectangle([cx - 30, cy + 80, cx + 30, cy + 160], fill=skin, outline=(15, 23, 42), width=6)
        else:
            draw.ellipse([cx - 220, cy + 180, cx + 220, cy + 600], fill=outfit, outline=(15, 23, 42), width=line_w)
            draw.ellipse([cx - 80, cy + 160, cx + 80, cy + 240], fill=(240, 240, 240), outline=(15, 23, 42), width=8)
            draw.rectangle([cx - 50, cy + 100, cx + 50, cy + 200], fill=skin, outline=(15, 23, 42), width=8)

        # Head
        if is_chibi:
            # Oversized cute round head
            draw.ellipse([cx - 190, cy - 160, cx + 190, cy + 170], fill=skin, outline=(15, 23, 42), width=line_w)
        elif is_doodle:
            draw.ellipse([cx - 120, cy - 110, cx + 120, cy + 130], fill=skin, outline=(20, 20, 20), width=5)
        else:
            draw.ellipse([cx - 150, cy - 120, cx + 150, cy + 170], fill=skin, outline=(15, 23, 42), width=line_w)

        # Hair
        if is_doodle:
            for sx in range(cx - 100, cx + 100, 25):
                draw.line([(sx, cy - 110), (sx + 10, cy - 150)], fill=(20, 20, 20), width=4)
        elif "curly" in hair_style.lower() or "afro" in hair_style.lower():
            for i in range(12):
                hx = cx - 140 + (i * 24)
                draw.ellipse([hx - 30, cy - 190, hx + 30, cy - 80], fill=hair, outline=(15, 23, 42), width=6)
        else:
            top_offset = -210 if is_chibi else -200
            draw.ellipse([cx - 175, cy + top_offset, cx + 175, cy + 40], fill=hair, outline=(15, 23, 42), width=line_w)
            for sx in range(cx - 130, cx + 130, 45):
                draw.polygon([(sx, cy - 50), (sx + 25, cy + 10), (sx + 50, cy - 50)], fill=hair, outline=(15, 23, 42))

        # Female Eyelashes
        if "female" in gender.lower() and not is_doodle:
            draw.line([(cx - 75, cy - 35), (cx - 95, cy - 45)], fill=(15, 23, 42), width=5)
            draw.line([(cx + 75, cy - 35), (cx + 95, cy - 45)], fill=(15, 23, 42), width=5)

        # Style-specific Face Features
        if is_chibi:
            # Rosy pink blush circles
            draw.ellipse([cx - 130, cy + 30, cx - 70, cy + 70], fill=(255, 105, 180))
            draw.ellipse([cx + 70, cy + 30, cx + 130, cy + 70], fill=(255, 105, 180))
            # Giant cute sparkling eyes
            draw.ellipse([cx - 110, cy - 40, cx - 30, cy + 30], fill=(15, 23, 42))
            draw.ellipse([cx + 30, cy - 40, cx + 110, cy + 30], fill=(15, 23, 42))
            # Highlights
            draw.ellipse([cx - 95, cy - 30, cx - 65, cy - 5], fill=(255, 255, 255))
            draw.ellipse([cx - 60, cy + 5, cx - 45, cy + 20], fill=(255, 255, 255))
            draw.ellipse([cx + 45, cy - 30, cx + 75, cy - 5], fill=(255, 255, 255))
            draw.ellipse([cx + 80, cy + 5, cx + 95, cy + 20], fill=(255, 255, 255))
            # Cute tiny mouth
            if emotion in ["talking_open", "happy"]:
                draw.ellipse([cx - 25, cy + 70, cx + 25, cy + 110], fill=(239, 68, 68), outline=(15, 23, 42), width=4)
            else:
                draw.arc([cx - 20, cy + 70, cx + 20, cy + 95], 0, 180, fill=(239, 68, 68), width=5)
            return

        if is_cyber:
            # Glowing cyber visor goggles
            draw.rectangle([cx - 110, cy - 40, cx + 110, cy + 20], fill=(15, 23, 42), outline=(6, 182, 212), width=6)
            draw.line([(cx - 90, cy - 10), (cx + 90, cy - 10)], fill=(236, 72, 153), width=4)
            # Tech cheek tattoo
            draw.line([(cx - 120, cy + 30), (cx - 80, cy + 30), (cx - 60, cy + 60)], fill=(6, 182, 212), width=4)
            # Cyber mouth
            if emotion in ["shock", "talking_open"]:
                draw.rectangle([cx - 30, cy + 70, cx + 30, cy + 110], fill=(6, 182, 212), outline=(15, 23, 42), width=4)
            else:
                draw.line([(cx - 30, cy + 80), (cx + 30, cy + 80)], fill=(6, 182, 212), width=5)
            return

        if is_pixel:
            # Chunky pixel eyes
            draw.rectangle([cx - 75, cy - 30, cx - 35, cy + 10], fill=(15, 23, 42))
            draw.rectangle([cx - 65, cy - 20, cx - 50, cy - 5], fill=(255, 255, 255))
            draw.rectangle([cx + 35, cy - 30, cx + 75, cy + 10], fill=(15, 23, 42))
            draw.rectangle([cx + 45, cy - 20, cx + 60, cy - 5], fill=(255, 255, 255))
            # Pixel mouth
            if emotion in ["shock", "talking_open"]:
                draw.rectangle([cx - 35, cy + 65, cx + 35, cy + 115], fill=(220, 38, 38))
            else:
                draw.rectangle([cx - 30, cy + 70, cx + 30, cy + 85], fill=(220, 38, 38))
            return

        if is_90s:
            # Pie-cut vintage retro cartoon eyes
            draw.ellipse([cx - 75, cy - 35, cx - 25, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=line_w)
            draw.ellipse([cx + 25, cy - 35, cx + 75, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=line_w)
            # Pupil with pie slice
            draw.ellipse([cx - 60, cy - 20, cx - 40, cy], fill=(15, 23, 42))
            draw.polygon([(cx - 50, cy - 10), (cx - 40, cy - 20), (cx - 40, cy)], fill=(255, 255, 255))
            draw.ellipse([cx + 40, cy - 20, cx + 60, cy], fill=(15, 23, 42))
            draw.polygon([(cx + 50, cy - 10), (cx + 60, cy - 20), (cx + 60, cy)], fill=(255, 255, 255))
            # Big retro mouth
            if emotion in ["shock", "talking_open"]:
                draw.ellipse([cx - 45, cy + 50, cx + 45, cy + 130], fill=(220, 38, 38), outline=(15, 23, 42), width=line_w)
            else:
                draw.ellipse([cx - 40, cy + 60, cx + 40, cy + 110], fill=(220, 38, 38), outline=(15, 23, 42), width=line_w)
            return

        if is_noir:
            # Grayscale eyes
            draw.ellipse([cx - 75, cy - 35, cx - 25, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx + 25, cy - 35, cx + 75, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx - 58, cy - 20, cx - 42, cy + 2], fill=(15, 23, 42))
            draw.ellipse([cx + 42, cy - 20, cx + 58, cy + 2], fill=(15, 23, 42))
            # Dramatic shadow over half face
            draw.polygon([(cx, cy - 120), (cx + 150, cy - 120), (cx + 150, cy + 170), (cx - 20, cy + 170)], fill=(0, 0, 0, 120))
            if emotion in ["shock", "talking_open"]:
                draw.ellipse([cx - 35, cy + 60, cx + 35, cy + 120], fill=(15, 23, 42), outline=(15, 23, 42), width=6)
            else:
                draw.line([(cx - 30, cy + 85), (cx + 30, cy + 85)], fill=(15, 23, 42), width=6)
            return

        # Eyes & Mouth based on emotion for Modern & Anime
        if emotion == "shock":
            draw.ellipse([cx - 85, cy - 50, cx - 25, cy + 20], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx + 25, cy - 50, cx + 85, cy + 20], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx - 60, cy - 25, cx - 45, cy - 5], fill=(15, 23, 42))
            draw.ellipse([cx + 50, cy - 25, cx + 65, cy - 5], fill=(15, 23, 42))
            draw.ellipse([cx - 45, cy + 50, cx + 45, cy + 140], fill=(239, 68, 68), outline=(15, 23, 42), width=8)
        elif emotion in ["talking_open", "happy"]:
            draw.ellipse([cx - 75, cy - 35, cx - 25, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx + 25, cy - 35, cx + 75, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx - 58, cy - 20, cx - 42, cy + 2], fill=(15, 23, 42))
            draw.ellipse([cx + 42, cy - 20, cx + 58, cy + 2], fill=(15, 23, 42))
            draw.ellipse([cx - 40, cy + 60, cx + 40, cy + 110], fill=(220, 38, 38), outline=(15, 23, 42), width=8)
            draw.arc([cx - 40, cy + 60, cx + 40, cy + 110], 0, 180, fill=(255, 255, 255), width=8)
        else: # avatar, closed
            draw.ellipse([cx - 75, cy - 35, cx - 25, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx + 25, cy - 35, cx + 75, cy + 15], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx - 58, cy - 20, cx - 42, cy + 2], fill=(15, 23, 42))
            draw.ellipse([cx + 42, cy - 20, cx + 58, cy + 2], fill=(15, 23, 42))
            draw.line([(cx - 35, cy + 85), (cx + 35, cy + 85)], fill=(15, 23, 42), width=8)

        if "anime" in s:
            # Anime blush dashes
            draw.line([(cx - 95, cy + 30), (cx - 75, cy + 45)], fill=(244, 114, 182), width=4)
            draw.line([(cx - 85, cy + 30), (cx - 65, cy + 45)], fill=(244, 114, 182), width=4)
            draw.line([(cx + 65, cy + 30), (cx + 85, cy + 45)], fill=(244, 114, 182), width=4)
            draw.line([(cx + 75, cy + 30), (cx + 95, cy + 45)], fill=(244, 114, 182), width=4)

    def _render_robot_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, accent: str, style: str = "Modern 2D Cartoon"):
        s = (style or "").lower()
        visor_color = (6, 182, 212)
        body_color = (226, 232, 240)
        outline_color = (30, 41, 59)
        is_pixel = "pixel" in s or "16-bit" in s
        is_noir = "noir" in s
        is_doodle = "doodle" in s
        is_chibi = "chibi" in s or "kawaii" in s
        
        if "cyber" in s:
            visor_color = (236, 72, 153)
            body_color = (15, 23, 42)
            outline_color = (6, 182, 212)
        elif is_noir:
            visor_color = (220, 220, 220)
            body_color = (55, 65, 81)
            outline_color = (15, 23, 42)
        elif is_pixel:
            visor_color = (250, 204, 21)
            body_color = (71, 85, 105)
            outline_color = (15, 23, 42)
        elif is_chibi:
            visor_color = (244, 114, 182)
            body_color = (255, 241, 242)
            outline_color = (15, 23, 42)
        elif is_doodle:
            visor_color = (20, 20, 20)
            body_color = (255, 255, 255)
            outline_color = (20, 20, 20)

        if is_pixel:
            # Blocky retro arcade robot chassis
            draw.rectangle([cx - 160, cy - 160, cx + 160, cy + 160], fill=body_color, outline=outline_color, width=12)
            draw.rectangle([cx - 15, cy - 240, cx + 15, cy - 160], fill=(148, 163, 184))
            draw.rectangle([cx - 30, cy - 290, cx + 30, cy - 240], fill=visor_color, outline=outline_color, width=8)
            draw.rectangle([cx - 120, cy - 60, cx + 120, cy + 60], fill=(15, 23, 42), outline=outline_color, width=8)
            if emotion in ["shock", "panic"]:
                draw.rectangle([cx - 90, cy - 30, cx - 30, cy + 30], fill=(239, 68, 68))
                draw.rectangle([cx + 30, cy - 30, cx + 90, cy + 30], fill=(239, 68, 68))
            else:
                draw.rectangle([cx - 80, cy - 20, cx - 40, cy + 20], fill=visor_color)
                draw.rectangle([cx + 40, cy - 20, cx + 80, cy + 20], fill=visor_color)
            return

        if is_doodle:
            # Simple hand-drawn box doodle robot
            draw.rectangle([cx - 140, cy - 130, cx + 140, cy + 140], fill=body_color, outline=outline_color, width=6)
            draw.line([(cx, cy - 130), (cx, cy - 220)], fill=outline_color, width=6)
            draw.ellipse([cx - 20, cy - 260, cx + 20, cy - 220], fill=body_color, outline=outline_color, width=6)
            draw.rectangle([cx - 100, cy - 50, cx + 100, cy + 50], fill=(255, 255, 255), outline=outline_color, width=5)
            draw.line([(cx - 60, cy), (cx - 20, cy)], fill=outline_color, width=6)
            draw.line([(cx + 20, cy), (cx + 60, cy)], fill=outline_color, width=6)
            return

        draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=body_color, outline=outline_color, width=12)
        # Antenna
        draw.line([(cx, cy - 180), (cx, cy - 260)], fill=(71, 85, 105), width=12)
        draw.ellipse([cx - 25, cy - 310, cx + 25, cy - 260], fill=visor_color, outline=(15, 23, 42), width=8)
        # Visor Screen
        draw.rectangle([cx - 130, cy - 70, cx + 130, cy + 70], fill=(15, 23, 42), outline=(56, 189, 248) if "cyber" not in s else visor_color, width=8)
        if emotion == "shock":
            draw.line([(cx - 80, cy - 30), (cx - 40, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx - 40, cy - 30), (cx - 80, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx + 40, cy - 30), (cx + 80, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx + 80, cy - 30), (cx + 40, cy + 30)], fill=(239, 68, 68), width=8)
        else:
            # Digital eyes
            draw.ellipse([cx - 85, cy - 25, cx - 35, cy + 25], fill=visor_color)
            draw.ellipse([cx + 35, cy - 25, cx + 85, cy + 25], fill=visor_color)

    def _render_cat_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, fur: str, ear_inner: str, style: str = "Modern 2D Cartoon"):
        s = (style or "").lower()
        if "noir" in s:
            fur = "#374151"
            ear_inner = "#9ca3af"
        elif "cyber" in s:
            fur = "#0f172a"
            ear_inner = "#06b6d4"
        elif "doodle" in s:
            fur = "#ffffff"
            ear_inner = "#f4f4f5"

        # Ears
        draw.polygon([(cx - 140, cy - 100), (cx - 90, cy - 240), (cx - 20, cy - 120)], fill=fur, outline=(15, 23, 42), width=8)
        draw.polygon([(cx + 20, cy - 120), (cx + 90, cy - 240), (cx + 140, cy - 100)], fill=fur, outline=(15, 23, 42), width=8)
        # Head
        draw.ellipse([cx - 150, cy - 120, cx + 150, cy + 140], fill=fur, outline=(15, 23, 42), width=10)
        # Cat eyes
        draw.ellipse([cx - 75, cy - 40, cx - 25, cy + 10], fill=(250, 204, 21), outline=(15, 23, 42), width=6)
        draw.ellipse([cx + 25, cy - 40, cx + 75, cy + 10], fill=(250, 204, 21), outline=(15, 23, 42), width=6)
        draw.ellipse([cx - 55, cy - 35, cx - 45, cy + 5], fill=(15, 23, 42))
        draw.ellipse([cx + 45, cy - 35, cx + 55, cy + 5], fill=(15, 23, 42))
        # Whiskers
        draw.line([(cx - 70, cy + 40), (cx - 160, cy + 25)], fill=(15, 23, 42), width=6)
        draw.line([(cx - 70, cy + 55), (cx - 160, cy + 65)], fill=(15, 23, 42), width=6)
        draw.line([(cx + 70, cy + 40), (cx + 160, cy + 25)], fill=(15, 23, 42), width=6)
        draw.line([(cx + 70, cy + 55), (cx + 160, cy + 65)], fill=(15, 23, 42), width=6)

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, style: str = "Modern 2D Cartoon", logger_func = None) -> str:
        if os.path.exists(bg_path):
            base_img = Image.open(bg_path).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
        else:
            base_img = Image.new("RGBA", (width, height), (30, 41, 59, 255))
            
        num_chars = len(char_specs)
        if num_chars == 1:
            positions = [(int(width * 0.5), int(height * 0.65))]
        elif num_chars == 2:
            positions = [(int(width * 0.28), int(height * 0.68)), (int(width * 0.72), int(height * 0.68))]
        else:
            positions = [(int(width * 0.2), int(height * 0.68)), (int(width * 0.5), int(height * 0.68)), (int(width * 0.8), int(height * 0.68))]

        for idx, spec in enumerate(char_specs):
            if idx >= len(positions):
                break
            spr_path = spec.get("sprite_path")
            if spr_path and os.path.exists(spr_path):
                spr_img = Image.open(spr_path).convert("RGBA")
                target_w = int(width * 0.85) if num_chars == 1 else int(width * 0.62)
                aspect = spr_img.height / spr_img.width
                target_h = int(target_w * aspect)
                spr_img = spr_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                pos_x, pos_y = positions[idx]
                paste_x = pos_x - target_w // 2
                paste_y = pos_y - target_h // 2
                
                base_img.paste(spr_img, (paste_x, paste_y), spr_img)

        # Dynamic comic action speedlines & impact bursts for dramatic beats
        if emotion in ["shock", "panic"] or any(k in (action_desc or "").lower() for k in ["scream", "yell", "panic", "shock", "blast", "flying", "fall"]):
            speedline_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_overlay = ImageDraw.Draw(speedline_overlay)
            cx, cy = width // 2, int(height * 0.45)
            for angle_deg in range(0, 360, 12):
                rad = math.radians(angle_deg)
                start_dist = int(min(width, height) * 0.42)
                end_dist = int(max(width, height) * 0.82)
                x1 = int(cx + start_dist * math.cos(rad))
                y1 = int(cy + start_dist * math.sin(rad))
                x2 = int(cx + end_dist * math.cos(rad))
                y2 = int(cy + end_dist * math.sin(rad))
                draw_overlay.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 120), width=5)
            base_img = Image.alpha_composite(base_img, speedline_overlay)

        # Apply rich art style post-processing
        base_img = self._apply_style_postprocessing(base_img, style=style, width=width, height=height, emotion=emotion)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        base_img.convert("RGB").save(output_path, "PNG", quality=95)
        return output_path

    def _apply_style_postprocessing(self, base_img: Image.Image, style: str, width: int = 1080, height: int = 1920, emotion: str = "happy") -> Image.Image:
        s = (style or "").lower()

        # 1. PIXEL ART 16-BIT ARCADE
        if "pixel" in s or "16-bit" in s or "arcade" in s:
            dw, dh = width // 4, height // 4
            down = base_img.resize((dw, dh), Image.Resampling.NEAREST)
            quant = down.convert("RGB").quantize(colors=32, method=Image.Quantize.MEDIANCUT).convert("RGBA")
            pixel_img = quant.resize((width, height), Image.Resampling.NEAREST)
            
            # Retro Arcade HUD Top Bar
            draw = ImageDraw.Draw(pixel_img)
            draw.rectangle([0, 0, width, 110], fill=(10, 10, 20, 230))
            draw.line([(0, 110), (width, 110)], fill=(250, 204, 21), width=6)
            
            font_hud = self._get_font(32, bold=True)
            draw.text((40, 35), "1UP", fill=(239, 68, 68), font=font_hud)
            draw.text((120, 35), "04290", fill=(255, 255, 255), font=font_hud)
            draw.text((380, 35), "STAGE 01", fill=(6, 182, 212), font=font_hud)
            draw.text((640, 35), "HIGH: 99420", fill=(250, 204, 21), font=font_hud)
            
            # Pixel health hearts
            for hi in range(3):
                hx = width - 180 + (hi * 45)
                hy = 42
                draw.rectangle([hx+4, hy, hx+12, hy+6], fill=(239, 68, 68))
                draw.rectangle([hx+16, hy, hx+24, hy+6], fill=(239, 68, 68))
                draw.rectangle([hx, hy+6, hx+28, hy+16], fill=(239, 68, 68))
                draw.rectangle([hx+4, hy+16, hx+24, hy+22], fill=(239, 68, 68))
                draw.rectangle([hx+8, hy+22, hx+20, hy+28], fill=(239, 68, 68))
                draw.rectangle([hx+12, hy+28, hx+16, hy+32], fill=(239, 68, 68))
                
            return pixel_img

        # 2. DARK NOIR DETECTIVE
        elif "noir" in s or "detective" in s:
            gray = base_img.convert("L")
            gray_rgb = ImageOps.colorize(gray, black="#080a10", white="#f3f4f6").convert("RGBA")
            enhancer = ImageEnhance.Contrast(gray_rgb)
            noir_img = enhancer.enhance(1.4)
            
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            step = 100
            for y in range(-width, height, step):
                draw_ov.polygon([
                    (0, y),
                    (width, y + int(width * 0.45)),
                    (width, y + int(width * 0.45) + 55),
                    (0, y + 55)
                ], fill=(0, 0, 0, 110))
                
            draw_ov.rectangle([0, 0, width, height], outline=(0, 0, 0, 200), width=24)
            
            font_stamp = self._get_font(28, bold=True)
            draw_ov.rectangle([40, 50, 480, 110], fill=(15, 23, 42, 220), outline=(220, 38, 38, 240), width=4)
            draw_ov.text((60, 65), "CASE FILE: #404 - CLASSIFIED", fill=(245, 245, 245), font=font_stamp)
            
            return Image.alpha_composite(noir_img, overlay)

        # 3. COMIC BOOK POP ART
        elif "comic" in s or "pop art" in s or "halftone" in s:
            enhancer = ImageEnhance.Color(base_img)
            comic_img = enhancer.enhance(1.4)
            
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            for dy in range(40, height - 40, 28):
                for dx in range(40, width - 40, 28):
                    if (dx + dy) % 56 == 0:
                        draw_ov.ellipse([dx-3, dy-3, dx+3, dy+3], fill=(0, 0, 0, 45))
                        
            draw_ov.rectangle([0, 0, width, height], outline=(15, 23, 42), width=22)
            draw_ov.rectangle([22, 22, width-22, height-22], outline=(250, 204, 21), width=8)
            
            burst_words = ["POW!", "WHAM!", "BAM!", "BOOM!", "ZAP!"]
            chosen_word = burst_words[hash(base_img.tobytes()[:32]) % len(burst_words)]
            
            bx, by = width - 260, 180
            pts = []
            for i in range(16):
                ang = math.radians(i * (360 / 16))
                r = 110 if i % 2 == 0 else 65
                pts.append((int(bx + r * math.cos(ang)), int(by + r * math.sin(ang))))
                
            draw_ov.polygon(pts, fill=(239, 68, 68), outline=(15, 23, 42), width=8)
            font_comic = self._get_font(44, bold=True)
            draw_ov.text((bx - 60, by - 26), chosen_word, fill=(255, 255, 255), font=font_comic)
            
            return Image.alpha_composite(comic_img, overlay)

        # 4. CYBERPUNK NEON ANIMATED
        elif "cyber" in s or "neon" in s or "synthwave" in s:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            for y in range(0, height, 10):
                draw_ov.line([(0, y), (width, y)], fill=(6, 182, 212, 35), width=2)
                
            neon_cyan = (6, 182, 212, 230)
            neon_pink = (236, 72, 153, 230)
            
            draw_ov.line([(40, 40), (140, 40)], fill=neon_cyan, width=6)
            draw_ov.line([(40, 40), (40, 140)], fill=neon_cyan, width=6)
            draw_ov.line([(width - 140, 40), (width - 40, 40)], fill=neon_pink, width=6)
            draw_ov.line([(width - 40, 40), (width - 40, 140)], fill=neon_pink, width=6)
            draw_ov.line([(40, height - 40), (140, height - 40)], fill=neon_pink, width=6)
            draw_ov.line([(40, height - 40), (40, height - 140)], fill=neon_pink, width=6)
            draw_ov.line([(width - 140, height - 40), (width - 40, height - 40)], fill=neon_cyan, width=6)
            draw_ov.line([(width - 40, height - 40), (width - 40, height - 140)], fill=neon_cyan, width=6)
            
            font_cyber = self._get_font(24, bold=True)
            draw_ov.text((60, 55), "SYS_ONLINE // 2088.v4", fill=(6, 182, 212, 255), font=font_cyber)
            draw_ov.text((width - 320, 55), "TARGET_LOCK: ACTIVE", fill=(236, 72, 153, 255), font=font_cyber)
            draw_ov.rectangle([0, 0, width, height], outline=(6, 182, 212, 120), width=10)
            
            return Image.alpha_composite(base_img, overlay)

        # 5. 90s SATURDAY MORNING RETRO
        elif "90s" in s or "retro" in s or "morning" in s:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            draw_ov.rectangle([0, 0, width, height], outline=(30, 41, 59, 255), width=28)
            corner_r = 70
            draw_ov.pieslice([0, 0, corner_r * 2, corner_r * 2], 180, 270, fill=(15, 23, 42))
            draw_ov.pieslice([width - corner_r * 2, 0, width, corner_r * 2], 270, 360, fill=(15, 23, 42))
            draw_ov.pieslice([0, height - corner_r * 2, corner_r * 2, height], 90, 180, fill=(15, 23, 42))
            draw_ov.pieslice([width - corner_r * 2, height - corner_r * 2, width, height], 0, 90, fill=(15, 23, 42))
            
            font_retro = self._get_font(34, bold=True)
            draw_ov.rectangle([60, 60, 250, 120], fill=(239, 68, 68), outline=(255, 255, 255), width=4)
            draw_ov.text((80, 72), "CH-09 CARTOON", fill=(255, 255, 255), font=font_retro)
            
            warm = ImageEnhance.Color(base_img).enhance(1.25)
            return Image.alpha_composite(warm, overlay)

        # 6. CHIBI / KAWAII CUTE
        elif "chibi" in s or "kawaii" in s or "cute" in s:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            sparkles = [
                (int(width * 0.15), int(height * 0.18), 35, (255, 182, 193, 230)),
                (int(width * 0.85), int(height * 0.22), 40, (255, 223, 186, 230)),
                (int(width * 0.12), int(height * 0.75), 30, (255, 255, 186, 230)),
                (int(width * 0.88), int(height * 0.70), 38, (186, 255, 201, 230)),
                (int(width * 0.50), int(height * 0.08), 28, (186, 225, 255, 230)),
            ]
            
            for sx, sy, rad, col in sparkles:
                draw_ov.polygon([
                    (sx, sy - rad),
                    (sx + int(rad * 0.3), sy - int(rad * 0.3)),
                    (sx + rad, sy),
                    (sx + int(rad * 0.3), sy + int(rad * 0.3)),
                    (sx, sy + rad),
                    (sx - int(rad * 0.3), sy + int(rad * 0.3)),
                    (sx - rad, sy),
                    (sx - int(rad * 0.3), sy - int(rad * 0.3)),
                ], fill=col)
                
            hearts = [
                (int(width * 0.22), int(height * 0.35)),
                (int(width * 0.78), int(height * 0.40)),
                (int(width * 0.30), int(height * 0.82))
            ]
            for hx, hy in hearts:
                draw_ov.ellipse([hx-16, hy-16, hx, hy], fill=(255, 105, 180, 210))
                draw_ov.ellipse([hx, hy-16, hx+16, hy], fill=(255, 105, 180, 210))
                draw_ov.polygon([(hx-16, hy-8), (hx+16, hy-8), (hx, hy+16)], fill=(255, 105, 180, 210))
                
            return Image.alpha_composite(base_img, overlay)

        # 7. DOODLE / STICK FIGURE COMEDY
        elif "doodle" in s or "stick figure" in s:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            draw_ov.line([(140, 0), (140, height)], fill=(239, 68, 68, 120), width=3)
            for y in range(80, height, 48):
                draw_ov.line([(0, y), (width, y)], fill=(59, 130, 246, 50), width=2)
                
            for offset in [14, 18]:
                draw_ov.rectangle([offset, offset, width - offset, height - offset], outline=(30, 41, 59, 160), width=3)
                
            font_doodle = self._get_font(28, bold=True)
            draw_ov.text((160, 40), "# DOODLE LOG // TOP SECRET", fill=(30, 41, 59, 200), font=font_doodle)
            
            return Image.alpha_composite(base_img, overlay)

        # 8. ANIME COMIC SHORTS
        elif "anime" in s:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            
            if emotion in ["shock", "panic", "excited"]:
                cx, cy = width // 2, int(height * 0.45)
                for angle_deg in range(0, 360, 10):
                    rad = math.radians(angle_deg)
                    start_dist = int(min(width, height) * 0.38)
                    end_dist = int(max(width, height) * 0.85)
                    x1 = int(cx + start_dist * math.cos(rad))
                    y1 = int(cy + start_dist * math.sin(rad))
                    x2 = int(cx + end_dist * math.cos(rad))
                    y2 = int(cy + end_dist * math.sin(rad))
                    draw_ov.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 140), width=6)
                    
            draw_ov.rectangle([0, 0, width, height], outline=(15, 23, 42, 220), width=12)
            return Image.alpha_composite(base_img, overlay)

        # 9. CLAYMATION / STOP-MOTION STYLE
        elif "clay" in s or "stop-motion" in s:
            enhancer = ImageEnhance.Color(base_img)
            clay_img = enhancer.enhance(1.15)
            
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            draw_ov.rectangle([0, 0, width, height], outline=(120, 80, 50, 180), width=20)
            return Image.alpha_composite(clay_img, overlay)

        # 10. MODERN 2D CARTOON (Default)
        return base_img


class VisualFactory:
    @staticmethod
    async def get_best_provider(preferred: str = "auto") -> VisualProvider:
        comfy = ComfyUIVisualProvider()
        if preferred in ["comfyui", "auto"]:
            if await comfy.is_available():
                return comfy
        return ToonVectorVisualProvider()
