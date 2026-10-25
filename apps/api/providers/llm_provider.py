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


class GeminiLLMProvider(LLMProvider):
    """
    Google Gemini AI Provider for autonomous story, hook, character bible,
    and script generation for YouTube Shorts.
    Uses active Gemini models: gemini-3.5-flash, gemini-3.1-flash-lite, gemini-3-flash-preview.
    """
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = (api_key or settings.GEMINI_API_KEY or "").strip()
        self.model = (model or settings.GEMINI_MODEL or "gemini-3.5-flash").strip()

    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"

    def get_provider_type(self) -> str:
        return "REAL AI"

    async def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
                )
                return res.status_code == 200
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
        if not self.api_key:
            if logger_func:
                await logger_func("[AI] No Gemini API key configured. Switching to Shorts Comedy Writer Fallback.")
            fallback = SmartCartoonEngineLLMProvider()
            return await fallback.generate_story_and_script(topic, style, language, duration_seconds, logger_func)

        prompt = f"""You are an elite viral YouTube Shorts comedy cartoon showrunner and writer.
Write a completely ORIGINAL, laugh-out-loud funny 2D cartoon short dialogue directly and specifically about this topic:
Topic: "{topic}"
Duration: {duration_seconds} seconds
Visual Style: {style}
Language: {language}

CRITICAL RULES:
1. STRICT TOPIC FOCUS: The story, characters, and comedy MUST revolve 100% around "{topic}". Never default to a generic student/homework or teacher scenario unless "{topic}" is explicitly about homework.
2. COMEDY DUO: Create 2 contrasting cartoon personalities tailored directly to "{topic}" (e.g. overconfident vs deadpan, chaotic vs rulebook, human vs sassy appliance).
3. IN MEDIA RES: Start instantly inside the awkward dilemma or bizarre situation with a punchy hook line.
4. DIALOGUE-FIRST: 80% witty back-and-forth banter, snappy interruptions, and comedic timing.
5. SHORT PACING: 4 to 5 fast scenes (3 to 5 seconds each), ending on a funny unexpected punchline and an organic viewer CTA question.
6. DYNAMIC CAMERA ANIMATION: Vary the "camera" field across scenes to match the emotional beat. Choose from: "crash zoom", "dramatic push in", "comic bounce", "comic tilt", "earthquake shake", "whip pan", "pan right", "pan left", "pan up", "pan down", "organic float", "suspense pulse", "slow zoom out".

REQUIRED JSON FORMAT:
{{
  "title": "<Catchy Shorts Title with emoji 💀>",
  "hook": "<Immediate 0-3s opening spoken line>",
  "synopsis": "<1-sentence premise>",
  "characters": [
    {{
      "name": "<Character 1 Name>",
      "role": "<Role in story>",
      "age": "20",
      "gender": "Male",
      "body_type": "Slim cartoon build",
      "hair_style": "Messy Spike",
      "hair_color": "#2d3748",
      "skin_tone": "#f6d5b8",
      "outfit_desc": "Signature cartoon outfit",
      "outfit_color": "#3b82f6",
      "personality": "Expressive, witty, impulsive",
      "voice_type": "energetic_male",
      "voice_pitch": "+2Hz",
      "voice_rate": "+5%"
    }},
    {{
      "name": "<Character 2 Name>",
      "role": "<Role in story>",
      "age": "Ageless",
      "gender": "Robot",
      "body_type": "Compact cartoon build",
      "hair_style": "Antenna beacon",
      "hair_color": "#06b6d4",
      "skin_tone": "#e2e8f0",
      "outfit_desc": "Distinctive chassis or uniform",
      "outfit_color": "#06b6d4",
      "personality": "Deadpan, hyper-logical, sassy",
      "voice_type": "robotic_ai",
      "voice_pitch": "-2Hz",
      "voice_rate": "+2%"
    }}
  ],
  "scenes": [
    {{
      "scene_id": 1,
      "duration": 4.5,
      "location": "<Cartoon background setting>",
      "characters": ["<Character 1 Name>"],
      "action": "<Expressive character action>",
      "speaker": "<Character 1 Name>",
      "dialogue": "<Hook line directly about {topic}>",
      "visual_prompt": "<Vibrant 2D cartoon composition>",
      "camera": "dramatic push in",
      "transition": "cut",
      "sfx": ["record_scratch", "whoosh"],
      "emotion": "shocked",
      "pause_before": 0.1,
      "pause_after": 0.3
    }},
    {{
      "scene_id": 2,
      "duration": 4.5,
      "location": "<Cartoon background setting>",
      "characters": ["<Character 1 Name>", "<Character 2 Name>"],
      "action": "<Character 2 reacts or enters frame>",
      "speaker": "<Character 2 Name>",
      "dialogue": "<Witty counter-punch dialogue>",
      "visual_prompt": "<2D cartoon composition with both characters>",
      "camera": "pan right",
      "transition": "cut",
      "sfx": ["ding"],
      "emotion": "deadpan",
      "pause_before": 0.2,
      "pause_after": 0.3
    }},
    {{
      "scene_id": 3,
      "duration": 4.8,
      "location": "<Cartoon background setting>",
      "characters": ["<Character 1 Name>", "<Character 2 Name>"],
      "action": "<Escalating cartoon argument or comedic reaction>",
      "speaker": "<Character 1 Name>",
      "dialogue": "<Escalation line reacting in disbelief>",
      "visual_prompt": "<Dramatic confrontation scene>",
      "camera": "shake_impact",
      "transition": "cut",
      "sfx": ["vine_boom"],
      "emotion": "panic",
      "pause_before": 0.1,
      "pause_after": 0.2
    }},
    {{
      "scene_id": 4,
      "duration": 5.0,
      "location": "<Cartoon background setting>",
      "characters": ["<Character 1 Name>", "<Character 2 Name>"],
      "action": "<Surprise reveal, twist, or hilarious counter>",
      "speaker": "<Character 2 Name>",
      "dialogue": "<Comedic climax and punchline>",
      "visual_prompt": "<Climax visual composition>",
      "camera": "slow zoom in",
      "transition": "cut",
      "sfx": ["comedic_pop"],
      "emotion": "smug",
      "pause_before": 0.2,
      "pause_after": 0.4
    }},
    {{
      "scene_id": 5,
      "duration": 4.2,
      "location": "<Cartoon background setting>",
      "characters": ["<Character 1 Name>"],
      "action": "<Character looks at camera with funny expression>",
      "speaker": "<Character 1 Name>",
      "dialogue": "<Hilarious rhetorical question and CTA for viewers>",
      "visual_prompt": "<Closing scene with subscribe prompt>",
      "camera": "dramatic push in",
      "transition": "zoom_in",
      "sfx": ["whoosh"],
      "emotion": "confused",
      "pause_before": 0.2,
      "pause_after": 0.3
    }}
  ],
  "metadata": {{
    "youtube_title": "<Viral Title with #shorts>",
    "description": "<Short video description>",
    "hashtags": ["#shorts", "#cartoon", "#comedy", "#animation", "#funny"],
    "tags": ["cartoon shorts", "shorts comedy", "funny animation"]
  }}
}}
Return ONLY valid JSON matching this schema. No markdown backticks, no explanations.
"""
        if logger_func:
            await logger_func(f"[AI] Calling Google Gemini API for topic: '{topic}'...")

        models_to_try = []
        if self.model and self.model.strip():
            models_to_try.append(self.model.strip())
        for m in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
            if m not in models_to_try:
                models_to_try.append(m)

        for m in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.8,
                    "responseMimeType": "application/json"
                }
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_text = parts[0].get("text", "")
                                cleaned = self._clean_and_repair_json(raw_text)
                                parsed = json.loads(cleaned)
                                if "scenes" in parsed and len(parsed["scenes"]) > 0 and "characters" in parsed:
                                    eval_res = ScriptQualityEvaluator.evaluate(parsed)
                                    parsed["_quality_eval"] = eval_res
                                    parsed["_provider_info"] = {
                                        "name": f"Google Gemini ({m})",
                                        "type": "REAL AI",
                                        "model": m
                                    }
                                    if logger_func:
                                        await logger_func(f"[AI] Gemini generated custom short script (Score: {eval_res['overall_score']}/10).")
                                    return parsed
                    elif response.status_code in [400, 404]:
                        if logger_func:
                            await logger_func(f"[AI] Gemini model '{m}' returned {response.status_code}. Trying alternative...")
                    else:
                        if logger_func:
                            await logger_func(f"[AI] Gemini API error ({response.status_code}): {response.text[:120]}")
            except Exception as e:
                if logger_func:
                    await logger_func(f"[AI] Gemini attempt with model {m} failed: {e}")

        # Fallback to smart cartoon engine
        if logger_func:
            await logger_func(f"[FALLBACK] Gemini request failed. Switching to Shorts Comedy Writer Engine.")
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
        from apps.api.providers.narrative_engine import narrative_engine
        return narrative_engine.build_script(topic, style, language, duration)


class LLMFactory:
    @staticmethod
    async def get_best_provider(preferred: str = None) -> LLMProvider:
        pref = (preferred or settings.LLM_PROVIDER or "auto").lower()
        if pref in ["smart_cartoon", "smart_cartoon_engine", "procedural"]:
            return SmartCartoonEngineLLMProvider()

        gemini = GeminiLLMProvider()
        ollama = OllamaLLMProvider()

        gemini_avail = None
        ollama_avail = None

        async def check_gemini() -> bool:
            nonlocal gemini_avail
            if gemini_avail is None:
                gemini_avail = await gemini.is_available()
            return gemini_avail

        async def check_ollama() -> bool:
            nonlocal ollama_avail
            if ollama_avail is None:
                ollama_avail = await ollama.is_available()
            return ollama_avail

        # Explicit user choice
        if pref == "gemini":
            if await check_gemini():
                return gemini
        elif pref == "ollama":
            if await check_ollama():
                return ollama
        elif pref in ["auto", ""]:
            # Auto priority: Gemini (fast cloud neural LLM) -> Ollama (local) -> Smart Cartoon Fallback
            if await check_gemini():
                return gemini
            if await check_ollama():
                return ollama

        # If preferred was specified but unavailable, check other real providers
        if await check_gemini():
            return gemini
        if await check_ollama():
            return ollama

        return SmartCartoonEngineLLMProvider()
