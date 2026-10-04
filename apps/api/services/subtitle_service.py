import os
from pathlib import Path
from typing import List, Dict, Any

class SubtitleService:
    """
    Generates YouTube Shorts style ASS (Advanced SubStation Alpha) subtitles
    with word-level bounce/color highlight, high-contrast outlines, and safe zones.
    """
    def generate_ass_subtitles(self, scenes_data: List[Dict[str, Any]], output_path: str, video_width: int = 1080, video_height: int = 1920) -> str:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        # ASS Header with YouTube Shorts Styling
        # MarginV = 380 places text in upper-middle bottom area, safe from YouTube UI overlays
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsDefault,Arial,72,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,420,1
Style: ShortsHighlight,Arial,76,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,105,105,0,0,1,10,6,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        cumulative_time = 0.0
        
        for scene in scenes_data:
            words = scene.get("words", [])
            dialogue = scene.get("dialogue", "")
            scene_duration = scene.get("duration", 4.0)
            
            if not words and dialogue:
                # Approximate 3-word chunks
                words_list = dialogue.split()
                chunk_size = 3
                step = scene_duration / max(1, (len(words_list) / chunk_size))
                for idx, i in enumerate(range(0, len(words_list), chunk_size)):
                    chunk = " ".join(words_list[i:i+chunk_size])
                    st = cumulative_time + idx * step
                    et = min(cumulative_time + scene_duration, st + step)
                    events.append(f"Dialogue: 0,{self._format_time(st)},{self._format_time(et)},ShortsDefault,,0,0,0,,{chunk.upper()}")
            else:
                # Group words into 2-4 word phrases for punchy Shorts reading
                idx = 0
                while idx < len(words):
                    chunk = words[idx:idx+3]
                    if not chunk:
                        break
                    st = cumulative_time + chunk[0]["start"]
                    et = cumulative_time + chunk[-1]["end"]
                    
                    # Highlight active word with animated color tag
                    phrase_text = " ".join([w["word"] for w in chunk]).upper()
                    events.append(f"Dialogue: 0,{self._format_time(st)},{self._format_time(et)},ShortsHighlight,,0,0,0,,{{\\c&H00FFFF&}}{phrase_text}")
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
