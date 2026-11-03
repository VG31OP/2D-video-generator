"""
In-Depth Viewers Analysis & Content Consumption Insights for @vrj.ai
"""

import sys
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from apps.api.services.instagram_service import instagram_service


def main():
    cl = instagram_service.get_client()
    user_info = cl.user_info(cl.user_id)
    medias = cl.user_medias(cl.user_id, amount=30)

    rows = []
    total_plays = 0
    total_likes = 0
    total_comments = 0

    for m in medias:
        plays = getattr(m, 'play_count', 0) or getattr(m, 'view_count', 0) or 0
        likes = getattr(m, 'like_count', 0) or 0
        comments = getattr(m, 'comment_count', 0) or 0
        caption = getattr(m, 'caption_text', '') or ''
        first_line = caption.split('\n')[0].strip() if caption else 'No title'
        code = getattr(m, 'code', '')

        total_plays += plays
        total_likes += likes
        total_comments += comments

        rows.append({
            'code': code,
            'url': f'https://www.instagram.com/reel/{code}/',
            'plays': plays,
            'likes': likes,
            'comments': comments,
            'title': first_line[:65]
        })

    print('=' * 80)
    print(f'📊 COMPREHENSIVE VIEWERS ANALYSIS — @{user_info.username}')
    print('=' * 80)
    print(f'Total Published Videos   : {len(rows)}')
    print(f'Total Organic Plays/Views: {total_plays:,}')
    print(f'Total Video Engagements  : {total_likes + total_comments} ({total_likes} likes, {total_comments} comments)')
    
    active_rows = [r for r in rows if r['plays'] > 0]
    avg_plays = total_plays / max(1, len(active_rows))
    print(f'Average Plays per Active Reel: {avg_plays:.1f}')
    print('-' * 80)
    print('INDEX | PLAYS | LIKES | COMMS | TITLE')
    print('-' * 80)
    for i, r in enumerate(rows, 1):
        print(f'{i:02d}    | {r["plays"]:5d} | {r["likes"]:5d} | {r["comments"]:5d} | {r["title"]}')
    print('=' * 80)


if __name__ == '__main__':
    main()
