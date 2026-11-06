"""
Autonomous Daily Instagram Reels Scheduler & Content Queue
Schedules and automatically publishes 3D Zack D. explainer reels at optimal hours.
Maintains a persistent topic queue and log to prevent duplicate content.
"""

import sys
import time
import json
import random
import argparse
import datetime
from pathlib import Path

# Configure Windows console encoding cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.pipeline import pipeline
from core.instagram import instagram_publisher

QUEUE_FILE = ROOT_DIR / "storage" / "content_queue.json"
HISTORY_FILE = ROOT_DIR / "storage" / "publishing_history.json"

DEFAULT_VIRAL_QUEUE = [
    {
        "topic": "What Happens If You Swallow Chewing Gum",
        "category": "Human Biology & Myths",
        "hook": "When you accidentally swallow a piece of sticky chewing gum,"
    },
    {
        "topic": "How Airplane Autopilot Actually Lands in Dense Fog",
        "category": "Aviation & Tech",
        "hook": "When an airliner touches down on a runway in zero-visibility fog,"
    },
    {
        "topic": "How Microwave Ovens Actually Heat Food",
        "category": "Everyday Physics",
        "hook": "When you heat up cold food inside a microwave oven,"
    },
    {
        "topic": "Why Lie Detectors Actually Fail",
        "category": "Forensics & Psychology",
        "hook": "When a criminal suspect is strapped to a polygraph lie detector machine,"
    },
    {
        "topic": "What Happens When You Experience Sleep Paralysis",
        "category": "Neuroscience & Sleep",
        "hook": "If you ever wake up in the middle of the night and find your body completely frozen,"
    },
    {
        "topic": "How Noise-Cancelling Headphones Silence the World",
        "category": "Acoustics & Tech",
        "hook": "When you toggle on active noise cancellation in crowded spaces,"
    },
    {
        "topic": "What Happens To Your Body at the Bottom of the Ocean",
        "category": "Deep Sea Physics",
        "hook": "If you ever dove thousands of meters beneath the ocean surface without a submarine,"
    },
    {
        "topic": "How Lightning Actually Strikes from the Ground Up",
        "category": "Meteorology & Atmospheric Physics",
        "hook": "When a thunderstorm erupts with a massive bolt of lightning across the sky,"
    },
    {
        "topic": "How Anesthesia Shuts Down Your Consciousness",
        "category": "Medical & Pharmacology",
        "hook": "When a surgeon administers general anesthesia right before an operation,"
    },
    {
        "topic": "Why You Get Brain Freeze When Eating Ice Cream Too Fast",
        "category": "Human Biology",
        "hook": "When you eat or drink something freezing cold way too fast,"
    }
]


def load_queue() -> list:
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text(json.dumps(DEFAULT_VIRAL_QUEUE, indent=2), encoding="utf-8")
        return DEFAULT_VIRAL_QUEUE
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_VIRAL_QUEUE


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def record_history(entry: dict) -> None:
    history = load_history()
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def get_next_topic() -> dict:
    queue = load_queue()
    history = load_history()
    published_topics = {h.get("topic", "").lower().strip() for h in history}

    for item in queue:
        t = item.get("topic", "").lower().strip()
        if t not in published_topics:
            return item

    # If all published, loop from beginning
    return random.choice(queue)


def execute_publish(topic_data: dict, share_story: bool = False) -> dict:
    topic = topic_data["topic"]
    print("\n" + "=" * 70)
    print(f"🚀 EXECUTING SCHEDULED 3D REEL GENERATION & PUBLISHING")
    print(f"   Topic: {topic}")
    print(f"   Category: {topic_data.get('category', 'Science')}")
    print(f"   Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    res = pipeline.run(
        topic=topic,
        publish=True,
        share_story=share_story
    )

    record_entry = {
        "topic": topic,
        "published_at": datetime.datetime.now().isoformat(),
        "media_id": res.get("media_id"),
        "reel_url": res.get("reel_url"),
        "duration": res.get("duration"),
        "file_size_mb": res.get("file_size_mb")
    }
    record_history(record_entry)
    return res


def main():
    parser = argparse.ArgumentParser(description="Autonomous Instagram Reels Content Scheduler")
    parser.add_argument("--now", action="store_true", help="Generate and publish the next topic immediately")
    parser.add_argument("--list", action="store_true", help="List upcoming content queue and publishing history")
    parser.add_argument("--add", type=str, default=None, help="Add a custom topic to the queue")
    parser.add_argument("--story", action="store_true", help="Enable story sharing during boost (default: False)")
    parser.add_argument("--daemon", action="store_true", help="Run background scheduler posting at 12:30 PM & 6:30 PM")

    args = parser.parse_args()

    if args.list:
        queue = load_queue()
        history = load_history()
        published_set = {h.get("topic", "").lower().strip() for h in history}

        print("\n" + "=" * 70)
        print("📋 CONTENT QUEUE & PUBLISHING HISTORY")
        print("=" * 70)
        print(f"Total Queue Items : {len(queue)}")
        print(f"Published Reels   : {len(history)}\n")

        print("--- UPCOMING QUEUE ---")
        for i, item in enumerate(queue):
            is_done = item["topic"].lower().strip() in published_set
            status = "✅ [Published]" if is_done else "⏳ [Pending]"
            print(f"  {i+1:02d}. {status} {item['topic']} ({item.get('category', 'Tech')})")

        if history:
            print("\n--- RECENT PUBLISHING LOG ---")
            for h in history[-5:]:
                print(f"  • {h.get('published_at', '')[:10]} | {h.get('topic')} -> {h.get('reel_url')}")
        print("=" * 70 + "\n")
        return 0

    if args.add:
        queue = load_queue()
        queue.append({
            "topic": args.add.strip(),
            "category": "User Added",
            "added_at": datetime.datetime.now().isoformat()
        })
        QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        print(f"[+] Added to queue: '{args.add}'")
        return 0

    if args.now:
        next_item = get_next_topic()
        res = execute_publish(next_item, share_story=args.story)
        print("\n" + "=" * 70)
        print(f"🎉 SCHEDULED REEL PUBLISHED SUCCESSFULLY!")
        print(f"   Reel URL : {res.get('reel_url')}")
        print(f"   Media ID : {res.get('media_id')}")
        print("=" * 70)
        return 0

    if args.daemon:
        print("\n" + "=" * 70)
        print("🕒 AUTONOMOUS DAILY SCHEDULER ACTIVE (Slots: 12:30 PM & 6:30 PM)")
        print("   Press Ctrl+C to stop.")
        print("=" * 70)
        TARGET_SLOTS = [(12, 30), (18, 30)]

        while True:
            now = datetime.datetime.now()
            today_slots = [
                now.replace(hour=h, minute=m, second=0, microsecond=0)
                for h, m in TARGET_SLOTS
            ]

            # Find next upcoming slot
            upcoming = [s for s in today_slots if s > now]
            if not upcoming:
                # Next slot is tomorrow 12:30 PM
                tomorrow = now + datetime.timedelta(days=1)
                next_slot = tomorrow.replace(hour=TARGET_SLOTS[0][0], minute=TARGET_SLOTS[0][1], second=0, microsecond=0)
            else:
                next_slot = upcoming[0]

            wait_secs = (next_slot - now).total_seconds()
            print(f"[i] Next scheduled post: {next_slot.strftime('%Y-%m-%d %I:%M %p')} (waiting {wait_secs/3600:.1f} hours)...")

            # Sleep in intervals to allow clean exit
            while (next_slot - datetime.datetime.now()).total_seconds() > 0:
                time.sleep(min(300, max(5, (next_slot - datetime.datetime.now()).total_seconds())))

            print("\n[!] Triggering scheduled publication...")
            next_topic = get_next_topic()
            try:
                execute_publish(next_topic, share_story=args.story)
            except Exception as e:
                print(f"[-] Scheduled publish error: {e}")
            time.sleep(120)

    # Default: Show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
