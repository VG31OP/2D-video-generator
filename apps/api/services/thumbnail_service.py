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

    def generate_thumbnail(self, title: str, character_sprite: str, output_path: str) -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. Background with radial anime burst
        bg = Image.new("RGBA", (self.width, self.height), (15, 23, 42, 255))
        draw = ImageDraw.Draw(bg)
        
        # Draw radial sunburst lines
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
            
        # Dark vignette overlay
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
            glow_draw.ellipse([char_x - 30, char_y - 30, char_x + target_w + 30, char_y + target_h + 30], fill=(255, 255, 255, 120))
            bg = Image.alpha_composite(bg, glow)
            
            bg.paste(char_img, (char_x, char_y), char_img)
            
        # 3. High-impact Viral Badge at top & bottom
        draw = ImageDraw.Draw(bg)
        
        # Top Badge: "TOONFORGE ORIGINAL"
        top_font = self._get_font(42, bold=True)
        draw.rectangle([self.width // 2 - 260, 100, self.width // 2 + 260, 180], fill=(15, 23, 42), outline=(236, 72, 153), width=6)
        draw.text((self.width // 2 - 220, 115), "🔥 YOUTUBE SHORT", fill=(255, 255, 255), font=top_font)
        
        # Bottom Title Banner
        banner_y = int(self.height * 0.76)
        draw.rectangle([60, banner_y, self.width - 60, banner_y + 240], fill=(245, 158, 11), outline=(0, 0, 0), width=10)
        
        # Bold Shortened Title Text
        clean_title = title.upper()
        if len(clean_title) > 28:
            clean_title = clean_title[:25] + "..."
            
        title_font = self._get_font(64, bold=True)
        draw.text((95, banner_y + 40), clean_title, fill=(0, 0, 0), font=title_font)
        
        sub_font = self._get_font(44, bold=True)
        draw.text((95, banner_y + 130), "WAIT FOR THE END! 💀", fill=(185, 28, 28), font=sub_font)
        
        bg.convert("RGB").save(str(out_file), "JPEG", quality=95)
        return str(out_file)
