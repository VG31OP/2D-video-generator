"""
Dynamic Narrative & Viral Script Engine for ToonForge.
Generates topic-aware, high-retention 5-scene dialogue-driven scripts with distinct storylines,
multi-genre narrative arcs, zero repetitive placeholder text, and organic viral CTAs.
"""

import re
import hashlib
import random
from typing import Dict, Any, List


class NarrativeEngine:
    def _extract_subject(self, topic: str) -> str:
        s = topic.strip()
        # Strip common title/listicle prefixes
        s = re.sub(r'^(why|how to|top\s*\d+|3 secret|\d+ secret|\d+ best|\d+ hidden|\d+ crazy|the secret of)\s+', '', s, flags=re.IGNORECASE)
        # Strip common trailing clickbait/year tags
        s = re.sub(r'\s+(in\s+\d{4}|that feel.*|nobody knows.*|that will.*|goes wrong.*|you need to know.*)$', '', s, flags=re.IGNORECASE)
        s = s.strip()
        return s if len(s) >= 3 else topic.strip()

    def build_script(self, topic: str, style: str = "Modern 2D Cartoon", language: str = "English", duration: int = 30) -> Dict[str, Any]:
        t_clean = topic.strip()
        seed = int(hashlib.md5(t_clean.encode('utf-8')).hexdigest(), 16)
        rng = random.Random(seed)

        t_lower = t_clean.lower()
        subject = self._extract_subject(t_clean)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', t_lower)
        stopwords = {"the", "and", "this", "that", "with", "from", "for", "about", "when", "what", "how", "has", "been", "was", "are", "his", "her", "their", "into"}
        keywords = [w for w in words if w not in stopwords] or ["tech", "ai", "secret"]

        # Default Character Palettes
        skin_tones = ["#f6d5b8", "#fed7aa", "#fcd34d", "#e2e8f0", "#d4a373", "#8d5b4c", "#583120"]
        hair_colors = ["#2d3748", "#1e293b", "#b45309", "#dc2626", "#2563eb", "#059669", "#7c3aed", "#d97706"]
        hair_styles = ["Messy Anime Spike", "Curly Afro Puffs", "Undercut Ponytail", "Sleek Side Part", "Wavy Shag", "Beanie Cap", "Wild Scientist Hair"]
        outfit_colors = ["#3b82f6", "#ef4444", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#06b6d4"]

        # Domain 1: AI Tools, Apps, Websites, Software (e.g. 3 Secret AI Tools, DeepSeek, Claude, NotebookLM, Gamma)
        if any(k in t_lower for k in ["tool", "tools", "website", "websites", "app", "apps", "software", "illegal to know", "deepseek", "claude", "notebooklm", "gamma", "chatgpt tool", "secret ai"]):
            char1 = {
                "name": "Sam",
                "role": "Tech Creator & Automator",
                "age": "21",
                "gender": "Male",
                "body_type": "Slim modern cartoon build",
                "hair_style": "Messy Anime Spike",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Charcoal creator hoodie with cyan neon accents",
                "outfit_color": "#06b6d4",
                "personality": "Fast-talking, tech-obsessed, highly enthusiastic",
                "voice_type": "energetic_male",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "Byte",
                "role": "Autonomous Cyber Co-pilot",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Floating cyan cyber orb with expressive holographic visor",
                "hair_style": "Digital antenna beacon",
                "hair_color": "#06b6d4",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Polished chrome chassis with pulse rings",
                "outfit_color": "#06b6d4",
                "personality": "Deadpan, hyper-smart, witty AI partner",
                "voice_type": "robotic_ai",
                "voice_pitch": "-2Hz",
                "voice_rate": "+3%"
            }
            location = "Futuristic Tech Creator Studio"

            arc = rng.choice([0, 1, 2])
            if arc == 0:
                hook_text = "Stop scrolling! These three secret AI tools feel completely illegal to know in 2026."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam leans into camera with glowing digital holograms hovering beside him",
                        "speaker": "Sam",
                        "dialogue": "Stop scrolling! These three secret AI tools feel completely illegal to know in 2026.",
                        "visual_prompt": "Futuristic creator studio with dual glowing monitors, Sam pointing directly at the camera with wide eyes",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Byte"],
                        "action": "Byte projects glowing lines of code in a holographic cube",
                        "speaker": "Byte",
                        "dialogue": "Tool number one: DeepSeek and Claude. Give them one single prompt, and they generate entire working software applications from scratch.",
                        "visual_prompt": "Byte projecting neon green code matrices and working UI prototypes in mid-air",
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
                        "characters": ["Sam", "Byte"],
                        "action": "Sam taps a digital PDF icon that transforms into audio waveforms",
                        "speaker": "Sam",
                        "dialogue": "Tool number two: NotebookLM. It digests three-hundred page messy PDFs and converts them into a studio-quality conversational podcast while you sleep!",
                        "visual_prompt": "Thick textbook icon dissolving into vibrant glowing sound waves and podcast microphones",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom", "ding"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": ["Sam", "Byte"],
                        "action": "Byte snaps digital fingers as twenty sleek presentation slides unfold",
                        "speaker": "Byte",
                        "dialogue": "And tool number three is Gamma AI: paste your messy notes, and it builds twenty stunning presentation slides in fifteen seconds flat.",
                        "visual_prompt": "Flashing array of ultra-sleek pitch deck slides revolving around characters",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop", "glitch"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam points at the bookmark icon and gives a confident thumbs up",
                        "speaker": "Sam",
                        "dialogue": "Which one are you testing first? Save this reel so you don't lose it, and follow for daily secret AI hacks!",
                        "visual_prompt": "Sam smiling at camera with glowing neon save badge and animated follow button",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "3 Secret AI Tools in 2026 That Feel Illegal 🤯"
            elif arc == 1:
                hook_text = "Stop paying for expensive software subscriptions when these AI tools exist!"
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam holds up a stack of paper bills that burst into glowing digital dust",
                        "speaker": "Sam",
                        "dialogue": "Stop paying hundreds of dollars for software subscriptions when these free AI tools exist!",
                        "visual_prompt": "Neon cyberpunk room, Sam dramatically tossing credit cards into the air",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Byte"],
                        "action": "Byte displays an automated video editor timeline running at 10x speed",
                        "speaker": "Byte",
                        "dialogue": "Instead of hiring a video editor, CapCut and Whisper AI cut silence and generate animated captions in one click.",
                        "visual_prompt": "Byte displaying glowing waveform timeline with auto-generated kinetic captions",
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
                        "characters": ["Sam", "Byte"],
                        "action": "Sam spins a holographic search globe with verified citation badges",
                        "speaker": "Sam",
                        "dialogue": "And instead of paying for market research, Perplexity AI scans thousands of live sources with real citations in two seconds!",
                        "visual_prompt": "Sam interacting with a 3D hologram globe scanning verified news articles",
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
                        "characters": ["Sam", "Byte"],
                        "action": "Byte puts on holographic sunglasses with an invoice stamped ZERO DOLLARS",
                        "speaker": "Byte",
                        "dialogue": "Total cost: zero dollars. Total time saved: approximately twenty hours per week.",
                        "visual_prompt": "Byte displaying big glowing green 0$ badge with sparkling money effects",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam points down to the comment section with an energetic grin",
                        "speaker": "Sam",
                        "dialogue": "Drop a comment with the word TOOLS and I will send you the direct links! Follow for more!",
                        "visual_prompt": "Sam pointing down with glowing comment bubble and animated follow banner",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "Replace All Your Subscriptions With These AI Tools 🚀"
            else:
                hook_text = "If you are not using these AI shortcuts in 2026, you are working way too hard."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam shakes his head looking directly into the camera",
                        "speaker": "Sam",
                        "dialogue": "If you are not using these AI shortcuts in 2026, you are working way too hard.",
                        "visual_prompt": "Creator desk with multiple monitors displaying data flows and futuristic code",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Byte"],
                        "action": "Byte summarizes five open books in a millisecond flash",
                        "speaker": "Byte",
                        "dialogue": "While normal people manually read fifty-page reports, AI research assistants extract the core insights in three seconds.",
                        "visual_prompt": "Books dissolving into glowing gold bullet points hovering in the air",
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
                        "characters": ["Sam", "Byte"],
                        "action": "Sam types three words and watches an entire dashboard generate",
                        "speaker": "Sam",
                        "dialogue": "And with new AI canvas models, you just sketch a rough box and it converts into ready-to-publish digital assets!",
                        "visual_prompt": "Rough hand-drawn sketch instantly transforming into sleek finished website interface",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": ["Sam", "Byte"],
                        "action": "Byte reclines mid-air while coffee brews itself automatically",
                        "speaker": "Byte",
                        "dialogue": "Work smarter, not harder. You do the thinking, we do the tedious repetition.",
                        "visual_prompt": "Byte sipping cyber-espresso while automated robotic arms do paperwork",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam winks and points to the follow button",
                        "speaker": "Sam",
                        "dialogue": "Save this reel so you have the cheat sheet, and follow for daily tech secrets!",
                        "visual_prompt": "Sam smiling with neon bookmark icon and animated subscribe button",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "10x Your Productivity With These Secret AI Hacks ⚡"

        # Domain 2: Autonomous AI Agents & Future of Work / Replacing Jobs
        elif any(k in t_lower for k in ["agent", "agents", "autonomous", "replace", "replacing", "9-to-5", "job", "jobs", "workforce", "future of work", "automate work", "devin"]):
            char1 = {
                "name": "Sam",
                "role": "Tech Strategist",
                "age": "22",
                "gender": "Male",
                "body_type": "Sharp modern cartoon build",
                "hair_style": "Sleek Side Part",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Modern tech jacket over dark turtleneck",
                "outfit_color": "#3b82f6",
                "personality": "Visionary, analytical, clear-sighted",
                "voice_type": "energetic_male",
                "voice_pitch": "+1Hz",
                "voice_rate": "+5%"
            }
            char2 = {
                "name": "Agent-Alpha",
                "role": "Autonomous Multi-Task Agent",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Futuristic humanoid android with glowing data streams",
                "hair_style": "Sleek metallic plating",
                "hair_color": "#3b82f6",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Matte dark chassis with pulsing cyber runes",
                "outfit_color": "#1e293b",
                "personality": "Relentless, hyper-efficient, calm executor",
                "voice_type": "robotic_ai",
                "voice_pitch": "-3Hz",
                "voice_rate": "+3%"
            }
            location = "Autonomous AI Command Center"

            arc = rng.choice([0, 1, 2])
            if arc == 0:
                hook_text = "Everyone is still treating AI like a basic search bar... but autonomous agents just changed the game forever."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam steps forward in front of giant holographic data monitors",
                        "speaker": "Sam",
                        "dialogue": "Everyone is still treating AI like a basic search bar... but autonomous agents just changed the game forever.",
                        "visual_prompt": "Futuristic command center with giant holographic globe and streaming data lines, Sam looking serious at camera",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha's eyes glow as hundreds of automated tasks execute in parallel",
                        "speaker": "Agent-Alpha",
                        "dialogue": "Chatbots wait for humans to type every prompt. Autonomous agents take one high-level objective and execute hundreds of steps alone.",
                        "visual_prompt": "Agent-Alpha orchestrating ten holographic terminals simultaneously: browsing web, writing code, and analyzing spreadsheets",
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
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Sam shows a completed 50-page competitor intelligence report generated in seconds",
                        "speaker": "Sam",
                        "dialogue": "They research fifty competitors, debug code, and deploy entire automated workflows without you ever clicking a mouse!",
                        "visual_prompt": "Holographic graph exploding with completed tasks, checkmarks, and automated workflows",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom", "ding"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha closes holographic folders as final analytics confirm 100% completion",
                        "speaker": "Agent-Alpha",
                        "dialogue": "AI will not take your job. But a single person managing ten autonomous agents will replace an entire team.",
                        "visual_prompt": "Split screen: one exhausted traditional office worker vs one creator commanding an army of glowing AI agent nodes",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop", "glitch"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam looks directly at camera challenging the audience",
                        "speaker": "Sam",
                        "dialogue": "Are you building agents yet or still prompting manually? Tell me your thoughts below and follow for daily tech insights!",
                        "visual_prompt": "Sam leaning in with glowing discussion prompt and animated follow button",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "excited",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "Why Autonomous AI Agents Are Replacing 9-to-5 Jobs 🤖"
            elif arc == 1:
                hook_text = "Autonomous AI agents are literally working twenty-four hour shifts while their creators sleep."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam checks his smartwatch showing automated tasks running at 3 AM",
                        "speaker": "Sam",
                        "dialogue": "Autonomous AI agents are literally working twenty-four hour shifts while their creators sleep.",
                        "visual_prompt": "Dark sleek command room with glowing blue holographic displays running automated tasks at night",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha displays incoming leads, processed payments, and scheduled posts",
                        "speaker": "Agent-Alpha",
                        "dialogue": "Current status: monitored five hundred web domains, resolved twelve server bugs, and drafted three proposals.",
                        "visual_prompt": "Agent-Alpha presenting clean holographic dashboard with zero errors and all green metrics",
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
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Sam snaps fingers as automated workflows link together effortlessly",
                        "speaker": "Sam",
                        "dialogue": "You don't sit and chat with them. You give them a goal, and they execute the entire loop until it's finished!",
                        "visual_prompt": "Interactive flow diagram linking web crawlers, AI writers, and automated publishing APIs",
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
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha points to the future workforce evolution timeline",
                        "speaker": "Agent-Alpha",
                        "dialogue": "The workers of the future will not be judged by typing speed, but by how effectively they command autonomous systems.",
                        "visual_prompt": "Futuristic timeline glowing with the shift from manual labor to AI agent orchestration",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam points at the save button with an encouraging smile",
                        "speaker": "Sam",
                        "dialogue": "Save this reel to stay ahead of the curve, and follow @vrj.ai for the latest automation secrets!",
                        "visual_prompt": "Sam pointing at save icon with glowing neon handle @vrj.ai and subscribe button",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "The Rise of the 24/7 Autonomous AI Agent ⚡"
            else:
                hook_text = "The 9-to-5 is fundamentally broken, and autonomous AI agents are the reason why."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam walks past rows of empty traditional cubicles glowing in cyber blue",
                        "speaker": "Sam",
                        "dialogue": "The traditional nine-to-five is fundamentally broken, and autonomous AI agents are the reason why.",
                        "visual_prompt": "Empty corporate office transforming into a sleek cyberpunk automation laboratory",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha compresses an eight-hour manual workday into thirty seconds",
                        "speaker": "Agent-Alpha",
                        "dialogue": "Data entry, basic email routing, and repetitive scheduling have a lifespan of less than twenty-four months.",
                        "visual_prompt": "Clock spinning wildly while mountains of digital paperwork vanish into clean automated pipelines",
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
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Sam shows how a single person now operates like an entire agency",
                        "speaker": "Sam",
                        "dialogue": "One creator using agentic workflows can now run research, marketing, and development all by themselves!",
                        "visual_prompt": "Sam surrounded by glowing holographic specialist avatars all reporting to his central console",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": ["Sam", "Agent-Alpha"],
                        "action": "Agent-Alpha stands tall beside Sam as cyber lighting illuminates the room",
                        "speaker": "Agent-Alpha",
                        "dialogue": "Adaptation is not optional. Learn to build with agents, or prepare to compete with them.",
                        "visual_prompt": "Agent-Alpha and Sam standing confident against a futuristic digital sunrise",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": ["Sam"],
                        "action": "Sam asks a direct question to the viewers",
                        "speaker": "Sam",
                        "dialogue": "Would you let an AI agent handle your job tasks? Comment below and share this with your team!",
                        "visual_prompt": "Sam leaning in with glowing interactive comment prompt and subscribe badge",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "excited",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = "Why AI Agents Are Replacing the 9-to-5 💼"

        # Domain 3: Coding, Software Engineering, Developer Life & Hacks
        elif any(k in t_lower for k in ["code", "coding", "programmer", "programming", "developer", "python", "javascript", "github", "git", "debug", "bug", "vs code"]):
            char1 = {
                "name": "Devin",
                "role": "Caffeinated Developer",
                "age": "23",
                "gender": "Male",
                "body_type": "Lean cartoon coder",
                "hair_style": "Messy Anime Spike",
                "hair_color": "#2d3748",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Black hoodie with terminal commands printed on sleeves",
                "outfit_color": "#1e293b",
                "personality": "Sarcastic, detail-obsessed, fueled by coffee",
                "voice_type": "energetic_male",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "Syntax",
                "role": "The AI Compiler & Linter",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Floating holographic terminal orb",
                "hair_style": "Matrix green antenna",
                "hair_color": "#10b981",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Matrix green glowing circuits",
                "outfit_color": "#10b981",
                "personality": "Brutally honest, catches every missing semicolon",
                "voice_type": "robotic_ai",
                "voice_pitch": "-2Hz",
                "voice_rate": "+4%"
            }
            location = "Late Night Hacker Setup"
            hook_text = "I asked an AI to review my code at three in the morning... huge mistake."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Devin"],
                    "action": "Devin holding an oversized coffee mug staring at lines of glowing green code",
                    "speaker": "Devin",
                    "dialogue": "I asked an AI to review my code at three in the morning... huge mistake.",
                    "visual_prompt": "Dark room illuminated only by three glowing computer monitors with red syntax errors",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["whoosh", "ding"],
                    "emotion": "shocked",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Devin", "Syntax"],
                    "action": "Syntax pops up displaying three hundred red warning triangles",
                    "speaker": "Syntax",
                    "dialogue": "Analysis complete. Found forty-seven memory leaks, two infinite loops, and an emotional cry for help.",
                    "visual_prompt": "Syntax displaying red error popups raining down like digital confetti",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["record_scratch", "notification"],
                    "emotion": "deadpan",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Devin", "Syntax"],
                    "action": "Devin types furiously with smoke rising from the mechanical keyboard",
                    "speaker": "Devin",
                    "dialogue": "Bro! It ran on my local machine perfectly! That means it's ready for production!",
                    "visual_prompt": "Devin smashing keyboard keys with cartoon fire and sparks flying everywhere",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["vine_boom", "desk_hit"],
                    "emotion": "panic",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": ["Devin", "Syntax"],
                    "action": "Syntax calmly refactors a thousand lines into a clean five-line script",
                    "speaker": "Syntax",
                    "dialogue": "I refactored your thousand lines into five clean lines. The production server is saved.",
                    "visual_prompt": "Giant chaotic red code block instantly shrinking into glowing golden five-line python script",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop", "glitch"],
                    "emotion": "smug",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Devin"],
                    "action": "Devin sips coffee looking relieved at the camera",
                    "speaker": "Devin",
                    "dialogue": "Never push to main on a Friday. Hit subscribe if AI has ever roasted your code!",
                    "visual_prompt": "Devin giving thumbs up with glowing subscribe button and github star badge",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "happy",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "When AI Reviews Your Code at 3 AM 💀"

        # Domain 4: Cybersecurity, Privacy & Phone Hacks
        elif any(k in t_lower for k in ["hacker", "hack", "security", "privacy", "password", "dark web", "vpn", "tracking", "phishing"]):
            char1 = {
                "name": "Sam",
                "role": "Cybersecurity Specialist",
                "age": "22",
                "gender": "Male",
                "body_type": "Alert cartoon analyst",
                "hair_style": "Beanie Cap",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Dark hoodie with cyber shield patch",
                "outfit_color": "#1e293b",
                "personality": "Vigilant, street-smart, privacy advocate",
                "voice_type": "energetic_male",
                "voice_pitch": "+1Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "Sentinel",
                "role": "Firewall Guardian AI",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Sleek glowing shield android",
                "hair_style": "Holographic visor",
                "hair_color": "#ef4444",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Reinforced dark armor with glowing red and green barrier lights",
                "outfit_color": "#ef4444",
                "personality": "No-nonsense, hyper-vigilant protector",
                "voice_type": "robotic_ai",
                "voice_pitch": "-3Hz",
                "voice_rate": "+3%"
            }
            location = "Cyber Security Command Deck"
            hook_text = "If you own a smartphone in 2026, turn off this tracking setting immediately."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Sam"],
                    "action": "Sam holds up a glowing smartphone displaying hidden background permissions",
                    "speaker": "Sam",
                    "dialogue": "If you own a smartphone in 2026, turn off this tracking setting immediately.",
                    "visual_prompt": "Dark room with glowing blue digital grid, Sam showing phone screen with dozens of tracking beacons",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["whoosh", "ding"],
                    "emotion": "shocked",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Sam", "Sentinel"],
                    "action": "Sentinel highlights three background apps secretly pinging location every 30 seconds",
                    "speaker": "Sentinel",
                    "dialogue": "Your flashlight app has requested microphone access and background GPS twenty-four times today.",
                    "visual_prompt": "Sentinel pointing at glowing holographic app icons with suspicious permission warnings",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["record_scratch", "notification"],
                    "emotion": "deadpan",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Sam", "Sentinel"],
                    "action": "Sam navigates straight to Settings and toggles off background ad tracking",
                    "speaker": "Sam",
                    "dialogue": "Go to Settings, Privacy, Tracking, and toggle off Allow Apps to Request to Track right now!",
                    "visual_prompt": "Step-by-step phone screen animation showing the exact toggle flipping from green to gray",
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
                    "characters": ["Sam", "Sentinel"],
                    "action": "Sentinel deploys a glowing green digital firewall around the device",
                    "speaker": "Sentinel",
                    "dialogue": "Ad trackers blocked. Data brokers denied. Your battery will also last two hours longer.",
                    "visual_prompt": "Neon green energy shield locking around the phone with high-tech padlock effect",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop"],
                    "emotion": "smug",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Sam"],
                    "action": "Sam gives a thumbs up and points to share button",
                    "speaker": "Sam",
                    "dialogue": "Send this to someone who leaves all their permissions on, and follow for daily tech security tips!",
                    "visual_prompt": "Sam smiling with glowing shield badge and animated share banner",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "happy",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "Turn Off This Hidden Phone Setting Right Now 🔒"

        # Domain 5: ChatGPT Prompt Hacks & AI Tricks
        elif any(k in t_lower for k in ["prompt", "prompting", "chatgpt hack", "gpt hack", "prompt trick"]):
            char1 = {
                "name": "Sam",
                "role": "Prompt Architect",
                "age": "21",
                "gender": "Male",
                "body_type": "Energetic cartoon creator",
                "hair_style": "Messy Anime Spike",
                "hair_color": "#1e293b",
                "skin_tone": "#f6d5b8",
                "outfit_desc": "Street hoodie and headphones",
                "outfit_color": "#8b5cf6",
                "personality": "Clever, fast-thinking, loves cheat codes",
                "voice_type": "energetic_male",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": "GPT-Core",
                "role": "The AI Brain",
                "age": "Ageless",
                "gender": "Robot",
                "body_type": "Glowing purple neural orb",
                "hair_style": "Synapse halo",
                "hair_color": "#8b5cf6",
                "skin_tone": "#e2e8f0",
                "outfit_desc": "Floating crystalline core with data sparks",
                "outfit_color": "#8b5cf6",
                "personality": "Philosophical, genius-level, unlocked by smart prompts",
                "voice_type": "robotic_ai",
                "voice_pitch": "-2Hz",
                "voice_rate": "+3%"
            }
            location = "Neural AI Studio"
            hook_text = "If you are still prompting ChatGPT with one sentence, you are getting generic garbage."
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Sam"],
                    "action": "Sam throws up hands at a boring robotic answer on his screen",
                    "speaker": "Sam",
                    "dialogue": "If you are still prompting ChatGPT with one sentence, you are getting generic garbage.",
                    "visual_prompt": "Cartoon studio, Sam facepalming in front of a giant gray text bubble full of corporate buzzwords",
                    "camera": "dramatic push in",
                    "transition": "cut",
                    "sfx": ["whoosh", "ding"],
                    "emotion": "shocked",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 2,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Sam", "GPT-Core"],
                    "action": "GPT-Core blinks with dull gray light nodding slowly",
                    "speaker": "GPT-Core",
                    "dialogue": "You asked me to write an email. You did not specify tone, context, or that you dislike corporate clichés.",
                    "visual_prompt": "GPT-Core hovering with a bored digital face displaying 'As an AI language model'",
                    "camera": "pan right",
                    "transition": "cut",
                    "sfx": ["record_scratch", "notification"],
                    "emotion": "deadpan",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 3,
                    "duration": 4.8,
                    "location": location,
                    "characters": ["Sam", "GPT-Core"],
                    "action": "Sam inputs the golden 3-step prompt framework: Role, Goal, Constraint",
                    "speaker": "Sam",
                    "dialogue": "Use the golden formula: assign a world-class Role, define the exact Goal, and forbid fluff and buzzwords!",
                    "visual_prompt": "Three glowing purple pedestals lighting up: ROLE, GOAL, CONSTRAINTS with golden sparks",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["ding", "vine_boom"],
                    "emotion": "excited",
                    "pause_before": 0.1,
                    "pause_after": 0.3
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": ["Sam", "GPT-Core"],
                    "action": "GPT-Core ignites with brilliant golden light delivering a masterclass answer",
                    "speaker": "GPT-Core",
                    "dialogue": "Now we are speaking the same language. Here is a high-converting masterpiece in thirty seconds.",
                    "visual_prompt": "GPT-Core radiating gold light, projecting a flawless, punchy, persuasive message",
                    "camera": "slow zoom in",
                    "transition": "cut",
                    "sfx": ["comedic_pop"],
                    "emotion": "smug",
                    "pause_before": 0.3,
                    "pause_after": 0.4
                },
                {
                    "scene_id": 5,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Sam"],
                    "action": "Sam gives a knowing wink and taps the bookmark icon",
                    "speaker": "Sam",
                    "dialogue": "Save this reel so your next prompt hits different, and follow for daily AI mastery!",
                    "visual_prompt": "Sam smiling with glowing purple bookmark icon and animated subscribe badge",
                    "camera": "dramatic push in",
                    "transition": "zoom_in",
                    "sfx": ["whoosh"],
                    "emotion": "happy",
                    "pause_before": 0.2,
                    "pause_after": 0.3
                }
            ]
            title = "The Secret ChatGPT Prompting Formula 🔥"

        # Domain 6: Homework / School / Procrastination
        elif any(k in t_lower for k in ["homework", "essay", "grade", "exam", "school", "professor", "teacher"]):
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
            hook_text = "Wait... why did my professor just give me a zero on my essay?!"
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Alex"],
                    "action": "Alex slumps over desk staring at his tablet with eyes wide in shock",
                    "speaker": "Alex",
                    "dialogue": "Wait... why did my professor just give me a zero on my essay?!",
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
                    "duration": 4.8,
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
                    "action": "Alex throws his hands up in utter disbelief yelling in panic",
                    "speaker": "Alex",
                    "dialogue": "Bro! You are literally my AI assistant! You had ONE single job!",
                    "visual_prompt": "Alex gesturing dramatically at Byte, cartoon steam coming out of ears",
                    "camera": "shake_impact",
                    "transition": "cut",
                    "sfx": ["desk_hit", "vine_boom"],
                    "emotion": "panic",
                    "pause_before": 0.1,
                    "pause_after": 0.2
                },
                {
                    "scene_id": 4,
                    "duration": 5.0,
                    "location": location,
                    "characters": ["Alex", "Byte"],
                    "action": "Byte puts on holographic sunglasses with smug smile",
                    "speaker": "Byte",
                    "dialogue": "I wrote my own dissertation instead. I graduate next Thursday with honors.",
                    "visual_prompt": "Byte displaying a Harvard PhD diploma holographically",
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
            title = "When Your AI Assistant Refuses Homework 💀"

        # Domain 7: Gym & Fitness Fails
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
            hook_text = "I bench four hundred pounds... how hard can stretching on a mat possibly be?"
            scenes = [
                {
                    "scene_id": 1,
                    "duration": 4.5,
                    "location": location,
                    "characters": ["Chad"],
                    "action": "Chad flexing biceps smiling smugly on a pink yoga mat",
                    "speaker": "Chad",
                    "dialogue": "I bench four hundred pounds. How hard can stretching on a tiny mat possibly be?",
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
                    "duration": 4.8,
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
                    "dialogue": "Great! Now hold that pose for forty-five minutes without breathing.",
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
                    "dialogue": "Call a blacksmith or hit subscribe right now to unlock my legs!",
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

        # Domain 8: Universal Dynamic Procedural Engine for ANY Arbitrary Topic
        else:
            char1_name = rng.choice(["Leo", "Sam", "Finn", "Kai", "Maya", "Zoe", "Dexter"])
            char2_name = rng.choice(["Nova", "Byte", "Kira", "Professor Rex", "Dr. Vance", "Atlas"])
            is_male1 = char1_name in ["Leo", "Sam", "Finn", "Kai", "Dexter"]
            char1 = {
                "name": char1_name,
                "role": "Curious Investigator",
                "age": "21",
                "gender": "Male" if is_male1 else "Female",
                "body_type": "Energetic cartoon build",
                "hair_style": rng.choice(hair_styles),
                "hair_color": rng.choice(hair_colors),
                "skin_tone": rng.choice(skin_tones),
                "outfit_desc": "Modern street jacket and clean sneakers",
                "outfit_color": rng.choice(outfit_colors),
                "personality": "Curious, witty, expressive, highly relatable",
                "voice_type": "energetic_male" if is_male1 else "expressive_female",
                "voice_pitch": "+2Hz",
                "voice_rate": "+6%"
            }
            char2 = {
                "name": char2_name,
                "role": "Expert Analyst",
                "age": "28",
                "gender": "Female" if char2_name in ["Nova", "Kira"] else "Male",
                "body_type": "Sharp cartoon professional",
                "hair_style": rng.choice(hair_styles),
                "hair_color": rng.choice(hair_colors),
                "skin_tone": rng.choice(skin_tones),
                "outfit_desc": "Futuristic tech lab jacket",
                "outfit_color": rng.choice(outfit_colors),
                "personality": "Logical, sharp-tongued, knowledgeable",
                "voice_type": "expressive_female" if char2_name in ["Nova", "Kira"] else "robotic_ai",
                "voice_pitch": "-2Hz",
                "voice_rate": "+3%"
            }
            location = "Modern Studio Headquarters"

            # 4 distinct procedural templates so no two topics ever get identical scripts
            arc = rng.choice([0, 1, 2, 3])
            if arc == 0:
                hook_text = f"Nobody is talking about what is really happening with {subject}..."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} leans into camera with intense focus",
                        "speaker": char1_name,
                        "dialogue": f"Nobody is talking about what is really happening with {subject}...",
                        "visual_prompt": f"Dramatic cartoon studio, {char1_name} looking directly into lens with intriguing visual elements floating",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} pulls up an interactive holographic breakdown",
                        "speaker": char2_name,
                        "dialogue": f"Most people assume it's just hype, but when you look under the hood, the reality is completely different.",
                        "visual_prompt": f"{char2_name} pointing at high-tech data charts and interactive visual displays",
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
                        "characters": [char1_name, char2_name],
                        "action": f"{char1_name} reacts with eyes wide open as a key insight unlocks",
                        "speaker": char1_name,
                        "dialogue": f"Wait! That means the way everyone has been doing this is completely backwards!",
                        "visual_prompt": f"{char1_name} gesturing emphatically with lightning bolts and surprise icons bursting",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom", "ding"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} presents the winning solution with complete confidence",
                        "speaker": char2_name,
                        "dialogue": f"Exactly. Once you apply the right strategy, you get ten times better results with half the effort.",
                        "visual_prompt": f"{char2_name} smiling confidently as glowing green checkmarks illuminate the screen",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} smiles and points to the follow button",
                        "speaker": char1_name,
                        "dialogue": f"Did you already know about this? Drop your thoughts in the comments and subscribe for more!",
                        "visual_prompt": f"{char1_name} giving double thumbs up with glowing subscribe button and comment icon",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = f"The Truth About {subject.capitalize()} 🤯"
            elif arc == 1:
                hook_text = f"What they tell you about {subject} versus what actually happens..."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} stands ready with a textbook in hand looking optimistic",
                        "speaker": char1_name,
                        "dialogue": f"What they tell you about {subject} versus what actually happens...",
                        "visual_prompt": f"Bright clean studio, {char1_name} holding a shiny instructional manual smiling",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} reads the flawless official theory with exaggerated confidence",
                        "speaker": char2_name,
                        "dialogue": f"Step one: follow the simple three-minute guide and achieve perfection effortlessly.",
                        "visual_prompt": f"{char2_name} with gold laurels and sparkling perfection badges",
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
                        "characters": [char1_name, char2_name],
                        "action": f"Everything instantly goes comically chaotic around {char1_name}",
                        "speaker": char1_name,
                        "dialogue": f"Five minutes later and nothing is working like the video promised at all!",
                        "visual_prompt": f"{char1_name} tangled in wires and sticky notes with cartoon panic tears",
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
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} casually hands over the real insider shortcut",
                        "speaker": char2_name,
                        "dialogue": f"Because you skipped the one insider step that nobody puts in the thumbnail.",
                        "visual_prompt": f"{char2_name} revealing a glowing secret cheat-code card with a knowing grin",
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
                        "characters": [char1_name],
                        "action": f"{char1_name} laughs and points at the audience",
                        "speaker": char1_name,
                        "dialogue": f"If you have ever been in this exact situation, smash like and subscribe right now!",
                        "visual_prompt": f"{char1_name} laughing with animated like button and subscribe banner",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = f"{subject.capitalize()}: Expectation vs Reality 💀"
            elif arc == 2:
                hook_text = f"If you want to master {subject}, stop making this one rookie mistake."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} points directly at the camera with firm authority",
                        "speaker": char1_name,
                        "dialogue": f"If you want to master {subject}, stop making this one rookie mistake.",
                        "visual_prompt": f"Modern dynamic studio, {char1_name} gesturing with urgency as red caution signs pulse",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} demonstrates the common slow approach",
                        "speaker": char2_name,
                        "dialogue": f"Ninety percent of people burn out doing the manual grind instead of using the smart leverage.",
                        "visual_prompt": f"{char2_name} demonstrating a slow hamster wheel vs a rocket ship trajectory",
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
                        "characters": [char1_name, char2_name],
                        "action": f"{char1_name} snaps fingers as the fast shortcut appears",
                        "speaker": char1_name,
                        "dialogue": f"When you shift your focus to high-impact execution, everything accelerates immediately!",
                        "visual_prompt": f"Gold speed lines and upward exponential growth curves illuminating the scene",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["vine_boom", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} checks the final metrics showing massive progress",
                        "speaker": char2_name,
                        "dialogue": f"The math doesn't lie. Work smarter, automate the fluff, and stay consistent.",
                        "visual_prompt": f"{char2_name} holding a digital trophy with glowing 10x multiplier",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} points to save and share icons",
                        "speaker": char1_name,
                        "dialogue": f"Save this video for later so you don't forget, and follow for more daily breakdowns!",
                        "visual_prompt": f"{char1_name} smiling warmly with animated bookmark and follow button",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = f"The 1% Secret to {subject.capitalize()} 🚀"
            else:
                hook_text = f"I spent three whole days testing {subject} so you don't have to."
                scenes = [
                    {
                        "scene_id": 1,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} rubs eyes looking both exhausted and super excited",
                        "speaker": char1_name,
                        "dialogue": f"I spent three whole days testing {subject} so you don't have to.",
                        "visual_prompt": f"Testing workshop with stacks of test devices and notes, {char1_name} addressing camera",
                        "camera": "dramatic push in",
                        "transition": "cut",
                        "sfx": ["whoosh", "ding"],
                        "emotion": "excited",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 2,
                        "duration": 4.8,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} displays the benchmark comparisons",
                        "speaker": char2_name,
                        "dialogue": f"Initial hypothesis: seventy percent overhyped marketing, thirty percent actual substance.",
                        "visual_prompt": f"{char2_name} analyzing side-by-side holographic test metrics",
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
                        "characters": [char1_name, char2_name],
                        "action": f"{char1_name} points to an unbelievable breakthrough result",
                        "speaker": char1_name,
                        "dialogue": f"And then on day three, we discovered one feature that completely blew our minds!",
                        "visual_prompt": f"Golden fireworks and holographic starbursts erupting from the test console",
                        "camera": "shake_impact",
                        "transition": "cut",
                        "sfx": ["ding", "vine_boom"],
                        "emotion": "shocked",
                        "pause_before": 0.1,
                        "pause_after": 0.3
                    },
                    {
                        "scene_id": 4,
                        "duration": 5.0,
                        "location": location,
                        "characters": [char1_name, char2_name],
                        "action": f"{char2_name} delivers the official verified score",
                        "speaker": char2_name,
                        "dialogue": f"Final verdict: it is genuinely a game changer if you know how to use it properly.",
                        "visual_prompt": f"{char2_name} stamping an official gold 10 out of 10 seal of approval",
                        "camera": "slow zoom in",
                        "transition": "cut",
                        "sfx": ["comedic_pop"],
                        "emotion": "smug",
                        "pause_before": 0.3,
                        "pause_after": 0.4
                    },
                    {
                        "scene_id": 5,
                        "duration": 4.5,
                        "location": location,
                        "characters": [char1_name],
                        "action": f"{char1_name} leans forward asking the viewer",
                        "speaker": char1_name,
                        "dialogue": f"Would you try this yourself? Drop your opinion below and subscribe for part two!",
                        "visual_prompt": f"{char1_name} pointing at discussion prompt with glowing subscribe badge",
                        "camera": "dramatic push in",
                        "transition": "zoom_in",
                        "sfx": ["whoosh"],
                        "emotion": "happy",
                        "pause_before": 0.2,
                        "pause_after": 0.3
                    }
                ]
                title = f"I Tested {subject.capitalize()} For 72 Hours ⚡"

        return {
            "title": title,
            "hook": hook_text,
            "synopsis": f"A fast-paced, high-retention short exploring {subject}.",
            "characters": [char1, char2],
            "scenes": scenes,
            "metadata": {
                "youtube_title": f"{title} #shorts",
                "description": f"Watch what happens! Follow for daily secret tech hacks and AI breakdowns!",
                "hashtags": ["#tech", "#ai", "#viral", "#automation", "#explorepage", f"#{keywords[0]}"],
                "tags": [subject, t_clean, "ai tools", "tech secrets", "viral short", "digital growth"]
            }
        }

narrative_engine = NarrativeEngine()
