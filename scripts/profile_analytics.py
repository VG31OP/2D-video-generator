"""
Comprehensive Instagram Profile & Content Performance Analytics for @vrj.ai
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service


def main():
    print("[+] Connecting to Instagram and fetching full profile analytics...")
    cl = instagram_service.get_client()

    # 1. Profile Information
    user_info = cl.user_info(cl.user_id)
    profile = {
        "user_id": str(user_info.pk),
        "username": user_info.username,
        "full_name": user_info.full_name,
        "is_private": user_info.is_private,
        "is_verified": getattr(user_info, "is_verified", False),
        "follower_count": getattr(user_info, "follower_count", 0),
        "following_count": getattr(user_info, "following_count", 0),
        "media_count": getattr(user_info, "media_count", 0),
        "biography": getattr(user_info, "biography", ""),
        "external_url": getattr(user_info, "external_url", ""),
        "category": getattr(user_info, "category", ""),
    }

    # 2. Fetch Media
    print(f"[+] Fetching recent media for @{profile['username']}...")
    medias = cl.user_medias(cl.user_id, amount=30)

    posts_data = []
    total_views = 0
    total_likes = 0
    total_comments = 0
    reels_with_views = 0

    for m in medias:
        code = getattr(m, "code", "")
        pk = str(getattr(m, "pk", ""))
        caption = getattr(m, "caption_text", "") or ""
        view_count = getattr(m, "view_count", 0) or getattr(m, "play_count", 0) or 0
        like_count = getattr(m, "like_count", 0) or 0
        comment_count = getattr(m, "comment_count", 0) or 0
        product_type = getattr(m, "product_type", "")
        taken_at = getattr(m, "taken_at", None)

        total_views += view_count
        total_likes += like_count
        total_comments += comment_count
        if view_count > 0:
            reels_with_views += 1

        posts_data.append({
            "id": pk,
            "code": code,
            "url": f"https://www.instagram.com/reel/{code}/" if product_type == "clips" else f"https://www.instagram.com/p/{code}/",
            "type": product_type or "post",
            "views": view_count,
            "likes": like_count,
            "comments": comment_count,
            "taken_at": taken_at.isoformat() if taken_at else "",
            "caption": caption[:120].replace("\n", " ") + ("..." if len(caption) > 120 else "")
        })

    avg_views = total_views / max(1, reels_with_views)
    avg_likes = total_likes / max(1, len(posts_data))

    # Top 5 most viewed
    top_by_views = sorted(posts_data, key=lambda x: x["views"], reverse=True)[:5]
    # Top 5 most liked
    top_by_likes = sorted(posts_data, key=lambda x: x["likes"], reverse=True)[:5]

    report = {
        "profile": profile,
        "summary": {
            "total_posts_analyzed": len(posts_data),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_engagements": total_likes + total_comments,
            "avg_views_per_active_reel": round(avg_views, 1),
            "avg_likes_per_post": round(avg_likes, 1),
        },
        "top_by_views": top_by_views,
        "top_by_likes": top_by_likes,
        "recent_posts": posts_data[:10]
    }

    output_path = ROOT_DIR / "storage" / "profile_stats.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 65)
    print(f"📊 INSTAGRAM PROFILE AUDIT & STATS: @{profile['username']}")
    print("=" * 65)
    print(f" Full Name       : {profile['full_name']}")
    print(f" Bio             : {profile['biography']}")
    print(f" Followers       : {profile['follower_count']}")
    print(f" Following       : {profile['following_count']}")
    print(f" Total Posts     : {profile['media_count']}")
    print("-" * 65)
    print(f" Total Views     : {total_views:,}")
    print(f" Total Likes     : {total_likes:,}")
    print(f" Total Comments  : {total_comments:,}")
    print(f" Avg Views/Reel  : {avg_views:.1f}")
    print(f" Avg Likes/Post  : {avg_likes:.1f}")
    print("=" * 65)
    print("\n🏆 TOP 5 PERFORMING REELS BY VIEWS:")
    for i, p in enumerate(top_by_views, 1):
        print(f" {i}. [{p['views']} views, {p['likes']} likes] {p['url']}")
        print(f"    └─ {p['caption']}")

    print("\n⏱️ 5 MOST RECENT REELS:")
    for i, p in enumerate(posts_data[:5], 1):
        print(f" {i}. [{p['views']} views, {p['likes']} likes] {p['url']}")
        print(f"    └─ {p['caption']}")
    print("=" * 65)

    return 0


if __name__ == "__main__":
    sys.exit(main())
