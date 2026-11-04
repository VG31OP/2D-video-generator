"""
AI Providers Package
"""

from apps.api.providers.zach_engine import zach_engine, ZachFilmsEngine
from apps.api.providers.llm_provider import LLMProvider, GeminiLLMProvider, OllamaLLMProvider, SmartCartoonEngineLLMProvider, LLMFactory
from apps.api.providers.voice_provider import VoiceProvider, EdgeTTSVoiceProvider, FallbackVoiceProvider, KokoroVoiceProvider, VoiceFactory
from apps.api.providers.sfx_provider import SFXProvider
from apps.api.providers.music_provider import MusicProvider
from apps.api.providers.system_detector import detect_system_capabilities

__all__ = [
    "zach_engine",
    "ZachFilmsEngine",
    "LLMProvider",
    "GeminiLLMProvider",
    "OllamaLLMProvider",
    "SmartCartoonEngineLLMProvider",
    "LLMFactory",
    "VoiceProvider",
    "EdgeTTSVoiceProvider",
    "FallbackVoiceProvider",
    "KokoroVoiceProvider",
    "VoiceFactory",
    "SFXProvider",
    "MusicProvider",
    "detect_system_capabilities",
]
