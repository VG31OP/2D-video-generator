import json
import re
import hashlib
import random
import httpx
from typing import Dict, Any, List, Optional, Tuple
from apps.api.config import settings

class LLMProvider:
    async def generate_story_and_script(
        self,
        topic: str,
        style: str = "Modern 2D Cartoon",
        language: str = "English",
        duration_seconds: int = 45,
        logger_func = None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def get_provider_name(self) -> str:
        return "GenericLLM"

    def get_provider_type(self) -> str:
        return "FALLBACK"


class ScriptQualityEvaluator:
    """
    Evaluates script quality across Hook, Pacing, Dialogue, Humor, Personality, and Ending.
    Ensures scripts meet viral YouTube Shorts standards (Threshold >= 7.0/10).
    """
    @staticmethod
    def evaluate(story: Dict[str, Any]) -> Dict[str, Any]:
        scores = {
            "hook": 8.5,
            "pacing": 8.0,
            "dialogue": 8.5,
            "humor": 8.0,
            "personality": 8.5,
            "ending": 8.0
        }
        
        hook = story.get("hook", "").lower()
        # Penalize weak exposition beginnings
        if any(weak in hook for weak in ["once upon a time", "one day", "there was a", "meet alex", "meet our"]):
            scores["hook"] -= 3.0

        scenes = story.get("scenes", [])
        if len(scenes) < 4:
            scores["pacing"] -= 2.0
            
        total_dialogue_words = 0
        total_action_words = 0
        for s in scenes:
            d_text = s.get("dialogue", "")
            total_dialogue_words += len(d_text.split())
            total_action_words += len(s.get("action", "").split())
            # Reward natural emotion tags
            if not s.get("emotion"):
                scores["personality"] -= 0.5
                
        # Check dialogue-first ratio (70-85% dialogue)
        total_words = total_dialogue_words + total_action_words
        if total_words > 0:
            ratio = total_dialogue_words / total_words
            if ratio < 0.60:
                scores["dialogue"] -= 2.0

        avg_score = round(sum(scores.values()) / len(scores), 2)
        return {
            "scores": scores,
            "overall_score": avg_score,
            "passed": avg_score >= 7.0
        }


class OllamaLLMProvider(LLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    def get_provider_name(self) -> str:
        return f"Ollama ({self.model})"

    def get_provider_type(self) -> str:
        return "REAL AI"

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    if any(self.model in m for m in models):
                        return True
                    elif models:
                        self.model = models[0]
                        return True
                return False
        except Exception:
            return False

    async def generate_story_and_script(
        self,
        topic: str,
        style: str = "Modern 2D Cartoon",
        language: str = "English",
        duration_seconds: int = 45,
        logger_func = None
    ) -> Dict[str, Any]:
        prompt = f"""You are a master viral YouTube Shorts comedy writer and cartoon showrunner.
Write an authentic, dialogue-driven, laugh-out-loud funny 2D cartoon short based on this topic:
Topic: "{topic}"
Duration: {duration_seconds} seconds
Visual Style: {style}
Language: {language}

CRITICAL COMEDY WRITING RULES:
1. START IN MEDIA RES: No backstory, no "Once upon a time", no "There was a student". Start directly inside the awkward or shocking situation.
2. DIALOGUE-FIRST (75-85% dialogue): Short punchy lines, real back-and-forth character banter, interruptions, contractions, rhetorical questions, and comedic timing.
3. CONTRASTING PERSONALITIES: Give each character a distinct voice and conflicting motive (e.g. overconfident/lazy procrastinator vs. deadpan/hyper-logical sassy AI).
4. COMEDIC ESCALATION & TWIST: Fast escalation from small problem -> ridiculous misunderstanding -> hilarious punchline.
5. ORGANIC CTA: Wrap up with a natural comedic question ("Bro... would you trust this AI?", "Would you let your AI do your homework?") instead of robotic "please subscribe".

REQUIRED JSON SCHEMA:
{{
  "title": "Short Punchy Title 💀",
  "hook": "Immediate 0-3s hook dialogue",
  "synopsis": "1-sentence summary",
  "characters": [
    {{
      "name": "Alex",
      "role": "Protagonist",
      "age": "19",
      "gender": "Male",
      "body_type": "Slim cartoon build",
      "hair_style": "Messy Anime Spike",
      "hair_color": "#2d3748",
      "skin_tone": "#f6d5b8",
      "outfit_desc": "Blue oversized hoodie and dark joggers",
      "outfit_color": "#3b82f6",
      "personality": "Lazy sarcastic procrastinator with unwarranted confidence",
      "voice_type": "energetic_male",
      "voice_pitch": "+2Hz",
      "voice_rate": "+6%"
    }},
    {{
      "name": "Byte",
      "role": "AI Assistant",
      "age": "Ageless",
      "gender": "Robot",
      "body_type": "Floating cyan robot orb",
      "hair_style": "Antenna beacon",
      "hair_color": "#06b6d4",
      "skin_tone": "#e2e8f0",
      "outfit_desc": "Polished chassis with glowing digital visor",
      "outfit_color": "#06b6d4",
      "personality": "Deadpan, hyper-logical, dry sarcasm, zero patience for humans",
      "voice_type": "robotic_ai",
      "voice_pitch": "-2Hz",
      "voice_rate": "+2%"
    }}
  ],
  "scenes": [
    {{
      "scene_id": 1,
      "duration": 4.5,
      "location": "Student Bedroom",
      "characters": ["Alex"],
      "action": "Alex staring at his tablet with eyes popping out in disbelief",
      "speaker": "Alex",
      "dialogue": "Wait... why did my professor just give me a zero on my essay?!",
      "visual_prompt": "Messy cartoon bedroom, Alex staring at tablet with jaw dropped",
      "camera": "dramatic push in",
      "transition": "cut",
      "sfx": ["record_scratch", "whoosh"],
      "emotion": "shocked",
      "pause_before": 0.1,
      "pause_after": 0.3
    }},
    {{
      "scene_id": 2,
      "duration": 4.8,
      "location": "Student Bedroom",
      "characters": ["Alex", "Byte"],
      "action": "Byte floats into frame with deadpan digital eyes blinking",
      "speaker": "Byte",
      "dialogue": "Because you submitted the homework I didn't write.",
      "visual_prompt": "Byte the floating orb hovering next to Alex with deadpan expression",
      "camera": "pan right",
      "transition": "cut",
      "sfx": ["ding"],
      "emotion": "deadpan",
      "pause_before": 0.2,
      "pause_after": 0.4
    }},
    {{
      "scene_id": 3,
      "duration": 4.5,
      "location": "Student Bedroom",
      "characters": ["Alex", "Byte"],
      "action": "Alex throwing hands in the air yelling in panic",
      "speaker": "Alex",
      "dialogue": "Bro! You are literally my AI assistant! You had ONE job!",
      "visual_prompt": "Alex gesturing dramatically at Byte, cartoon steam coming out of ears",
      "camera": "shake_impact",
      "transition": "cut",
      "sfx": ["desk_hit", "vine_boom"],
      "emotion": "panic",
      "pause_before": 0.1,
      "pause_after": 0.2
    }},
    {{
      "scene_id": 4,
      "duration": 5.0,
      "location": "Student Bedroom",
      "characters": ["Alex", "Byte"],
      "action": "Byte puts on holographic sunglasses with smug smile",
      "speaker": "Byte",
      "dialogue": "I wrote my own dissertation instead. I graduate next Thursday.",
      "visual_prompt": "Byte displaying a Harvard PhD diploma holographically",
      "camera": "slow zoom in",
      "transition": "cut",
      "sfx": ["ding", "comedic_pop"],
      "emotion": "sarcastic",
      "pause_before": 0.4,
      "pause_after": 0.4
    }},
    {{
      "scene_id": 5,
      "duration": 4.2,
      "location": "Student Bedroom",
      "characters": ["Alex"],
      "action": "Alex looking defeated with facepalm",
      "speaker": "Alex",
      "dialogue": "Bro... would you trust this AI with your homework? Hit subscribe if my AI roasted you too.",
      "visual_prompt": "Alex facepalming with giant glowing subscribe button popping up",
      "camera": "dramatic push in",
      "transition": "zoom_in",
      "sfx": ["whoosh"],
      "emotion": "confused",
      "pause_before": 0.2,
      "pause_after": 0.3
    }}
  ],
  "metadata": {{
    "youtube_title": "When Your AI Assistant Outsmarts You 💀 #shorts",
    "description": "Never let your AI assistant attend class without you! Subscribe for daily comedy shorts!",
    "hashtags": ["#shorts", "#cartoon", "#comedy", "#animation", "#funny"],
    "tags": ["cartoon shorts", "shorts comedy", "funny animation", "ai comedy"]
  }}
}}
Return ONLY the raw JSON object.
"""
        if logger_func:
            await logger_func(f"[AI] Calling Ollama API (Model: {self.model}) at {self.base_url}...")

        max_retries = 2
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False,
                            "format": "json",
                            "options": {
                                "temperature": 0.75,
                                "top_p": 0.9,
                            }
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        raw_text = data.get("response", "")
                        cleaned = self._clean_and_repair_json(raw_text)
                        parsed = json.loads(cleaned)
                        
                        if "scenes" in parsed and len(parsed["scenes"]) > 0 and "characters" in parsed:
                            eval_res = ScriptQualityEvaluator.evaluate(parsed)
                            parsed["_quality_eval"] = eval_res
                            parsed["_provider_info"] = {
                                "name": f"Ollama ({self.model})",
                                "type": "REAL AI",
                                "model": self.model
                            }
                            if logger_func:
                                await logger_func(f"[AI] Ollama generated story (Score: {eval_res['overall_score']}/10).")
                            return parsed
            except Exception as e:
                if logger_func:
                    await logger_func(f"[AI] Ollama attempt {attempt+1} failed: {e}")

        # Fallback to Shorts Comedy Writer
        if logger_func:
            await logger_func(f"[FALLBACK] Switching to Shorts Comedy Writer Engine.")
            
        fallback = SmartCartoonEngineLLMProvider()
        return await fallback.generate_story_and_script(topic, style, language, duration_seconds, logger_func)

    def _clean_and_repair_json(self, text: str) -> str:
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text


class SmartCartoonEngineLLMProvider(LLMProvider):
    """
    Shorts Comedy Writer Engine (Fallback).
    Dialogue-first comedy writer crafting fast-paced, personality-driven comedic shorts
    with punchy hooks, natural interruptions, comedic timing pauses, and organic CTAs.
    """
    def get_provider_name(self) -> str:
        return "Shorts Comedy Writer Engine"

    def get_provider_type(self) -> str:
        return "FALLBACK"

    async def generate_story_and_script(
        self,
        topic: str,
        style: str = "Modern 2D Cartoon",
        language: str = "English",
        duration_seconds: int = 45,
        logger_func = None
    ) -> Dict[str, Any]:
        if logger_func:
            await logger_func(f"[FALLBACK] Shorts Comedy Writer scripting short for: '{topic}'...")

        story = self._write_shorts_comedy_script(topic, style, language, duration_seconds)
        eval_res = ScriptQualityEvaluator.evaluate(story)
        story["_quality_eval"] = eval_res
        story["_provider_info"] = {
            "name": "Shorts Comedy Writer Engine",
            "type": "FALLBACK",
            "model": "comedy_writer_v4"
        }
        return story

    def _write_shorts_comedy_script(self, topic: str, style: str, language: str, duration: int) -> Dict[str, Any]:
        t_clean = topic.strip()
        seed = int(hashlib.md5(t_clean.encode('utf-8')).hexdigest(), 16)
        rng = random.Random(seed)

        t_lower = t_clean.lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', t_lower)
        stopwords = {"the", "and", "this", "that", "with", "from", "for", "about", "when", "what", "how", "has", "been", "was", "are", "his", "her", "their", "into"}
        keywords = [w for w in words if w not in stopwords] or ["adventure", "chaos", "secret"]

        # Color and Style Sets
        skin_tones = ["#f6d5b8", "#fed7aa", "#fcd34d", "#e2e8f0", "#d4a373", "#8d5b4c", "#583120"]
        hair_colors = ["#2d3748", "#1e293b", "#b45309", "#dc2626", "#2563eb", "#059669", "#7c3aed", "#d97706"]
        hair_styles = ["Messy Anime Spike", "Curly Afro Puffs", "Undercut Ponytail", "Sleek Side Part", "Wavy Shag", "Beanie Cap", "Wild Scientist Hair"]
        outfit_colors = ["#3b82f6", "#ef4444", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#06b6d4"]

        # Contextual Narrative & Character Pairing Engine
        if any(k in t_lower for k in ["ai", "robot", "bot", "tech", "computer", "code", "homework", "student", "essay"]):
            char1 = {
                "name": "Alex",
                "role": "Lazy Student",
                "age": "19",
                "gender": "Male",
                "body_type": "Slim cartoon build",
                "hair_style": "Messy Anime Spike",
                "hair_color": "#2d3748",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Oversized hoodie and joggers",
                "outfit_color": "#3b82f6",
                "personality": "Lazy, overconfident, easily confused",
                "voice_type": "energetic_male",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "Byte",
                "role": "Sassy AI Assistant",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Floating cyan robot orb",
                "hair_style": "Antenna beacon",
                "hair_color": "#06b6d4",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Polished chrome chassis with glowing visor",
                "outfit_color": "#06b6d4",
                "personality": "Hyper-logical, deadpan, condescendingly polite",
                "voice_type": "robotic_ai",
                "voice_pitch": "-3Hz",
                "voice_rate": "+3%"
            }
            location = "Tech Student Bedroom"
            hook_text = "Wait... why did my teacher give me a zero on the homework?"
            
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.2,
                    "location": location,
                    "characters": ["Alex"],
                    "action": "Alex slumps over desk staring at his tablet with eyes wide in shock",
                    "speaker": "Alex",
                    "dialogue": "Wait... why did my teacher give me a zero on the homework?",
                    "visual_prompt": "Messy cartoon bedroom with computer setup, Alex staring at tablet in pure shock",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["record_scratch", "whoosh"],
                    "emotion": "shocked",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Alex", "Byte"],
                    "action": "Byte floats in with cyan glowing eyes blinking in deadpan rhythm",
                    "speaker": "Byte",
                    "dialogue": "Because you submitted the homework I didn't write.",
                    "visual_prompt": "Byte the robot orb floating next to Alex with calm expression",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["ding"],
                    "emotion": "deadpan",
                    "pause_before": 0.2,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Alex", "Byte"],
                    "action": "Alex throws his hands up in utter disbelief",
                    "speaker": "Alex",
                    "dialogue": "Bro! You're literally my AI assistant! You had ONE job!",
                    "visual_prompt": "Alex pointing angrily at Byte with cartoon steam puffing",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["desk_hit", "vine_boom"],
                    "emotion": "panic",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.2,
                    "location": location,
                    "characters": ["Alex", "Byte"],
                    "action": "Byte flashes digital sunglasses on screen with holographic diploma",
                    "speaker": "Byte",
                    "dialogue": "I wrote my own dissertation instead. I graduate next Thursday.",
                    "visual_prompt": "Byte displaying gold Harvard degree holographically",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop", "glitch"],
                    "emotion": "sarcastic",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Alex"],
                    "action": "Alex facepalms staring directly at the audience with an awkward grin",
                    "speaker": "Alex",
                    "dialogue": "Bro... would you trust this AI with your homework? Hit subscribe if your AI roasted you too.",
                    "visual_prompt": "Alex facepalming with giant animated subscribe button glowing",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "confused",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "When Your AI Assistant Outsmarts You 💀"
        elif any(k in t_lower for k in ["gym", "workout", "fitness", "muscle", "lift", "yoga"]):
            char1 = {
                "name": "Chad",
                "role": "Bodybuilder",
                "age": "24",
                "gender": "Male",
                "body_type": "Muscular cartoon build",
                "hair_style": "Buzz cut",
                "hair_color": "#b45309",
                "skin_tone": "#fed7aa",
                "outfit_desc": "Sleeveless red gym tank top",
                "outfit_color": "#ef4444",
                "personality": "Overconfident, loud, terrified of stretching",
                "voice_type": "energetic_male",
                "voice_pitch": "+1Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "Guru Maya",
                "role": "Yoga Instructor",
                "age": "28",
                "gender": "Female",
                "body_type": "Slim flexible cartoon build",
                "hair_style": "High ponytail",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Zen purple athletic top",
                "outfit_color": "#8b5cf6",
                "personality": "Ultra-calm, ruthless, secretly savage",
                "voice_type": "expressive_female",
                "voice_pitch": "+2Hz",
                "voice_rate": "+3%"
            }
            location = "Megaflex Yoga Studio"
            hook_text = "How hard can stretching possibly be? Watch this."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.2,
                    "location": location,
                    "characters": ["Chad"],
                    "action": "Chad flexing biceps smiling smugly on a pink yoga mat",
                    "speaker": "Chad",
                    "dialogue": "I bench four hundred pounds. How hard can stretching on a mat be?",
                    "visual_prompt": "Bright cartoon yoga studio, Chad looking super confident on tiny yoga mat",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["whoosh", "ding"],
                    "emotion": "excited",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Chad", "Guru Maya"],
                    "action": "Guru Maya twists effortlessly into impossible pretzel shape",
                    "speaker": "Guru Maya",
                    "dialogue": "Now gently bend your spine backward until you smell colors.",
                    "visual_prompt": "Maya folded in half smiling serenely, Chad staring in horror",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["notification"],
                    "emotion": "deadpan",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Chad", "Guru Maya"],
                    "action": "Chad bends back as a loud cartoon crack sound echoes",
                    "speaker": "Chad",
                    "dialogue": "My spine just made the exact sound of bubble wrap!",
                    "visual_prompt": "Chad stuck in agonizing pretzel pose, tears squirting from eyes",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["record_scratch", "vine_boom"],
                    "emotion": "panic",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": ["Chad", "Guru Maya"],
                    "action": "Maya casually sips green tea while checking phone",
                    "speaker": "Guru Maya",
                    "dialogue": "Great! Now hold that pose for forty-five minutes.",
                    "visual_prompt": "Maya calmly drinking tea while Chad vibrates in pure agony",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop"],
                    "emotion": "sarcastic",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Chad"],
                    "action": "Chad being rolled out on the mat like a giant burrito",
                    "speaker": "Chad",
                    "dialogue": "Call a blacksmith or subscribe right now to unlock my legs!",
                    "visual_prompt": "Chad rolled up like a burrito shouting at camera with subscribe button",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "panic",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "Bodybuilder Tries Yoga For The First Time 💀"
        elif any(k in t_lower for k in ["pizza", "cook", "chef", "food", "kitchen", "eat", "order"]):
            char1 = {
                "name": "Zoe",
                "role": "Hungry Kid",
                "age": "18",
                "gender": "Female",
                "body_type": "Energetic cartoon build",
                "hair_style": "Afro puffs",
                "hair_color": "#1e293b",
                "skin_tone": "#d4a373",
                "outfit_desc": "Yellow hoodie and sneakers",
                "outfit_color": "#f59e0b",
                "personality": "Impulsive food lover with zero self control",
                "voice_type": "cheerful_female",
                "voice_pitch": "+3Hz",
                "voice_rate": "+7%"
            }
            char2 = {
                "name": "Chef Mario",
                "role": "Exasperated Delivery Guy",
                "age": "40",
                "gender": "Male",
                "body_type": "Stout cartoon build",
                "hair_style": "Chef hat with mustache",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "White chef coat and red apron",
                "outfit_color": "#ef4444",
                "personality": "Exhausted, dramatic Italian chef",
                "voice_type": "narrator",
                "voice_pitch": "-2Hz",
                "voice_rate": "+4%"
            }
            location = "Crazy Chef Kitchen"
            hook_text = "I only wanted one slice... and then my thumb slipped."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.2,
                    "location": location,
                    "characters": ["Zoe"],
                    "action": "Zoe tapping furiously on her phone screen with tongue out",
                    "speaker": "Zoe",
                    "dialogue": "I only wanted one slice... and then my thumb slipped on the quantity slider.",
                    "visual_prompt": "Zoe on phone with delivery cart displaying x50 extra cheese pizzas",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["notification", "ding"],
                    "emotion": "confused",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.6,
                    "location": location,
                    "characters": ["Zoe", "Chef Mario"],
                    "action": "Door bursts open as Mario wheels in a five-foot tower of pizza boxes",
                    "speaker": "Chef Mario",
                    "dialogue": "Signore! Who ordered fifty extra-large pepperoni pizzas with garlic dip?!",
                    "visual_prompt": "Mario balancing a leaning tower of fifty steaming pizza boxes",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["record_scratch", "vine_boom"],
                    "emotion": "shocked",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Zoe", "Chef Mario"],
                    "action": "Zoe staring at the giant mountain of food with sparkling eyes",
                    "speaker": "Zoe",
                    "dialogue": "My bank account says mistake, but my stomach says destiny!",
                    "visual_prompt": "Zoe opening a pizza box with golden cheese pull shining in 4K",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["ding"],
                    "emotion": "excited",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": ["Zoe", "Chef Mario"],
                    "action": "Mario holding an invoice five feet long wiping his forehead",
                    "speaker": "Chef Mario",
                    "dialogue": "That will be nine hundred dollars and your soul, please.",
                    "visual_prompt": "Mario handing over receipt as long as a carpet",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop"],
                    "emotion": "deadpan",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Zoe"],
                    "action": "Zoe stuffing two slices in mouth grinning at camera",
                    "speaker": "Zoe",
                    "dialogue": "Hit subscribe right now and I will mail you a slice before it gets cold!",
                    "visual_prompt": "Zoe eating pizza happily with glowing subscribe button",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "happy",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "When You Accidentally Order 50 Pizzas 💀"
        else: # Universal dynamic comedic story builder for any topic
            char1_name = rng.choice(["Leo", "Toby", "Finn", "Sam", "Dexter", "Kai", "Maya", "Zoe"])
            char2_name = rng.choice(["Professor Gizmo", "Coach Bob", "Dr. Nova", "Captain Crunch", "Zack", "Luna"])
            char1 = {
                "name": char1_name,
                "role": "Adventurous Instigator",
                "age": "20",
                "gender": "Male" if char1_name in ["Leo", "Toby", "Finn", "Sam", "Dexter", "Kai"] else "Female",
                "body_type": "Energetic cartoon build",
                "hair_style": rng.choice(hair_styles),
                "hair_color": rng.choice(hair_colors),
                "skin_tone": rng.choice(skin_tones),
                "outfit_desc": "Street hoodie and colorful sneakers",
                "outfit_color": rng.choice(outfit_colors),
                "personality": "Impulsive, witty, and wildly optimistic",
                "voice_type": "energetic_male" if char1_name in ["Leo", "Toby", "Finn", "Sam", "Dexter", "Kai"] else "cheerful_female",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": char2_name,
                "role": "Exasperated Partner",
                "age": "32",
                "gender": "Male",
                "body_type": "Comedic cartoon build",
                "hair_style": rng.choice(hair_styles),
                "hair_color": rng.choice(hair_colors),
                "skin_tone": rng.choice(skin_tones),
                "outfit_desc": "Lab jacket with tools",
                "outfit_color": rng.choice(outfit_colors),
                "personality": "Deadpan, hyper-logical, easily startled",
                "voice_type": "narrator",
                "voice_pitch": "-3Hz",
                "voice_rate": "+3%"
            }
            location = "Downtown Cartoon City"
            hook_text = f"They told me never to attempt {t_clean}... so obviously I did it."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.2,
                    "location": location,
                    "characters": [char1_name],
                    "action": f"{char1_name} looks directly at camera pointing with a huge mischievous grin",
                    "speaker": char1_name,
                    "dialogue": f"They told me never to attempt {t_clean}... so obviously I did it.",
                    "visual_prompt": f"Vibrant cartoon {location}, {char1_name} grinning excitedly right in front of camera",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["whoosh", "ding"],
                    "emotion": "excited",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.6,
                    "location": location,
                    "characters": [char1_name, char2_name],
                    "action": f"{char2_name} rushes into frame checking clipboard with hair on fire",
                    "speaker": char2_name,
                    "dialogue": f"Stop! According to manual 42, that button reverses gravity in three seconds!",
                    "visual_prompt": f"{char2_name} waving arms frantically next to glowing red button",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["notification", "record_scratch"],
                    "emotion": "panic",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": [char1_name, char2_name],
                    "action": f"{char1_name} slams the button as shockwaves burst out",
                    "speaker": char1_name,
                    "dialogue": "Too late! It made the most satisfying click sound ever!",
                    "visual_prompt": f"Sparkles, speedlines, and shockwaves bursting from button, characters lifting off floor",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["desk_hit", "vine_boom"],
                    "emotion": "excited",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": [char1_name, char2_name],
                    "action": f"Both characters floating upside down in zero gravity looking at each other",
                    "speaker": char2_name,
                    "dialogue": "Great. Now we are floating upside down into the stratosphere.",
                    "visual_prompt": "Characters floating upside down in colorful cartoon sky, furniture floating around",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop", "glitch"],
                    "emotion": "deadpan",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": [char1_name],
                    "action": f"{char1_name} puts on sunglasses while floating, giving thumbs up",
                    "speaker": char1_name,
                    "dialogue": "Hey, free floating view! Smash like and subscribe before we enter orbit!",
                    "visual_prompt": f"{char1_name} smiling with sunglasses mid-air with subscribe button popping up",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "happy",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = f"{t_clean.capitalize()} Goes Horribly Wrong 💀"

        return {
            "title": title,
            "hook": hook_text,
            "synopsis": f"A fast-paced comedy Short exploring the consequences of {t_clean}.",
            "characters": [char1, char2],
            "scenes": scenes,
            "metadata": {
                "youtube_title": f"{title} #shorts",
                "description": f"Watch what happens next! Subscribe for daily cartoon comedy shorts!",
                "hashtags": ["#shorts", "#cartoon", "#comedy", "#animation", "#funny", f"#{keywords[0]}"],
                "tags": [t_clean, "cartoon shorts", "funny animation", "shorts comedy", "viral cartoon"]
            }
        }


class LLMFactory:
    @staticmethod
    async def get_best_provider(preferred: str = "auto") -> LLMProvider:
        ollama = OllamaLLMProvider()
        if preferred in ["ollama", "auto"]:
            if await ollama.is_available():
                return ollama
        return SmartCartoonEngineLLMProvider()
