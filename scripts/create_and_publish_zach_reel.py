"""
Standalone CLI: Create and Publish Zack D. Films 3D Reel
Usage:
    python scripts/create_and_publish_zach_reel.py "Topic / Title"
    python scripts/create_and_publish_zach_reel.py "How Solar Panels Actually Work" --no-publish
"""

import sys
import argparse
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.pipeline import pipeline


def main():
    parser = argparse.ArgumentParser(description="Autonomous Zack D. Films 3D Reel Generator & Instagram Publisher")
    parser.add_argument("topic", help="Topic or title for the explainer short")
    parser.add_argument("--no-publish", action="store_true", help="Only render locally, do not upload to Instagram")

    args = parser.parse_args()
    publish = not args.no_publish

    print("=" * 70)
    print("       🚀 AUTONOMOUS 3D ZACK D. FILMS PIPELINE INITIATED       ")
    print(f"  Topic   : {args.topic}")
    print(f"  Publish : {'YES (@vrj.ai)' if publish else 'NO (Local Only)'}")
    print("=" * 70)

    res = pipeline.run(topic=args.topic, publish=publish)

    print("\n" + "=" * 70)
    print("                 🎉 PIPELINE COMPLETE! 🎉                 ")
    print("=" * 70)
    print(f" Video File : {res['video_path']}")
    print(f" Cover File : {res['cover_path']}")
    print(f" Duration   : {res['duration']:.2f}s")
    if res.get("published"):
        print(f" Media ID   : {res.get('media_id')}")
        print(f" Instagram  : {res.get('reel_url')}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
