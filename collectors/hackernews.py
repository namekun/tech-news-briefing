import requests
from config import HN_TOP_STORIES_URL, HN_ITEM_URL, HN_FETCH_COUNT


def fetch():
    """Hacker News API에서 상위 뉴스를 가져온다."""
    resp = requests.get(HN_TOP_STORIES_URL, timeout=15)
    resp.raise_for_status()

    story_ids = resp.json()[:HN_FETCH_COUNT]
    items = []

    for story_id in story_ids:
        item_resp = requests.get(HN_ITEM_URL.format(story_id), timeout=10)
        if item_resp.status_code != 200:
            continue

        data = item_resp.json()
        if not data or data.get("type") != "story":
            continue

        title = data.get("title", "")
        url = data.get("url", f"https://news.ycombinator.com/item?id={story_id}")

        items.append({
            "source": "Hacker News",
            "title": title,
            "url": url,
            "description": "",
        })

    return items
