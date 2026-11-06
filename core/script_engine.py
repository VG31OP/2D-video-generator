"""
Viral 8-Sentence Script Engine (Zack D. Films Formula)
Hook -> Misconception -> "But" Twist -> 4-Step Mechanism -> Payoff
"""

import os
import re
from typing import List, Optional


class ScriptEngine:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def generate(self, topic: str) -> List[str]:
        """
        Produces an 8-sentence viral explainer script for any topic.
        If Gemini API key is available, attempts dynamic neural writing;
        otherwise uses rich domain-specific rule templates.
        """
        clean_topic = topic.strip()

        # Try Gemini if key is provided
        if self.gemini_api_key:
            try:
                script = self._generate_with_gemini(clean_topic)
                if script and len(script) == 8:
                    return script
            except Exception:
                pass

        # Fallback to domain-specific viral template
        return self._generate_rule_based(clean_topic)

    def _generate_rule_based(self, topic: str) -> List[str]:
        t_lower = topic.lower()

        # Domain 1: Smartphones, Electronics & Gadgets
        if any(w in t_lower for w in ["phone", "screen", "oled", "touchscreen", "battery", "face id", "camera", "pixel", "charger", "wireless charging"]):
            if "oled" in t_lower or "burn" in t_lower:
                return [
                    "When you leave a static image on an OLED screen for too long,",
                    "some people assume the pixels just get tired and permanently dim.",
                    "But in reality, the organic material inside is literally decaying unevenly.",
                    "First, every single pixel on an OLED display produces its own independent light.",
                    "Subpixels made of organic molecules emit red, green, and blue light under electric current.",
                    "Blue organic subpixels degrade significantly faster than red or green ones.",
                    "When static UI elements stay on screen, those specific blue subpixels lose brightness permanently.",
                    "Leaving behind a faint ghost outline etched into the glass forever called burn-in."
                ]
            if "rice" in t_lower:
                return [
                    "When you drop your wet smartphone into a bowl of dry rice,",
                    "some people think the grains miraculously suck all the water out of the phone.",
                    "But in reality, rice does almost nothing to save your device.",
                    "First, surface tension traps water droplets deep inside the charging port and speaker mesh.",
                    "Dry rice only absorbs moisture in the immediate surrounding air at an extremely slow rate.",
                    "Meanwhile, microscopic starch dust from the rice creeps inside your open ports.",
                    "When mixed with trapped water, this starch turns into a sticky sludge that accelerates corrosion.",
                    "Which permanently fries your motherboard circuits faster than just letting it air dry."
                ]
            if any(w in t_lower for w in ["battery", "puncture", "explode"]):
                return [
                    "When a smartphone lithium-ion battery gets punctured by a sharp nail,",
                    "some people assume the liquid chemicals inside instantly catch fire like gasoline.",
                    "But in reality, what actually triggers the explosion is an internal thermal runaway.",
                    "First, a microscopic plastic separator membrane between the positive and negative layers tears open.",
                    "The cathode and anode make direct physical contact, creating a massive electrical short circuit.",
                    "Uncontrolled current surges through the battery, spiking internal temperatures past six hundred degrees.",
                    "This extreme heat instantly boils the flammable liquid electrolyte into high-pressure oxygen gas.",
                    "Causing the metal casing to violently burst into an uncontrollable blowtorch of fire."
                ]
            # General Smartphone / Gadget
            return [
                f"When you use modern technology like {topic.rstrip('?.!')},",
                "some people think the process is relatively simple and ordinary.",
                "But in reality, the underlying mechanism is completely unexpected.",
                "First, microscopic internal sensors detect user input in fractions of a millisecond.",
                "High-speed microchips convert physical interaction into digital frequency signals.",
                "Dedicated processors calculate probability algorithms to ensure absolute stability.",
                "Electromagnetic components coordinate the entire chain reaction with microsecond precision.",
                f"Until the complete payoff executes, delivering {topic.rstrip('?.!')} right before your eyes."
            ]

        # Domain 2: Satellites, Space & Physics
        elif any(w in t_lower for w in ["space", "satellite", "gps", "orbit", "starlink", "gravity", "black hole", "telescope"]):
            return [
                f"When you look at how {topic.rstrip('?.!')} operates,",
                "some people assume satellites and spacecraft are constantly being guided by humans.",
                "But in reality, the vast majority of space tech runs on pure celestial physics.",
                "First, orbital velocity balances the pull of Earth's gravity in perpetual free-fall.",
                "Microscopic ion thrusters or reaction wheels make precision adjustments without fuel.",
                "Atomic clocks onboard maintain timing accuracy down to fractions of a nanosecond.",
                "Radio frequencies travel across thousands of kilometers of vacuum at the speed of light.",
                "Allowing space systems to connect with Earth seamlessly across infinite distances."
            ]

        # Domain 2b: Aviation, Aircraft & Autoland
        elif any(w in t_lower for w in ["plane", "airplane", "autopilot", "flight", "pilot", "runway", "landing", "jet"]):
            return [
                "When an airliner touches down on a runway in zero-visibility fog,",
                "some people assume the pilots are peering through the windshield hoping for a visual.",
                "But in reality, the pilots do not even touch the flight controls during an autoland.",
                "First, the airport's Instrument Landing System beams dual radio signals through the fog.",
                "The localizer transmitter locks horizontal alignment, while the glideslope guides vertical descent.",
                "Triple-redundant onboard flight computers cross-check radio altimeters twenty times per second.",
                "At fifty feet above the asphalt, the autothrottle cuts engine thrust and gently flares the nose.",
                "Allowing the heavy landing gear to smoothly kiss the tarmac with zero human hands on the yoke."
            ]

        # Domain 3: Human Biology, Body & Medical
        elif any(w in t_lower for w in ["body", "brain", "heart", "sleep", "dream", "caffeine", "coffee", "muscle", "eye", "ear", "blood", "gum", "swallow"]):
            if "gum" in t_lower:
                return [
                    "When you accidentally swallow a piece of sticky chewing gum,",
                    "some people believe the myth that it stays trapped inside your stomach for seven whole years.",
                    "But in reality, your digestive system handles it much faster than you think.",
                    "First, your stomach acid and powerful enzymes attempt to break down the gum sugars.",
                    "However, the synthetic gum base is made of indigestible polymers that resist gastric acid.",
                    "Unable to dissolve it, your gastrointestinal tract activates involuntary muscular contractions called peristalsis.",
                    "These rhythmic waves push the wad of gum along with other digested food straight through your intestines.",
                    "Until your body safely excretes it out within a couple of days, completely unharmed."
                ]
            return [
                f"When you experience {topic.rstrip('?.!')} inside your body,",
                "some people think the sensation is caused by a simple external trigger.",
                "But in reality, your nervous system is executing a complex chemical chain reaction.",
                "First, specialized cellular receptors detect changes and send electrical impulses along nerves.",
                "Your brain releases neurotransmitters that flood through neural pathways in milliseconds.",
                "Hormones like adrenaline and dopamine surge into your bloodstream, altering your heart rate.",
                "Microscopic muscle fibers contract and relax in response to these biochemical commands.",
                "Until your body balances itself out, completely unaware of the millions of calculations that just took place."
            ]

        # Domain 4: Cybersecurity, Internet & Computing
        elif any(w in t_lower for w in ["hack", "security", "password", "vpn", "internet", "quantum", "chip", "cpu", "ai"]):
            return [
                f"When you interact with {topic.rstrip('?.!')} online,",
                "some people think digital systems work just like physical machines.",
                "But in reality, modern computing operates on abstract mathematical cryptography.",
                "First, raw data is scrambled into trillions of mathematical permutations.",
                "Microscopic transistors on silicon chips switch on and off billions of times per second.",
                "Complex encryption algorithms guarantee that only the intended recipient can read the output.",
                "Global fiber optic networks beam light pulses through glass cables under oceans.",
                "Delivering instant, secure results to your device in less time than a single blink."
            ]

        # Default Universal Viral Explainer
        else:
            clean_sub = re.sub(r'^(how|why|what happens when|can|could)\s+', '', topic, flags=re.IGNORECASE).rstrip("?.! ")
            return [
                f"When you look at how {clean_sub} actually works,",
                "some people assume the process is relatively simple and straightforward.",
                "But in reality, the underlying mechanism is completely unexpected.",
                "First, the system initiates the core interaction in a fraction of a second.",
                "Specialized components break the process down into multiple rapid stages.",
                "Precise physical forces guide each step to ensure absolute stability.",
                "High-speed signals coordinate the entire chain reaction with microsecond precision.",
                f"Until the final payoff executes, completing {clean_sub} right before your eyes."
            ]

    def _generate_with_gemini(self, topic: str) -> Optional[List[str]]:
        import json
        import httpx

        prompt = f"""Write a viral 8-sentence 3D explainer script in the signature Zack D. Films style for: "{topic}".
Structure MUST follow this EXACT 8-sentence formula:
1. Hook: Relatable everyday scenario or curious question.
2. Misconception: "Some people assume / think that..."
3. Twist: "But in reality, [shocking truth/twist]." (Dip to black occurs here)
4. Step 1: First physical/mechanical stage.
5. Step 2: Microscopic/sensor/chemical reaction.
6. Step 3: Coordinating forces or calculation.
7. Step 4: Secondary physical reaction or locking mechanism.
8. Payoff: "Until..." or "Which means..." punchline/resolution.

Return ONLY a valid JSON list of 8 strings: ["line 1", "line 2", ..., "line 8"]"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "response_mime_type": "application/json"}
        }

        with httpx.Client(timeout=10.0) as client:
            res = client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                lines = json.loads(text)
                if isinstance(lines, list) and len(lines) == 8:
                    return [str(l).strip() for l in lines]
        return None


script_engine = ScriptEngine()

