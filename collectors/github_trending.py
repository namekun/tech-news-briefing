import requests
from bs4 import BeautifulSoup
from config import GITHUB_TRENDING_URL


def fetch():
    """GitHub Trending 페이지에서 프로젝트를 크롤링한다."""
    headers = {"Accept": "text/html"}
    resp = requests.get(GITHUB_TRENDING_URL, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    for article in soup.select("article.Box-row"):
        name_el = article.select_one("h2 a")
        if not name_el:
            continue

        repo_path = name_el.get("href", "").strip("/")
        title = repo_path
        url = f"https://github.com/{repo_path}"

        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # 스타 수
        star_el = article.select_one("a.Link--muted")
        stars = star_el.get_text(strip=True) if star_el else ""

        # 언어
        lang_el = article.select_one("[itemprop='programmingLanguage']")
        language = lang_el.get_text(strip=True) if lang_el else ""

        items.append({
            "source": "GitHub Trending",
            "title": title,
            "url": url,
            "description": description,
            "stars": stars,
            "language": language,
        })

    return items
