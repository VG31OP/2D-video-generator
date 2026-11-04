"""
Zack D. Films 3D Explainer Autonomous Engine
Bridges legacy provider calls directly into the new core pipeline.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from core.pipeline import pipeline as core_pipeline
from core.script_engine import ScriptEngine
from core.voice_engine import VoiceEngine
from core.scene_builder import SceneBuilder
from core.renderer import Renderer


class ZachFilmsEngine:
    def __init__(self):
        self.script_engine = ScriptEngine()
        self.voice_engine = VoiceEngine()
        self.scene_builder = SceneBuilder()
        self.renderer = Renderer()

    def generate_script(self, topic: str) -> List[str]:
        return self.script_engine.generate(topic)

    def build_and_publish(self, topic: str, custom_script: Optional[List[str]] = None) -> Dict[str, Any]:
        return core_pipeline.run(
            topic=topic,
            publish=True,
            custom_script=custom_script
        )


zach_engine = ZachFilmsEngine()
