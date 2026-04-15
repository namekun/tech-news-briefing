from concurrent.futures import ThreadPoolExecutor

import requests
from config import HN_TOP_STORIES_URL, HN_ITEM_URL, HN_FETCH_COUNT


def _fetch_item(story_id):
    """단일 HN 아이템을 가져온다."""
    try:
        item_resp = requests.get(HN_ITEM_URL.format(story_id), timeout=10)
        if item_resp.status_code != 200:
            return None
        data = item_resp.json()
        if not data or data.get("type") != "story":
            return None
        return {
            "source": "Hacker News",
            "title": data.get("title", ""),
            "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "description": "",
        }
    except Exception:
        return None


def fetch():
    """Hacker News API에서 상위 뉴스를 가져온다."""
    resp = requests.get(HN_TOP_STORIES_URL, timeout=15)
    resp.raise_for_status()

    story_ids = resp.json()[:HN_FETCH_COUNT]
    items = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # map은 story_ids 순서를 그대로 유지
        results = executor.map(_fetch_item, story_ids)

    items = [r for r in results if r is not None]
    return items
