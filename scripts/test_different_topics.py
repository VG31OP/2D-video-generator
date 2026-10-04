import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apps.api.providers.llm_provider import SmartCartoonEngineLLMProvider

async def main():
    engine = SmartCartoonEngineLLMProvider()
    
    topic1 = "A cat orders 50 pizzas using a smartphone"
    topic2 = "A bodybuilder tries yoga for the first time"
    topic3 = "An astronaut finds a dancing alien on Mars"
    
    print("==================================================")
    print("TESTING DYNAMIC TOPIC GENERATION DIVERSITY")
    print("==================================================")
    
    for t in [topic1, topic2, topic3]:
        res = await engine.generate_story_and_script(t)
        title = res.get('title', '').encode('ascii', 'replace').decode('ascii')
        print(f"\n[Topic]: {t}")
        print(f"Title:   {title}")
        print(f"Hook:    {res.get('hook')}")
        chars = [f"{c['name']} ({c['role']}, {c['gender']}, Outfit: {c['outfit_color']})" for c in res.get('characters', [])]
        print(f"Chars:   {', '.join(chars)}")
        print(f"Scene 1: [{res['scenes'][0]['location']}] {res['scenes'][0]['speaker']}: \"{res['scenes'][0]['dialogue']}\"")
        print(f"Scene 2: [{res['scenes'][1]['location']}] {res['scenes'][1]['speaker']}: \"{res['scenes'][1]['dialogue']}\"")

if __name__ == "__main__":
    asyncio.run(main())
