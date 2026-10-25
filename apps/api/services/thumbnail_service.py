import os
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class ThumbnailService:
    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height
        self._font_cache = {}

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.ImageFont:
        font_key = (size, bold)
        if font_key in self._font_cache:
            return self._font_cache[font_key]
        for p in ["C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\impact.ttf", "C:\\Windows\\Fonts\\segoeuib.ttf"]:
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

    def generate_thumbnail(self, title: str, character_sprite: str, output_path: str, style: str = "Modern 2D Cartoon") -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        s = (style or "").lower()
        
        # 1. Style-Specific Background Generation
        if "pixel" in s or "16-bit" in s or "arcade" in s:
            # 16-bit retro arcade starfield with grid horizon
            bg = Image.new("RGBA", (self.width, self.height), (10, 10, 26, 255))
            draw = ImageDraw.Draw(bg)
            # Grid floor
            grid_y_start = int(self.height * 0.58)
            draw.rectangle([0, grid_y_start, self.width, self.height], fill=(20, 14, 45))
            for i in range(12):
                gy = int(grid_y_start + ((i / 12) ** 1.8) * (self.height - grid_y_start))
                draw.line([(0, gy), (self.width, gy)], fill=(147, 51, 234), width=3)
            for x in range(0, self.width + 100, 70):
                draw.line([(self.width // 2, grid_y_start), (x, self.height)], fill=(236, 72, 153), width=2)
            # Starfield dots
            for sx, sy in [(120, 180), (320, 240), (840, 160), (920, 320), (220, 480), (760, 440)]:
                draw.rectangle([sx, sy, sx + 8, sy + 8], fill=(250, 204, 21))
        elif "noir" in s or "detective" in s:
            # High-contrast dramatic noir detective room
            bg = Image.new("RGBA", (self.width, self.height), (12, 14, 20, 255))
            draw = ImageDraw.Draw(bg)
            # Slanted venetian blind light beams
            for y in range(-self.width, self.height, 90):
                draw.polygon([
                    (0, y), (self.width, y + int(self.width * 0.4)),
                    (self.width, y + int(self.width * 0.4) + 45), (0, y + 45)
                ], fill=(240, 240, 255, 35))
        elif "cyber" in s or "neon" in s or "synthwave" in s:
            # Deep cyberpunk synthwave neon grid
            bg = Image.new("RGBA", (self.width, self.height), (10, 10, 25, 255))
            draw = ImageDraw.Draw(bg)
            # Neon sun
            sun_y = int(self.height * 0.42)
            draw.ellipse([self.width // 2 - 280, sun_y - 280, self.width // 2 + 280, sun_y + 280], fill=(236, 72, 153))
            for sl in range(sun_y - 60, sun_y + 260, 36):
                draw.line([(self.width // 2 - 300, sl), (self.width // 2 + 300, sl)], fill=(10, 10, 25), width=8)
            # Scanlines
            for y in range(0, self.height, 12):
                draw.line([(0, y), (self.width, y)], fill=(6, 182, 212, 40), width=2)
        elif "comic" in s or "pop art" in s or "halftone" in s:
            # Vintage comic book pop art burst
            bg = Image.new("RGBA", (self.width, self.height), (254, 240, 138, 255))
            draw = ImageDraw.Draw(bg)
            cx, cy = self.width // 2, int(self.height * 0.45)
            num_rays = 28
            for i in range(num_rays):
                if i % 2 == 0:
                    a1 = (i / num_rays) * 2 * math.pi
                    a2 = ((i + 1) / num_rays) * 2 * math.pi
                    r = self.height * 1.2
                    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
                    p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
                    draw.polygon([(cx, cy), p1, p2], fill=(239, 68, 68))
            # Halftone dots
            for dy in range(40, self.height - 40, 32):
                for dx in range(40, self.width - 40, 32):
                    if (dx + dy) % 64 == 0:
                        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(0, 0, 0, 50))
        elif "chibi" in s or "kawaii" in s or "cute" in s:
            # Sweet kawaii pastel gradient
            bg = Image.new("RGBA", (self.width, self.height), (255, 228, 230, 255))
            draw = ImageDraw.Draw(bg)
            for y in range(self.height):
                ratio = y / self.height
                r = int(255 * (1 - ratio) + 219 * ratio)
                g = int(228 * (1 - ratio) + 234 * ratio)
                b = int(230 * (1 - ratio) + 254 * ratio)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))
            # Floating stars & hearts
            for hx, hy in [(160, 220), (920, 280), (140, 720), (940, 680)]:
                draw.ellipse([hx - 22, hy - 22, hx, hy], fill=(255, 105, 180, 220))
                draw.ellipse([hx, hy - 22, hx + 22, hy], fill=(255, 105, 180, 220))
                draw.polygon([(hx - 22, hy - 11), (hx + 22, hy - 11), (hx, hy + 22)], fill=(255, 105, 180, 220))
        elif "doodle" in s or "stick" in s:
            # Lined notebook paper background
            bg = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(bg)
            # Red margin
            draw.line([(140, 0), (140, self.height)], fill=(239, 68, 68, 160), width=4)
            # Blue rules
            for y in range(80, self.height, 48):
                draw.line([(0, y), (self.width, y)], fill=(59, 130, 246, 60), width=2)
        else:
            # Default dynamic modern cartoon radial burst
            bg = Image.new("RGBA", (self.width, self.height), (15, 23, 42, 255))
            draw = ImageDraw.Draw(bg)
            cx, cy = self.width // 2, int(self.height * 0.45)
            colors = [(139, 92, 246), (236, 72, 153), (245, 158, 11), (6, 182, 212)]
            num_rays = 32
            for i in range(num_rays):
                angle1 = (i / num_rays) * 2 * math.pi
                angle2 = ((i + 0.5) / num_rays) * 2 * math.pi
                r = self.height * 1.2
                p1 = (cx + r * math.cos(angle1), cy + r * math.sin(angle1))
                p2 = (cx + r * math.cos(angle2), cy + r * math.sin(angle2))
                draw.polygon([(cx, cy), p1, p2], fill=colors[i % len(colors)])
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 70))
            bg = Image.alpha_composite(bg, overlay)

        # 2. Main Character cutout
        if character_sprite and os.path.exists(character_sprite):
            char_img = Image.open(character_sprite).convert("RGBA")
            target_h = int(self.height * 0.55)
            ratio = target_h / char_img.height
            target_w = int(char_img.width * ratio)
            char_img = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # White stroke glow behind character
            glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            char_x = (self.width - target_w) // 2
            char_y = int(self.height * 0.32)
            glow_color = (6, 182, 212, 160) if "cyber" in s else ((0, 0, 0, 160) if "noir" in s else (255, 255, 255, 130))
            glow_draw.ellipse([char_x - 30, char_y - 30, char_x + target_w + 30, char_y + target_h + 30], fill=glow_color)
            bg = Image.alpha_composite(bg, glow)
            bg.paste(char_img, (char_x, char_y), char_img)
            
        # 3. High-impact Viral Badge at top & bottom
        draw = ImageDraw.Draw(bg)
        
        # Style-Specific Top Badge
        top_font = self._get_font(40, bold=True)
        if "pixel" in s or "arcade" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(10, 10, 20), outline=(250, 204, 21), width=6)
            draw.text((self.width // 2 - 240, 115), "👾 16-BIT RETRO SHORT", fill=(250, 204, 21), font=top_font)
        elif "noir" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(15, 23, 42), outline=(220, 38, 38), width=6)
            draw.text((self.width // 2 - 240, 115), "🕵️ CASE FILE: TOP SECRET", fill=(245, 245, 245), font=top_font)
        elif "cyber" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(10, 15, 30), outline=(6, 182, 212), width=6)
            draw.text((self.width // 2 - 240, 115), "⚡ CYBERPUNK // 2088", fill=(6, 182, 212), font=top_font)
        elif "comic" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(239, 68, 68), outline=(15, 23, 42), width=8)
            draw.text((self.width // 2 - 220, 115), "💥 COMIC POP ART SHORT", fill=(255, 255, 255), font=top_font)
        elif "chibi" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(255, 105, 180), outline=(255, 255, 255), width=6)
            draw.text((self.width // 2 - 240, 115), "✨ KAWAII CHIBI TOON ✨", fill=(255, 255, 255), font=top_font)
        elif "doodle" in s:
            draw.rectangle([self.width // 2 - 280, 100, self.width // 2 + 280, 180], fill=(255, 255, 255), outline=(30, 41, 59), width=5)
            draw.text((self.width // 2 - 230, 115), "✏️ VIRAL DOODLE SKETCH", fill=(30, 41, 59), font=top_font)
        else:
            draw.rectangle([self.width // 2 - 260, 100, self.width // 2 + 260, 180], fill=(15, 23, 42), outline=(236, 72, 153), width=6)
            draw.text((self.width // 2 - 220, 115), "🔥 YOUTUBE SHORT", fill=(255, 255, 255), font=top_font)
        
        # Bottom Title Banner
        banner_y = int(self.height * 0.76)
        banner_fill = (250, 204, 21) if "pixel" in s else ((15, 23, 42) if "cyber" in s or "noir" in s else (245, 158, 11))
        banner_outline = (6, 182, 212) if "cyber" in s else ((220, 38, 38) if "noir" in s else (0, 0, 0))
        text_color = (6, 182, 212) if "cyber" in s else ((255, 255, 255) if "noir" in s else (0, 0, 0))
        
        draw.rectangle([60, banner_y, self.width - 60, banner_y + 240], fill=banner_fill, outline=banner_outline, width=10)
        
        clean_title = title.upper()
        if len(clean_title) > 28:
            clean_title = clean_title[:25] + "..."
            
        title_font = self._get_font(64, bold=True)
        draw.text((95, banner_y + 40), clean_title, fill=text_color, font=title_font)
        
        sub_font = self._get_font(44, bold=True)
        sub_color = (236, 72, 153) if "cyber" in s else ((220, 38, 38) if "noir" in s else (185, 28, 28))
        draw.text((95, banner_y + 130), "WAIT FOR THE END! 💀", fill=sub_color, font=sub_font)
        
        # 4. Final Style Post-Processing for Pixel Art & Noir
        if "pixel" in s or "16-bit" in s:
            dw, dh = self.width // 4, self.height // 4
            down = bg.resize((dw, dh), Image.Resampling.NEAREST)
            quant = down.convert("RGB").quantize(colors=32, method=Image.Quantize.MEDIANCUT).convert("RGBA")
            bg = quant.resize((self.width, self.height), Image.Resampling.NEAREST)
        elif "noir" in s:
            gray = bg.convert("L")
            from PIL import ImageOps
            bg = ImageOps.colorize(gray, black="#080a10", white="#f3f4f6").convert("RGBA")
        
        bg.convert("RGB").save(str(out_file), "JPEG", quality=95)
        return str(out_file)
