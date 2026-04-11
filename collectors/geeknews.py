import requests
from bs4 import BeautifulSoup
from config import GEEKNEWS_URL


def fetch():
    """GeekNews 메인 페이지에서 뉴스 항목을 크롤링한다."""
    resp = requests.get(GEEKNEWS_URL, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for topic in soup.select(".topic_row"):
        link_el = topic.select_one(".topictitle a")
        if not link_el:
            continue

        title = link_el.get_text(strip=True)
        url = link_el.get("href", "")

        # 상대 경로인 경우 절대 경로로 변환
        if not url.startswith("http"):
            url = GEEKNEWS_URL + "/" + url.lstrip("/")

        desc_el = topic.select_one(".topicdesc")
        description = desc_el.get_text(strip=True) if desc_el else ""

        items.append({
            "source": "GeekNews",
            "title": title,
            "url": url,
            "description": description,
        })

    return items
