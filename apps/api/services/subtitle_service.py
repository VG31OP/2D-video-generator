import os
from pathlib import Path
from typing import List, Dict, Any

class SubtitleService:
    """
    World-Class Kinetic Motion Graphics Subtitle Engine (Advanced SubStation Alpha).
    Designed to emulate MrBeast / Hormozi / Vox high-retention social video typography:
    - Word-level spring pop bounce animation ({\\t(0,70,\\fscx118\\fscy118)\\t(70,160,\\fscx100\\fscy100)})
    - High-contrast 9px solid borders with 4px soft drop shadows
    - Contextual vibrant highlight color palette (Cyber Gold, Neon Lime, Hot Coral, Electric Cyan)
    - Instagram / TikTok / YouTube Shorts UI safe zones (MarginV = 440)
    """
    def __init__(self):
        # Color palette in ASS hex format (&H00BBGGRR&)
        self.highlight_colors = [
            "&H002BF5FF&",  # Cyber Gold / Electric Yellow
            "&H0033FF55&",  # Neon Lime
            "&H00FFFF00&",  # Electric Cyan
            "&H004444FF&",  # Hot Coral / Orange
            "&H00B026FF&"   # Vivid Magenta
        ]

    def generate_ass_subtitles(
        self,
        scenes_data: List[Dict[str, Any]],
        output_path: str,
        video_width: int = 1080,
        video_height: int = 1920
    ) -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ASS Header with Premium Kinetic Typography Styling
        # Arial Black provides thick, unmistakable punch for vertical mobile formats
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticBase,Arial Black,80,&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,9,4,2,40,40,440,1
Style: KineticPop,Arial Black,84,&H002BF5FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,108,108,1,0,1,10,5,2,40,40,440,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        cumulative_time = 0.0
        color_idx = 0
        
        for scene in scenes_data:
            words = scene.get("words", [])
            dialogue = scene.get("dialogue", "")
            scene_duration = scene.get("duration", 4.0)
            
            if not words and dialogue:
                # Procedural dynamic chunking for scenes without granular word stamps
                words_list = dialogue.split()
                chunk_size = 3
                step = scene_duration / max(1, (len(words_list) / chunk_size))
                for idx, i in enumerate(range(0, len(words_list), chunk_size)):
                    chunk = words_list[i:i+chunk_size]
                    st = cumulative_time + idx * step
                    et = min(cumulative_time + scene_duration, st + step)
                    
                    accent_color = self.highlight_colors[color_idx % len(self.highlight_colors)]
                    color_idx += 1
                    
                    # First word pops with accent color and spring scale
                    first_word = chunk[0].upper()
                    rest_words = " ".join(chunk[1:]).upper() if len(chunk) > 1 else ""
                    
                    line_text = (
                        f"{{\\t(0,70,\\fscx118\\fscy118)\\t(70,160,\\fscx100\\fscy100)\\c{accent_color}}}{first_word}"
                    )
                    if rest_words:
                        line_text += f" {{\\c&H00FFFFFF&}}{rest_words}"
                        
                    events.append(f"Dialogue: 0,{self._format_time(st)},{self._format_time(et)},KineticBase,,0,0,0,,{line_text}")
            else:
                # Granular word-level kinetic bounce tracking
                idx = 0
                while idx < len(words):
                    chunk = words[idx:idx+3]
                    if not chunk:
                        break
                    
                    st = cumulative_time + chunk[0].get("start", 0.0)
                    et = cumulative_time + chunk[-1].get("end", st + 1.2)
                    
                    accent_color = self.highlight_colors[color_idx % len(self.highlight_colors)]
                    color_idx += 1
                    
                    # Active word pops with spring scale
                    first_word = chunk[0].get("word", "").upper()
                    rest_words = " ".join([w.get("word", "").upper() for w in chunk[1:]]) if len(chunk) > 1 else ""
                    
                    line_text = (
                        f"{{\\t(0,70,\\fscx120\\fscy120)\\t(70,160,\\fscx100\\fscy100)\\c{accent_color}}}{first_word}"
                    )
                    if rest_words:
                        line_text += f" {{\\c&H00FFFFFF&}}{rest_words}"
                        
                    events.append(f"Dialogue: 0,{self._format_time(st)},{self._format_time(et)},KineticBase,,0,0,0,,{line_text}")
                    idx += 3
                    
            cumulative_time += scene_duration
            
        ass_content = header + "\n".join(events) + "\n"
        with open(str(out_file), "w", encoding="utf-8") as f:
            f.write(ass_content)
            
        return str(out_file)

    def _format_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds * 100) % 100)
        return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"
