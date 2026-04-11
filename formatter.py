from datetime import datetime
from config import OUTPUT_DIR


def format_briefing(items):
    """요약된 항목들을 마크다운 브리핑으로 포맷한다."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"# 🗞️ 테크 뉴스 브리핑 - {today}\n"]

    # 소스별 분류
    by_source = {}
    for item in items:
        source = item["source"]
        by_source.setdefault(source, []).append(item)

    # GeekNews, Hacker News 섹션
    for source in ["GeekNews", "Hacker News"]:
        source_items = by_source.get(source, [])
        if not source_items:
            continue

        lines.append(f"\n## {source}\n")
        for item in source_items:
            rel = item.get("relevance", "💡")
            summary = item.get("summary", "")
            lines.append(f"- {rel} **{item['title']}**")
            lines.append(f"  {summary}")
            lines.append(f"  <{item['url']}>")

    # GitHub Trending 섹션
    gh_items = by_source.get("GitHub Trending", [])
    if gh_items:
        lines.append("\n## 🔥 Hot OSS Today (GitHub Trending)\n")
        for item in gh_items:
            rel = item.get("relevance", "💡")
            summary = item.get("summary", "")
            stars = item.get("stars", "")
            lang = item.get("language", "")

            meta_parts = []
            if stars:
                meta_parts.append(f"⭐{stars}")
            if lang:
                meta_parts.append(lang)
            meta = " · ".join(meta_parts)

            title_line = f"- {rel} **{item['title']}**"
            if meta:
                title_line += f" ({meta})"
            lines.append(title_line)
            lines.append(f"  {summary}")
            lines.append(f"  <{item['url']}>")

    # 푸터
    now = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    lines.append(f"\n---\n*Generated at {now}*\n")

    return "\n".join(lines)


def save_briefing(content):
    """브리핑을 파일로 저장한다."""
    today = datetime.now().strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"briefing-{today}.md"
    path.write_text(content, encoding="utf-8")
    print(f"  브리핑 저장: {path}")
    return path
