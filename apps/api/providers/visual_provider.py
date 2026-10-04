import os
import math
import random
import hashlib
import json
import asyncio
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from apps.api.config import settings

class VisualProvider:
    def get_provider_name(self) -> str:
        return "GenericVisualProvider"

    def get_provider_type(self) -> str:
        return "FALLBACK"

    async def is_available(self) -> bool:
        return True

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, logger_func = None) -> str:
        raise NotImplementedError

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
        raise NotImplementedError

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, logger_func = None) -> Dict[str, str]:
        raise NotImplementedError

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
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

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, logger_func = None) -> str:
        name = char_data.get("name", "Character")
        prompt = f"masterpiece, best quality, 2d cartoon character sheet, {name}, {char_data.get('gender', '')}, {char_data.get('age', '')} years old, {char_data.get('hair_style', '')}, {char_data.get('outfit_desc', '')}, vibrant colors, clean lineart, modern anime cartoon shorts style, white background"
        
        if logger_func:
            await logger_func(f"[AI] ComfyUI generating character reference sheet for {name}...")

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
        return await fallback.generate_character_reference(char_data, output_path, logger_func)

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
        positive_prompt = f"masterpiece, best quality, 2d modern cartoon background, {location}, {prompt}, anime shorts style, clean vector shapes, vibrant colors, detailed interior scenery, 8k resolution, vertical composition"
        negative_prompt = "low quality, photo, 3d, realistic, deformed, noisy, text, watermark, blurry, human, character, face"

        if logger_func:
            await logger_func(f"[AI] ComfyUI generating AI background for {location}...")

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
        return await fallback.generate_background(location, prompt, output_path, width, height, logger_func)

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

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, logger_func = None) -> Dict[str, str]:
        fallback = ToonVectorVisualProvider()
        return await fallback.generate_character_rig(char_data, output_dir, logger_func)

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
        fallback = ToonVectorVisualProvider()
        return await fallback.compose_scene_frame(bg_path, char_specs, action_desc, emotion, output_path, width, height, logger_func)


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
        return "FALLBACK"

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

    async def generate_character_reference(self, char_data: Dict[str, Any], output_path: str, logger_func = None) -> str:
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
            self._render_robot_character(draw, 400, 500, "avatar", outfit)
        elif is_cat:
            self._render_cat_character(draw, 400, 500, "avatar", skin, hair)
        else:
            self._render_human_character(draw, 400, 500, "avatar", skin, hair, outfit, char_data.get("hair_style", "Messy Anime"), gender)
            
        img.convert("RGB").save(str(out_file), "PNG")
        if logger_func:
            await logger_func(f"[FALLBACK] Generated character reference sheet for {name}.")
        return str(out_file)

    async def generate_background(self, location: str, prompt: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
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
            
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(output_path, "PNG", quality=95)
        
        if logger_func:
            await logger_func(f"[FALLBACK] Rendered dynamic background for {location}.")
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

    async def generate_character_rig(self, char_data: Dict[str, Any], output_dir: str, logger_func = None) -> Dict[str, str]:
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
                self._render_robot_character(draw, 400, 500, exp, outfit)
            elif is_cat:
                self._render_cat_character(draw, 400, 500, exp, skin, hair)
            else:
                self._render_human_character(draw, 400, 500, exp, skin, hair, outfit, char_data.get("hair_style", "Messy Anime"), gender)
                
            img.save(file_path, "PNG")
            sprites[exp] = file_path
            
        if logger_func:
            await logger_func(f"[FALLBACK] Generated 5-expression sprite rig for {name}.")
        return sprites

    def _render_human_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, skin: str, hair: str, outfit: str, hair_style: str, gender: str = "Male"):
        # Torso & Clothing
        draw.ellipse([cx - 220, cy + 180, cx + 220, cy + 600], fill=outfit, outline=(15, 23, 42), width=10)
        draw.ellipse([cx - 80, cy + 160, cx + 80, cy + 240], fill=(240, 240, 240), outline=(15, 23, 42), width=8)
        # Neck
        draw.rectangle([cx - 50, cy + 100, cx + 50, cy + 200], fill=skin, outline=(15, 23, 42), width=8)
        # Head
        draw.ellipse([cx - 150, cy - 120, cx + 150, cy + 170], fill=skin, outline=(15, 23, 42), width=10)
        # Hair
        if "curly" in hair_style.lower() or "afro" in hair_style.lower():
            for i in range(12):
                hx = cx - 140 + (i * 24)
                draw.ellipse([hx - 30, cy - 190, hx + 30, cy - 80], fill=hair, outline=(15, 23, 42), width=6)
        else:
            draw.ellipse([cx - 165, cy - 200, cx + 165, cy + 40], fill=hair, outline=(15, 23, 42), width=10)
            for sx in range(cx - 130, cx + 130, 45):
                draw.polygon([(sx, cy - 50), (sx + 25, cy + 10), (sx + 50, cy - 50)], fill=hair, outline=(15, 23, 42))

        # Female Eyelashes
        if "female" in gender.lower():
            draw.line([(cx - 75, cy - 35), (cx - 95, cy - 45)], fill=(15, 23, 42), width=5)
            draw.line([(cx + 75, cy - 35), (cx + 95, cy - 45)], fill=(15, 23, 42), width=5)

        # Eyes & Mouth based on emotion
        if emotion == "shock":
            draw.ellipse([cx - 85, cy - 50, cx - 25, cy + 20], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx + 25, cy - 50, cx + 85, cy + 20], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
            draw.ellipse([cx - 60, cy - 25, cx - 45, cy - 5], fill=(15, 23, 42))
            draw.ellipse([cx + 50, cy - 25, cx + 65, cy - 5], fill=(15, 23, 42))
            # Shocked dropped jaw
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

    def _render_robot_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, accent: str):
        draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=(226, 232, 240), outline=(30, 41, 59), width=12)
        # Antenna
        draw.line([(cx, cy - 180), (cx, cy - 260)], fill=(71, 85, 105), width=12)
        draw.ellipse([cx - 25, cy - 310, cx + 25, cy - 260], fill=(6, 182, 212), outline=(15, 23, 42), width=8)
        # Visor Screen
        draw.rectangle([cx - 130, cy - 70, cx + 130, cy + 70], fill=(15, 23, 42), outline=(56, 189, 248), width=8)
        if emotion == "shock":
            draw.line([(cx - 80, cy - 30), (cx - 40, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx - 40, cy - 30), (cx - 80, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx + 40, cy - 30), (cx + 80, cy + 30)], fill=(239, 68, 68), width=8)
            draw.line([(cx + 80, cy - 30), (cx + 40, cy + 30)], fill=(239, 68, 68), width=8)
        else:
            # Cyan digital eyes
            draw.ellipse([cx - 85, cy - 25, cx - 35, cy + 25], fill=(6, 182, 212))
            draw.ellipse([cx + 35, cy - 25, cx + 85, cy + 25], fill=(6, 182, 212))

    def _render_cat_character(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, emotion: str, fur: str, ear_inner: str):
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

    async def compose_scene_frame(self, bg_path: str, char_specs: List[Dict[str, Any]], action_desc: str, emotion: str, output_path: str, width: int = 1080, height: int = 1920, logger_func = None) -> str:
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

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        base_img.convert("RGB").save(output_path, "PNG", quality=95)
        return output_path


class VisualFactory:
    @staticmethod
    async def get_best_provider(preferred: str = "auto") -> VisualProvider:
        comfy = ComfyUIVisualProvider()
        if preferred in ["comfyui", "auto"]:
            if await comfy.is_available():
                return comfy
        return ToonVectorVisualProvider()
